from fastapi import APIRouter, HTTPException, status

from app.connectors.base import ProviderNotConfiguredError, ProviderRequestError
from app.schemas.wallet import WalletSyncRequest, WalletSyncResponse
from app.services.wallet_service import refresh_public_wallet, wallet_capabilities

router = APIRouter()


@router.get("/capabilities")
def get_wallet_capabilities() -> dict[str, object]:
    return wallet_capabilities()


@router.post("/sync", response_model=WalletSyncResponse)
async def sync_wallet(request: WalletSyncRequest) -> WalletSyncResponse:
    """Fetch a current public-address snapshot without saving the address."""
    try:
        return await refresh_public_wallet(
            network_id=request.network,
            public_address=request.address,
            quote_currency=request.quote_currency,
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
