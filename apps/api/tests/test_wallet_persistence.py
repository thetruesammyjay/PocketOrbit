import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.models import (
    Balance,
    Base,
    Portfolio,
    Price,
    Source,
    User,
    ValuationSnapshot,
    WalletSnapshot,
)
from app.schemas.common import QualityStatus
from app.schemas.wallet import (
    BalanceProvenance,
    LiveWalletBalance,
    PriceProvenance,
    WalletSyncResponse,
)
from app.services.persistent_portfolios import get_portfolio_summary
from app.services.wallet_persistence import save_wallet_snapshot


class WalletPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine, expire_on_commit=False)
        user = User(email="wallet-owner@example.test", password_hash="not-used-in-this-test")
        self.session.add(user)
        self.session.flush()
        self.portfolio = Portfolio(user_id=user.id, name="Wallet", reporting_currency="USD")
        self.session.add(self.portfolio)
        self.session.flush()
        self.source = Source(
            portfolio_id=self.portfolio.id,
            kind="wallet",
            name="Main EVM wallet",
            network_id="ethereum",
            public_address="0x0000000000000000000000000000000000000001",
            quality_status="fresh",
        )
        self.session.add(self.source)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _snapshot_result(self, retrieved_at: datetime, quantity: Decimal) -> WalletSyncResponse:
        return WalletSyncResponse(
            network="ethereum",
            network_name="Ethereum",
            coverage="native_and_indexed_erc20_balances",
            address=self.source.public_address,
            retrieved_at=retrieved_at,
            quote_currency="USD",
            total_value=quantity * Decimal("2000"),
            known_value=quantity * Decimal("2000"),
            quality=QualityStatus.FRESH,
            balances=[
                LiveWalletBalance(
                    asset_id="ethereum:native",
                    symbol="ETH",
                    name="Ether",
                    network="ethereum",
                    quantity=quantity,
                    decimals=18,
                    quote_currency="USD",
                    unit_price=Decimal("2000"),
                    value=quantity * Decimal("2000"),
                    quality=QualityStatus.FRESH,
                    balance_provenance=BalanceProvenance(
                        source_name="Ethereum RPC",
                        retrieved_at=retrieved_at,
                        block_reference=f"block:{int(retrieved_at.timestamp())}",
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

    def test_sync_saves_snapshots_and_dashboard_uses_the_latest_balance(self) -> None:
        first_time = datetime.now(UTC) - timedelta(minutes=2)
        first = save_wallet_snapshot(
            self.session,
            self.portfolio,
            self.source,
            self._snapshot_result(first_time, Decimal("1")),
        )
        second_time = first_time + timedelta(minutes=1)
        second = save_wallet_snapshot(
            self.session,
            self.portfolio,
            self.source,
            self._snapshot_result(second_time, Decimal("2")),
        )
        self.session.commit()

        summary = get_portfolio_summary(self.session, self.portfolio)
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(WalletSnapshot)),
            2,
        )
        self.assertEqual(self.session.scalar(select(func.count()).select_from(Balance)), 2)
        self.assertEqual(self.session.scalar(select(func.count()).select_from(Price)), 2)
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(ValuationSnapshot)), 2
        )
        self.assertEqual(summary.total_value, Decimal("4000.00"))
        self.assertEqual(summary.holdings[0].quantity, Decimal("2.000000000000000000"))
        self.assertEqual(summary.holdings[0].provenance.balance_sources, ["Main EVM wallet"])


if __name__ == "__main__":
    unittest.main()
