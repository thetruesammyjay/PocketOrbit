from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal


def aggregate_quantities(records: Iterable[tuple[str, Decimal]]) -> dict[str, Decimal]:
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for asset_id, quantity in records:
        totals[asset_id] += quantity
    return dict(totals)
