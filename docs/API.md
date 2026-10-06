# PocketOrbit API

Base path: `/api/v1`. Interactive FastAPI documentation is available at `/docs` while the API is running.

| Method | Path | Current behavior |
|---|---|---|
| `GET` | `/health` | Returns process status, environment, and whether a database URL is configured. |
| `GET` | `/portfolios/demo/summary` | Returns an explicitly illustrative portfolio summary. |
| `GET` | `/sources/demo` | Returns the sample sources shown in the demo portfolio. |
| `POST` | `/imports/preview` | Reads a CSV header and up to five rows; max file size is 5 MB; never persists the upload. |
| `GET` | `/wallets/capabilities` | Reports which read-only RPC networks and market-price provider are configured. |
| `POST` | `/wallets/sync` | Fetches one current public-wallet snapshot, values known assets, and returns provenance. The address and results are not persisted. |
| `GET` | `/reports/demo/holdings.csv` | Downloads a CSV explicitly labeled as illustrative sample data. |
| `GET` | `/admin/status` | Reports that authentication and live admin services are not configured. |

## Contracts

The TypeScript shapes are in `packages/types/src`. Pydantic response models are in `apps/api/app/schemas`. Keep API response fields stable and preserve provenance and quality status when a response is extended.

### Live wallet snapshot

Example request:

```json
{
  "network": "solana",
  "address": "<public-address>",
  "quoteCurrency": "USD"
}
```

Supported network IDs are `solana`, `ethereum`, `base`, and `arbitrum`. Responses include the coverage class, balance source, retrieval time, block or slot reference when available, price source and provider update time, per-asset quality, warnings, and a `knownValue`. `totalValue` is `null` when coverage or pricing is incomplete; the API does not present a partial sum as a complete portfolio total.

Solana reads include native SOL and SPL / Token-2022 fungible token accounts. EVM reads include the native coin and only ERC-20 contracts explicitly configured for that network. Standard EVM JSON-RPC cannot enumerate arbitrary token contracts. NFTs, DeFi positions, activity history, portfolio aggregation, and persistence are not part of this endpoint yet.

The endpoint only performs public read calls. It does not store wallet addresses, balances, or prices and cannot sign transactions. Provider API keys stay in the API environment and are never returned to the browser.

### Provider configuration

Set provider values in `apps/api/.env`:

- `SOLANA_RPC_URL` for Solana mainnet RPC.
- `ETHEREUM_RPC_URL` or the legacy `EVM_RPC_URL` for Ethereum. Set `BASE_RPC_URL` and `ARBITRUM_RPC_URL` separately for those networks. EVM endpoints are checked against their expected chain ID.
- `*_TOKEN_CONTRACTS` as comma-separated, explicitly selected ERC-20 contract addresses per EVM network. Up to 30 addresses per network are read.
- `COINGECKO_API_KEY` for USD or another supported quote currency. Demo API is the default; for a Pro key, set `COINGECKO_API_BASE_URL` and `COINGECKO_API_KEY_HEADER` to the Pro endpoint and header.

`GET /wallets/capabilities` reports configuration presence only; it never returns endpoint URLs or keys.

## Error behavior

Use status codes that explain the failure: `413` for an oversized preview file, `415` for a non-CSV upload, `422` for an invalid address, `502` when the blockchain RPC cannot return balances, and `503` when that RPC is not configured. If the optional price provider fails, return the live balance snapshot with missing prices and a warning. Do not expose stack traces, credentials, or provider secrets in user-facing messages.

## Future API work

Authentication, portfolio CRUD and aggregation, persistent import jobs, transaction history, and admin operations remain future work. The wallet snapshot is a live, stateless preview rather than an authenticated or saved account source. Do not present stub or demo responses as account data.
