from pydantic import Field

from app.schemas.common import APIModel


class AssetRead(APIModel):
    id: str
    symbol: str = Field(min_length=1, max_length=32)
    name: str
    network: str | None = None
    contract_address: str | None = None
