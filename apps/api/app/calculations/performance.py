from decimal import ROUND_HALF_UP, Decimal


def percentage_change(current: Decimal, previous: Decimal) -> Decimal | None:
    if previous == 0:
        return None
    return ((current - previous) / previous * Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
