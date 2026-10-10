import unittest
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.connectors.exchanges.csv.normalizer import parse_csv_transactions
from app.models import Asset, Base, ImportJob, Portfolio, Transaction, User
from app.schemas.imports import CsvFieldMapping
from app.services.csv_import_service import import_csv_transactions
from app.services.import_service import preview_csv
from app.services.persistent_portfolios import get_portfolio_summary


class CsvImportPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine, expire_on_commit=False)
        user = User(email="importer@example.test", password_hash="not-used-in-this-test")
        self.session.add(user)
        self.session.flush()
        self.portfolio = Portfolio(
            user_id=user.id, name="Imported records", reporting_currency="USD"
        )
        self.session.add(self.portfolio)
        self.session.commit()
        self.mapping = CsvFieldMapping(
            occurred_at="date",
            asset="asset",
            quantity="amount",
            kind="type",
            network="network",
            contract_address="contract",
            transaction_id="id",
        )

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_import_persists_rows_and_exposes_them_in_portfolio_activity(self) -> None:
        contents = (
            b"date,asset,amount,type,network,contract,id\n"
            b"2026-01-01,SOL,2,deposit,solana,,sol-deposit-1\n"
            b"2026-01-02,USDC,3,receive,ethereum,"
            b"0x0000000000000000000000000000000000000001,usdc-receive-1\n"
        )

        result = import_csv_transactions(
            self.session, self.portfolio, r"C:\exports\wallet.csv", contents, self.mapping
        )

        self.assertEqual(result.filename, "wallet.csv")
        self.assertEqual(
            (result.rows_received, result.rows_accepted, result.rows_rejected), (2, 2, 0)
        )
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(ImportJob)),
            1,
        )
        rows = self.session.scalars(select(Transaction).order_by(Transaction.occurred_at)).all()
        self.assertEqual([row.quantity for row in rows], [Decimal("2"), Decimal("3")])
        self.assertTrue(all(row.quality_status == "needs_review" for row in rows))

        summary = get_portfolio_summary(self.session, self.portfolio)
        self.assertEqual(len(summary.activity), 2)
        self.assertIsNone(summary.total_value)
        self.assertTrue(
            any("not added to current wallet balances" in warning for warning in summary.warnings)
        )

        with self.assertRaises(HTTPException) as duplicate:
            import_csv_transactions(
                self.session, self.portfolio, "wallet.csv", contents, self.mapping
            )
        self.assertEqual(duplicate.exception.status_code, 409)
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(Transaction)),
            2,
        )

    def test_repeated_exchange_record_id_keeps_distinct_transaction_rows(self) -> None:
        contents = (
            b"date,asset,amount,type,network,id\n"
            b"2026-02-01,ETH,1,buy,ethereum,duplicate-id\n"
            b"2026-02-02,ETH,2,buy,ethereum,duplicate-id\n"
        )
        mapping = CsvFieldMapping(
            occurred_at="date",
            asset="asset",
            quantity="amount",
            kind="type",
            network="network",
            transaction_id="id",
        )

        result = import_csv_transactions(
            self.session, self.portfolio, "partial.csv", contents, mapping
        )

        self.assertEqual(
            (result.rows_received, result.rows_accepted, result.rows_rejected), (2, 2, 0)
        )
        job = self.session.scalar(select(ImportJob))
        self.assertIsNotNone(job)
        self.assertEqual(job.status, "needs_review")
        rows = self.session.scalars(select(Transaction).order_by(Transaction.occurred_at)).all()
        self.assertEqual([row.external_record_id for row in rows], ["duplicate-id", "duplicate-id"])
        self.assertNotEqual(rows[0].source_record_id, rows[1].source_record_id)
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(Transaction)),
            2,
        )

    def test_transaction_quantities_accept_grouped_thousands_and_reject_bad_commas(self) -> None:
        contents = (
            b'date,asset,amount,type\n2026-02-01,ETH,"1,234.5",buy\n2026-02-02,ETH,"1,2",buy\n'
        )
        mapping = CsvFieldMapping(occurred_at="date", asset="asset", quantity="amount", kind="type")

        parsed = parse_csv_transactions(contents, mapping)

        self.assertEqual(parsed.rows_received, 2)
        self.assertEqual(len(parsed.accepted), 1)
        self.assertEqual(parsed.accepted[0].quantity, Decimal("1234.5"))
        self.assertEqual(parsed.rejected[0]["row"], 3)
        self.assertIn("thousands separators", parsed.rejected[0]["reason"])

    def test_repeated_unmatched_asset_rows_share_one_asset_record(self) -> None:
        contents = (
            b"date,asset,amount,type,id\n"
            b"2026-03-01,NEWTOKEN,1,buy,newtoken-buy-1\n"
            b"2026-03-02,NEWTOKEN,2,buy,newtoken-buy-2\n"
        )
        mapping = CsvFieldMapping(
            occurred_at="date",
            asset="asset",
            quantity="amount",
            kind="type",
            transaction_id="id",
        )

        result = import_csv_transactions(
            self.session, self.portfolio, "repeated-token.csv", contents, mapping
        )

        self.assertEqual((result.rows_accepted, result.rows_rejected), (2, 0))
        rows = self.session.scalars(select(Transaction).order_by(Transaction.occurred_at)).all()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].asset_id, rows[1].asset_id)
        self.assertEqual(
            self.session.scalar(
                select(func.count()).select_from(Asset).where(Asset.symbol == "NEWTOKEN")
            ),
            1,
        )

    def test_ticker_only_assets_on_different_networks_remain_separate(self) -> None:
        contents = (
            b"date,asset,amount,type,network,id\n"
            b"2026-03-01,USDC,1,receive,ethereum,usdc-eth-1\n"
            b"2026-03-02,USDC,2,receive,base,usdc-base-1\n"
        )
        mapping = CsvFieldMapping(
            occurred_at="date",
            asset="asset",
            quantity="amount",
            kind="type",
            network="network",
            transaction_id="id",
        )

        result = import_csv_transactions(
            self.session, self.portfolio, "multi-network.csv", contents, mapping
        )

        self.assertEqual((result.rows_accepted, result.rows_rejected), (2, 0))
        rows = self.session.scalars(select(Transaction).order_by(Transaction.occurred_at)).all()
        self.assertNotEqual(rows[0].asset_id, rows[1].asset_id)
        assets = [self.session.get(Asset, row.asset_id) for row in rows]
        self.assertEqual([asset.network_id for asset in assets], ["ethereum", "base"])

    def test_preview_rejects_a_csv_with_too_many_columns(self) -> None:
        contents = (",".join(f"field_{index}" for index in range(257)) + "\n").encode()

        with self.assertRaisesRegex(ValueError, "up to 256 columns"):
            preview_csv(contents, "wide.csv")


if __name__ == "__main__":
    unittest.main()
