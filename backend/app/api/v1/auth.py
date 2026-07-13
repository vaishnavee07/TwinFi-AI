from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User, RefreshToken
from app.models.customer_profile import CustomerProfile
from datetime import datetime, timezone
import uuid

router = APIRouter()
auth_service = AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer",
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new TwinFi AI customer.
    - Validates email/phone uniqueness
    - Hashes password with bcrypt
    - Creates User + CustomerProfile records
    - Returns user details (no tokens — user must verify email first)
    """
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Check phone uniqueness
    existing_phone = await db.execute(select(User).where(User.phone == user_in.phone))
    if existing_phone.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this phone number already exists.",
        )

    # Create User
    new_user = User(
        id=uuid.uuid4(),
        email=user_in.email,
        phone=user_in.phone,
        password_hash=auth_service.get_password_hash(user_in.password),
        role="customer",
    )
    db.add(new_user)
    await db.flush()  # Get new_user.id before committing

    # Create linked CustomerProfile
    profile = CustomerProfile(
        id=uuid.uuid4(),
        user_id=new_user.id,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token, summary="Login and get JWT tokens")
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user credentials and return a JWT access + refresh token pair.
    - Verifies email + bcrypt password
    - Creates a stored refresh token (hashed in DB for security)
    - Returns Bearer tokens
    """
    # Find user
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()

    if not user or not auth_service.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )

    # Generate tokens
    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    access_token = auth_service.create_access_token(token_data)
    refresh_token = auth_service.create_refresh_token(token_data)

    # Store hashed refresh token in DB
    from app.config import settings
    from datetime import timedelta

    rt = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=auth_service.hash_token(refresh_token),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(rt)

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    user.failed_attempts = 0
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    Implements token rotation — the old refresh token is revoked.
    """
    # Validate the refresh token JWT
    payload = auth_service.validate_refresh_token(refresh_token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    # Check token exists in DB and is not revoked
    token_hash = auth_service.hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or does not exist.",
        )

    # Check expiry
    if stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired."
        )

    # Revoke old token (rotation)
    stored_token.revoked = True

    # Fetch user
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    # Issue new tokens
    from app.config import settings
    from datetime import timedelta

    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    new_access = auth_service.create_access_token(token_data)
    new_refresh = auth_service.create_refresh_token(token_data)

    new_rt = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=auth_service.hash_token(new_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_rt)
    await db.commit()

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout and revoke token")
async def logout(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Revoke the refresh token (logout). The access token will expire naturally
    (short-lived). For immediate access token invalidation, use a Redis denylist.
    """
    token_hash = auth_service.hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    stored_token = result.scalar_one_or_none()

    if stored_token:
        stored_token.revoked = True
        await db.commit()
    # Return 204 regardless — prevents token enumeration attacks
