from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.request_limits import RequestBodyLimitMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    settings.validate_runtime_configuration()
    yield


app = FastAPI(
    title=settings.app_name,
    description="A read-only API for normalized portfolio data and source provenance.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class SameOriginMutationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if not origin:
                referer = request.headers.get("referer")
                if referer:
                    parsed_referer = urlparse(referer)
                    origin = f"{parsed_referer.scheme}://{parsed_referer.netloc}"
            expected = urlparse(settings.web_origin)
            received = urlparse(origin) if origin else None
            same_origin = bool(
                received
                and received.scheme == expected.scheme
                and received.netloc == expected.netloc
            )
            is_production = settings.app_env.strip().lower() in {"production", "prod"}
            if (origin and not same_origin) or (is_production and not same_origin):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "This request did not come from the configured web app."},
                )
        return await call_next(request)


app.add_middleware(RequestBodyLimitMiddleware, max_bytes=settings.max_request_body_bytes)
app.add_middleware(SameOriginMutationMiddleware)
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"name": "PocketOrbit API", "docs": "/docs", "health": "/api/v1/health"}
