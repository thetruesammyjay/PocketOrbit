import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.persistent_portfolios import get_portfolio_summary, require_owned_portfolio
from app.services.portfolio_service import get_demo_portfolio_summary

router = APIRouter()


def _safe_csv_text(value: object | None) -> str:
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text


@router.get("/demo/holdings.csv")
def export_demo_holdings() -> StreamingResponse:
    summary = get_demo_portfolio_summary()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["asset", "symbol", "quantity", "unit_price", "value", "currency", "data_type"])
    for holding in summary["holdings"]:
        writer.writerow(
            [
                holding["asset"]["name"],
                holding["asset"]["symbol"],
                holding["quantity"],
                holding["unitPrice"],
                holding["value"],
                summary["reportingCurrency"],
                "illustrative demo data",
            ]
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pocketorbit-demo-holdings.csv"},
    )


@router.get("/portfolios/{portfolio_id}/holdings.csv")
def export_portfolio_holdings(
    portfolio_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    summary = get_portfolio_summary(session, portfolio)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "asset",
            "symbol",
            "network",
            "contract_address",
            "quantity",
            "unit_price",
            "value",
            "currency",
            "data_quality",
            "balance_sources",
            "balance_updated_at",
            "price_provider",
            "price_provider_updated_at",
            "price_checked_at",
        ]
    )
    for holding in summary.holdings:
        writer.writerow(
            [
                _safe_csv_text(holding.asset.get("name")),
                _safe_csv_text(holding.asset.get("symbol")),
                _safe_csv_text(holding.asset.get("network")),
                _safe_csv_text(holding.asset.get("contractAddress")),
                holding.quantity,
                holding.unit_price,
                holding.value,
                portfolio.reporting_currency,
                holding.provenance.quality.value,
                _safe_csv_text("; ".join(holding.provenance.balance_sources)),
                holding.provenance.balance_retrieved_at,
                _safe_csv_text(holding.provenance.price_provider),
                holding.provenance.price_provider_updated_at,
                holding.provenance.price_retrieved_at,
            ]
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pocketorbit-holdings.csv"},
    )
