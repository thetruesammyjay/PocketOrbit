from decimal import Decimal
from typing import Mapping


def allocation_percentages(values: Mapping[str, Decimal]) -> dict[str, Decimal]:
    total = sum(values.values(), start=Decimal("0"))
    if total <= 0:
        return {key: Decimal("0") for key in values}
    return {key: (value / total * Decimal("100")).quantize(Decimal("0.1")) for key, value in values.items()}
