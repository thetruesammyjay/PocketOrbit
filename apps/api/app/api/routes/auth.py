import hmac
import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import enforce_rate_limit, rate_limit_bucket_hash, request_client_ip
from app.core.security import (
    clear_session_cookie,
    create_session,
    get_current_user,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.models.activity import Transaction
from app.models.asset import Asset, AssetMapping
from app.models.audit_event import AuditEvent
from app.models.auth_action_token import AuthActionToken
from app.models.auth_session import AuthSession
from app.models.balance import Balance
from app.models.import_job import ImportJob
from app.models.portfolio import Portfolio
from app.models.price import Price
from app.models.rate_limit import RateLimitWindow
from app.models.source import Source
from app.models.sync_job import SyncJob
from app.models.user import User
from app.models.valuation import ValuationSnapshot
from app.models.wallet_snapshot import WalletSnapshot
from app.schemas.auth import (
    ActionResponse,
    DeleteAccountRequest,
    EmailActionRequest,
    PasswordResetRequest,
    RegisterRequest,
    RegistrationResponse,
    SignInRequest,
    TokenActionRequest,
    UserRead,
)
from app.services.auth_email import (
    EMAIL_VERIFY,
    PASSWORD_RESET,
    deliver_action_email,
    find_valid_action_token,
    issue_action_token,
)

router = APIRouter()


def _user_read(user: User, *, is_admin: bool = False) -> UserRead:
    return UserRead(id=str(user.id), email=user.email, is_admin=is_admin)


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    session: Session = Depends(get_db),
) -> RegistrationResponse:
    email = str(payload.email).strip().lower()
    enforce_rate_limit(
        session,
        scope="auth-register-ip",
        subject=request_client_ip(request),
        max_requests=10,
        window_seconds=3600,
    )
    enforce_rate_limit(
        session,
        scope="auth-register-email",
        subject=email,
        max_requests=5,
        window_seconds=3600,
    )
    if session.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="An account already uses this email."
        )

    user = User(email=email, password_hash=hash_password(payload.password))
    session.add(user)
    try:
        session.flush()
        session.add(Portfolio(user_id=user.id, name="My portfolio", reporting_currency="USD"))
        create_session(user, session, response)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already uses this email.",
        ) from exc
    return RegistrationResponse(
        id=str(user.id),
        email=email,
        verification_required=False,
        message="Your account is ready. You are signed in.",
    )


@router.post("/login", response_model=UserRead)
def login(
    payload: SignInRequest,
    request: Request,
    response: Response,
    session: Session = Depends(get_db),
) -> UserRead:
    email = str(payload.email).strip().lower()
    enforce_rate_limit(
        session,
        scope="auth-login-ip",
        subject=request_client_ip(request),
        max_requests=40,
        window_seconds=900,
    )
    enforce_rate_limit(
        session,
        scope="auth-login-email",
        subject=email,
        max_requests=12,
        window_seconds=900,
    )
    user = session.scalar(select(User).where(User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect."
        )
    create_session(user, session, response)
    return _user_read(user)


@router.post("/admin-login", response_model=UserRead)
def admin_login(
    payload: SignInRequest,
    request: Request,
    response: Response,
    session: Session = Depends(get_db),
) -> UserRead:
    email = str(payload.email).strip().lower()
    enforce_rate_limit(
        session,
        scope="auth-login-ip",
        subject=request_client_ip(request),
        max_requests=40,
        window_seconds=900,
    )
    enforce_rate_limit(
        session,
        scope="auth-login-email",
        subject=email,
        max_requests=12,
        window_seconds=900,
    )
    admin_emails = {
        address.strip().lower()
        for address in settings.admin_emails.split(",")
        if address.strip()
    }
    password_matches = bool(settings.admin_password) and hmac.compare_digest(
        payload.password.encode("utf-8"), settings.admin_password.encode("utf-8")
    )
    if email not in admin_emails or not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect.",
        )

    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        # The shared admin password stays in the API environment and is never stored.
        user = User(email=email, password_hash=hash_password(secrets.token_urlsafe(48)))
        session.add(user)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            user = session.scalar(select(User).where(User.email == email))
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Administrator sign-in is temporarily unavailable.",
                )

    create_session(user, session, response, is_admin=True)
    return _user_read(user, is_admin=True)


@router.post("/verification/resend", response_model=ActionResponse)
def resend_verification(
    payload: EmailActionRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db),
) -> ActionResponse:
    email = str(payload.email).strip().lower()
    _limit_email_action(session, request, "verification-resend", email)
    user = session.scalar(select(User).where(User.email == email))
    if user and user.email_verified_at is None and _smtp_available():
        token = issue_action_token(session, user, EMAIL_VERIFY)
        session.commit()
        background_tasks.add_task(deliver_action_email, email, token, EMAIL_VERIFY)
    if not _smtp_available():
        return ActionResponse(message="Email confirmation is not required for account access.")
    return ActionResponse(message="If the account needs verification, a link will be sent.")


@router.post("/verification/confirm", response_model=ActionResponse)
def confirm_verification(
    payload: TokenActionRequest,
    session: Session = Depends(get_db),
) -> ActionResponse:
    action_token = find_valid_action_token(session, payload.token, EMAIL_VERIFY)
    user = session.get(User, action_token.user_id) if action_token else None
    if not action_token or not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link is invalid or has expired.",
        )
    now = datetime.now(UTC)
    action_token.consumed_at = now
    user.email_verified_at = now
    session.commit()
    return ActionResponse(message="Your email is verified. You can sign in now.")


@router.post("/password/forgot", response_model=ActionResponse)
def request_password_reset(
    payload: EmailActionRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db),
) -> ActionResponse:
    email = str(payload.email).strip().lower()
    _limit_email_action(session, request, "password-forgot", email)
    user = session.scalar(select(User).where(User.email == email))
    if user and _smtp_available():
        token = issue_action_token(session, user, PASSWORD_RESET)
        session.commit()
        background_tasks.add_task(deliver_action_email, email, token, PASSWORD_RESET)
    if not _smtp_available():
        return ActionResponse(
            message="Password recovery is unavailable until email delivery is configured."
        )
    return ActionResponse(
        message="If an account uses this email, a password reset link will be sent."
    )


@router.post("/password/reset", response_model=ActionResponse)
def reset_password(
    payload: PasswordResetRequest,
    request: Request,
    session: Session = Depends(get_db),
) -> ActionResponse:
    enforce_rate_limit(
        session,
        scope="password-reset-ip",
        subject=request_client_ip(request),
        max_requests=15,
        window_seconds=900,
    )
    action_token = find_valid_action_token(session, payload.token, PASSWORD_RESET)
    user = session.get(User, action_token.user_id) if action_token else None
    if not action_token or not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link is invalid or has expired.",
        )
    action_token.consumed_at = datetime.now(UTC)
    user.password_hash = hash_password(payload.password)
    user.email_verified_at = user.email_verified_at or datetime.now(UTC)
    session.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    session.commit()
    return ActionResponse(message="Your password was changed. Sign in with the new password.")


@router.post("/account/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    payload: DeleteAccountRequest,
    response: Response,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The password is incorrect. Your account was not deleted.",
        )

    enforce_rate_limit(
        session,
        scope="account-delete",
        subject=str(user.id),
        max_requests=3,
        window_seconds=3600,
    )
    portfolio_ids = list(
        session.scalars(select(Portfolio.id).where(Portfolio.user_id == user.id)).all()
    )
    if portfolio_ids:
        source_ids = list(
            session.scalars(select(Source.id).where(Source.portfolio_id.in_(portfolio_ids))).all()
        )
        if source_ids:
            session.execute(delete(Transaction).where(Transaction.source_id.in_(source_ids)))
            session.execute(delete(Balance).where(Balance.source_id.in_(source_ids)))
            session.execute(delete(WalletSnapshot).where(WalletSnapshot.source_id.in_(source_ids)))
            session.execute(delete(SyncJob).where(SyncJob.source_id.in_(source_ids)))
        session.execute(delete(ImportJob).where(ImportJob.portfolio_id.in_(portfolio_ids)))
        session.execute(
            delete(ValuationSnapshot).where(ValuationSnapshot.portfolio_id.in_(portfolio_ids))
        )
        session.execute(delete(Source).where(Source.portfolio_id.in_(portfolio_ids)))
        session.execute(delete(Portfolio).where(Portfolio.id.in_(portfolio_ids)))
        imported_asset_ids = list(
            session.scalars(
                select(Asset.id).where(
                    or_(
                        *(
                            Asset.canonical_id.like(f"import:{portfolio_id}:%")
                            for portfolio_id in portfolio_ids
                        )
                    )
                )
            ).all()
        )
        if imported_asset_ids:
            session.execute(
                delete(AssetMapping).where(AssetMapping.asset_id.in_(imported_asset_ids))
            )
            session.execute(delete(Price).where(Price.asset_id.in_(imported_asset_ids)))
            session.execute(delete(Asset).where(Asset.id.in_(imported_asset_ids)))

    session.execute(delete(AuthActionToken).where(AuthActionToken.user_id == user.id))
    session.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    session.execute(delete(AuditEvent).where(AuditEvent.actor_id == user.id))
    private_rate_limit_scopes = (
        "auth-register-email",
        "auth-login-email",
        "verification-resend-email",
        "password-forgot-email",
        "wallet-sync-account",
        "csv-import-account",
        "account-delete",
    )
    private_bucket_hashes = [
        rate_limit_bucket_hash(scope, subject)
        for scope in private_rate_limit_scopes
        for subject in (user.email, str(user.id))
    ]
    session.execute(
        delete(RateLimitWindow).where(RateLimitWindow.bucket_hash.in_(private_bucket_hashes))
    )
    session.delete(user)
    session.commit()
    clear_session_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_db),
) -> Response:
    token = request.cookies.get(settings.auth_cookie_name)
    if token:
        digest = hash_session_token(token)
        auth_session = session.scalar(select(AuthSession).where(AuthSession.token_hash == digest))
        if auth_session:
            session.delete(auth_session)
            session.commit()
    clear_session_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserRead)
def me(request: Request, user: User = Depends(get_current_user)) -> UserRead:
    return _user_read(user, is_admin=bool(getattr(request.state, "is_admin_session", False)))


def _smtp_available() -> bool:
    return bool(settings.smtp_host and settings.smtp_from_email)


def _limit_email_action(session: Session, request: Request, action: str, email: str) -> None:
    enforce_rate_limit(
        session,
        scope=f"{action}-ip",
        subject=request_client_ip(request),
        max_requests=8,
        window_seconds=3600,
    )
    enforce_rate_limit(
        session,
        scope=f"{action}-email",
        subject=email,
        max_requests=5,
        window_seconds=3600,
    )
