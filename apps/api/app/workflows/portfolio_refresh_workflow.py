from app.services.portfolio_service import get_demo_portfolio_summary


def refresh_demo_portfolio() -> dict[str, object]:
    """Recalculate the documented demo fixture using deterministic calculations."""
    return get_demo_portfolio_summary()
