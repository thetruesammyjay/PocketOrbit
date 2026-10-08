# PocketOrbit API

The FastAPI service uses `/api/v1`. Interactive API documentation is available at `/docs` while the service is running.

## Account and portfolio routes

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Create an account and default portfolio; production accounts verify email before sign-in. |
| `POST` | `/auth/login` | Sign in and issue an HttpOnly session cookie. |
| `POST` | `/auth/verification/resend` | Request an email verification link without revealing whether an account exists. |
| `POST` | `/auth/verification/confirm` | Consume a one-time email verification link. |
| `POST` | `/auth/password/forgot` | Request a one-time password reset link. |
| `POST` | `/auth/password/reset` | Set a new password and revoke existing sessions. |
| `POST` | `/auth/account/delete` | Confirm the password and permanently remove the account's active data. |
| `POST` | `/auth/logout` | Revoke the current session and clear its cookie. |
| `GET` | `/auth/me` | Return the signed-in account. |
| `GET` | `/portfolios` | List the signed-in account's portfolios. |
| `POST` | `/portfolios` | Create a portfolio. |
| `GET` | `/portfolios/{id}/summary` | Load persisted holdings, history, sources, activity, and data quality. |
| `GET` | `/portfolios/{id}/sources` | List saved wallet and import sources. |
| `POST` | `/portfolios/{id}/sources/wallets` | Read and save a public wallet and its first snapshot. |
| `POST` | `/portfolios/{id}/sources/{source_id}/sync` | Refresh a saved wallet and append a snapshot. |
| `DELETE` | `/portfolios/{id}/sources/{source_id}` | Remove a saved wallet source and its balance snapshots. |
| `POST` | `/portfolios/{id}/imports` | Validate and save CSV transaction history or a current balance statement. The file itself is discarded. |
| `GET` | `/portfolios/{id}/imports` | List saved imports. |
| `DELETE` | `/portfolios/{id}/imports/{import_id}` | Remove an import and its saved activity or balance snapshot. |
| `GET` | `/reports/portfolios/{id}/holdings.csv` | Export the signed-in account's saved holdings with values, quality, sources, and update times. |

Every portfolio route checks ownership against the signed-in account. Mutating browser requests must come from the configured `WEB_ORIGIN` in production.

Production registration sends a 24-hour verification link and does not create a session until the email is verified. Password reset links expire after 30 minutes and can be used once. Both token types are stored as keyed hashes, and password changes revoke all active sessions. Development accounts are verified immediately so local work does not require an SMTP service.

## Wallet data

Supported network IDs are `solana`, `ethereum`, `base`, and `arbitrum`. The wallet flow reads public addresses only. It does not request keys or sign transactions.

`POST /portfolios/{id}/sources/wallets` saves the wallet source before its first provider read. A successful read saves each returned balance, a timestamped snapshot, and available price provenance. If the provider is unavailable, the source remains connected with `offline` quality and no fabricated snapshot; retry it through the saved-source sync route. Later successful syncs append snapshots instead of overwriting history. Sync attempts are recorded as completed or failed jobs. `GET /wallets/capabilities` reports configured networks without exposing RPC URLs or credentials. `POST /wallets/sync` remains available for a non-persistent one-time read.

Solana reads native SOL and fungible SPL / Token-2022 balances. EVM reads the native coin and first tries the indexed RPC method `alchemy_getTokenBalances`. If that method is unavailable, it uses Alchemy's metadata-enabled Portfolio API when `ALCHEMY_API_KEY` is configured; if chain RPC reads also fail, the Portfolio API can provide native and ERC-20 balances. Otherwise, `auto` mode falls back to explicitly configured ERC-20 contracts. Set `EVM_TOKEN_DISCOVERY=alchemy` to require indexed discovery, or `configured_only` to disable it. Indexed discovery inspects at most 200 positive-balance contracts and 10 pages per sync, stopping as soon as a page proves the 200-token cap was exceeded. At most eight token reads run concurrently. Additional positive balances, later pages, values outside the stored quantity precision (20 whole digits and 18 decimal places), and individual token balances that cannot be normalized are omitted; the snapshot is marked partial and `totalValue` is withheld. NFTs, DeFi positions, exchange API connections, and full chain transaction indexing are outside the current connector coverage.

The response separates `knownValue` from `totalValue`. `totalValue` is `null` when token coverage or pricing is incomplete. Prices include the provider, provider update time, retrieval time, and quality when available. Prices older than ten minutes are marked delayed; wallet snapshots older than 24 hours are marked delayed. Unknown or missing data is not silently counted as zero.

## CSV imports

`POST /imports/preview` reads a CSV header and up to five rows, suggests column mappings, and does not save data. `POST /portfolios/{id}/imports` requires authentication and accepts `mode=transactions` (the default) or `mode=balances`. Transaction history maps date, asset, and quantity; transaction type is needed when a file uses unsigned amounts. A current balance statement maps asset and quantity, with optional network and contract/mint columns. Files are limited to 5 MB, 20,000 rows, and 256 columns.

Balance statements are attached to a named account source. Select that source on later imports to append a new snapshot; the portfolio summary uses only its latest snapshot, while history remains available. Removing an import removes only its snapshot; removing the final import also removes that source. A duplicate account name must select the existing source instead of creating a second balance source.

Transaction mode stores normalized rows and shows them as activity. It does not infer current holdings from a possibly incomplete ledger. Balance mode saves a timestamped balance snapshot and shows the quantities as holdings; these are user-provided, marked `needs_review`, and do not produce a complete portfolio total. For exact token pricing, map the supported network and contract or mint; ticker-only rows stay unmatched and unpriced. Both modes store a SHA-256 file fingerprint and discard the original upload. Duplicate files are blocked until the saved import is removed. The API's configured body cap rejects oversized multipart requests before parsing.

Both import modes report accepted and rejected rows, up to 100 row-level rejection reasons, unmatched symbols, and warnings. Users can remove an import, which deletes its saved activity or balance snapshot and allows a corrected re-import.

The import response includes accepted and rejected row counts, up to 100 row-level rejection reasons, unmatched symbols, and warnings. Users can remove an import to correct a mapping and re-import it.

## Provider configuration

Set values in `apps/api/.env` for local development and use the deployment secret manager in production. Production startup requires at least one public wallet RPC endpoint, indexed EVM RPC endpoint, or `ALCHEMY_API_KEY`; unsupported or missing wallet providers are reported through `/wallets/capabilities` and sync responses.

- `SOLANA_RPC_URL` for Solana mainnet RPC.
- `ETHEREUM_RPC_URL`, `BASE_RPC_URL`, and `ARBITRUM_RPC_URL` for those networks. `EVM_RPC_URL` remains an Ethereum fallback. EVM endpoints are checked against the expected chain ID.
- `ETHEREUM_INDEXED_RPC_URL`, `BASE_INDEXED_RPC_URL`, and `ARBITRUM_INDEXED_RPC_URL` optionally set per-network RPC endpoints for indexed token methods. These take precedence for discovery and are tried as a chain-read fallback; they must support `eth_chainId` and `alchemy_getTokenBalances`, and the API verifies the chain ID before accepting balances. Token metadata is optional and falls back to ERC-20 contract reads. If used as a chain-read fallback, the endpoint must also support standard EVM RPC methods.
- `ALCHEMY_API_KEY` optionally supplies dedicated Alchemy Token API endpoints for Ethereum, Base, and Arbitrum, and enables the metadata-enabled Portfolio API fallback. A per-network indexed RPC URL overrides the generated Alchemy endpoint for that network. Existing chain RPC URLs remain primary for chain ID, native balances, and standard contract calls; the indexed endpoint is tried as fallback if a chain-ID check fails. Portfolio API balances are timestamped but are not pinned to the EVM block read by a separate RPC.
- `*_TOKEN_CONTRACTS` for comma-separated ERC-20 contracts used in configured-only mode or automatic-discovery fallback.
- `EVM_TOKEN_DISCOVERY=auto|alchemy|configured_only` to select token discovery behavior. `auto` tries indexed RPC, then the Alchemy Portfolio API when configured, then configured contracts; `alchemy` fails the wallet sync if indexed discovery is unavailable; `configured_only` disables indexed discovery. Provider method support is checked during sync.
- `COINGECKO_API_KEY` and the optional base URL/header settings for asset prices.
- In production, configured RPC and CoinGecko endpoints must use HTTPS; CoinGecko API keys are sent in the supported header, not in the base URL.
- `DATABASE_URL` for PostgreSQL, a unique `SECRET_KEY` of at least 32 characters for session-token hashing, and `WEB_ORIGIN` for the exact web origin.
- Browser API calls use the fixed same-origin path `/api/v1` through the Next.js proxy. Set `API_INTERNAL_URL` in the web environment to a server-reachable API base URL that includes `/api/v1`; the value is used by the Next.js proxy and server-rendered portfolio fetches. Set it during the web build and deployment. Keep the API auth cookie host-only (`AUTH_COOKIE_DOMAIN` blank) and use `AUTH_COOKIE_SAMESITE=lax`. This lets the browser store the API's session cookie under the web origin, and lets SSR forward that cookie to the API. Direct browser calls to an unrelated API host do not make a host-only cookie available to the web server.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM_EMAIL`, and `SMTP_SECURITY=starttls|ssl` for production verification and recovery email. If the server requires authentication, set both `SMTP_USERNAME` and `SMTP_PASSWORD` in the secret manager.

`GET /health` is a liveness check. `GET /ready` returns `503` until the database is reachable and its Alembic revision matches the application head. Apply migrations as a deployment release step before routing application traffic.

## Request limits

Authentication, wallet refresh, and CSV actions use shared fixed-window counters in PostgreSQL. Limits are keyed by hashed account, email, or client IP values; raw identifiers are not stored in the counter table. Rejected requests return `429` and a `Retry-After` header. A limiter database error returns `503` rather than allowing an uncounted request. Development without a database uses an in-process fallback and does not provide cross-worker protection.

The API rejects request bodies over `MAX_REQUEST_BODY_BYTES` before parsing them. The default is 8 MiB. Keep this above 5 MiB plus multipart overhead so valid CSV imports fit. `TRUSTED_PROXY_CIDRS` accepts comma-separated CIDR ranges. Set it only to reverse proxies that sanitize or append `X-Forwarded-For`; otherwise forwarded values are ignored. Also configure edge request, connection, and concurrency limits in the hosting platform.

## Current launch limitations

This implementation provides persistent accounts, sources, wallet snapshots, CSV transaction history, shared API rate limits, a request-body cap, email verification, password recovery, and account deletion. Before opening registration to the public, set up backup and restore procedures, monitoring, incident response, and retention policies. The app does not yet calculate explainable cost basis or realized/unrealized P&L, reconcile internal transfers, or guarantee a complete exchange transaction history.
