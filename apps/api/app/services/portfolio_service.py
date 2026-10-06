from decimal import Decimal

from app.calculations.allocation import allocation_percentages
from app.calculations.valuation import value_holdings
from app.services.demo_data import DEMO_ACTIVITY, DEMO_HOLDINGS, DEMO_SOURCES


def get_demo_portfolio_summary() -> dict[str, object]:
    quantities = {item["asset"]["id"]: Decimal(item["quantity"]) for item in DEMO_HOLDINGS}
    prices = {item["asset"]["id"]: Decimal(item["unitPrice"]) for item in DEMO_HOLDINGS}
    values, total = value_holdings(quantities, prices)
    percentages = allocation_percentages(values)
    allocations = [
        {
            "name": item["asset"]["symbol"],
            "value": str(values[item["asset"]["id"]]),
            "percentage": float(percentages[item["asset"]["id"]]),
            "color": color,
        }
        for item, color in zip(DEMO_HOLDINGS, ["#6C5CE7", "#56B7FF", "#18C98B", "#FFC857"], strict=True)
    ]

    return {
        "id": "demo-portfolio",
        "name": "My portfolio",
        "isDemo": True,
        "reportingCurrency": "USD",
        "totalValue": str(total),
        "change24h": "352.01",
        "changePercent24h": "1.12",
        "calculatedAt": "sample",
        "quality": "estimated",
        "holdings": DEMO_HOLDINGS,
        "sources": DEMO_SOURCES,
        "allocation": allocations,
        "activity": DEMO_ACTIVITY,
        "history": [29720, 30110, 29980, 30550, 30280, 31022, 31334, 31686.37],
    }
