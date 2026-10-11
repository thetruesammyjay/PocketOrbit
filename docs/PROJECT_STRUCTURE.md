# PocketOrbit Project Structure

This document maps the current PocketOrbit repository and explains the boundaries between the web app, API, shared packages, and providers.

## Repository status

PocketOrbit is a working monorepo prototype. Accounts, ownership-checked portfolios, persistent public-wallet snapshots, CSV transaction and balance imports, bounded price lookups, and a live portfolio dashboard are implemented. The public demo remains illustrative. EVM indexed token discovery can use dedicated Alchemy endpoints or compatible RPC providers and falls back to operator-configured contracts.

The inventory below lists the repository, application, package, brand, and documentation files. Local environment files, generated build output, virtual environments, dependency caches, and installed packages are excluded. Dependency manifests and lockfiles are maintained at the repository root and in the API package.

## Current file inventory

    PocketOrbit/
    ├── .github/
    │   └── workflows/
    │       └── ci.yml
    ├── .editorconfig
    ├── .env.example
    ├── .gitignore
    ├── CONTRIBUTING.md
    ├── LICENSE.md
    ├── package.json
    ├── pnpm-lock.yaml
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
    │   │   │   ├── marketing.css
    │   │   │   ├── layout.tsx
    │   │   │   ├── page.tsx
    │   │   │   ├── how-it-works/page.tsx
    │   │   │   ├── learn/page.tsx
    │   │   │   ├── login/page.tsx
    │   │   │   ├── forgot-password/page.tsx
    │   │   │   ├── privacy/page.tsx
    │   │   │   ├── register/page.tsx
    │   │   │   ├── reset-password/page.tsx
    │   │   │   ├── security/page.tsx
    │   │   │   ├── terms/page.tsx
    │   │   │   ├── verify-email/page.tsx
    │   │   │   ├── app/
    │   │   │   │   ├── layout.tsx
    │   │   │   │   ├── error.tsx
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
    │   │   │       ├── login/page.tsx
    │   │   │       └── (protected)/
    │   │   │           ├── layout.tsx
    │   │   │           ├── page.tsx
    │   │   │           ├── assets/page.tsx
    │   │   │           ├── audit/page.tsx
    │   │   │           ├── imports/page.tsx
    │   │   │           ├── jobs/page.tsx
    │   │   │           ├── portfolios/page.tsx
    │   │   │           ├── settings/page.tsx
    │   │   │           ├── sources/page.tsx
    │   │   │           ├── system/page.tsx
    │   │   │           └── users/page.tsx
    │   │   ├── components/
    │   │   │   ├── admin-data-page.tsx
    │   │   │   ├── admin-feature-page.tsx
    │   │   │   ├── admin-shell.tsx
    │   │   │   ├── app-shell.tsx
    │   │   │   ├── feature-page.tsx
    │   │   │   ├── icon.tsx
    │   │   │   ├── crypto-asset-icon.tsx
    │   │   │   ├── page-heading.tsx
    │   │   │   ├── portfolio-preview.tsx
    │   │   │   ├── quality-status.tsx
    │   │   │   ├── scroll-reveal.tsx
    │   │   │   ├── site-footer.tsx
    │   │   │   └── site-header.tsx
    │   │   ├── features/
    │   │   │   ├── activity/activity-list.tsx
    │   │   │   ├── imports/import-preview-form.tsx
    │   │   │   ├── auth/account-action-form.tsx
    │   │   │   ├── auth/delete-account-form.tsx
    │   │   │   ├── auth/auth-form.tsx
    │   │   │   ├── wallets/add-wallet-form.tsx
    │   │   │   ├── wallets/wallet-source-actions.tsx
    │   │   │   └── portfolio/
    │   │   │       ├── allocation-breakdown.tsx
    │   │   │       ├── dashboard.tsx
    │   │   │       ├── demo-data.ts
    │   │   │       ├── holdings-table.tsx
    │   │   │       ├── portfolio-api.ts
    │   │   │       └── portfolio-chart.tsx
    │   │   ├── lib/
    │   │   │   ├── api-base-path.ts
    │   │   │   ├── format.ts
    │   │   │   ├── internal-api-url.ts
    │   │   │   ├── routes.ts
    │   │   │   └── server-session-cookie.ts
    │   │   └── public/
    │   │       ├── illustrations/
    │   │       │   ├── activity-trail.svg
    │   │       │   ├── number-receipt.svg
    │   │       │   ├── orbit-scene-left.svg
    │   │       │   ├── orbit-scene-right.svg
    │   │       │   ├── read-only-orbit.svg
    │   │       │   └── source-assembly.svg
    │   │       └── brand/
    │   │           ├── PocketOrbit-Logo.png
    │   │           ├── PocketOrbit-Logo-Horizontal.svg
    │   │           ├── PocketOrbit-Mascot-Comet.svg
    │   │           ├── PocketOrbit-Mascot-Orbit.svg
    │   │           ├── PocketOrbit-Mascot-Scout.svg
    │   │           ├── PocketOrbit-Orbit.png
    │   │           ├── PocketOrbit-Product-Flow.png
    │   │           ├── PocketOrbit-Favico.png
    │   │           ├── pocketorbit-comet.png
    │   │           └── pocketorbit-scout.png
    │   └── api/
    │       ├── .env.example
    │       ├── README.md
    │       ├── alembic.ini
    │       ├── pyproject.toml
    │       ├── uv.lock
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
    │       │   │       ├── auth.py
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
    │       │   │   │       ├── normalizer.py
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
    │       │   │   ├── rate_limit.py
    │       │   │   ├── request_limits.py
    │       │   │   └── security.py
    │       │   ├── models/
    │       │   │   ├── __init__.py
    │       │   │   ├── auth_action_token.py
    │       │   │   ├── auth_session.py
    │       │   │   ├── activity.py
    │       │   │   ├── asset.py
    │       │   │   ├── audit_event.py
    │       │   │   ├── balance.py
    │       │   │   ├── import_job.py
    │       │   │   ├── portfolio.py
    │       │   │   ├── price.py
    │       │   │   ├── rate_limit.py
    │       │   │   ├── source.py
    │       │   │   ├── sync_job.py
    │       │   │   ├── user.py
    │       │   │   ├── valuation.py
    │       │   │   └── wallet_snapshot.py
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
    │       │   │   ├── auth_email.py
    │       │   │   ├── activity_service.py
    │       │   │   ├── asset_service.py
    │       │   │   ├── demo_data.py
    │       │   │   ├── import_service.py
    │       │   │   ├── csv_import_service.py
    │       │   │   ├── csv_balance_import_service.py
    │       │   │   ├── import_pricing_service.py
    │       │   │   ├── portfolio_service.py
    │       │   │   ├── persistent_portfolios.py
    │       │   │   ├── pricing_service.py
    │       │   │   ├── quality_service.py
    │       │   │   ├── report_service.py
    │       │   │   ├── source_service.py
    │       │   │   ├── wallet_service.py
    │       │   │   └── wallet_persistence.py
    │       │   ├── workers/
    │       │   │   ├── __init__.py
    │       │   │   └── jobs.py
    │       │   └── workflows/
    │       │       ├── __init__.py
    │       │       ├── import_workflow.py
    │       │       ├── portfolio_refresh_workflow.py
    │       │       └── wallet_sync_workflow.py
    │       ├── migrations/
    │       │   ├── env.py
    │       │   ├── script.py.mako
    │       │   └── versions/
    │       │       ├── 0001_initial.py
    │       │       ├── 0002_auth_sessions.py
    │       │       ├── 0003_persist_wallet_and_import_history.py
    │       │       ├── 0004_shared_rate_limits.py
    │       │       ├── 0005_email_verification_and_recovery.py
    │       │       ├── 0006_valuation_calculation_version.py
    │       │       ├── 0007_price_provenance.py
    │       │       ├── 0008_portfolio_read_indexes.py
    │       │       ├── 0009_import_balance_snapshot_reference.py
    │       │       ├── 0010_transaction_provenance_and_transfers.py
    │       │       └── 0011_admin_session_marker.py
    │       └── tests/
    │           ├── test_auth_sessions.py
    │           ├── test_csv_balance_import.py
    │           ├── test_csv_import.py
    │           ├── test_evm_discovery.py
    │           ├── test_network_config.py
    │           ├── test_portfolio_routes.py
    │           ├── test_postgres_rate_limit.py
    │           ├── test_production_config.py
    │           ├── test_provider_errors.py
    │           ├── test_wallet_persistence.py
    │           └── test_wallet_quality.py
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
        ├── DEPLOYMENT.md
        ├── demo/
        │   ├── README.md
        │   └── pocketorbit-sample-balances.csv
        ├── DESIGN.md
        ├── HACKATHON.md
        ├── HACKATHON_SUBMISSION.md
        ├── PROJECT_STRUCTURE.md
        └── SECURITY.md

Runtime behavior and responsibilities are described below. Current connection coverage, deployment steps, and release limitations are documented in [API.md](API.md), [DEPLOYMENT.md](DEPLOYMENT.md), and [SECURITY.md](SECURITY.md).

API regression coverage lives in the `apps/api/tests/` files listed above. Most tests use in-memory SQLite and mocked RPC responses. `test_postgres_rate_limit.py` exercises shared limiter behavior against PostgreSQL when `POCKETORBIT_POSTGRES_TEST_URL` is configured.

## Application boundaries

| Area | Responsibility | Runtime / target |
|---|---|---|
| `apps/web` | Public pages, account experience, portfolio UI, admin operations | Next.js, TypeScript, Tailwind CSS, Hugeicons; Vercel |
| `apps/api` | Sessions, account-owned portfolios, imports, wallet sync, normalized data, deterministic calculations | Python, FastAPI, Pydantic, SQLAlchemy, Alembic |
| PostgreSQL | Users, sessions, portfolios, source records, wallet snapshots, transactions, prices, and valuations | PostgreSQL |
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

The SQLAlchemy models and Alembic migrations cover:

- **User, auth session, and portfolio:** account identity, password hash, revocable session token hash, portfolio ownership, and reporting currency.
- **Source and wallet snapshot:** public wallet or imported file identity, network, quality, last retrieval, coverage, warnings, and saved balance history.
- **Asset and asset mapping:** canonical asset identity plus provider identifiers, symbol, network, contract address or mint, and exchange identifier. A symbol alone is not a safe identifier.
- **Balance and transaction:** normalized quantities tied to wallet snapshots or imported activity tied to a source.
- **Price and valuation snapshot:** provider-specific prices and calculated portfolio values at recorded times.
- **Import and sync job:** CSV fingerprint, processing state, accepted/rejected counts, and operational diagnostics.
- **Audit event:** administrative actions and other events needed for operational review.

Balances keep source IDs, retrieval times, and snapshot IDs. Prices keep provider, provider update time, retrieval time, and quality. Transactions keep source record IDs, event time, and review status. Data quality is calculated from source coverage, price availability, and freshness.

## Connector responsibilities and status

Connectors translate external records to normalized PocketOrbit records. Portfolio aggregation and quality evaluation live in backend services. Solana and EVM RPC balance reads, saved wallet snapshots, CoinGecko prices, and validated CSV transaction and current-balance imports are implemented.

- **Generic CSV importer:** lets users map columns, validates dates/types/amounts and exact network identities, stores transaction history and an import fingerprint, and reports rejected or unmatched rows. Exchange-specific templates are still planned.
- **Blockchain connectors:** retrieve current public balances for Solana and EVM-compatible networks. Solana includes SPL and Token-2022 fungible balances; EVM can use dedicated Alchemy endpoints or indexed methods on a compatible RPC, then can fall back to configured contracts.
- **Market-data connector:** optionally returns CoinGecko spot prices by asset ID and token contract or mint with provider timestamps. The API key and endpoint are configured server-side; unknown prices remain missing.
- **Future exchange APIs:** if added, use the smallest available read-only permission set. Trading, withdrawal, and transfer permissions are out of scope.

Each price record keeps its provider and retrieval time. There is no assumed universal crypto price; different providers or markets can report different values.

## Product routes

These routes reflect the screen map in [DESIGN.md](DESIGN.md). Account, portfolio, wallet source, import, dashboard, and read-only admin operations are connected. Admin APIs require a signed-in allowlisted account and persist page-access events in `audit_events`; account settings, privacy, and terms remain placeholders or drafts and are not ready for public operations.

| Route | Purpose |
|---|---|
| `/` | Product landing page |
| `/how-it-works`, `/security`, `/learn`, `/privacy`, `/terms` | Public product, education, and policy pages |
| `/login`, `/register` | Account access |
| `/app` | Portfolio overview |
| `/app/portfolio`, `/app/activity`, `/app/sources`, `/app/insights` | Portfolio detail, timeline, source management, and explanations |
| `/app/learn`, `/app/import`, `/app/wallets/add` | Education, exchange-file import, and public-wallet setup |
| `/app/reports`, `/app/settings` | Exports and account preferences |
| `/admin/login` | Administrator account sign-in; uses the normal account session |
| `/admin` | Operational overview |
| `/admin/users`, `/admin/portfolios`, `/admin/imports`, `/admin/sources` | Support and source operations |
| `/admin/assets`, `/admin/jobs`, `/admin/system`, `/admin/audit`, `/admin/settings` | Asset registry, job and system health, audit, and admin configuration |

The admin area is for platform operations. It must not expose credentials or secrets in diagnostics.

## Security and privacy boundaries

- Public wallet tracking uses public addresses. Never request seed phrases, private keys, recovery words, or wallet signing permissions.
- Linking a public address to a PocketOrbit account is private application data. Users can remove saved wallet sources, CSV imports, and accounts. Backup copies still require an operator-defined retention schedule.
- The initial exchange workflow prioritizes user-imported files. Any later API connection must be read-only, clearly disclose permissions, and allow disconnecting it.
- Keep credentials separate from normalized portfolio records and encrypt them if a later integration requires storage. Never show a full secret after creation.
- Send portfolio data to an AI provider only when the feature requires it and the user has opted in.
- Keep native asset quantities independent of converted values. Reporting currency changes display values, not underlying quantities.
- Keep the portfolio model global. Do not assume a country, fiat currency, time zone, network, exchange, or tax regime. Jurisdiction-specific reporting requires separate review.

## Environment and deployment

The API includes `apps/api/railway.toml`, which runs Alembic migrations before deployment and gates traffic on the API readiness endpoint. The web deployment target is not configured in this repository. `.env.example` files document variable names and safe local defaults only; real credentials belong in an untracked local environment or deployment secret store.

Likely environment settings include the API base URL, database connection URL, authentication/session settings, and provider credentials. Add provider keys only when the corresponding connector is implemented. Never commit real credentials.

## Product roadmap boundaries

1. **Implemented foundation:** account sessions, ownership-checked portfolios, source metadata, asset identity, and database migrations.
2. **Implemented prototype flows:** public wallet snapshots, generic CSV transaction imports, bounded price lookups, data provenance, and portfolio views.
3. **Launch readiness:** SMTP and proxy configuration, admin authorization, backups, restore drills, monitoring, retention policies, and reviewed legal documents.
4. **Portfolio integrity:** internal transfer matching, complete exchange statement coverage, explainable cost basis, and realized/unrealized P&L.
5. **Expansion:** exchange APIs, scheduled synchronization, provider health, richer activity classification, and optional plain-language explanations.
6. **Reporting:** exports, cost-basis tools, jurisdiction-specific tax exports after review, and additional reporting currencies.

The event build scope is defined separately in [HACKATHON.md](HACKATHON.md). Product direction and planned integrations in this file are not claims that those integrations are currently supported.
