"""
FastAPI Dependency Injection – Authentication & Authorization
------------------------------------------------------------
Usage:
    from app.api.deps import get_current_user, require_role

    @router.get("/protected")
    async def protected(current_user: User = Depends(get_current_user)):
        ...

    @router.get("/admin-only")
    async def admin(current_user: User = Depends(require_role("admin"))):
        ...
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.user import User
from app.services.auth_service import AuthService

# OAuth2 token scheme – reads Bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate JWT access token and return the authenticated User model.
    Raises HTTP 401 if token is invalid, expired, or user is not found.
    """
    payload = AuthService.validate_access_token(token)

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: missing subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the authenticated user is active (not suspended/deleted)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact support.",
        )
    return current_user


def require_role(*allowed_roles: str):
    """
    Role-Based Access Control (RBAC) dependency factory.

    Example:
        @router.get("/rm-only")
        async def rm_endpoint(user = Depends(require_role("rm", "admin"))):
            ...
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}.",
            )
        return current_user

    return role_checker


# ── Convenience type aliases (for cleaner route signatures) ───────────────────
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_role("admin"))]
RMUser = Annotated[User, Depends(require_role("rm", "admin"))]
