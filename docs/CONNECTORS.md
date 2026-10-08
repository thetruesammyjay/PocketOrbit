# Connector contracts

Connectors translate provider data into PocketOrbit's normalized records. Provider payloads do not define the internal data model.

## Implemented connectors

- **Solana RPC:** reads SOL and fungible SPL / Token-2022 balances for a public address.
- **EVM RPC:** checks chain ID, reads the native coin, and reads configured ERC-20 contracts when needed.
- **Alchemy indexed token discovery:** set `ALCHEMY_API_KEY` to use generated Ethereum, Base, and Arbitrum indexer endpoints, or set `*_INDEXED_RPC_URL` to override them per network. Configured chain RPCs remain primary for chain reads; if a chain-ID read fails, the matching indexed endpoint is tried. The connector first uses `alchemy_getTokenBalances`; when unavailable, the metadata-enabled Portfolio API can provide token balances and can also provide native balances if chain RPC reads fail. Without either indexer, `auto` mode falls back to configured contracts. A wallet sync inspects at most 200 positive token contracts across up to 10 pages and stops when a page proves the 200-token cap was exceeded. At most eight token reads run concurrently. Balances that exceed database storage precision (20 whole digits or 18 decimal places), omitted assets, page truncation, provider partial errors, and token-specific balance or metadata failures mark coverage partial. Portfolio API balances use the provider's latest state, not the separate RPC block. Malformed indexer responses fail the sync. Set `alchemy` to require indexed discovery or `configured_only` to disable it.
- **CoinGecko:** optionally looks up native-asset and exact network/contract prices. CSV imports trigger bounded price lookups for supported, identified assets.
- **Generic CSV:** previews column names, suggests mappings, validates transaction dates, signed quantities, transaction kinds, balance quantities, supported networks, and contract or mint identities. Users choose between transaction history and current balance statements. The upload itself is discarded.

See [`API.md`](API.md) for setup, endpoints, limits, and unsupported asset classes.

## Required connector behavior

Every connector should:

1. validate provider input and preserve source record identifiers where safe;
2. normalize records to stable PocketOrbit fields;
3. return retrieval time and data quality;
4. report unsupported or ambiguous records instead of guessing;
5. handle provider rate limits, outages, and partial responses explicitly;
6. avoid storing private keys or requesting signing permissions.

Asset matching must use canonical IDs or network plus contract/mint identifiers. Never identify an asset from its ticker alone. CSV rows remain user-provided and need review even when the asset identity is exact.

## Coverage and trust behavior

- Missing prices remain missing; they are not changed to zero or inferred from a symbol.
- A portfolio with incomplete source coverage has `totalValue: null`; `knownValue` is the priced subtotal of the records currently included, not a guarantee of completeness.
- Transaction-history imports do not establish current balances and may be incomplete or overlap wallet sources. Current balance statements populate reviewable holdings, but remain user-provided and keep the portfolio total partial.
- A successful RPC response does not prove that every token was discovered. EVM coverage reports whether indexed discovery or configured contracts were used.
- Indexed ERC-20 balances use the provider's latest state and do not claim the same block reference as the native balance. Configured-contract reads are pinned to the reported block.
- If the indexer cannot read or normalize individual token balances, those contracts are omitted, the snapshot is marked partial, and `totalValue` is withheld.
- NFTs, DeFi positions, complete chain activity indexing, exchange-specific parsers, and direct exchange APIs are not currently implemented.
- Public wallet addresses and provider endpoints must not be written to logs or diagnostics. Provider secrets stay in API-side settings and never appear in `NEXT_PUBLIC_*` variables.
