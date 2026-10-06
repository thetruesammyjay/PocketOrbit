from datetime import datetime, timedelta, timezone


def freshness_status(retrieved_at: datetime | None, max_age: timedelta) -> str:
    if retrieved_at is None:
        return "offline"
    if retrieved_at.tzinfo is None:
        retrieved_at = retrieved_at.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - retrieved_at
    return "fresh" if age <= max_age else "delayed"
