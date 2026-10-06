from fastapi import APIRouter

from app.services.portfolio_service import get_demo_portfolio_summary

router = APIRouter()


@router.get("/demo/summary")
def demo_portfolio_summary() -> dict[str, object]:
    """Return a deterministic sample portfolio, never live account data."""
    return get_demo_portfolio_summary()
