import csv
import io
from collections.abc import Iterable


def preview_csv(contents: bytes, filename: str, limit: int = 5) -> dict[str, object]:
    text = contents.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    columns = reader.fieldnames or []
    preview = [{key: value for key, value in row.items()} for row in _take(reader, limit)]
    rows_received = sum(1 for _ in csv.DictReader(io.StringIO(text)))
    warnings = []
    if not columns:
        warnings.append("The file has no header row.")
    if columns and not {"date", "timestamp", "time"}.intersection(name.lower() for name in columns):
        warnings.append("No date column was recognized in this preview.")
    warnings.append("Preview only: rows have not been normalized or added to a portfolio.")
    return {
        "filename": filename,
        "columns": columns,
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
