from pydantic import BaseModel


class ImportPreviewRead(BaseModel):
    filename: str
    columns: list[str]
    rows_received: int
    preview: list[dict[str, str | None]]
    warnings: list[str]
    records_added: bool = False
