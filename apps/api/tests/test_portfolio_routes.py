import csv
import io
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from json import dumps
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.routes import portfolios as portfolio_routes
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.models import (
    Asset,
    Balance,
    Base,
    ImportJob,
    Portfolio,
    Source,
    SyncJob,
    Transaction,
    User,
    WalletSnapshot,
)
from app.schemas.common import QualityStatus
from app.schemas.wallet import (
    BalanceProvenance,
    LiveWalletBalance,
    PriceProvenance,
    WalletSyncResponse,
)

WALLET = "0x0000000000000000000000000000000000000002"


class PortfolioWalletRouteTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.original_database_url = settings.database_url
        # The request-body middleware owns its own session factory. Use its local
        # fallback here so upload integration tests never depend on a developer DB.
        settings.database_url = None
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        with Session(self.engine, expire_on_commit=False) as session:
            user = User(email="route-owner@example.test", password_hash="not-used-in-this-test")
            session.add(user)
            session.flush()
            self.user_id = user.id
            portfolio = Portfolio(user_id=user.id, name="Route portfolio", reporting_currency="USD")
            session.add(portfolio)
            session.commit()
            self.portfolio_id = portfolio.id

        self.original_overrides = dict(app.dependency_overrides)

        def override_database():
            with Session(self.engine, expire_on_commit=False) as session:
                yield session

        def override_user():
            with Session(self.engine, expire_on_commit=False) as session:
                return session.get(User, self.user_id)

        app.dependency_overrides[get_db] = override_database
        app.dependency_overrides[get_current_user] = override_user

    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        )
        self.sync_patch = patch.object(
            portfolio_routes,
            "_sync_wallet",
            new_callable=AsyncMock,
            return_value=self._wallet_result(),
        )
        self.sync_mock = self.sync_patch.start()

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    def tearDown(self) -> None:
        self.sync_patch.stop()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)
        self.engine.dispose()
        settings.database_url = self.original_database_url

    @staticmethod
    def _wallet_result() -> WalletSyncResponse:
        retrieved_at = datetime.now(UTC)
        return WalletSyncResponse(
            network="ethereum",
            network_name="Ethereum",
            coverage="native_and_indexed_erc20_balances",
            address=WALLET,
            retrieved_at=retrieved_at,
            quote_currency="USD",
            total_value=Decimal("2000"),
            known_value=Decimal("2000"),
            quality=QualityStatus.FRESH,
            balances=[
                LiveWalletBalance(
                    asset_id="ethereum:native",
                    symbol="ETH",
                    name="Ether",
                    network="ethereum",
                    quantity=Decimal("1"),
                    decimals=18,
                    quote_currency="USD",
                    unit_price=Decimal("2000"),
                    value=Decimal("2000"),
                    quality=QualityStatus.FRESH,
                    balance_provenance=BalanceProvenance(
                        source_name="Ethereum RPC",
                        retrieved_at=retrieved_at,
                        block_reference="block:291",
                    ),
                    price_provenance=PriceProvenance(
                        source_name="CoinGecko",
                        retrieved_at=retrieved_at,
                        provider_updated_at=retrieved_at,
                        quality=QualityStatus.FRESH,
                    ),
                )
            ],
        )

    async def test_add_wallet_route_saves_source_and_summary_data(self) -> None:
        response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )

        self.assertEqual(response.status_code, 201, response.text)
        payload = response.json()
        self.assertTrue(payload["isPersisted"])
        self.assertTrue(payload["sourceId"])
        self.assertTrue(payload["snapshotId"])

        summary_response = await self.client.get(
            f"/api/v1/portfolios/{self.portfolio_id}/summary",
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(summary_response.status_code, 200, summary_response.text)
        summary = summary_response.json()
        self.assertEqual(summary["totalValue"], "2000.00")
        self.assertEqual(summary["holdings"][0]["asset"]["symbol"], "ETH")
        self.assertEqual(summary["sources"][0]["name"], "Main wallet")
        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(Source)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(Balance)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(SyncJob)), 1)

    async def test_add_wallet_rejects_case_variant_of_existing_evm_address(self) -> None:
        address = "0xAbCd0000000000000000000000000000000000Ef"
        first_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": address, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(first_response.status_code, 201, first_response.text)

        duplicate_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={
                "network": "ethereum",
                "address": address.lower(),
                "name": "Same wallet, lowercase",
            },
            headers={"origin": settings.web_origin},
        )

        self.assertEqual(duplicate_response.status_code, 409, duplicate_response.text)
        self.sync_mock.assert_awaited_once()
        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(Source)), 1)

    async def test_holdings_report_exports_saved_data_and_checks_portfolio_ownership(self) -> None:
        add_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(add_response.status_code, 201, add_response.text)

        response = await self.client.get(
            f"/api/v1/reports/portfolios/{self.portfolio_id}/holdings.csv"
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn(
            "attachment; filename=pocketorbit-holdings.csv", response.headers["content-disposition"]
        )
        rows = list(csv.reader(io.StringIO(response.text)))
        self.assertEqual(rows[0][0:2], ["asset", "symbol"])
        self.assertEqual(rows[1][0:2], ["Ether", "ETH"])
        self.assertIn("Main wallet", rows[1][9])
        self.assertEqual(rows[1][11], "CoinGecko")

        unauthorized = await self.client.get(f"/api/v1/reports/portfolios/{uuid4()}/holdings.csv")
        self.assertEqual(unauthorized.status_code, 404)

    async def test_add_wallet_persists_source_when_first_live_sync_fails(self) -> None:
        self.sync_mock.side_effect = HTTPException(
            status_code=502,
            detail="The configured data provider returned HTTP 525.",
        )

        response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )

        self.assertEqual(response.status_code, 201, response.text)
        payload = response.json()
        self.assertFalse(payload["isLive"])
        self.assertTrue(payload["isPersisted"])
        self.assertEqual(payload["coverage"], "not_synced")
        self.assertIsNone(payload["snapshotId"])
        self.assertEqual(payload["quality"], "offline")
        self.assertEqual(payload["warnings"], ["The configured data provider returned HTTP 525."])

        summary_response = await self.client.get(f"/api/v1/portfolios/{self.portfolio_id}/summary")
        self.assertEqual(summary_response.status_code, 200, summary_response.text)
        self.assertIn(
            "The configured data provider returned HTTP 525.",
            summary_response.json()["sources"][0]["warnings"],
        )

        with Session(self.engine) as session:
            source = session.scalar(select(Source))
            self.assertIsNotNone(source)
            self.assertEqual(source.quality_status, "offline")
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 0)
            sync_job = session.scalar(select(SyncJob))
            self.assertEqual(sync_job.status, "failed")

    async def test_unexpected_first_sync_failure_does_not_leave_a_queued_job(self) -> None:
        self.sync_mock.side_effect = RuntimeError("provider detail must not be stored")

        with self.assertRaisesRegex(RuntimeError, "provider detail"):
            await self.client.post(
                f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
                json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
                headers={"origin": settings.web_origin},
            )

        with Session(self.engine) as session:
            source = session.scalar(select(Source).where(Source.kind == "wallet"))
            sync_job = session.scalar(select(SyncJob))
            self.assertIsNotNone(source)
            self.assertEqual(source.quality_status, QualityStatus.OFFLINE.value)
            self.assertEqual(sync_job.status, "failed")
            self.assertNotIn("provider detail", sync_job.message)

    async def test_failed_refresh_marks_source_offline_without_replacing_snapshot(self) -> None:
        add_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(add_response.status_code, 201, add_response.text)
        source_id = add_response.json()["sourceId"]
        self.sync_mock.side_effect = HTTPException(
            status_code=502,
            detail="The configured data provider returned HTTP 525.",
        )

        response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/{source_id}/sync",
            headers={"origin": settings.web_origin},
        )

        self.assertEqual(response.status_code, 502)
        summary_response = await self.client.get(f"/api/v1/portfolios/{self.portfolio_id}/summary")
        self.assertEqual(summary_response.status_code, 200, summary_response.text)
        self.assertEqual(summary_response.json()["quality"], "partial")
        self.assertEqual(summary_response.json()["sources"][0]["quality"], "offline")
        self.assertIn(
            "The configured data provider returned HTTP 525.",
            summary_response.json()["sources"][0]["warnings"],
        )

        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(Balance)), 1)
            jobs = session.scalars(select(SyncJob).order_by(SyncJob.created_at)).all()
            self.assertEqual([job.status for job in jobs], ["completed", "failed"])

    async def test_unexpected_refresh_failure_marks_job_failed_and_keeps_last_snapshot(
        self,
    ) -> None:
        add_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(add_response.status_code, 201, add_response.text)
        source_id = add_response.json()["sourceId"]
        self.sync_mock.side_effect = RuntimeError("provider detail must not be stored")

        with self.assertRaisesRegex(RuntimeError, "provider detail"):
            await self.client.post(
                f"/api/v1/portfolios/{self.portfolio_id}/sources/{source_id}/sync",
                headers={"origin": settings.web_origin},
            )

        with Session(self.engine) as session:
            source = session.get(Source, UUID(source_id))
            jobs = session.scalars(select(SyncJob).order_by(SyncJob.created_at)).all()
            self.assertEqual(source.quality_status, QualityStatus.OFFLINE.value)
            self.assertEqual([job.status for job in jobs], ["completed", "failed"])
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 1)
            self.assertNotIn("provider detail", jobs[-1].message)

    async def test_sync_wallet_route_appends_snapshot_used_by_portfolio_summary(self) -> None:
        add_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(add_response.status_code, 201, add_response.text)
        source_id = add_response.json()["sourceId"]

        sync_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/{source_id}/sync",
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(sync_response.status_code, 200, sync_response.text)
        self.assertTrue(sync_response.json()["isPersisted"])

        summary_response = await self.client.get(f"/api/v1/portfolios/{self.portfolio_id}/summary")
        self.assertEqual(summary_response.status_code, 200, summary_response.text)
        self.assertEqual(summary_response.json()["totalValue"], "2000.00")

        with Session(self.engine) as session:
            self.assertEqual(
                session.scalar(select(func.count()).select_from(WalletSnapshot)),
                2,
            )
            self.assertEqual(session.scalar(select(func.count()).select_from(Balance)), 2)

    async def test_remove_wallet_deletes_sync_jobs_and_saved_snapshots(self) -> None:
        add_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/wallets",
            json={"network": "ethereum", "address": WALLET, "name": "Main wallet"},
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(add_response.status_code, 201, add_response.text)
        source_id = add_response.json()["sourceId"]

        sync_response = await self.client.post(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/{source_id}/sync",
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(sync_response.status_code, 200, sync_response.text)

        delete_response = await self.client.delete(
            f"/api/v1/portfolios/{self.portfolio_id}/sources/{source_id}",
            headers={"origin": settings.web_origin},
        )

        self.assertEqual(delete_response.status_code, 204, delete_response.text)
        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(Source)), 0)
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 0)
            self.assertEqual(session.scalar(select(func.count()).select_from(Balance)), 0)
            self.assertEqual(session.scalar(select(func.count()).select_from(SyncJob)), 0)

    async def test_import_route_saves_transactions_lists_import_and_removes_it(self) -> None:
        contents = (
            b"date,asset,amount,type,network,id\n2026-01-01,SOL,2,deposit,solana,sol-deposit-1\n"
        )
        mapping = dumps(
            {
                "occurredAt": "date",
                "asset": "asset",
                "quantity": "amount",
                "kind": "type",
                "network": "network",
                "transactionId": "id",
            }
        )

        with (
            patch.object(
                portfolio_routes,
                "price_imported_assets",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            import_response = await self.client.post(
                f"/api/v1/portfolios/{self.portfolio_id}/imports",
                data={"mapping": mapping},
                files={"file": ("exchange.csv", contents, "text/csv")},
                headers={"origin": settings.web_origin},
            )

        self.assertEqual(import_response.status_code, 201, import_response.text)
        imported = import_response.json()
        self.assertEqual(imported["rowsAccepted"], 1)
        self.assertEqual(imported["rowsRejected"], 0)

        imports_response = await self.client.get(f"/api/v1/portfolios/{self.portfolio_id}/imports")
        self.assertEqual(imports_response.status_code, 200, imports_response.text)
        self.assertEqual(imports_response.json()[0]["id"], imported["importId"])

        summary_response = await self.client.get(f"/api/v1/portfolios/{self.portfolio_id}/summary")
        self.assertEqual(summary_response.status_code, 200, summary_response.text)
        self.assertEqual(summary_response.json()["activity"][0]["assetSymbol"], "SOL")
        self.assertIsNone(summary_response.json()["totalValue"])

        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(ImportJob)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(Transaction)), 1)

        remove_response = await self.client.delete(
            f"/api/v1/portfolios/{self.portfolio_id}/imports/{imported['importId']}",
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(remove_response.status_code, 204)

        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(ImportJob)), 0)
            self.assertEqual(session.scalar(select(func.count()).select_from(Transaction)), 0)

    async def test_balance_statement_route_populates_reviewable_holdings_and_removes_them(
        self,
    ) -> None:
        contents = b"asset,balance,network\nSOL,2,solana\n"
        mapping = dumps({"asset": "asset", "quantity": "balance", "network": "network"})
        with patch.object(
            portfolio_routes,
            "price_imported_assets",
            new_callable=AsyncMock,
            return_value=[],
        ):
            import_response = await self.client.post(
                f"/api/v1/portfolios/{self.portfolio_id}/imports",
                data={"mode": "balances", "mapping": mapping},
                files={"file": ("balances.csv", contents, "text/csv")},
                headers={"origin": settings.web_origin},
            )

        self.assertEqual(import_response.status_code, 201, import_response.text)
        imported = import_response.json()
        self.assertEqual(imported["rowsAccepted"], 1)

        summary_response = await self.client.get(f"/api/v1/portfolios/{self.portfolio_id}/summary")
        self.assertEqual(summary_response.status_code, 200, summary_response.text)
        summary = summary_response.json()
        self.assertIsNone(summary["totalValue"])
        self.assertEqual(summary["holdings"][0]["asset"]["symbol"], "SOL")
        self.assertEqual(summary["sources"][0]["kind"], "exchange_balance_import")
        self.assertEqual(summary["sources"][0]["quality"], "needs_review")

        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(Asset)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(Balance)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 1)

        delete_response = await self.client.delete(
            f"/api/v1/portfolios/{self.portfolio_id}/imports/{imported['importId']}",
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(delete_response.status_code, 204)
        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(Balance)), 0)
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 0)

    async def test_balance_imports_can_append_and_remove_one_account_snapshot(self) -> None:
        mapping = dumps({"asset": "asset", "quantity": "balance", "network": "network"})
        with patch.object(
            portfolio_routes,
            "price_imported_assets",
            new_callable=AsyncMock,
            return_value=[],
        ):
            first_response = await self.client.post(
                f"/api/v1/portfolios/{self.portfolio_id}/imports",
                data={
                    "mode": "balances",
                    "mapping": mapping,
                    "balanceSourceName": "Exchange main",
                },
                files={
                    "file": (
                        "balances.csv",
                        b"asset,balance,network\nSOL,2,solana\n",
                        "text/csv",
                    )
                },
                headers={"origin": settings.web_origin},
            )
            self.assertEqual(first_response.status_code, 201, first_response.text)
            first = first_response.json()

            second_response = await self.client.post(
                f"/api/v1/portfolios/{self.portfolio_id}/imports",
                data={
                    "mode": "balances",
                    "mapping": mapping,
                    "balanceSourceId": first["sourceId"],
                },
                files={
                    "file": (
                        "balances-latest.csv",
                        b"asset,balance,network\nSOL,3,solana\n",
                        "text/csv",
                    )
                },
                headers={"origin": settings.web_origin},
            )
        self.assertEqual(second_response.status_code, 201, second_response.text)
        second = second_response.json()
        self.assertEqual(second["sourceId"], first["sourceId"])

        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(ImportJob)), 2)
            second_job = session.get(ImportJob, UUID(second["importId"]))
            second_snapshot_id = second_job.snapshot_id
            self.assertIsNotNone(second_snapshot_id)

        remove_first = await self.client.delete(
            f"/api/v1/portfolios/{self.portfolio_id}/imports/{first['importId']}",
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(remove_first.status_code, 204)
        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(Source)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(ImportJob)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(Balance)), 1)
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 1)
            self.assertEqual(session.scalar(select(WalletSnapshot.id)), second_snapshot_id)

        remove_second = await self.client.delete(
            f"/api/v1/portfolios/{self.portfolio_id}/imports/{second['importId']}",
            headers={"origin": settings.web_origin},
        )
        self.assertEqual(remove_second.status_code, 204)
        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(Source)), 0)
            self.assertEqual(session.scalar(select(func.count()).select_from(WalletSnapshot)), 0)


if __name__ == "__main__":
    unittest.main()
