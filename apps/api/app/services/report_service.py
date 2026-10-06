from app.services.portfolio_service import get_demo_portfolio_summary


def get_demo_report_rows() -> list[dict[str, object]]:
    summary = get_demo_portfolio_summary()
    return [
        {
            "asset": holding["asset"]["name"],
            "symbol": holding["asset"]["symbol"],
            "quantity": holding["quantity"],
            "value": holding["value"],
            "currency": summary["reportingCurrency"],
            "data_type": "illustrative demo data",
        }
        for holding in summary["holdings"]
    ]
