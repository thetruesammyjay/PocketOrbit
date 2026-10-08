"""One-time account action tokens and SMTP delivery."""

import hashlib
import hmac
import logging
import secrets
import smtplib
import ssl
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from urllib.parse import quote

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_action_token import AuthActionToken
from app.models.user import User

logger = logging.getLogger(__name__)

EMAIL_VERIFY = "email_verify"
PASSWORD_RESET = "password_reset"


def issue_action_token(session: Session, user: User, purpose: str) -> str:
    now = datetime.now(UTC)
    session.execute(delete(AuthActionToken).where(AuthActionToken.expires_at < now))
    session.execute(
        delete(AuthActionToken).where(
            AuthActionToken.user_id == user.id,
            AuthActionToken.purpose == purpose,
            AuthActionToken.consumed_at.is_(None),
        )
    )
    raw_token = secrets.token_urlsafe(48)
    lifetime = timedelta(hours=24) if purpose == EMAIL_VERIFY else timedelta(minutes=30)
    session.add(
        AuthActionToken(
            user_id=user.id,
            token_hash=hash_action_token(raw_token),
            purpose=purpose,
            expires_at=now + lifetime,
        )
    )
    return raw_token


def hash_action_token(token: str) -> str:
    return hmac.new(settings.secret_key.encode(), token.encode(), hashlib.sha256).hexdigest()


def find_valid_action_token(
    session: Session, raw_token: str, purpose: str
) -> AuthActionToken | None:
    token = session.scalar(
        select(AuthActionToken)
        .where(
            AuthActionToken.token_hash == hash_action_token(raw_token),
            AuthActionToken.purpose == purpose,
            AuthActionToken.consumed_at.is_(None),
        )
        .with_for_update()
    )
    if token is None:
        return None
    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return token if expires_at > datetime.now(UTC) else None


def deliver_action_email(recipient: str, raw_token: str, purpose: str) -> None:
    """Send a verification or password-reset link without logging its contents."""
    if purpose == EMAIL_VERIFY:
        path = "/verify-email"
        subject = "Verify your PocketOrbit email"
        introduction = "Confirm your email address to finish setting up your PocketOrbit account."
    else:
        path = "/reset-password"
        subject = "Reset your PocketOrbit password"
        introduction = "Use this link to choose a new password for your PocketOrbit account."

    link = f"{settings.web_origin.rstrip('/')}{path}#token={quote(raw_token, safe='')}"
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email or ""
    message["To"] = recipient
    message.set_content(
        f"{introduction}\n\n{link}\n\n"
        "If you did not request this, you can ignore this email. "
        "PocketOrbit will never ask for your seed phrase or private keys."
    )

    if not settings.smtp_host or not settings.smtp_from_email:
        logger.warning("Account action email delivery is not configured")
        return

    try:
        context = ssl.create_default_context()
        if settings.smtp_security.strip().lower() == "ssl":
            with smtplib.SMTP_SSL(
                settings.smtp_host, settings.smtp_port, timeout=10, context=context
            ) as smtp:
                _send_message(smtp, message)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                _send_message(smtp, message)
    except (OSError, smtplib.SMTPException):
        # The API response is intentionally generic; users can request a fresh link.
        logger.warning("Account action email delivery failed")


def _send_message(smtp: smtplib.SMTP, message: EmailMessage) -> None:
    if settings.smtp_username and settings.smtp_password:
        smtp.login(settings.smtp_username, settings.smtp_password)
    smtp.send_message(message)
