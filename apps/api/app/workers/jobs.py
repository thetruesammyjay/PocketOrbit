"""Job hooks. Scheduling is intentionally not enabled in the initial scaffold."""

from app.workflows.portfolio_refresh_workflow import refresh_demo_portfolio


def refresh_demo_job() -> dict[str, object]:
    return refresh_demo_portfolio()
