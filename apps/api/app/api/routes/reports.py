import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.portfolio_service import get_demo_portfolio_summary

router = APIRouter()


@router.get("/demo/holdings.csv")
def export_demo_holdings() -> StreamingResponse:
    summary = get_demo_portfolio_summary()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["asset", "symbol", "quantity", "unit_price", "value", "currency", "data_type"])
    for holding in summary["holdings"]:
        writer.writerow([
            holding["asset"]["name"],
            holding["asset"]["symbol"],
            holding["quantity"],
            holding["unitPrice"],
            holding["value"],
            summary["reportingCurrency"],
            "illustrative demo data",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pocketorbit-demo-holdings.csv"},
    )
