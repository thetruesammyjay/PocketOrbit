# Architecture

PocketOrbit separates provider reads, validation and normalization, portfolio calculations, persistence, and presentation. The API owns source interpretation and portfolio aggregation. The web app renders saved results with their provenance and quality labels.

```text
Public wallet / exchange CSV / price provider
                    ↓
        RPC connector or CSV normalizer
                    ↓
       Validate identity and normalize rows
                    ↓
     Save sources, balances, and transactions
                    ↓
          Calculate values and quality
                    ↓
           FastAPI portfolio API
                    ↓
          Next.js web application
```

## Services

- `apps/web`: Next.js App Router frontend, TypeScript, and shared UI components.
- `apps/api`: FastAPI service with Pydantic contracts, SQLAlchemy models, and Alembic migrations.
- PostgreSQL: accounts, portfolios, source records, snapshots, transactions, prices, and import history.
- `packages/types`: shared TypeScript API and domain types.
- `packages/ui`: shared React UI primitives.

## Current data flow

- Browser users register or sign in. The API issues an opaque HttpOnly session cookie and stores only an HMAC of its token in PostgreSQL.
- Login, registration, wallet refresh, and CSV operations update atomic fixed-window rate counters in PostgreSQL. Hashed rate-limit keys work across API replicas; development without a database uses a local-only fallback.
- Each account owns its portfolios. Every portfolio API operation checks that ownership.
- Adding a public wallet saves the source first, then reads the supported chain through a configured RPC endpoint and resolves available prices. Successful reads save a wallet snapshot and portfolio valuation; failed reads keep the source marked offline without creating a fake snapshot, so the user can retry it later. Refreshing a saved wallet appends another snapshot and records a completed or failed sync job. Users can remove the wallet source and its saved history.
- CSV preview suggests column mappings without storing the upload. Transaction-history imports save normalized activity, account identity, observed coverage, optional costs/proceeds, and row-level provenance; current-balance imports save a balance snapshot. Overlapping exports skip duplicate normalized events. Both modes validate mapped rows, store a file fingerprint, and discard the original file. A saved import can be removed and imported again with a corrected mapping.
- The portfolio API calculates current holdings from saved wallet snapshots and current-balance CSV snapshots. Imported balance statements remain marked for review and keep the portfolio total partial. Transaction-history rows appear separately as activity and are never treated as current balances, because an incomplete ledger cannot establish what an account holds now.
- Users review imported activity explicitly. Reviewed sends/withdrawals and receives/deposits can produce a transfer suggestion when exact asset identity, amount, and time align; users confirm or reject every suggestion. FIFO performance explains realized events and open lots and reports why its total remains unavailable when coverage is incomplete.
- The web dashboard reads the authenticated portfolio through Next.js server-side requests. Unauthenticated visitors see an explicitly labeled sample portfolio.

## Provider boundaries and quality

Solana reads native SOL and fungible SPL / Token-2022 balances. EVM reads native assets and prefers indexed `alchemy_getTokenBalances` methods, while preserving configured RPCs for standard chain reads. If that method is unavailable and an Alchemy key is configured, the metadata-enabled Portfolio API supplies ERC-20 balances and can also provide native balances when chain RPC reads fail. The response records the source and marks partial provider results. NFTs, DeFi positions, full wallet transaction history, historical currency conversion, and direct exchange API connections are not implemented.

CoinGecko pricing uses exact supported network and contract identity. Ticker-only CSV assets are not looked up by symbol. The API includes source timestamps and data quality; snapshots older than 24 hours are marked delayed. Optional AI explanations may describe computed results but must not calculate authoritative balances or prices.

## Deployment boundary

Production configuration requires HTTPS `WEB_ORIGIN`, PostgreSQL, a unique 32-character `SECRET_KEY`, valid session-cookie settings, and a request-body limit large enough for supported CSV imports. Forwarded IP headers are trusted only from configured proxy CIDRs. Run Alembic migrations as a release step. `/api/v1/health` is process liveness; `/api/v1/ready` checks database connectivity and schema revision. See [`API.md`](API.md) and [`SECURITY.md`](SECURITY.md) for current launch blockers. No production deployment is configured in this repository.
