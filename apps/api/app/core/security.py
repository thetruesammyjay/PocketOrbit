"""Security dependencies are wired here when the authentication provider is selected."""

from fastapi import HTTPException, status


def authentication_not_configured() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication is not configured in this scaffold.",
    )
