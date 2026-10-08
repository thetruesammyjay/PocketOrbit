from collections.abc import Mapping
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def value_holdings(
    quantities: Mapping[str, Decimal], prices: Mapping[str, Decimal]
) -> tuple[dict[str, Decimal], Decimal]:
    values = {
        asset_id: (quantity * prices[asset_id]).quantize(CENT, rounding=ROUND_HALF_UP)
        for asset_id, quantity in quantities.items()
        if asset_id in prices
    }
    return values, sum(values.values(), start=Decimal("0.00")).quantize(CENT)
