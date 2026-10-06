# Architecture

PocketOrbit separates source adapters, record normalization, deterministic calculations, persistence, and presentation. The API owns data interpretation and portfolio math; the web app renders the result and its provenance.

```text
Public wallet / exchange file / price provider
                    ↓
       Read-only RPC connector or CSV parser
                    ↓
         Validation and normalization
                    ↓
       Asset identity and activity review
                    ↓
        Deterministic portfolio engine
                    ↓
       FastAPI API with live provider reads
                    ↓
         Next.js web application
```

## Services

- `apps/web`: Next.js App Router frontend, TypeScript, Tailwind CSS 4, and Hugeicons. Intended hosting target: Vercel.
- `apps/api`: FastAPI service with Pydantic contracts, SQLAlchemy models, and Alembic migrations. Intended hosting target: Railway.
- PostgreSQL: planned persistent store; NeonDB is the intended managed provider.
- `packages/types`: shared browser-side domain types.
- `packages/ui`: shared React primitives. Product screens own composition and data behavior.

## Calculation boundary

The API calculates balances, values, allocations, and performance from normalized records and selected price inputs. It must preserve the price provider and retrieval time used for each result. Optional AI explanations may describe verified results but do not calculate authoritative values.

## Current API behavior

- The overview uses illustrative fixture data, either from the demo API endpoint or a local fallback.
- `GET /api/v1/health` works without PostgreSQL.
- `GET /api/v1/portfolios/demo/summary` returns a deterministic fixture response.
- `POST /api/v1/imports/preview` previews CSV headings and sample rows. It does not save or normalize records.
- `POST /api/v1/wallets/sync` reads a public address through configured RPC and attaches optional CoinGecko pricing and provenance. It is stateless and does not persist the address or snapshot.
- Solana token balances are read from the standard token programs. EVM reads cover the native coin and configured ERC-20 contracts only; arbitrary token discovery is not supported by plain EVM JSON-RPC.
- Authentication and administrative authorization are not configured.

The web overview still uses labeled fixture data until it is connected to the live wallet endpoint. Do not treat demo data as live wallet data or current market prices. Before public deployment, add authentication and stronger per-user API limits for wallet lookups.
