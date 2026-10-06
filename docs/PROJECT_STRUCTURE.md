# PocketOrbit Project Structure

This document maps the repository, explains the role of each planned application area, and records the system boundaries that keep PocketOrbit understandable and read-only.

## Repository status

The current checkout is a documentation-and-assets starter. It contains the files listed under **Present in this checkout**. Application and configuration files in the target map are **planned**; their presence in this document does not mean that they have been implemented.

### Present in this checkout

```text
PocketOrbit/
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
└── docs/
    ├── DESIGN.md
    ├── HACKATHON.md
    └── PROJECT_STRUCTURE.md
```

The SVG files are the scalable brand artwork. PNG files are raster versions for contexts that need them. Keep these source assets in `assets/`; a web deployment may expose copies from its public directory when static URLs are needed.

### Target repository map

The following is the intended monorepo layout for the product. `planned` labels distinguish future implementation files from the current checkout. Generated lockfiles and migration revisions are created by their tools as the project is implemented.

```text
PocketOrbit/
├── .editorconfig                         # planned: shared editor formatting
├── .env.example                          # planned: documented variable names, no secrets
├── .gitignore                            # planned: build output, caches, local secrets
├── package.json                          # planned: root scripts and workspace commands
├── pnpm-workspace.yaml                   # planned: JavaScript workspace definition
├── pnpm-lock.yaml                        # generated: pinned JavaScript dependencies
├── LICENSE                               # optional: add after the project license is chosen
├── README.md                             # present: short product introduction
├── assets/                               # present: brand and mascot source artwork
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
│   └── PocketOrbit-Product-Flow.png             # present: README product explainer
├── apps/
│   ├── web/                              # planned: Next.js user and admin application
│   │   ├── package.json
│   │   ├── next.config.ts
│   │   ├── postcss.config.mjs
│   │   ├── tsconfig.json
│   │   ├── public/
│   │   │   └── brand/                    # static copies of the root brand assets
│   │   │       ├── PocketOrbit-Logo-Horizontal.svg
│   │   │       ├── PocketOrbit-Logo-Horizontal.png
│   │   │       ├── PocketOrbit-Mascot-Orbit.svg
│   │   │       ├── PocketOrbit-Mascot-Orbit.png
│   │   │       ├── PocketOrbit-Mascot-Scout.svg
│   │   │       ├── PocketOrbit-Mascot-Scout.png
│   │   │       ├── PocketOrbit-Mascot-Comet.svg
│   │   │       ├── PocketOrbit-Mascot-Comet.png
│   │   │       ├── PocketOrbit-Mascot-Family.svg
│   │   │       └── PocketOrbit-Mascot-Family.png
│   │   ├── app/
│   │   │   ├── layout.tsx                # global metadata, font, and providers
│   │   │   ├── globals.css               # Tailwind entry and global styles
│   │   │   ├── page.tsx                  # public landing page: /
│   │   │   ├── how-it-works/page.tsx     # public product explanation
│   │   │   ├── security/page.tsx         # public security explanation
│   │   │   ├── learn/page.tsx            # public education landing page
│   │   │   ├── privacy/page.tsx          # public privacy information
│   │   │   ├── terms/page.tsx            # public terms
│   │   │   ├── login/page.tsx            # sign-in screen
│   │   │   ├── register/page.tsx         # account creation screen
│   │   │   ├── app/
│   │   │   │   ├── layout.tsx            # authenticated user-app shell
│   │   │   │   ├── page.tsx              # overview dashboard: /app
│   │   │   │   ├── portfolio/page.tsx
│   │   │   │   ├── activity/page.tsx
│   │   │   │   ├── sources/page.tsx
│   │   │   │   ├── insights/page.tsx
│   │   │   │   ├── learn/page.tsx
│   │   │   │   ├── import/page.tsx
│   │   │   │   ├── wallets/add/page.tsx
│   │   │   │   ├── reports/page.tsx
│   │   │   │   └── settings/page.tsx
│   │   │   └── admin/
│   │   │       ├── layout.tsx            # protected operational shell
│   │   │       ├── page.tsx              # admin overview
│   │   │       ├── users/page.tsx
│   │   │       ├── portfolios/page.tsx
│   │   │       ├── imports/page.tsx
│   │   │       ├── sources/page.tsx
│   │   │       ├── assets/page.tsx
│   │   │       ├── jobs/page.tsx
│   │   │       ├── system/page.tsx
│   │   │       ├── audit/page.tsx
│   │   │       └── settings/page.tsx
│   │   ├── components/
│   │   │   ├── app-shell.tsx             # shared user navigation and layout
│   │   │   ├── admin-shell.tsx           # admin navigation and layout
│   │   │   ├── site-header.tsx           # public-site navigation
│   │   │   ├── mobile-navigation.tsx     # user bottom navigation and More sheet
│   │   │   ├── source-freshness.tsx      # provenance and retrieval details
│   │   │   ├── quality-status.tsx        # Fresh/Partial/etc. status display
│   │   │   ├── empty-state.tsx
│   │   │   └── page-heading.tsx
│   │   ├── features/
│   │   │   ├── portfolio/
│   │   │   │   ├── portfolio-value-card.tsx
│   │   │   │   ├── portfolio-history-chart.tsx
│   │   │   │   ├── allocation-breakdown.tsx
│   │   │   │   ├── account-list.tsx
│   │   │   │   └── portfolio-api.ts
│   │   │   ├── activity/
│   │   │   │   ├── activity-table.tsx
│   │   │   │   ├── activity-card.tsx
│   │   │   │   └── activity-api.ts
│   │   │   ├── sources/
│   │   │   │   ├── source-list.tsx
│   │   │   │   └── source-api.ts
│   │   │   ├── imports/
│   │   │   │   ├── import-form.tsx
│   │   │   │   ├── import-review.tsx
│   │   │   │   └── import-api.ts
│   │   │   ├── wallets/
│   │   │   │   ├── add-wallet-form.tsx
│   │   │   │   └── wallet-api.ts
│   │   │   ├── insights/
│   │   │   │   ├── insight-list.tsx
│   │   │   │   └── insight-api.ts
│   │   │   └── admin/
│   │   │       ├── source-health-table.tsx
│   │   │       ├── import-diagnostics.tsx
│   │   │       └── admin-api.ts
│   │   ├── hooks/
│   │   │   ├── use-portfolio.ts
│   │   │   └── use-refresh.ts
│   │   └── lib/
│   │       ├── api-client.ts             # typed API transport
│   │       ├── auth.ts                   # client-side auth helpers
│   │       ├── format.ts                 # money, quantity, and date formatting
│   │       └── routes.ts                 # route constants
│   └── api/                              # planned: Python FastAPI service
│       ├── pyproject.toml                # Python dependencies and tool config
│       ├── alembic.ini                   # migration tool configuration
│       ├── railway.toml                   # planned deployment configuration
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py                    # ASGI entry point
│       │   ├── api/
│       │   │   ├── __init__.py
│       │   │   ├── router.py              # API route registration
│       │   │   └── routes/
│       │   │       ├── __init__.py
│       │   │       ├── health.py
│       │   │       ├── auth.py
│       │   │       ├── portfolios.py
│       │   │       ├── sources.py
│       │   │       ├── imports.py
│       │   │       ├── wallets.py
│       │   │       ├── activity.py
│       │   │       ├── insights.py
│       │   │       ├── reports.py
│       │   │       └── admin.py
│       │   ├── core/
│       │   │   ├── config.py              # environment-backed settings
│       │   │   ├── database.py            # PostgreSQL session and engine
│       │   │   ├── security.py            # authentication and authorization
│       │   │   └── logging.py
│       │   ├── models/                    # SQLAlchemy persistence models
│       │   │   ├── user.py
│       │   │   ├── portfolio.py
│       │   │   ├── source.py
│       │   │   ├── asset.py
│       │   │   ├── balance.py
│       │   │   ├── transaction.py
│       │   │   ├── price.py
│       │   │   ├── valuation.py
│       │   │   ├── import_job.py
│       │   │   ├── sync_job.py
│       │   │   └── audit_event.py
│       │   ├── schemas/                   # Pydantic request/response contracts
│       │   │   ├── auth.py
│       │   │   ├── portfolio.py
│       │   │   ├── source.py
│       │   │   ├── asset.py
│       │   │   ├── activity.py
│       │   │   ├── imports.py
│       │   │   └── common.py
│       │   ├── services/                  # application use cases
│       │   │   ├── portfolio_service.py
│       │   │   ├── import_service.py
│       │   │   ├── wallet_service.py
│       │   │   ├── asset_service.py
│       │   │   ├── pricing_service.py
│       │   │   ├── activity_service.py
│       │   │   ├── quality_service.py
│       │   │   └── report_service.py
│       │   ├── connectors/
│       │   │   ├── base.py                # provider-neutral connector contracts
│       │   │   ├── exchanges/
│       │   │   │   └── csv/
│       │   │   │       ├── base.py
│       │   │   │       └── registry.py
│       │   │   ├── blockchain/
│       │   │   │   ├── solana.py
│       │   │   │   └── evm.py
│       │   │   └── market_data/
│       │   │       ├── base.py
│       │   │       └── coingecko.py
│       │   ├── workflows/
│       │   │   ├── import_workflow.py
│       │   │   ├── wallet_sync_workflow.py
│       │   │   └── portfolio_refresh_workflow.py
│       │   ├── calculations/              # deterministic portfolio math
│       │   │   ├── balances.py
│       │   │   ├── valuation.py
│       │   │   ├── allocation.py
│       │   │   └── performance.py
│       │   └── workers/
│       │       └── jobs.py                # background refresh and import jobs
│       ├── migrations/
│       │   ├── env.py
│       │   └── versions/                  # generated Alembic revisions
│       ├── scripts/
│       │   └── seed_demo_data.py
│       └── tests/
│           ├── conftest.py
│           ├── unit/
│           │   ├── test_calculations.py
│           │   ├── test_asset_matching.py
│           │   └── test_csv_parsers.py
│           └── integration/
│               ├── test_import_api.py
│               └── test_portfolio_api.py
├── packages/
│   ├── config/                            # planned: shared TypeScript/lint settings
│   │   ├── package.json
│   │   ├── eslint.config.mjs
│   │   └── tsconfig.base.json
│   ├── types/                             # planned: shared API/domain TypeScript types
│   │   ├── package.json
│   │   └── src/
│   │       ├── index.ts
│   │       ├── asset.ts
│   │       ├── portfolio.ts
│   │       ├── source.ts
│   │       └── activity.ts
│   └── ui/                                # planned: shared accessible React primitives
│       ├── package.json
│       └── src/
│           ├── index.ts
│           ├── button.tsx
│           ├── card.tsx
│           ├── dialog.tsx
│           └── badge.tsx
└── docs/
    ├── DESIGN.md                          # present: brand and UI design specification
    ├── HACKATHON.md                       # present: event MVP and demo scope
    ├── PROJECT_STRUCTURE.md               # present: this repository map
    ├── ARCHITECTURE.md                    # planned: component and runtime boundaries
    ├── API.md                              # planned: endpoint contracts
    ├── CONNECTORS.md                       # planned: provider integration contracts
    ├── DATA-MODEL.md                       # planned: entities and relationships
    └── SECURITY.md                         # planned: threat model and security controls
```

This is the planned v1 repository map, not a promise that every future feature will land in the first release. Add a file when its owning feature is implemented; avoid creating placeholder modules for deferred product ideas.

## Application boundaries

| Area | Responsibility | Planned runtime |
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

## Main domain records

The planned database model covers:

- **User and portfolio:** account identity, portfolio ownership, reporting currency, and preferences.
- **Source:** wallet, imported file, or later provider connection; includes its type, label, network, and sync state.
- **Asset and asset mapping:** canonical asset identity plus provider identifiers, symbol, network, contract address or mint, and exchange identifier. A symbol alone is not a safe identifier.
- **Balance and transaction:** normalized quantities and activity associated with an asset and source.
- **Price and valuation snapshot:** provider-specific prices and calculated portfolio values at recorded times.
- **Import and sync job:** processing state, accepted/rejected counts, warnings, and operational diagnostics.
- **Audit event:** administrative actions and other events needed for operational review.

Records that contribute to displayed values should carry relevant provenance fields: `source_type`, `source_name`, `source_record_id`, `retrieved_at`, `effective_at`, `asset_id`, `network_id`, `contract_address`, `quality_status`, `is_estimated`, `is_stale`, `match_confidence`, and `normalization_version`.

## Connector responsibilities

Connectors translate external records to normalized PocketOrbit records. They do not calculate authoritative portfolio totals or set product-wide asset identity rules.

- **Exchange CSV parsers:** identify the statement format, validate rows, normalize transaction types, and report rejected or unmatched rows.
- **Blockchain connectors:** retrieve public wallet balances, token metadata, and supported public activity for named networks. Initial targets are Solana and EVM-compatible networks.
- **Market-data connectors:** return spot or historical prices and provider identifiers with retrieval times. CoinGecko is the initial example provider in the product notes.
- **Future exchange APIs:** if added, use the smallest available read-only permission set. Trading, withdrawal, and transfer permissions are out of scope.

Each price record keeps its provider and retrieval time. There is no assumed universal crypto price; different providers or markets can report different values.

## Planned product routes

These routes reflect the screen map in [DESIGN.md](DESIGN.md). They are target routes, not implemented routes.

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

The planned deployment targets are Vercel for `apps/web`, Railway for `apps/api`, and NeonDB for PostgreSQL. `.env.example` should document variable names and safe local defaults only; real credentials belong in an untracked local environment or deployment secret store.

Likely environment settings include the API base URL, database connection URL, authentication/session settings, and provider credentials. Add provider keys only when the corresponding connector is implemented. Never commit real credentials.

## Product roadmap boundaries

1. **Foundation:** app shell, authentication, database schema, asset identity, source metadata, portfolio model, reporting currency.
2. **Import MVP:** exchange CSV parsing, validation, normalization, price lookup, deterministic portfolio calculation, overview, and activity timeline.
3. **Wallets:** supported public addresses, blockchain connectors, balances, public activity, and provenance.
4. **Intelligence:** richer transaction classification, insights, reconciliation, plain-language explanations, and optional Guide.
5. **Connected accounts:** read-only exchange APIs, scheduled synchronization, provider health, and alerts.
6. **Reporting:** exports, cost-basis tools, jurisdiction-specific tax exports after review, and additional reporting currencies.

The event build scope is defined separately in [HACKATHON.md](HACKATHON.md). Product direction and planned integrations in this file are not claims that those integrations are currently supported.
