import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from app.core.rate_limit import enforce_rate_limit, rate_limit_bucket_hash
from app.models.rate_limit import RateLimitWindow

POSTGRES_TEST_URL = os.environ.get("POCKETORBIT_POSTGRES_TEST_URL")
FIXED_NOW = 1_700_000_000


class PostgresRateLimitIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not POSTGRES_TEST_URL:
            raise unittest.SkipTest("Set POCKETORBIT_POSTGRES_TEST_URL to run PostgreSQL checks.")

        cls.engine = create_engine(POSTGRES_TEST_URL, pool_size=10, max_overflow=0)
        if cls.engine.dialect.name != "postgresql":
            cls.engine.dispose()
            raise unittest.SkipTest("POCKETORBIT_POSTGRES_TEST_URL must use PostgreSQL.")
        cls.scope = f"postgres-rate-limit-test-{uuid4()}"
        cls.subject = str(uuid4())
        cls.bucket_hash = rate_limit_bucket_hash(cls.scope, cls.subject)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "engine"):
            if hasattr(cls, "bucket_hash"):
                with cls.engine.begin() as connection:
                    connection.execute(
                        delete(RateLimitWindow).where(
                            RateLimitWindow.bucket_hash == cls.bucket_hash
                        )
                    )
            cls.engine.dispose()

    def _attempt(self) -> bool:
        with Session(self.engine) as session:
            try:
                enforce_rate_limit(
                    session,
                    scope=self.scope,
                    subject=self.subject,
                    max_requests=3,
                    window_seconds=900,
                )
            except HTTPException as exc:
                if exc.status_code != 429:
                    raise
                return False
            return True

    def test_postgres_upsert_enforces_a_shared_limit_under_concurrency(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                delete(RateLimitWindow).where(RateLimitWindow.bucket_hash == self.bucket_hash)
            )

        fixed_clock = SimpleNamespace(time=lambda: FIXED_NOW)
        with patch("app.core.rate_limit.time", fixed_clock):
            with ThreadPoolExecutor(max_workers=8) as executor:
                accepted = list(executor.map(lambda _: self._attempt(), range(8)))

        self.assertEqual(sum(accepted), 3)
        with Session(self.engine) as session:
            count = session.scalar(
                select(RateLimitWindow.hit_count).where(
                    RateLimitWindow.bucket_hash == self.bucket_hash
                )
            )
        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()
