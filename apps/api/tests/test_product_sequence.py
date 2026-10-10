import unittest
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.models import (
    Asset,
    Base,
    ImportJob,
    Portfolio,
    Price,
    Source,
    Transaction,
    TransferMatch,
    User,
)
from app.schemas.imports import CsvFieldMapping
from app.services.csv_import_service import import_csv_transactions
from app.services.performance_service import get_portfolio_performance
from app.services.transfer_matching import refresh_transfer_suggestions


class ProductSequenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine, expire_on_commit=False)
        user = User(email="sequence@example.test", password_hash="not-used")
        self.session.add(user)
        self.session.flush()
        self.portfolio = Portfolio(user_id=user.id, name="Sequence", reporting_currency="USD")
        self.session.add(self.portfolio)
        self.session.commit()
        self.mapping = CsvFieldMapping(
            occurred_at="date",
            asset="asset",
            quantity="amount",
            kind="type",
            network="network",
            transaction_id="id",
            quote_amount="value",
            quote_currency="currency",
        )

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_overlapping_exports_skip_already_imported_rows_and_reuse_account_source(self) -> None:
        first = (
            b"date,asset,amount,type,network,id,value,currency\n"
            b"2026-08-01,ETH,1,buy,ethereum,order-1,,\n"
        )
        second = (
            b"date,asset,amount,type,network,id,value,currency,note\n"
            b"2026-08-01,ETH,1,buy,ethereum,order-1,,,overlap\n"
            b"2026-08-02,ETH,2,buy,ethereum,order-2,,,new\n"
        )
        first_result = import_csv_transactions(
            self.session,
            self.portfolio,
            "first.csv",
            first,
            self.mapping,
            source_name="Exchange A",
        )
        second_result = import_csv_transactions(
            self.session,
            self.portfolio,
            "second.csv",
            second,
            self.mapping,
            source_name="exchange a",
        )

        self.assertEqual(first_result.rows_accepted, 1)
        self.assertEqual((second_result.rows_accepted, second_result.rows_duplicate), (1, 1))
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(Source)),
            1,
        )
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(Transaction)),
            2,
        )
        jobs = self.session.scalars(select(ImportJob).order_by(ImportJob.created_at)).all()
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[1].rows_duplicate, 1)

    def test_full_history_fifo_shows_realized_and_unrealized_explanation(self) -> None:
        buy = (
            b"date,asset,amount,type,network,id,value,currency\n"
            b"2026-08-01,ETH,2,buy,ethereum,buy-1,4000,USD\n"
        )
        sale = (
            b"date,asset,amount,type,network,id,value,currency\n"
            b"2026-08-10,ETH,1,sell,ethereum,sell-1,2500,USD\n"
        )
        import_csv_transactions(
            self.session,
            self.portfolio,
            "buys.csv",
            buy,
            self.mapping,
            source_name="Exchange A",
            history_complete=True,
        )
        import_csv_transactions(
            self.session,
            self.portfolio,
            "sells.csv",
            sale,
            self.mapping,
            source_name="Exchange A",
            history_complete=True,
        )
        transactions = self.session.scalars(select(Transaction)).all()
        for transaction in transactions:
            transaction.quality_status = "user_confirmed"
        asset = self.session.scalar(select(Asset).where(Asset.canonical_id == "ethereum:native"))
        assert asset is not None
        self.session.add(
            Price(
                asset_id=asset.id,
                provider="test-feed",
                quote_currency="USD",
                price=Decimal("3000"),
                quality_status="fresh",
                retrieved_at=datetime.now(UTC),
            )
        )
        self.session.commit()

        performance = get_portfolio_performance(self.session, self.portfolio)

        self.assertEqual(performance.status, "complete")
        self.assertEqual(performance.method, "FIFO")
        self.assertEqual(performance.realized_pnl, Decimal("500.00"))
        self.assertEqual(performance.unrealized_pnl, Decimal("1000.00"))
        self.assertEqual(performance.total_pnl, Decimal("1500.00"))
        self.assertEqual(
            performance.realized_events[0].cost_basis, Decimal("2000.000000000000000000")
        )
        self.assertEqual(performance.coverage[0].rows_imported, 2)

    def test_unasserted_history_withholds_total_pnl(self) -> None:
        contents = (
            b"date,asset,amount,type,network,id,value,currency\n"
            b"2026-08-01,ETH,1,buy,ethereum,buy-1,2000,USD\n"
        )
        import_csv_transactions(
            self.session,
            self.portfolio,
            "partial.csv",
            contents,
            self.mapping,
            source_name="Exchange A",
        )
        transaction = self.session.scalar(select(Transaction))
        assert transaction is not None
        transaction.quality_status = "user_confirmed"
        asset = self.session.scalar(select(Asset).where(Asset.canonical_id == "ethereum:native"))
        assert asset is not None
        self.session.add(
            Price(
                asset_id=asset.id,
                provider="test-feed",
                quote_currency="USD",
                price=Decimal("3000"),
                quality_status="fresh",
                retrieved_at=datetime.now(UTC),
            )
        )
        self.session.commit()

        performance = get_portfolio_performance(self.session, self.portfolio)

        self.assertEqual(performance.status, "partial")
        self.assertIsNone(performance.total_pnl)
        self.assertTrue(any("full available history" in reason for reason in performance.reasons))

    def test_reviewed_outbound_and_inbound_rows_create_unconfirmed_transfer_suggestion(
        self,
    ) -> None:
        outgoing = (
            b"date,asset,amount,type,network,id,value,currency\n"
            b"2026-08-01T12:00:00Z,ETH,1.5,withdrawal,ethereum,withdraw-1,,\n"
        )
        incoming = (
            b"date,asset,amount,type,network,id,value,currency\n"
            b"2026-08-01T12:10:00Z,ETH,1.5,deposit,ethereum,deposit-1,,\n"
        )
        import_csv_transactions(
            self.session,
            self.portfolio,
            "outgoing.csv",
            outgoing,
            self.mapping,
            source_name="Exchange A",
        )
        import_csv_transactions(
            self.session,
            self.portfolio,
            "incoming.csv",
            incoming,
            self.mapping,
            source_name="Wallet B",
        )
        for transaction in self.session.scalars(select(Transaction)).all():
            transaction.quality_status = "user_confirmed"

        refresh_transfer_suggestions(self.session, self.portfolio)
        self.session.flush()
        suggestion = self.session.scalar(select(TransferMatch))

        self.assertIsNotNone(suggestion)
        assert suggestion is not None
        self.assertEqual(suggestion.status, "suggested")
        self.assertGreaterEqual(suggestion.confidence, Decimal("0.8"))
        self.assertEqual(self.session.scalar(select(func.count()).select_from(TransferMatch)), 1)

    def test_ambiguous_transfer_candidates_are_left_for_manual_review(self) -> None:
        exports = [
            (
                "Exchange A",
                "outgoing.csv",
                b"date,asset,amount,type,network,id,value,currency\n"
                b"2026-08-01T12:00:00Z,ETH,1.5,withdrawal,ethereum,withdraw-1,,\n",
            ),
            (
                "Wallet B",
                "incoming-one.csv",
                b"date,asset,amount,type,network,id,value,currency\n"
                b"2026-08-01T12:10:00Z,ETH,1.5,deposit,ethereum,deposit-1,,\n",
            ),
            (
                "Wallet C",
                "incoming-two.csv",
                b"date,asset,amount,type,network,id,value,currency\n"
                b"2026-08-01T12:11:00Z,ETH,1.5,deposit,ethereum,deposit-2,,\n",
            ),
        ]
        for source_name, filename, contents in exports:
            import_csv_transactions(
                self.session,
                self.portfolio,
                filename,
                contents,
                self.mapping,
                source_name=source_name,
            )
        for transaction in self.session.scalars(select(Transaction)).all():
            transaction.quality_status = "user_confirmed"

        refresh_transfer_suggestions(self.session, self.portfolio)
        self.session.flush()

        self.assertEqual(self.session.scalar(select(func.count()).select_from(TransferMatch)), 0)


if __name__ == "__main__":
    unittest.main()
