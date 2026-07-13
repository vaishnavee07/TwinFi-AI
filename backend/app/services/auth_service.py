import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.config import settings

# Bcrypt password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handles password hashing, JWT creation/validation, and token management."""

    # ── Password Utilities ──────────────────────────────────────────────────
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against its bcrypt hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a plain-text password using bcrypt."""
        return pwd_context.hash(password)

    # ── JWT Creation ────────────────────────────────────────────────────────
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """Create a short-lived JWT access token (default: 15 min)."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a long-lived JWT refresh token (default: 7 days)."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # ── Token Hashing (for DB storage) ──────────────────────────────────────
    @staticmethod
    def hash_token(token: str) -> str:
        """SHA-256 hash a token for safe storage in the database."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token (for OTPs, reset links)."""
        return secrets.token_urlsafe(length)

    # ── JWT Decoding & Validation ────────────────────────────────────────────
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and validate a JWT token.
        Raises HTTP 401 on expiry, invalid signature, or malformed token.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not decode token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def validate_access_token(token: str) -> dict:
        """Validate token and ensure it is an access token (not a refresh token)."""
        payload = AuthService.decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    @staticmethod
    def validate_refresh_token(token: str) -> dict:
        """Validate token and ensure it is a refresh token."""
        payload = AuthService.decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
