# Data model

SQLAlchemy models live in `apps/api/app/models`. Alembic revisions in `apps/api/migrations/versions` create and evolve the PostgreSQL schema.

## Entities

| Entity | Purpose |
|---|---|
| `User` | Account email, password hash, email verification time, and creation time. |
| `AuthSession` | HMAC of a random browser token, owning account, admin-session marker, expiry, and creation time. |
| `AuthActionToken` | Hashed, single-use email verification or password reset token with expiry. |
| `Portfolio` | Owner, display name, reporting currency, and the first imported-history timestamp used to keep older valuation calculations out of current history. |
| `Source` | Account-owned public wallet or imported CSV record; stores source kind, network, masked display label, quality, and last retrieval. |
| `WalletSnapshot` | A timestamped wallet read with quote currency, coverage, warnings, quality, and known/complete value. |
| `Asset` | Canonical asset identity with network, contract or mint, symbol, and decimals. |
| `AssetMapping` | Provider-specific identifier mapped to a canonical asset. |
| `Balance` | Asset quantity observed from a source in a particular wallet snapshot. |
| `Transaction` | Normalized activity with source/import provenance, external record ID, stable row identity, hash, asset quantity/type/time, optional fee and quote values, and review quality. |
| `TransferMatch` | A suggested, confirmed, or rejected pair of outgoing/incoming records with confidence, rationale, and review time. |
| `Price` | Provider price in a quote currency with retrieval timestamp. |
| `ValuationSnapshot` | Calculated portfolio value, known subtotal, reporting currency, and calculation version. |
| `ImportJob` | CSV fingerprint, source, status, filename, accepted/rejected/duplicate row counts, observed activity date range, and the user's history completeness assertion. The uploaded file itself is not stored. |
| `SyncJob` | Recorded source refresh status and result. |
| `AuditEvent` | Database-backed administrator page-access event with actor, page, and time. |
| `RateLimitWindow` | Hashed subject and time-window request count shared by API replicas. |

## Provenance and quality

Wallet balances and imported exchange balance statements link to their source and saved snapshot. Transactions link to an import, their original external record ID, a stable normalized row ID, and activity time. Overlapping exports for the same named account share a source; duplicate normalized events are skipped. Prices carry the provider, provider update time, retrieval time, and quality. Portfolio summaries read the latest snapshot per balance source, latest price per asset, and latest 12 activity rows; the Activity route pages through the saved ledger. User-provided balance snapshots are marked for review and keep the portfolio total partial. Prices older than ten minutes are delayed; wallet snapshots older than 24 hours are delayed.

Transaction review is a user assertion and does not mean a provider independently verified the record. Transfer matches remain suggestions until the user confirms them. FIFO performance uses reviewed activity and supported quote values. It reports observed source ranges and an explicit history completeness claim; it withholds a total when it finds gaps, unresolved transfers, unknown basis, unsupported fees/currencies, wallet sources without transaction history, or unreconciled imported balances.

Ticker symbols are display labels, not unique identifiers. CSV ticker-only rows are stored as unmatched assets. An exact contract or mint identifies a network asset, but a CSV transaction remains user-provided and needs review until independently verified.

Wallet and price data older than 24 hours are marked delayed. Missing prices are not zero-filled. `knownValue` is the priced subtotal of the data currently included; it does not guarantee that the portfolio is complete. `totalValue` is withheld when source coverage or history is partial.

Native quantities remain separate from converted values. A reporting-currency change must not mutate the source quantity.
