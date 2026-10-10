import unittest
from unittest.mock import patch

import httpx
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.routes import auth as auth_routes
from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models import AuthActionToken, AuthSession, Base, Portfolio, User


class AuthSessionLifecycleTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.original_overrides = dict(app.dependency_overrides)
        self.original_settings = {
            "app_env": settings.app_env,
            "database_url": settings.database_url,
            "secret_key": settings.secret_key,
            "web_origin": settings.web_origin,
            "auth_cookie_domain": settings.auth_cookie_domain,
            "auth_cookie_samesite": settings.auth_cookie_samesite,
        }
        settings.app_env = "development"
        settings.database_url = None
        settings.secret_key = "test-session-secret-that-is-long-enough"
        settings.web_origin = "https://pocketorbit.example.test"
        settings.auth_cookie_domain = None
        settings.auth_cookie_samesite = "lax"

        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)

        def override_database():
            with Session(self.engine, expire_on_commit=False) as session:
                yield session

        app.dependency_overrides[get_db] = override_database

    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)
        self.engine.dispose()
        for name, value in self.original_settings.items():
            setattr(settings, name, value)

    async def test_register_login_and_logout_manage_persistent_session(self) -> None:
        email = "pocketorbit-session@example.com"
        password = "correct-horse-battery-staple"

        registration = await self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password},
        )

        self.assertEqual(registration.status_code, 201, registration.text)
        self.assertFalse(registration.json()["verificationRequired"])
        raw_cookie = self.client.cookies.get(settings.auth_cookie_name)
        self.assertTrue(raw_cookie)
        self.assertIn("httponly", registration.headers["set-cookie"].lower())

        with Session(self.engine) as session:
            user = session.scalar(select(User).where(User.email == email))
            self.assertIsNotNone(user)
            self.assertEqual(
                session.scalar(select(func.count()).select_from(Portfolio)),
                1,
            )
            saved_session = session.scalar(select(AuthSession))
            self.assertIsNotNone(saved_session)
            self.assertNotEqual(saved_session.token_hash, raw_cookie)
            self.assertEqual(len(saved_session.token_hash), 64)

        authenticated = await self.client.get("/api/v1/auth/me")
        self.assertEqual(authenticated.status_code, 200, authenticated.text)
        self.assertEqual(authenticated.json()["email"], email)

        logout = await self.client.post("/api/v1/auth/logout")
        self.assertEqual(logout.status_code, 204)
        self.assertEqual(self.client.cookies.get(settings.auth_cookie_name), None)
        self.assertEqual((await self.client.get("/api/v1/auth/me")).status_code, 401)
        with Session(self.engine) as session:
            self.assertEqual(session.scalar(select(func.count()).select_from(AuthSession)), 0)

        login = await self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(login.status_code, 200, login.text)
        self.assertEqual((await self.client.get("/api/v1/auth/me")).status_code, 200)

    async def test_production_registration_requires_email_verification(self) -> None:
        settings.app_env = "production"
        email = "pocketorbit-verify@example.com"
        password = "correct-horse-battery-staple"
        headers = {"origin": settings.web_origin}

        with patch.object(auth_routes, "deliver_action_email") as send_email:
            registration = await self.client.post(
                "/api/v1/auth/register",
                json={"email": email, "password": password},
                headers=headers,
            )

        self.assertEqual(registration.status_code, 201, registration.text)
        self.assertTrue(registration.json()["verificationRequired"])
        self.assertIsNone(self.client.cookies.get(settings.auth_cookie_name))
        send_email.assert_called_once()
        raw_token = send_email.call_args.args[1]

        login_before_verification = await self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
            headers=headers,
        )
        self.assertEqual(login_before_verification.status_code, 403)

        verification = await self.client.post(
            "/api/v1/auth/verification/confirm",
            json={"token": raw_token},
            headers=headers,
        )
        self.assertEqual(verification.status_code, 200, verification.text)
        with Session(self.engine) as session:
            action_token = session.scalar(select(AuthActionToken))
            self.assertIsNotNone(action_token)
            self.assertIsNotNone(action_token.consumed_at)
            user = session.scalar(select(User).where(User.email == email))
            self.assertIsNotNone(user.email_verified_at)

        login_after_verification = await self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
            headers=headers,
        )
        self.assertEqual(login_after_verification.status_code, 200, login_after_verification.text)
        self.assertIn("secure", login_after_verification.headers["set-cookie"].lower())


if __name__ == "__main__":
    unittest.main()
