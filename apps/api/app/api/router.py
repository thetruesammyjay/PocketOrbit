from fastapi import APIRouter

from app.api.routes import admin, auth, health, imports, portfolios, reports, sources, wallets

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(imports.router, prefix="/imports", tags=["imports"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
