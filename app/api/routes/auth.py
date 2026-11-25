"""
GlobeTrotter AI - Admin Authentication Router.
Provides secure credential verification against environment settings (.env)
and HMAC-SHA256 session token generation for the Admin Control Portal.
"""

import hmac
import hashlib
import time
import base64
import json
import secrets
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, Field
from app.config import get_settings
from app.utils.logging import logger

router = APIRouter(prefix="/auth", tags=["Admin Authentication"])


class LoginRequest(BaseModel):
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")


class LoginResponse(BaseModel):
    status: str
    token: str
    username: str
    expires_in: int


class VerifyResponse(BaseModel):
    valid: bool
    username: str


def generate_admin_token(username: str, secret: str, ttl_seconds: int = 86400) -> str:
    """
    Generates a cryptographically signed HMAC-SHA256 session token.
    Token format: base64(payload).signature
    """
    payload = {
        "sub": username,
        "exp": int(time.time()) + ttl_seconds,
        "iat": int(time.time()),
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")
    sig = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def verify_admin_token(token: str, secret: str) -> Optional[str]:
    """
    Validates token signature and expiration.
    Returns username if valid, None if invalid or expired.
    """
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig = parts
        expected_sig = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None

        # Re-add padding for base64 decode
        padding = "=" * (4 - len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode((payload_b64 + padding).encode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))

        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload.get("sub")
    except Exception as exc:
        logger.warning(f"[Auth] Token verification failed: {exc}")
        return None


@router.post("/login", response_model=LoginResponse)
def login_admin(payload: LoginRequest):
    """
    Verifies admin credentials from .env settings.
    Uses timing-attack safe constant-time string comparison.
    """
    settings = get_settings()

    # Constant-time comparison prevents timing analysis attacks
    username_match = secrets.compare_digest(payload.username.strip(), settings.ADMIN_USERNAME.strip())
    password_match = secrets.compare_digest(payload.password, settings.ADMIN_PASSWORD)

    if not (username_match and password_match):
        logger.warning(f"[Auth] Failed admin login attempt for username '{payload.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin username or password. Please check your credentials in .env.",
        )

    token = generate_admin_token(settings.ADMIN_USERNAME, settings.JWT_SECRET_KEY, ttl_seconds=86400)
    logger.info(f"[Auth] Admin user '{settings.ADMIN_USERNAME}' successfully authenticated.")

    return LoginResponse(
        status="success",
        token=token,
        username=settings.ADMIN_USERNAME,
        expires_in=86400,
    )


@router.get("/verify", response_model=VerifyResponse)
def verify_session(authorization: Optional[str] = Header(None)):
    """
    Validates whether the current request holds a valid signed admin session.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
        )

    token = parts[1]
    settings = get_settings()
    username = verify_admin_token(token, settings.JWT_SECRET_KEY)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin session expired or invalid. Please log in again.",
        )

    return VerifyResponse(valid=True, username=username)
