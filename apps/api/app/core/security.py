"""Password hashing and opaque, database-backed browser sessions."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.auth_session import AuthSession
from app.models.user import User

SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        maxmem=128 * 1024 * 1024,
        dklen=64,
    )
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${derived.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        algorithm, n, r, p, salt_hex, expected_hex = password_hash.split("$", 5)
        if (
            algorithm != "scrypt"
            or int(n) != SCRYPT_N
            or int(r) != SCRYPT_R
            or int(p) != SCRYPT_P
            or len(salt_hex) != 32
            or len(expected_hex) != 128
        ):
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            maxmem=128 * 1024 * 1024,
            dklen=len(expected),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def hash_session_token(token: str) -> str:
    return hmac.new(
        settings.secret_key.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_session(user: User, session: Session, response: Response) -> None:
    token = secrets.token_urlsafe(48)
    expires_at = datetime.now(UTC) + timedelta(days=settings.auth_session_days)
    session.add(
        AuthSession(user_id=user.id, token_hash=hash_session_token(token), expires_at=expires_at)
    )
    session.commit()
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=settings.auth_session_days * 24 * 60 * 60,
        expires=expires_at,
        httponly=True,
        secure=settings.app_env.strip().lower() in {"production", "prod"},
        samesite=settings.auth_cookie_samesite.lower(),
        domain=settings.auth_cookie_domain,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        domain=settings.auth_cookie_domain,
        path="/",
        secure=settings.app_env.strip().lower() in {"production", "prod"},
        httponly=True,
        samesite=settings.auth_cookie_samesite.lower(),
    )


def get_current_user(request: Request, session: Session = Depends(get_db)) -> User:
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue.")
    auth_session = session.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_session_token(token))
    )
    now = datetime.now(UTC)
    expires_at = auth_session.expires_at if auth_session else None
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if not auth_session or expires_at <= now:
        if auth_session:
            session.delete(auth_session)
            session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired."
        )
    user = session.get(User, auth_session.user_id)
    if not user:
        session.delete(auth_session)
        session.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue.")
    return user
