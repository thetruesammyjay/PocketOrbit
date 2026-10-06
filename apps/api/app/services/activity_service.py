from collections.abc import Mapping


def classify_activity(record: Mapping[str, str]) -> tuple[str, str]:
    """Return a conservative kind and review state from a normalized source record."""
    raw_kind = record.get("kind", "").strip().lower()
    known = {"received", "sent", "trade", "fee", "deposit", "withdrawal"}
    if raw_kind in known:
        return raw_kind, "confirmed"
    return "needs_review", "needs_review"
