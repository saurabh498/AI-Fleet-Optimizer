"""
JWT authentication + password hashing.

Uses bcrypt for password hashing and PyJWT for tokens.
Env vars:
    SECRET_KEY           - required in production, defaults for local dev
    ACCESS_TOKEN_MINUTES - default 30
    REFRESH_TOKEN_DAYS   - default 7
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException, status

from backend.models.user import User


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-only-change-me-in-production-6f9c3d8a2b1e4f5a",
)
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))


# -------------------------------------------------
# Password hashing
# -------------------------------------------------

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


# -------------------------------------------------
# Token creation
# -------------------------------------------------

def _build_token(
    user: User,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user: User) -> str:
    return _build_token(
        user, "access", timedelta(minutes=ACCESS_TOKEN_MINUTES)
    )


def create_refresh_token(user: User) -> str:
    return _build_token(
        user, "refresh", timedelta(days=REFRESH_TOKEN_DAYS)
    )


# -------------------------------------------------
# Token decoding
# -------------------------------------------------

def decode_token(token: str, expected_type: Optional[str] = None) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if expected_type and payload.get("type") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Expected {expected_type} token",
        )

    return payload
