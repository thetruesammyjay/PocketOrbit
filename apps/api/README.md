# PocketOrbit API

FastAPI service for normalized portfolio data. The demo endpoints run without a database or third-party provider.

From the repository root:

```sh
pnpm dev:api
```

The service listens on `http://localhost:8000`; interactive API docs are at `/docs`. Copy `.env.example` to `.env` only if a local `.env` does not already exist. Keep real credentials out of source control.

`GET /api/v1/portfolios/demo/summary` returns explicitly labeled fixture data. `POST /api/v1/imports/preview` reads CSV headings and sample rows only; it does not persist records. `POST /api/v1/wallets/sync` reads a public wallet through configured Solana or EVM RPC, adds optional CoinGecko quotes, and returns a provenance-rich snapshot without saving it. See `../../docs/API.md` for provider configuration and EVM token-coverage limits.

PostgreSQL models, Alembic configuration, and an initial schema migration are scaffolded. Review the migration before using it with real account data, then apply it to a configured database. The API health and demo endpoints do not require a database.
