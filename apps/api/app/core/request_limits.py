"""Enforce a hard request-body limit before FastAPI parses multipart forms."""

import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import HTTPException, Request
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.database import get_session_factory
from app.core.rate_limit import enforce_rate_limit, request_client_ip


class RequestBodyLimitMiddleware:
    def __init__(self, app: Callable[..., Awaitable[None]], *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: dict[str, Any], receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                declared_bytes = int(content_length)
            except ValueError:
                await self._reject(send, 400, b'{"detail":"Invalid Content-Length header."}')
                return
            if declared_bytes < 0:
                await self._reject(send, 400, b'{"detail":"Invalid Content-Length header."}')
                return
            if declared_bytes > self.max_bytes:
                await self._reject(send, 413, b'{"detail":"Request body is too large."}')
                return

        if scope.get("method") == "POST":
            try:
                await run_in_threadpool(self._limit_upload_ip, scope, receive)
            except HTTPException as exc:
                body = json.dumps({"detail": exc.detail}).encode("utf-8")
                extra_headers = [
                    (key.lower().encode("ascii"), value.encode("latin-1"))
                    for key, value in (exc.headers or {}).items()
                ]
                await self._reject(send, exc.status_code, body, extra_headers)
                return

        chunks: list[bytes] = []
        total_bytes = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            total_bytes += len(chunk)
            if total_bytes > self.max_bytes:
                await self._reject(send, 413, b'{"detail":"Request body is too large."}')
                return
            chunks.append(chunk)
            if not message.get("more_body", False):
                break

        body = b"".join(chunks)
        replayed = False

        async def replay_receive() -> dict[str, Any]:
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        await self.app(scope, replay_receive, send)

    def _limit_upload_ip(self, scope: dict[str, Any], receive) -> None:
        path = scope.get("path", "")
        if path.endswith("/imports/preview"):
            limit_scope, max_requests, window_seconds = "csv-preview-ip", 20, 600
        elif "/portfolios/" in path and path.endswith("/imports"):
            limit_scope, max_requests, window_seconds = "csv-import-ip", 30, 3600
        else:
            return

        request = Request(scope, receive)
        subject = request_client_ip(request)
        if not settings.database_url:
            enforce_rate_limit(
                None,
                scope=limit_scope,
                subject=subject,
                max_requests=max_requests,
                window_seconds=window_seconds,
            )
            return

        with get_session_factory()() as session:
            enforce_rate_limit(
                session,
                scope=limit_scope,
                subject=subject,
                max_requests=max_requests,
                window_seconds=window_seconds,
            )

    async def _reject(
        self,
        send,
        status_code: int,
        body: bytes,
        extra_headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"connection", b"close"),
                    *(extra_headers or []),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body, "more_body": False})
