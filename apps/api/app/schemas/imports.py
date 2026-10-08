from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import APIModel


class ImportPreviewRead(BaseModel):
    filename: str
    columns: list[str]
    rows_received: int
    preview: list[dict[str, str | None]]
    warnings: list[str]
    records_added: bool = False


class CsvFieldMapping(APIModel):
    occurred_at: str = Field(min_length=1, max_length=128)
    asset: str = Field(min_length=1, max_length=128)
    quantity: str = Field(min_length=1, max_length=128)
    kind: str | None = Field(default=None, max_length=128)
    network: str | None = Field(default=None, max_length=128)
    contract_address: str | None = Field(default=None, max_length=128)
    transaction_id: str | None = Field(default=None, max_length=128)


class CsvBalanceFieldMapping(APIModel):
    asset: str = Field(min_length=1, max_length=128)
    quantity: str = Field(min_length=1, max_length=128)
    network: str | None = Field(default=None, max_length=128)
    contract_address: str | None = Field(default=None, max_length=128)


class ImportResultRead(APIModel):
    import_id: str
    source_id: str
    filename: str
    rows_received: int
    rows_accepted: int
    rows_rejected: int
    unmatched_assets: list[str]
    warnings: list[str]
    rejected_rows: list[dict[str, object]]


class ImportJobRead(APIModel):
    id: str
    filename: str
    status: str
    rows_received: int
    rows_accepted: int
    rows_rejected: int
    created_at: datetime
