import csv
import io
from collections.abc import Iterable

from app.connectors.exchanges.csv.normalizer import (
    MAX_IMPORT_COLUMNS,
    MAX_IMPORT_ROWS,
    suggest_mapping,
)


def preview_csv(contents: bytes, filename: str, limit: int = 5) -> dict[str, object]:
    text = contents.decode("utf-8-sig", errors="strict")
    reader = csv.DictReader(io.StringIO(text))
    columns = reader.fieldnames or []
    if len(columns) > MAX_IMPORT_COLUMNS:
        raise ValueError(f"A file can contain up to {MAX_IMPORT_COLUMNS} columns.")
    preview = [{key: value for key, value in row.items()} for row in _take(reader, limit)]
    row_reader = csv.DictReader(io.StringIO(text), strict=True)
    rows_received = 0
    for _ in row_reader:
        rows_received += 1
        if rows_received > MAX_IMPORT_ROWS:
            raise ValueError(f"A file can contain up to {MAX_IMPORT_ROWS:,} transaction rows.")
    warnings = []
    if not columns:
        warnings.append("The file has no header row.")
    if columns and not {"date", "timestamp", "time"}.intersection(name.lower() for name in columns):
        warnings.append("No date column was recognized in this preview.")
    warnings.append("Preview only: rows have not been normalized or added to a portfolio.")
    return {
        "filename": filename,
        "columns": columns,
        "suggestedMapping": suggest_mapping(columns),
        "rowsReceived": rows_received,
        "preview": preview,
        "warnings": warnings,
        "recordsAdded": False,
    }


def _take(items: Iterable[dict[str, str | None]], limit: int) -> list[dict[str, str | None]]:
    result = []
    for item in items:
        if len(result) >= limit:
            break
        result.append(item)
    return result
