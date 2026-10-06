# PocketOrbit

> **Your crypto, in one clear view.**

PocketOrbit is a read-only crypto portfolio companion. It brings records from public wallets and exchange files into one portfolio view, then shows where balances, prices, and activity came from.

## How PocketOrbit works

![Infographic: Add a public wallet or exchange file, organize the records, see the portfolio, and check where the information came from. PocketOrbit is read-only and never asks for private keys or seed phrases.](assets/PocketOrbit-Product-Flow.png)

Add a public wallet address or upload an exchange statement. PocketOrbit brings the records together so you can see balances, portfolio value, and activity in one place. You can check where each number came from and when it was last updated. PocketOrbit can read and organize records, but it cannot move your crypto.

## What is scaffolded

- A responsive Next.js web app with public pages, a sample portfolio dashboard, portfolio views, and admin route placeholders.
- A FastAPI service with a health endpoint, deterministic sample portfolio, sample CSV preview/export, and stateless read-only wallet snapshots for configured Solana and EVM RPC endpoints.
- Shared TypeScript types, UI primitives, SQLAlchemy models, calculation modules, and Alembic configuration.
- Provider adapters for public wallet balances and market prices, with exchange CSV formats still at the generic preview stage.

**The dashboard still uses illustrative sample data.** CSV preview does not save records. The wallet API needs server-side RPC endpoints and a CoinGecko API key for live prices; EVM token coverage is limited to explicitly configured contracts. Wallet snapshots are not saved, and the web UI is not yet wired to them. Authentication, portfolio persistence, exchange-specific parsers, and protected admin access are not connected. See [API.md](docs/API.md) for wallet API configuration, [HACKATHON.md](docs/HACKATHON.md) for the MVP target, and [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for the full file map.

## Run locally

Requirements: Node.js 20.9 or newer, pnpm, Python 3.11 or newer, and [uv](https://docs.astral.sh/uv/).

From the repository root in PowerShell:

```powershell
if (-not (Test-Path apps/web/.env.local)) { Copy-Item apps/web/.env.example apps/web/.env.local }
if (-not (Test-Path apps/api/.env)) { Copy-Item apps/api/.env.example apps/api/.env }
pnpm install
```

Start the API in one terminal:

```powershell
pnpm dev:api
```

Start the web app in another terminal:

```powershell
pnpm dev
```

Open `http://localhost:3000`. The sample dashboard works without PostgreSQL or provider credentials. With the API running, the CSV page can preview a file locally and the reports page can download a clearly labeled sample CSV. Interactive API documentation is at `http://localhost:8000/docs`.

## Product principles

- **Clear:** Explain portfolio and crypto terms in plain language.
- **Traceable:** Keep source and freshness information with important values.
- **Read-only:** Never request a seed phrase, private key, or permission to move assets.
- **Honest:** Label sample, missing, conflicting, stale, and uncertain information.
- **Global:** Keep native asset quantities separate from reporting-currency values.

## Documentation

- [Design system and product UI specification](docs/DESIGN.md)
- [Project architecture and complete file map](docs/PROJECT_STRUCTURE.md)
- [2026 Crypto World's Fair hackathon MVP](docs/HACKATHON.md)

<p align="center">
  <strong>PocketOrbit</strong><br />
  Know what you own. Know where it is. Know where the numbers came from.
</p>
