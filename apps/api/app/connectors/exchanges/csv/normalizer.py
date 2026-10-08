import csv
import io
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from app.schemas.imports import CsvBalanceFieldMapping, CsvFieldMapping
from app.schemas.wallet import EVM_ADDRESS_PATTERN, _is_solana_public_key

MAX_IMPORT_ROWS = 20_000
MAX_IMPORT_COLUMNS = 256
HEADER_ALIASES = {
    "occurred_at": ("date", "time", "timestamp", "datetime", "created_at", "transaction_date"),
    "asset": ("asset", "currency", "symbol", "coin", "token", "asset_symbol"),
    "quantity": ("amount", "quantity", "size", "volume", "units", "change"),
    "kind": ("type", "transaction_type", "side", "action", "direction", "operation"),
    "network": ("network", "chain", "blockchain"),
    "contract_address": ("contract", "contract_address", "mint", "token_address"),
    "transaction_id": ("transaction_id", "txid", "tx_hash", "id", "reference"),
}
INBOUND_KINDS = {
    "buy",
    "deposit",
    "receive",
    "received",
    "reward",
    "staking",
    "transfer_in",
    "swap_in",
}
OUTBOUND_KINDS = {"sell", "withdrawal", "send", "sent", "transfer_out", "swap_out", "fee"}
KIND_ALIASES = {
    "withdraw": "withdrawal",
    "withdrawal": "withdrawal",
    "deposit": "deposit",
    "receive": "receive",
    "received": "received",
    "send": "send",
    "sent": "sent",
    "buy": "buy",
    "purchase": "buy",
    "sell": "sell",
    "sale": "sell",
    "transfer in": "transfer_in",
    "transfer_in": "transfer_in",
    "transfer out": "transfer_out",
    "transfer_out": "transfer_out",
    "reward": "reward",
    "staking reward": "staking",
    "staking": "staking",
    "swap in": "swap_in",
    "swap_in": "swap_in",
    "swap out": "swap_out",
    "swap_out": "swap_out",
    "fee": "fee",
}
SUPPORTED_NETWORKS = {"solana", "ethereum", "base", "arbitrum"}
THOUSANDS_SEPARATOR_PATTERN = re.compile(
    r"^[+-]?\d{1,3}(?:,\d{3})+(?:\.\d*)?(?:[eE][+-]?\d+)?$"
)


@dataclass(frozen=True)
class NormalizedCsvTransaction:
    row_number: int
    source_record_id: str
    occurred_at: datetime
    symbol: str
    quantity: Decimal
    kind: str
    network_id: str | None
    contract_address: str | None
    quality_status: str


@dataclass(frozen=True)
class CsvParseResult:
    rows_received: int
    accepted: tuple[NormalizedCsvTransaction, ...]
    rejected: tuple[dict[str, object], ...]
    warnings: tuple[str, ...]
    unmatched_assets: tuple[str, ...]


@dataclass(frozen=True)
class NormalizedCsvBalance:
    row_number: int
    symbol: str
    quantity: Decimal
    network_id: str | None
    contract_address: str | None


@dataclass(frozen=True)
class CsvBalanceParseResult:
    rows_received: int
    accepted: tuple[NormalizedCsvBalance, ...]
    rejected: tuple[dict[str, object], ...]
    warnings: tuple[str, ...]
    unmatched_assets: tuple[str, ...]


def suggest_mapping(columns: list[str]) -> dict[str, str | None]:
    normalized = {_normalize_header(column): column for column in columns if column}
    suggestions: dict[str, str | None] = {}
    for field, aliases in HEADER_ALIASES.items():
        suggestions[field] = next(
            (normalized[alias] for alias in aliases if alias in normalized), None
        )
    return suggestions


def parse_csv_transactions(contents: bytes, mapping: CsvFieldMapping) -> CsvParseResult:
    try:
        text = contents.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("Save the exchange file as UTF-8 CSV and try again.") from exc

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        columns = reader.fieldnames or []
        if not columns or any(not (column or "").strip() for column in columns):
            raise ValueError("The CSV needs a header row with named columns.")
        if len(columns) > MAX_IMPORT_COLUMNS:
            raise ValueError(f"A file can contain up to {MAX_IMPORT_COLUMNS} columns.")
        if len({_normalize_header(column) for column in columns}) != len(columns):
            raise ValueError("The CSV contains duplicate column names. Rename them and try again.")
    except csv.Error as exc:
        raise ValueError("The CSV has invalid quoting or row formatting.") from exc

    mapped_columns = [
        mapping.occurred_at,
        mapping.asset,
        mapping.quantity,
        mapping.kind,
        mapping.network,
        mapping.contract_address,
        mapping.transaction_id,
    ]
    missing = [column for column in mapped_columns if column and column not in columns]
    if missing:
        raise ValueError("One or more selected columns are not in this CSV.")
    accepted: list[NormalizedCsvTransaction] = []
    rejected: list[dict[str, object]] = []
    unmatched_assets: set[str] = set()
    warnings: set[str] = set()
    seen_record_ids: set[str] = set()
    rows_received = 0
    try:
        for row_number, row in enumerate(reader, start=2):
            rows_received += 1
            if rows_received > MAX_IMPORT_ROWS:
                raise ValueError(f"A file can contain up to {MAX_IMPORT_ROWS:,} transaction rows.")
            try:
                if None in row:
                    raise ValueError("This row has more values than the CSV header.")
                normalized = _normalize_row(row, row_number, mapping)
                if normalized.source_record_id in seen_record_ids:
                    raise ValueError("This transaction ID appears more than once in the CSV.")
                seen_record_ids.add(normalized.source_record_id)
                accepted.append(normalized)
                if normalized.quality_status != "fresh":
                    unmatched_assets.add(normalized.symbol)
            except ValueError as exc:
                if len(rejected) < 100:
                    rejected.append({"row": row_number, "reason": str(exc)})
    except csv.Error as exc:
        raise ValueError("The CSV has invalid quoting or row formatting.") from exc

    if not accepted and not rejected:
        raise ValueError("The CSV has no transaction rows.")
    if unmatched_assets:
        warnings.add(
            "Rows with a ticker only are saved as unmatched until the asset identity is confirmed."
        )
    if rejected:
        warnings.add(
            "Rejected rows were not added. Review the row numbers and reasons "
            "before importing again."
        )
    if not accepted:
        warnings.add("No transaction rows passed validation, so nothing was imported.")
    return CsvParseResult(
        rows_received=rows_received,
        accepted=tuple(accepted),
        rejected=tuple(rejected),
        warnings=tuple(sorted(warnings)),
        unmatched_assets=tuple(sorted(unmatched_assets)),
    )


def parse_csv_balances(contents: bytes, mapping: CsvBalanceFieldMapping) -> CsvBalanceParseResult:
    """Validate an exchange's current-balance statement without treating it as a ledger."""
    try:
        text = contents.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("Save the exchange file as UTF-8 CSV and try again.") from exc

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        columns = reader.fieldnames or []
        if not columns or any(not (column or "").strip() for column in columns):
            raise ValueError("The CSV needs a header row with named columns.")
        if len(columns) > MAX_IMPORT_COLUMNS:
            raise ValueError(f"A file can contain up to {MAX_IMPORT_COLUMNS} columns.")
        if len({_normalize_header(column) for column in columns}) != len(columns):
            raise ValueError("The CSV contains duplicate column names. Rename them and try again.")
    except csv.Error as exc:
        raise ValueError("The CSV has invalid quoting or row formatting.") from exc

    mapped_columns = [mapping.asset, mapping.quantity, mapping.network, mapping.contract_address]
    missing = [column for column in mapped_columns if column and column not in columns]
    if missing:
        raise ValueError("One or more selected columns are not in this CSV.")

    native_symbols = {
        ("solana", "SOL"),
        ("ethereum", "ETH"),
        ("base", "ETH"),
        ("arbitrum", "ETH"),
    }
    accepted: list[NormalizedCsvBalance] = []
    rejected: list[dict[str, object]] = []
    unmatched_assets: set[str] = set()
    rows_received = 0
    try:
        for row_number, row in enumerate(reader, start=2):
            rows_received += 1
            if rows_received > MAX_IMPORT_ROWS:
                raise ValueError(f"A file can contain up to {MAX_IMPORT_ROWS:,} balance rows.")
            try:
                if None in row:
                    raise ValueError("This row has more values than the CSV header.")
                symbol = (row.get(mapping.asset) or "").strip().upper()
                if not re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{0,31}", symbol):
                    raise ValueError("Asset symbol is missing or invalid.")

                raw_quantity = (row.get(mapping.quantity) or "").strip()
                quantity = _parse_decimal_value(raw_quantity, "Balance")
                if not quantity.is_finite() or quantity < 0:
                    raise ValueError("Balance must be a finite, non-negative number.")
                if quantity != 0 and (
                    quantity.adjusted() >= 20 or max(0, -quantity.as_tuple().exponent) > 18
                ):
                    raise ValueError(
                        "Balance exceeds supported precision (20 whole digits and "
                        "18 decimal places)."
                    )

                raw_network = (row.get(mapping.network or "") or "").strip().lower()
                network = _normalize_network(raw_network) if raw_network else None
                if raw_network and network is None:
                    raise ValueError("The network is not supported for wallet valuation.")
                contract = (row.get(mapping.contract_address or "") or "").strip()
                if contract:
                    if not network:
                        raise ValueError("A token contract needs a supported network column.")
                    if network == "solana":
                        if not _is_solana_public_key(contract):
                            raise ValueError("The token mint is not a valid Solana address.")
                    elif not EVM_ADDRESS_PATTERN.fullmatch(contract):
                        raise ValueError("The token contract is not a valid EVM address.")
                    if network != "solana":
                        contract = contract.lower()
                elif (network, symbol) not in native_symbols:
                    unmatched_assets.add(symbol)

                accepted.append(
                    NormalizedCsvBalance(
                        row_number=row_number,
                        symbol=symbol,
                        quantity=quantity,
                        network_id=network,
                        contract_address=contract or None,
                    )
                )
            except ValueError as exc:
                if len(rejected) < 100:
                    rejected.append({"row": row_number, "reason": str(exc)})
    except csv.Error as exc:
        raise ValueError("The CSV has invalid quoting or row formatting.") from exc

    if rows_received == 0:
        raise ValueError("The CSV has no balance rows.")
    warnings: set[str] = {
        "Balance statements are user-provided and are not independently verified."
    }
    if unmatched_assets:
        warnings.add(
            "Ticker-only assets stay unpriced until their network and exact identity are confirmed."
        )
    if rejected:
        warnings.add("Rejected rows were not added. Review the row numbers and reasons.")
    if not accepted:
        warnings.add("No balance rows passed validation, so no balances were saved.")
    return CsvBalanceParseResult(
        rows_received=rows_received,
        accepted=tuple(accepted),
        rejected=tuple(rejected),
        warnings=tuple(sorted(warnings)),
        unmatched_assets=tuple(sorted(unmatched_assets)),
    )


def _normalize_row(
    row: dict[str, str | None], row_number: int, mapping: CsvFieldMapping
) -> NormalizedCsvTransaction:
    raw_symbol = (row.get(mapping.asset) or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{0,31}", raw_symbol):
        raise ValueError("Asset symbol is missing or invalid.")

    raw_quantity = (row.get(mapping.quantity) or "").strip()
    quantity = _parse_decimal_value(raw_quantity, "Quantity")
    if not quantity.is_finite() or quantity == 0:
        raise ValueError("Quantity must be a finite, non-zero number.")
    if quantity.adjusted() >= 20 or max(0, -quantity.as_tuple().exponent) > 18:
        raise ValueError(
            "Quantity exceeds supported precision (20 whole digits and 18 decimal places)."
        )

    if mapping.kind:
        raw_kind = (row.get(mapping.kind) or "").strip().lower()
        kind = KIND_ALIASES.get(raw_kind)
        if kind not in INBOUND_KINDS | OUTBOUND_KINDS:
            raise ValueError(
                "Transaction type is ambiguous. Map a buy, sell, deposit, withdrawal, "
                "receive, or send type."
            )
        if quantity < 0 and kind in INBOUND_KINDS:
            raise ValueError("A negative quantity conflicts with an incoming transaction type.")
        signed_quantity = abs(quantity) if kind in INBOUND_KINDS else -abs(quantity)
    else:
        if quantity > 0:
            raise ValueError("A transaction type is needed when the amount is positive.")
        kind = "received" if quantity > 0 else "sent"
        signed_quantity = quantity

    occurred_at = _parse_datetime((row.get(mapping.occurred_at) or "").strip())
    raw_id = (row.get(mapping.transaction_id or "") or "").strip()
    if len(raw_id) > 256 or any(ord(character) < 32 for character in raw_id):
        raise ValueError("Transaction ID is too long or contains control characters.")
    source_record_id = raw_id if raw_id else f"row:{row_number}"

    network_value = (row.get(mapping.network or "") or "").strip().lower()
    network = _normalize_network(network_value) if network_value else None
    contract = (row.get(mapping.contract_address or "") or "").strip()
    if contract:
        if not network or network not in SUPPORTED_NETWORKS:
            raise ValueError(
                "A contract or mint needs a supported network in the mapped network column."
            )
        if network == "solana":
            if not _is_solana_public_key(contract):
                raise ValueError("The token mint is not a valid Solana address.")
        elif not EVM_ADDRESS_PATTERN.fullmatch(contract):
            raise ValueError("The token contract is not a valid EVM address.")
        if network != "solana":
            contract = contract.lower()
        quality_status = "fresh"
    else:
        network = network if network in SUPPORTED_NETWORKS else None
        quality_status = "unmatched"

    return NormalizedCsvTransaction(
        row_number=row_number,
        source_record_id=source_record_id,
        occurred_at=occurred_at,
        symbol=raw_symbol,
        quantity=signed_quantity,
        kind=kind,
        network_id=network,
        contract_address=contract or None,
        quality_status=quality_status,
    )


def _parse_datetime(value: str) -> datetime:
    if not value:
        raise ValueError("Transaction date is missing.")
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        parsed = None
    if parsed is None:
        for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y"):
            try:
                parsed = datetime.strptime(value, pattern)
                break
            except ValueError:
                continue
    if parsed is None:
        raise ValueError("Use an ISO date or a date like 2026-10-01.")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _parse_decimal_value(value: str, label: str) -> Decimal:
    if "," in value:
        if not THOUSANDS_SEPARATOR_PATTERN.fullmatch(value):
            raise ValueError(f"{label} has invalid thousands separators.")
        value = value.replace(",", "")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{label} is not a valid number.") from exc


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _normalize_network(value: str) -> str | None:
    aliases = {
        "solana mainnet": "solana",
        "solana mainnet-beta": "solana",
        "ethereum mainnet": "ethereum",
        "ethereum l1": "ethereum",
        "eth mainnet": "ethereum",
        "base mainnet": "base",
        "arbitrum one": "arbitrum",
        "arbitrum mainnet": "arbitrum",
    }
    normalized = aliases.get(value, value)
    return normalized if normalized in SUPPORTED_NETWORKS else None
