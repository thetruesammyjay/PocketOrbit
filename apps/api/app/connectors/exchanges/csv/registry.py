"""Registry for exchange-specific CSV parser implementations."""

SUPPORTED_FORMATS: tuple[str, ...] = ()


def get_parser(exchange: str) -> None:
    raise LookupError(f"No exchange-specific CSV parser is registered for {exchange!r}.")
