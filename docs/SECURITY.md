# Security and privacy

PocketOrbit is designed to read public information. It must never request seed phrases, private keys, recovery words, or wallet signing permissions. A public address linked to an account is still private application data.

## Implemented controls

- Account passwords are stored as scrypt hashes. Browser sessions use random tokens in HttpOnly cookies; the database stores HMAC token digests and supports revocation at logout.
- Account registration and sign-in do not require email confirmation. Account email ownership is therefore not verified. Password reset links expire after 30 minutes, are single-use, and are stored as HMAC digests; password reset revokes every active browser session. Recovery links require optional SMTP configuration.
- Users can delete their account after confirming their password. The API removes the active account, portfolios, sources, snapshots, transactions, imports, sessions, and account-specific rate-limit counters.
- Portfolio reads and writes check account ownership.
- Production startup requires HTTPS `WEB_ORIGIN`, PostgreSQL, a unique `SECRET_KEY` of at least 32 characters, and valid session settings. Production mutation requests must include a matching `Origin` or `Referer`.
- Admin sign-in checks the API-side `ADMIN_EMAILS` allowlist and `ADMIN_PASSWORD`. The password remains in the API secret manager and is neither stored in the database nor exposed to browser JavaScript. Admin sessions are marked in the database; regular account sessions cannot access admin pages or `/api/v1/admin/*` endpoints, even when their email matches the allowlist. Configure the same comma-separated list in web and API environments. The API returns `404` to non-admin sessions; admin page views are recorded in the existing `audit_events` table. The admin console is read-only and does not expose secrets or full wallet addresses.
- Authentication, wallet refresh, and CSV operations use atomic PostgreSQL fixed-window rate limits shared across API instances. Limits return `429` with `Retry-After`; limiter database failures fail closed. Development without a database uses a process-local limiter only.
- Request bodies are capped before FastAPI parses them. The default `MAX_REQUEST_BODY_BYTES` is 8 MiB, allowing a 5 MB CSV with multipart overhead.
- Forwarded client IPs are trusted only when the direct peer belongs to an explicitly configured `TRUSTED_PROXY_CIDRS` network. Untrusted `X-Forwarded-For` headers are ignored.
- RPC and price-provider credentials remain in the API environment. Provider errors are reduced to generic messages.
- CSV files are limited to 5 MB and 20,000 rows. The original file is discarded; normalized transaction rows or balance snapshots and a SHA-256 file fingerprint are stored. Users can remove imports and their saved rows or balances.
- EVM automatic token discovery and configured-contract fallback are bounded. Wallet addresses and snapshots are scoped to account-owned portfolios.
- Missing prices, partial source coverage, delayed snapshots, unmatched assets, unverified CSV transactions, and user-provided balance statements are labeled.

## Remaining launch blockers

This is an implementation baseline, not a completed security program. Before opening public registration:

- decide whether accepting unconfirmed email addresses is acceptable for the intended audience; an attacker can register an address they do not own and prevent its owner from using it;
- publish and enforce retention schedules for backups and operational records after account deletion;
- configure additional edge-level rate limits and connection/concurrency limits for the deployment;
- define a review and retention policy for admin audit events before public launch; current events record admin page access, not every user-facing mutation;
- review the privacy and terms documents with appropriate counsel and publish retention/deletion policies;
- configure database backups, restore drills, monitoring, alerting, and incident response;
- review dependency updates, secret rotation, deployment access, log retention, and provider data-processing terms;
- review CSV import semantics, transaction duplication, cost basis, internal-transfer handling, and source overlap before presenting account totals as complete.

The sample portfolio is illustrative. Never treat fixture data as a connected account. Do not put provider credentials in `NEXT_PUBLIC_*` variables or commit local `.env` files.
