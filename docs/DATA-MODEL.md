# Data model

The initial SQLAlchemy models live in `apps/api/app/models`. The initial Alembic revision creates the same tables.

## Entities

| Entity | Purpose |
|---|---|
| `User` | Account identity. Authentication is not implemented yet. |
| `Portfolio` | Owner, name, and reporting currency. |
| `Source` | Public wallet, imported file, or later provider connection. |
| `Asset` | Canonical asset identity with network and contract data where relevant. |
| `AssetMapping` | Provider-specific ID mapped to one canonical asset. |
| `Balance` | Asset quantity observed from a source at a recorded time. |
| `Transaction` | Normalized activity record with source, asset, quantity, fee, and timestamp. |
| `Price` | Provider price in a quote currency with retrieval timestamp. |
| `ValuationSnapshot` | Calculated portfolio value in the selected reporting currency. |
| `ImportJob` | File import status and row counts. |
| `SyncJob` | Source refresh status. |
| `AuditEvent` | Operational event record. |

## Provenance and quality

Records used to calculate a displayed value should carry source type/name, provider or source-record ID, retrieval/effective timestamps, canonical asset and network identifiers, quality status, estimated/stale flags, match confidence, and normalization version. The initial models contain core provenance fields; extend them before implementing persistent provider ingestion.

Native quantities remain separate from converted fiat values. A reporting-currency change must not mutate the source quantity.

## Asset identity

Ticker symbols are display labels, not unique keys. Match assets by a canonical asset ID, provider ID, or a network plus contract/mint pair. Conflicts remain reviewable instead of being silently merged.
