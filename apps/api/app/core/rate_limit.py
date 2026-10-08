"""Shared API rate limits backed by PostgreSQL in production."""

import hashlib
import hmac
import ipaddress
import secrets
import threading
import time

from fastapi import HTTPException, Request, status
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.rate_limit import RateLimitWindow

_local_lock = threading.Lock()
_local_windows: dict[str, tuple[int, int]] = {}


def request_client_ip(request: Request) -> str:
    """Use forwarding data only when the direct peer is explicitly trusted."""
    peer = request.client.host if request.client else "unknown"
    peer_ip = _parse_ip(peer)
    trusted = _trusted_proxy_networks()
    if peer_ip is None or not any(peer_ip in network for network in trusted):
        return peer_ip.compressed if peer_ip else "unknown"

    forwarded = request.headers.get("x-forwarded-for", "")
    chain = [ip for value in forwarded.split(",") if (ip := _parse_ip(value.strip()))]
    chain.append(peer_ip)
    for candidate in reversed(chain):
        if not any(candidate in network for network in trusted):
            return candidate.compressed
    return chain[0].compressed if chain else peer_ip.compressed


def enforce_rate_limit(
    session: Session | None,
    *,
    scope: str,
    subject: str,
    max_requests: int,
    window_seconds: int,
) -> None:
    """Atomically count a request and reject once the fixed window is full.

    A local in-memory counter is used only for development without a database.
    Configured databases fail closed if their shared counter cannot be updated.
    """
    now = int(time.time())
    window_start = now - (now % window_seconds)
    digest = rate_limit_bucket_hash(scope, subject)

    if session is None:
        allowed = _increment_local(digest, window_start, max_requests)
    else:
        allowed = _increment_shared(session, digest, window_start, max_requests, now)

    if not allowed:
        retry_after = max(1, window_start + window_seconds - now)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again after the current limit window.",
            headers={"Retry-After": str(retry_after)},
        )


def rate_limit_bucket_hash(scope: str, subject: str) -> str:
    return hmac.new(
        settings.secret_key.encode("utf-8"),
        f"rate-limit:{scope}:{subject}".encode(),
        hashlib.sha256,
    ).hexdigest()


def _increment_shared(
    session: Session, digest: str, window_start: int, max_requests: int, now: int
) -> bool:
    try:
        dialect = session.get_bind().dialect.name
        if dialect == "postgresql":
            insert_statement = postgres_insert(RateLimitWindow)
        elif dialect == "sqlite":
            insert_statement = sqlite_insert(RateLimitWindow)
        else:
            raise RuntimeError("Shared rate limits require PostgreSQL or SQLite.")

        statement = insert_statement.values(
            bucket_hash=digest,
            window_start=window_start,
            hit_count=1,
        ).on_conflict_do_update(
            index_elements=[RateLimitWindow.bucket_hash, RateLimitWindow.window_start],
            set_={"hit_count": RateLimitWindow.hit_count + 1},
            where=RateLimitWindow.hit_count < max_requests,
        )
        statement = statement.returning(RateLimitWindow.hit_count)
        count = session.execute(statement).scalar_one_or_none()

        # Opportunistic bounded cleanup prevents expired counters accumulating forever.
        if secrets.randbelow(1024) == 0:
            session.execute(
                delete(RateLimitWindow).where(RateLimitWindow.window_start < now - 86_400)
            )
        session.commit()
        return count is not None
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Request protection is temporarily unavailable.",
        ) from exc
    except RuntimeError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Request protection is not configured for this database.",
        ) from exc


def _increment_local(digest: str, window_start: int, max_requests: int) -> bool:
    with _local_lock:
        if len(_local_windows) > 10_000:
            stale_before = window_start - 86_400
            for key, (key_window, _) in list(_local_windows.items()):
                if key_window < stale_before:
                    _local_windows.pop(key, None)
        saved_window, count = _local_windows.get(digest, (window_start, 0))
        if saved_window != window_start:
            saved_window, count = window_start, 0
        if count >= max_requests:
            return False
        _local_windows[digest] = (saved_window, count + 1)
        return True


def _trusted_proxy_networks() -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    for value in settings.trusted_proxy_cidrs.split(","):
        item = value.strip()
        if not item:
            continue
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            continue
    return networks


def _parse_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value.strip().strip("[]"))
    except ValueError:
        return None
