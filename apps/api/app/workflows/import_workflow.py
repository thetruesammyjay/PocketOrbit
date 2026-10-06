from app.services.import_service import preview_csv


def preview_exchange_file(contents: bytes, filename: str) -> dict[str, object]:
    """Preview source rows only; exchange-specific normalization is not configured yet."""
    return preview_csv(contents, filename)
