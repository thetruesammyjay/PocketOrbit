# PocketOrbit Project Structure

This document records the files in the current scaffold and the boundaries between the web app, API, shared packages, and providers.

## Repository status

PocketOrbit now has an initial monorepo scaffold. The web app includes public pages and a sample portfolio experience. The API includes health, deterministic demo, CSV preview, and a stateless live wallet snapshot endpoint for configured RPC providers. Authentication, persistence, and exchange-specific integrations are not connected.

The inventory below lists files currently present. No JavaScript or Python dependency lockfile has been generated yet; pnpm and uv create them during installation or first run. No test files are included in this scaffold.

## Current file inventory

    PocketOrbit/
    ├── .editorconfig
    ├── .env.example
    ├── .gitignore
    ├── package.json
    ├── pnpm-workspace.yaml
    ├── README.md
    ├── assets/
    │   ├── PocketOrbit-Logo-Horizontal.svg
    │   ├── PocketOrbit-Logo-Horizontal.png
    │   ├── PocketOrbit-Mascot-Orbit.svg
    │   ├── PocketOrbit-Mascot-Orbit.png
    │   ├── PocketOrbit-Mascot-Scout.svg
    │   ├── PocketOrbit-Mascot-Scout.png
    │   ├── PocketOrbit-Mascot-Comet.svg
    │   ├── PocketOrbit-Mascot-Comet.png
    │   ├── PocketOrbit-Mascot-Family.svg
    │   ├── PocketOrbit-Mascot-Family.png
    │   └── PocketOrbit-Product-Flow.png
    ├── apps/
    │   ├── web/
    │   │   ├── .env.example
    │   │   ├── eslint.config.mjs
    │   │   ├── next.config.ts
    │   │   ├── next-env.d.ts
    │   │   ├── package.json
    │   │   ├── postcss.config.mjs
    │   │   ├── tsconfig.json
    │   │   ├── app/
    │   │   │   ├── globals.css
    │   │   │   ├── layout.tsx
    │   │   │   ├── page.tsx
    │   │   │   ├── how-it-works/page.tsx
    │   │   │   ├── learn/page.tsx
    │   │   │   ├── login/page.tsx
    │   │   │   ├── privacy/page.tsx
    │   │   │   ├── register/page.tsx
    │   │   │   ├── security/page.tsx
    │   │   │   ├── terms/page.tsx
    │   │   │   ├── app/
    │   │   │   │   ├── layout.tsx
    │   │   │   │   ├── page.tsx
    │   │   │   │   ├── activity/page.tsx
    │   │   │   │   ├── import/page.tsx
    │   │   │   │   ├── insights/page.tsx
    │   │   │   │   ├── learn/page.tsx
    │   │   │   │   ├── portfolio/page.tsx
    │   │   │   │   ├── reports/page.tsx
    │   │   │   │   ├── settings/page.tsx
    │   │   │   │   ├── sources/page.tsx
    │   │   │   │   └── wallets/add/page.tsx
    │   │   │   └── admin/
    │   │   │       ├── layout.tsx
    │   │   │       ├── page.tsx
    │   │   │       ├── assets/page.tsx
    │   │   │       ├── audit/page.tsx
    │   │   │       ├── imports/page.tsx
    │   │   │       ├── jobs/page.tsx
    │   │   │       ├── portfolios/page.tsx
    │   │   │       ├── settings/page.tsx
    │   │   │       ├── sources/page.tsx
    │   │   │       ├── system/page.tsx
    │   │   │       └── users/page.tsx
    │   │   ├── components/
    │   │   │   ├── admin-feature-page.tsx
    │   │   │   ├── admin-shell.tsx
    │   │   │   ├── app-shell.tsx
    │   │   │   ├── feature-page.tsx
    │   │   │   ├── icon.tsx
    │   │   │   ├── page-heading.tsx
    │   │   │   ├── quality-status.tsx
    │   │   │   └── site-header.tsx
    │   │   ├── features/
    │   │   │   ├── activity/activity-list.tsx
    │   │   │   ├── imports/import-preview-form.tsx
    │   │   │   └── portfolio/
    │   │   │       ├── allocation-breakdown.tsx
    │   │   │       ├── dashboard.tsx
    │   │   │       ├── demo-data.ts
    │   │   │       ├── holdings-table.tsx
    │   │   │       ├── portfolio-api.ts
    │   │   │       └── portfolio-chart.tsx
    │   │   ├── lib/
    │   │   │   ├── format.ts
    │   │   │   └── routes.ts
    │   │   └── public/brand/
    │   │       ├── PocketOrbit-Logo-Horizontal.svg
    │   │       ├── PocketOrbit-Mascot-Comet.svg
    │   │       ├── PocketOrbit-Mascot-Orbit.svg
    │   │       ├── PocketOrbit-Mascot-Scout.svg
    │   │       ├── PocketOrbit-Orbit.png
    │   │       ├── PocketOrbit-Product-Flow.png
    │   │       ├── PocketOrbit-Favico.png
    │   │       ├── pocketorbit-comet.png
    │   │       └── pocketorbit-scout.png
    │   └── api/
    │       ├── .env.example
    │       ├── README.md
    │       ├── alembic.ini
    │       ├── pyproject.toml
    │       ├── railway.toml
    │       ├── app/
    │       │   ├── __init__.py
    │       │   ├── main.py
    │       │   ├── api/
    │       │   │   ├── __init__.py
    │       │   │   ├── router.py
    │       │   │   └── routes/
    │       │   │       ├── __init__.py
    │       │   │       ├── admin.py
    │       │   │       ├── health.py
    │       │   │       ├── imports.py
    │       │   │       ├── portfolios.py
    │       │   │       ├── reports.py
    │       │   │       ├── sources.py
    │       │   │       └── wallets.py
    │       │   ├── calculations/
    │       │   │   ├── __init__.py
    │       │   │   ├── allocation.py
    │       │   │   ├── balances.py
    │       │   │   ├── performance.py
    │       │   │   └── valuation.py
    │       │   ├── connectors/
    │       │   │   ├── __init__.py
    │       │   │   ├── base.py
    │       │   │   ├── blockchain/
    │       │   │   │   ├── __init__.py
    │       │   │   │   ├── evm.py
    │       │   │   │   ├── networks.py
    │       │   │   │   └── solana.py
    │       │   │   ├── exchanges/
    │       │   │   │   ├── __init__.py
    │       │   │   │   └── csv/
    │       │   │   │       ├── __init__.py
    │       │   │   │       ├── base.py
    │       │   │   │       └── registry.py
    │       │   │   ├── market_data/
    │       │   │   │   ├── __init__.py
    │       │   │   │   ├── base.py
    │       │   │   │   └── coingecko.py
    │       │   │   └── rpc.py
    │       │   ├── core/
    │       │   │   ├── __init__.py
    │       │   │   ├── config.py
    │       │   │   ├── database.py
    │       │   │   ├── logging.py
    │       │   │   └── security.py
    │       │   ├── models/
    │       │   │   ├── __init__.py
    │       │   │   ├── activity.py
    │       │   │   ├── asset.py
    │       │   │   ├── audit_event.py
    │       │   │   ├── balance.py
    │       │   │   ├── import_job.py
    │       │   │   ├── portfolio.py
    │       │   │   ├── price.py
    │       │   │   ├── source.py
    │       │   │   ├── sync_job.py
    │       │   │   ├── user.py
    │       │   │   └── valuation.py
    │       │   ├── schemas/
    │       │   │   ├── __init__.py
    │       │   │   ├── activity.py
    │       │   │   ├── asset.py
    │       │   │   ├── auth.py
    │       │   │   ├── common.py
    │       │   │   ├── imports.py
    │       │   │   ├── portfolio.py
    │       │   │   ├── source.py
    │       │   │   └── wallet.py
    │       │   ├── services/
    │       │   │   ├── __init__.py
    │       │   │   ├── activity_service.py
    │       │   │   ├── asset_service.py
    │       │   │   ├── demo_data.py
    │       │   │   ├── import_service.py
    │       │   │   ├── portfolio_service.py
    │       │   │   ├── pricing_service.py
    │       │   │   ├── quality_service.py
    │       │   │   ├── report_service.py
    │       │   │   ├── source_service.py
    │       │   │   └── wallet_service.py
    │       │   ├── workers/
    │       │   │   ├── __init__.py
    │       │   │   └── jobs.py
    │       │   └── workflows/
    │       │       ├── __init__.py
    │       │       ├── import_workflow.py
    │       │       ├── portfolio_refresh_workflow.py
    │       │       └── wallet_sync_workflow.py
    │       └── migrations/
    │           ├── env.py
    │           ├── script.py.mako
    │           └── versions/0001_initial.py
    ├── packages/
    │   ├── config/
    │   │   ├── eslint.config.mjs
    │   │   ├── package.json
    │   │   └── tsconfig.base.json
    │   ├── types/
    │   │   ├── package.json
    │   │   └── src/
    │   │       ├── activity.ts
    │   │       ├── asset.ts
    │   │       ├── index.ts
    │   │       ├── portfolio.ts
    │   │       ├── source.ts
    │   │       └── wallet.ts
    │   └── ui/
    │       ├── package.json
    │       └── src/
    │           ├── badge.tsx
    │           ├── button.tsx
    │           ├── card.tsx
    │           └── index.ts
    └── docs/
        ├── API.md
        ├── ARCHITECTURE.md
        ├── CONNECTORS.md
        ├── DATA-MODEL.md
        ├── DESIGN.md
        ├── HACKATHON.md
        ├── PROJECT_STRUCTURE.md
        └── SECURITY.md

Runtime behavior and responsibilities are described below. Provider adapters and most account features exist only as extension points; check the status notes before connecting real data.

## Application boundaries

| Area | Responsibility | Runtime / target |
|---|---|---|
| `apps/web` | Public pages, account experience, portfolio UI, admin operations | Next.js, TypeScript, Tailwind CSS, Hugeicons; Vercel |
| `apps/api` | Authentication, imports, wallet sync, normalized data, APIs, deterministic calculations | Python, FastAPI, Pydantic, SQLAlchemy, Alembic; Railway |
| PostgreSQL | Users, portfolios, source records, assets, balances, activity, prices, snapshots, jobs, quality metadata | NeonDB-hosted PostgreSQL |
| `packages/types` | Shared browser-side domain and API types | TypeScript package |
| `packages/ui` | Reusable accessible visual primitives | React package |
| `assets` and `docs` | Source brand artwork and product/engineering documentation | Repository content |

The web app talks to the API over HTTPS. Provider-specific formats stay behind API connectors, and external providers do not define PocketOrbit's internal data model.

## Data flow

```text
Wallet / exchange file / market provider
                ↓
       Provider connector or parser
                ↓
     Validate and normalize records
                ↓
       Identify assets and activity
                ↓
 Resolve prices and calculate balances
                ↓
 Persist values with provenance metadata
                ↓
            FastAPI endpoints
                ↓
     Next.js presentation and review
```

Import and refresh stages can report warnings without rejecting otherwise useful records. The interface must show those warnings and make clear when incomplete records are excluded from a total.

### Deterministic calculation boundary

Portfolio balances, valuations, allocations, and historical calculations are computed by deterministic backend code. An optional PocketOrbit Guide can explain an already-computed result or terminology. It must not invent balances, prices, transactions, or tax claims, and it is not the calculation authority.

## Current domain records

The scaffolded SQLAlchemy models and initial migration cover:

- **User and portfolio:** account identity, portfolio ownership, reporting currency, and preferences.
- **Source:** wallet, imported file, or later provider connection; includes its type, label, network, and sync state.
- **Asset and asset mapping:** canonical asset identity plus provider identifiers, symbol, network, contract address or mint, and exchange identifier. A symbol alone is not a safe identifier.
- **Balance and transaction:** normalized quantities and activity associated with an asset and source.
- **Price and valuation snapshot:** provider-specific prices and calculated portfolio values at recorded times.
- **Import and sync job:** processing state, accepted/rejected counts, warnings, and operational diagnostics.
- **Audit event:** administrative actions and other events needed for operational review.

Records that contribute to displayed values should carry relevant provenance fields: `source_type`, `source_name`, `source_record_id`, `retrieved_at`, `effective_at`, `asset_id`, `network_id`, `contract_address`, `quality_status`, `is_estimated`, `is_stale`, `match_confidence`, and `normalization_version`.

## Connector responsibilities and status

Connectors translate external records to normalized PocketOrbit records. They do not calculate authoritative portfolio totals or set product-wide asset identity rules. Solana and EVM RPC balance reads and optional CoinGecko spot pricing are implemented for the stateless wallet snapshot; the generic CSV parser only previews rows.

- **Exchange CSV parsers:** identify the statement format, validate rows, normalize transaction types, and report rejected or unmatched rows.
- **Blockchain connectors:** retrieve current public balances for Solana and EVM-compatible networks. Solana includes SPL and Token-2022 fungible balances; EVM includes native assets and only explicitly configured token contracts. Activity history is not yet implemented.
- **Market-data connector:** optionally returns CoinGecko spot prices by asset ID and token contract or mint with provider timestamps. The API key and endpoint are configured server-side; unknown prices remain missing.
- **Future exchange APIs:** if added, use the smallest available read-only permission set. Trading, withdrawal, and transfer permissions are out of scope.

Each price record keeps its provider and retrieval time. There is no assumed universal crypto price; different providers or markets can report different values.

## Product routes

These routes reflect the screen map in [DESIGN.md](DESIGN.md). The scaffold includes a page for each route. Some pages are informational or placeholder screens; working data flows include the sample portfolio, CSV preview, demo export, and stateless live wallet snapshot API. The web wallet page and dashboard are not yet wired to the live snapshot endpoint.

| Route | Purpose |
|---|---|
| `/` | Product landing page |
| `/how-it-works`, `/security`, `/learn`, `/privacy`, `/terms` | Public product, education, and policy pages |
| `/login`, `/register` | Account access |
| `/app` | Portfolio overview |
| `/app/portfolio`, `/app/activity`, `/app/sources`, `/app/insights` | Portfolio detail, timeline, source management, and explanations |
| `/app/learn`, `/app/import`, `/app/wallets/add` | Education, exchange-file import, and public-wallet setup |
| `/app/reports`, `/app/settings` | Exports and account preferences |
| `/admin` | Operational overview |
| `/admin/users`, `/admin/portfolios`, `/admin/imports`, `/admin/sources` | Support and source operations |
| `/admin/assets`, `/admin/jobs`, `/admin/system`, `/admin/audit`, `/admin/settings` | Asset registry, job and system health, audit, and admin configuration |

The admin area is for platform operations. It must not expose credentials or secrets in diagnostics.

## Security and privacy boundaries

- Public wallet tracking uses public addresses. Never request seed phrases, private keys, recovery words, or wallet signing permissions.
- Linking a public address to a PocketOrbit account is private application data. Users should be able to remove a wallet, imported file, portfolio records, and account.
- The initial exchange workflow prioritizes user-imported files. Any later API connection must be read-only, clearly disclose permissions, and allow disconnecting it.
- Keep credentials separate from normalized portfolio records and encrypt them if a later integration requires storage. Never show a full secret after creation.
- Send portfolio data to an AI provider only when the feature requires it and the user has opted in.
- Keep native asset quantities independent of converted values. Reporting currency changes display values, not underlying quantities.
- Keep the portfolio model global. Do not assume a country, fiat currency, time zone, network, exchange, or tax regime. Jurisdiction-specific reporting requires separate review.

## Environment and deployment

The intended deployment targets are Vercel for `apps/web`, Railway for `apps/api`, and NeonDB for PostgreSQL. `.env.example` files document variable names and safe local defaults only; real credentials belong in an untracked local environment or deployment secret store. No deployment is configured by this scaffold.

Likely environment settings include the API base URL, database connection URL, authentication/session settings, and provider credentials. Add provider keys only when the corresponding connector is implemented. Never commit real credentials.

## Product roadmap boundaries

1. **Foundation:** app shell, authentication, database schema, asset identity, source metadata, portfolio model, reporting currency.
2. **Import MVP:** exchange CSV parsing, validation, normalization, price lookup, deterministic portfolio calculation, overview, and activity timeline.
3. **Wallets:** supported public addresses, blockchain connectors, balances, public activity, and provenance.
4. **Intelligence:** richer transaction classification, insights, reconciliation, plain-language explanations, and optional Guide.
5. **Connected accounts:** read-only exchange APIs, scheduled synchronization, provider health, and alerts.
6. **Reporting:** exports, cost-basis tools, jurisdiction-specific tax exports after review, and additional reporting currencies.

The event build scope is defined separately in [HACKATHON.md](HACKATHON.md). Product direction and planned integrations in this file are not claims that those integrations are currently supported.
