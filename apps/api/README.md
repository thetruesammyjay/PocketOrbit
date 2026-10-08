# PocketOrbit API

FastAPI service for private portfolios, public-wallet snapshots, and validated exchange CSV history or balance statements.

From the repository root:

```sh
pnpm dev:api
```

The API listens on `http://localhost:8000`; interactive documentation is at `/docs`. Copy `apps/api/.env.example` to `apps/api/.env` only when you need local provider or database settings. Keep real credentials out of source control.

## Local setup

The liveness route, sample portfolio, and CSV preview can run without a database. Account registration, saved wallets, portfolio summaries, and transaction imports require PostgreSQL and the current Alembic migrations:

```sh
uv run --directory apps/api alembic upgrade head
```

Set `DATABASE_URL`, `SECRET_KEY`, and `WEB_ORIGIN` in the API environment. Configure a public RPC endpoint for each network you plan to support. `ALCHEMY_API_KEY` can provide dedicated Ethereum, Base, and Arbitrum token discovery while existing RPC endpoints continue to handle chain reads. See [`../../docs/API.md`](../../docs/API.md) for API routes, token coverage behavior, CSV limitations, and remaining launch requirements.

Run the API regression suite from the repository root:

```sh
uv run --directory apps/api python -m unittest discover -s tests -v
```

## Production deployment

Set `APP_ENV=production`, use a PostgreSQL `DATABASE_URL`, set a unique `SECRET_KEY` with at least 32 characters, set `WEB_ORIGIN` to the exact deployed HTTPS origin, and configure at least one public wallet RPC endpoint, indexed EVM RPC endpoint, or `ALCHEMY_API_KEY`. Startup validation rejects unsafe or incomplete production settings. The API requires a matching `Origin` or `Referer` for production mutations. Browser API traffic uses the fixed `/api/v1` Next.js same-origin proxy. Set the web `API_INTERNAL_URL` to a server-reachable API base URL including `/api/v1`, during both build and deployment. Keep `AUTH_COOKIE_DOMAIN` blank and `AUTH_COOKIE_SAMESITE=lax`; the API's session cookie will then be stored under the web origin and can be forwarded during server rendering.

For broader EVM token coverage, set `ALCHEMY_API_KEY` or per-network `*_INDEXED_RPC_URL` values in the deployment secret manager. The shared Alchemy key configures dedicated token indexer endpoints for Ethereum, Base, and Arbitrum and enables the Portfolio API fallback. Per-network indexed URLs override generated RPC endpoints. Explicit chain RPC endpoints remain primary; indexed RPC is tried after a chain-ID failure, and its chain ID is checked before token balances are accepted. Alchemy's Portfolio API can provide native and ERC-20 balances if needed. Verify each endpoint for the methods it will serve.

`GET /api/v1/health` is a liveness check. `GET /api/v1/ready` checks database connectivity and returns `503` until the database schema matches the application's Alembic head. The Railway pre-deploy step runs `uv run alembic upgrade head`, and its deployment health check waits for `/api/v1/ready`; for other hosts, run that migration command as a release step before routing traffic. Production startup also requires SMTP settings for verification and password recovery. Set up database backups, restore drills, monitoring, edge request limits, and incident procedures before public registration.

Authentication uses password hashes, verified email, single-use recovery links, and revocable, server-side sessions in an HttpOnly cookie. Account deletion removes active user-owned data after password confirmation. Production deployments still need SMTP, protected admin access, backup retention, and operational controls.
