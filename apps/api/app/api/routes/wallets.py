from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.connectors.base import ProviderNotConfiguredError, ProviderRequestError
from app.core.database import get_optional_db
from app.core.rate_limit import enforce_rate_limit, request_client_ip
from app.schemas.wallet import WalletSyncRequest, WalletSyncResponse
from app.services.wallet_service import refresh_public_wallet, wallet_capabilities

router = APIRouter()


@router.get("/capabilities")
def get_wallet_capabilities() -> dict[str, object]:
    return wallet_capabilities()


@router.post("/sync", response_model=WalletSyncResponse)
async def sync_wallet(
    payload: WalletSyncRequest,
    request: Request,
    session: Session | None = Depends(get_optional_db),
) -> WalletSyncResponse:
    """Fetch a current public-address snapshot without saving the address."""
    enforce_rate_limit(
        session,
        scope="wallet-sync-preview-ip",
        subject=request_client_ip(request),
        max_requests=30,
        window_seconds=3600,
    )
    try:
        return await refresh_public_wallet(
            network_id=payload.network,
            public_address=payload.address,
            quote_currency=payload.quote_currency,
        )
    except ProviderNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ProviderRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
