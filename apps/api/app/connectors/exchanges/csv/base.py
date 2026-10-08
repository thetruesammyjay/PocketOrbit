import csv
import io


class GenericCsvPreview:
    """Read a CSV header and sample rows without adding them to a portfolio."""

    def preview(
        self, contents: bytes, limit: int = 5
    ) -> tuple[list[str], list[dict[str, str | None]]]:
        reader = csv.DictReader(io.StringIO(contents.decode("utf-8-sig", errors="replace")))
        columns = reader.fieldnames or []
        rows = []
        for row in reader:
            if len(rows) == limit:
                break
            rows.append(dict(row))
        return columns, rows
