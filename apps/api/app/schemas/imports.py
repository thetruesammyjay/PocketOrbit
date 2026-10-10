from datetime import datetime
from decimal import Decimal

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
    transaction_hash: str | None = Field(default=None, max_length=128)
    fee_quantity: str | None = Field(default=None, max_length=128)
    fee_asset: str | None = Field(default=None, max_length=128)
    quote_amount: str | None = Field(default=None, max_length=128)
    quote_currency: str | None = Field(default=None, max_length=128)


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
    rows_duplicate: int = 0
    unmatched_assets: list[str]
    warnings: list[str]
    rejected_rows: list[dict[str, object]]
    coverage_start_at: datetime | None = None
    coverage_end_at: datetime | None = None
    history_complete: bool = False


class ImportJobRead(APIModel):
    id: str
    filename: str
    status: str
    rows_received: int
    rows_accepted: int
    rows_rejected: int
    rows_duplicate: int = 0
    created_at: datetime
    coverage_start_at: datetime | None = None
    coverage_end_at: datetime | None = None
    history_complete: bool = False


class TransactionReview(APIModel):
    accepted: bool


class TransferReview(APIModel):
    accepted: bool


class TransferMatchRead(APIModel):
    id: str
    outgoing_transaction_id: str
    incoming_transaction_id: str
    asset_symbol: str
    quantity_sent: str
    quantity_received: str
    outgoing_source: str
    incoming_source: str
    occurred_at: datetime
    confidence: float
    rationale: str
    status: str


class PerformanceLotRead(APIModel):
    asset_symbol: str
    quantity: Decimal
    cost_basis: Decimal | None
    market_value: Decimal | None
    pnl: Decimal | None
    source_names: list[str]


class RealizedPnlRead(APIModel):
    transaction_id: str
    asset_symbol: str
    source_name: str
    quantity: Decimal
    proceeds: Decimal | None
    cost_basis: Decimal | None
    pnl: Decimal | None
    method: str = "FIFO"


class PerformanceCoverageRead(APIModel):
    source_name: str
    start_at: datetime | None = None
    end_at: datetime | None = None
    complete_history_asserted: bool
    rows_imported: int
    rows_rejected: int


class PerformanceRead(APIModel):
    status: str
    method: str = "FIFO"
    currency: str
    realized_pnl: Decimal | None = None
    unrealized_pnl: Decimal | None = None
    total_pnl: Decimal | None = None
    open_positions: list[PerformanceLotRead]
    realized_events: list[RealizedPnlRead]
    coverage: list[PerformanceCoverageRead]
    reasons: list[str]
    calculated_at: datetime
