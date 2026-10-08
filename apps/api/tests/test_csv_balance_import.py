import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.connectors.exchanges.csv.normalizer import parse_csv_balances
from app.connectors.market_data.base import MarketPrice, MarketPriceBatch
from app.models import (
    Asset,
    Balance,
    Base,
    ImportJob,
    Portfolio,
    Price,
    Source,
    User,
    WalletSnapshot,
)
from app.schemas.common import QualityStatus
from app.schemas.imports import CsvBalanceFieldMapping
from app.services.csv_balance_import_service import import_csv_balance_statement
from app.services.import_pricing_service import price_imported_assets
from app.services.persistent_portfolios import get_portfolio_summary


class CsvBalanceImportTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine, expire_on_commit=False)
        user = User(email="balance-importer@example.test", password_hash="not-used-in-this-test")
        self.session.add(user)
        self.session.flush()
        self.portfolio = Portfolio(
            user_id=user.id, name="Exchange balances", reporting_currency="USD"
        )
        self.session.add(self.portfolio)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_parser_validates_balance_amount_and_network(self) -> None:
        contents = (
            b"asset,balance,network,contract\n"
            b"SOL,2,Solana mainnet,\n"
            b"USDC,-1,ethereum,0x0000000000000000000000000000000000000001\n"
        )
        mapping = CsvBalanceFieldMapping(
            asset="asset", quantity="balance", network="network", contract_address="contract"
        )

        parsed = parse_csv_balances(contents, mapping)

        self.assertEqual(parsed.rows_received, 2)
        self.assertEqual(len(parsed.accepted), 1)
        self.assertEqual(parsed.accepted[0].network_id, "solana")
        self.assertEqual(parsed.accepted[0].quantity, Decimal("2"))
        self.assertEqual(parsed.rejected[0]["row"], 3)
        self.assertIn("non-negative", parsed.rejected[0]["reason"])

    def test_balance_quantities_accept_grouped_thousands_and_reject_bad_commas(self) -> None:
        contents = (
            b"asset,balance,network\n"
            b"ETH,\"1,234.5\",ethereum\n"
            b"ETH,\"1,2\",ethereum\n"
        )
        mapping = CsvBalanceFieldMapping(asset="asset", quantity="balance", network="network")

        parsed = parse_csv_balances(contents, mapping)

        self.assertEqual(parsed.rows_received, 2)
        self.assertEqual(len(parsed.accepted), 1)
        self.assertEqual(parsed.accepted[0].quantity, Decimal("1234.5"))
        self.assertEqual(parsed.rejected[0]["row"], 3)
        self.assertIn("thousands separators", parsed.rejected[0]["reason"])

    def test_balance_statement_persists_visible_holdings_as_needs_review(self) -> None:
        contents = b"asset,balance,network\nSOL,2,solana\n"
        mapping = CsvBalanceFieldMapping(asset="asset", quantity="balance", network="network")

        result = import_csv_balance_statement(
            self.session, self.portfolio, "balances.csv", contents, mapping
        )

        self.assertEqual((result.rows_accepted, result.rows_rejected), (1, 0))
        self.assertTrue(any("not chain-verified" in warning for warning in result.warnings))
        self.assertEqual(self.session.scalar(select(func.count()).select_from(ImportJob)), 1)
        self.assertEqual(self.session.scalar(select(func.count()).select_from(WalletSnapshot)), 1)
        self.assertEqual(self.session.scalar(select(func.count()).select_from(Balance)), 1)

        source = self.session.scalar(select(Source))
        balance = self.session.scalar(select(Balance))
        asset = self.session.get(Asset, balance.asset_id)
        summary = get_portfolio_summary(self.session, self.portfolio)

        self.assertEqual(source.kind, "exchange_balance_import")
        self.assertEqual(source.quality_status, "needs_review")
        self.assertEqual(asset.symbol, "SOL")
        self.assertEqual(summary.holdings[0].quantity, Decimal("2.000000000000000000"))
        self.assertIsNone(summary.total_value)
        self.assertTrue(
            any("known value separately" in warning for warning in summary.sources[0].warnings)
        )

        with self.assertRaises(HTTPException) as duplicate:
            import_csv_balance_statement(
                self.session, self.portfolio, "balances.csv", contents, mapping
            )
        self.assertEqual(duplicate.exception.status_code, 409)

    async def test_exact_balance_assets_get_prices_but_keep_total_under_review(self) -> None:
        contents = b"asset,balance,network\nSOL,2,solana\n"
        mapping = CsvBalanceFieldMapping(asset="asset", quantity="balance", network="network")
        result = import_csv_balance_statement(
            self.session, self.portfolio, "balances.csv", contents, mapping
        )
        now = datetime.now(UTC)
        quote = MarketPrice(
            amount=Decimal("20"),
            source_name="Test market provider",
            retrieved_at=now,
            provider_updated_at=now,
            quality=QualityStatus.FRESH,
        )

        with patch(
            "app.services.import_pricing_service.resolve_prices",
            new_callable=AsyncMock,
            return_value=MarketPriceBatch(quotes={"solana": quote}),
        ):
            warnings = await price_imported_assets(
                self.session, self.portfolio, UUID(result.source_id)
            )

        snapshot = self.session.scalar(select(WalletSnapshot))
        summary = get_portfolio_summary(self.session, self.portfolio)
        self.assertEqual(snapshot.known_value, Decimal("40.00"))
        self.assertIsNone(snapshot.total_value)
        self.assertEqual(summary.known_value, Decimal("40.00"))
        self.assertIsNone(summary.total_value)
        self.assertEqual(self.session.scalar(select(func.count()).select_from(Price)), 1)
        self.assertEqual(warnings, [])

    async def test_reimport_prices_only_assets_from_the_latest_account_snapshot(self) -> None:
        mapping = CsvBalanceFieldMapping(
            asset="asset", quantity="balance", network="network", contract_address="contract"
        )
        first = import_csv_balance_statement(
            self.session,
            self.portfolio,
            "first.csv",
            b"asset,balance,network,contract\nSOL,2,solana,\n",
            mapping,
        )
        first_snapshot = self.session.scalar(select(WalletSnapshot))
        first_snapshot.retrieved_at = datetime.now(UTC) - timedelta(minutes=1)
        self.session.commit()
        import_csv_balance_statement(
            self.session,
            self.portfolio,
            "second.csv",
            (
                b"asset,balance,network,contract\nUSDC,10,ethereum,"
                b"0x0000000000000000000000000000000000000001\n"
            ),
            mapping,
            source_id=UUID(first.source_id),
        )
        captured_asset_ids: list[str] = []

        async def capture_prices(balances, network, currency, client):
            captured_asset_ids.extend(balance.asset_id for balance in balances)
            return MarketPriceBatch(quotes={})

        with patch(
            "app.services.import_pricing_service.resolve_prices",
            new_callable=AsyncMock,
            side_effect=capture_prices,
        ):
            await price_imported_assets(self.session, self.portfolio, UUID(first.source_id))

        self.assertEqual(
            captured_asset_ids,
            ["ethereum:0x0000000000000000000000000000000000000001"],
        )

    def test_updated_statement_on_same_source_uses_latest_snapshot_only(self) -> None:
        mapping = CsvBalanceFieldMapping(asset="asset", quantity="balance", network="network")
        first = import_csv_balance_statement(
            self.session,
            self.portfolio,
            "balances.csv",
            b"asset,balance,network\nSOL,2,solana\n",
            mapping,
        )
        first_snapshot = self.session.scalar(select(WalletSnapshot))
        first_snapshot.retrieved_at = datetime.now(UTC) - timedelta(minutes=1)
        self.session.commit()

        second = import_csv_balance_statement(
            self.session,
            self.portfolio,
            "balances-latest.csv",
            b"asset,balance,network\nSOL,3,solana\n",
            mapping,
            source_id=UUID(first.source_id),
        )

        summary = get_portfolio_summary(self.session, self.portfolio)
        self.assertEqual(second.source_id, first.source_id)
        self.assertEqual(len(summary.sources), 1)
        self.assertEqual(len(summary.holdings), 1)
        self.assertEqual(summary.holdings[0].quantity, Decimal("3.000000000000000000"))
        self.assertEqual(self.session.scalar(select(func.count()).select_from(WalletSnapshot)), 2)

    def test_new_balance_source_cannot_reuse_an_existing_account_name(self) -> None:
        contents = b"asset,balance,network\nSOL,2,solana\n"
        mapping = CsvBalanceFieldMapping(asset="asset", quantity="balance", network="network")
        import_csv_balance_statement(
            self.session,
            self.portfolio,
            "balances.csv",
            contents,
            mapping,
            source_name="Exchange main",
        )

        with self.assertRaises(HTTPException) as duplicate:
            import_csv_balance_statement(
                self.session,
                self.portfolio,
                "balances-latest.csv",
                b"asset,balance,network\nSOL,3,solana\n",
                mapping,
                source_name="exchange MAIN",
            )

        self.assertEqual(duplicate.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
