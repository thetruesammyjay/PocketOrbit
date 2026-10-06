# Connector contracts

Connectors translate provider-specific information into PocketOrbit records. Provider payloads must not become the product's internal data model.

## Current implementation

- `app/connectors/exchanges/csv/base.py` can preview a generic CSV header and sample rows.
- `app/connectors/exchanges/csv/registry.py` has no registered exchange formats yet.
- `app/connectors/blockchain/solana.py` reads native SOL and fungible SPL / Token-2022 balances through a configured Solana JSON-RPC endpoint.
- `app/connectors/blockchain/evm.py` reads native balances and configured ERC-20 contracts through chain-checked EVM JSON-RPC endpoints. It does not discover arbitrary token contracts.
- `app/connectors/rpc.py` makes bounded HTTP JSON-RPC requests without exposing endpoint credentials in errors.
- `app/services/pricing_service.py` uses an optional configured CoinGecko API key to retrieve native-asset and contract-address prices, with price retrieval and provider-update times.
- `POST /api/v1/wallets/sync` returns a live, stateless snapshot with separate balance and price provenance. It does not save addresses or results.

## Required connector behavior

Every implemented connector should:

1. validate provider input and preserve the original source record identifier where safe;
2. normalize records to stable PocketOrbit fields;
3. return retrieval time and a quality state;
4. report unsupported or ambiguous records instead of guessing;
5. handle provider rate limits, outages, and partial responses explicitly;
6. avoid storing private keys or requesting signing permissions.

Asset matching must use canonical IDs, provider IDs, or network plus contract/mint identifiers. Never identify an asset from its ticker alone.

## Planned provider categories

- Exchange CSV statement parsers, implemented one supported export format at a time.
- Public blockchain data for named networks such as Solana and EVM-compatible chains.
- Market prices with provider ID, quote currency, and retrieval time.
- Direct exchange APIs only if they can use a minimal read-only permission set.

## Coverage and trust behavior

- A missing or unknown market price leaves the asset value blank and produces a warning. It is not changed to zero or inferred from its symbol.
- A partial snapshot returns `totalValue: null` and the subtotal as `knownValue`.
- EVM coverage is limited to the native coin plus ERC-20 contracts explicitly configured by the operator. A successful RPC response is not evidence that every token in the wallet was discovered.
- Public wallet addresses and provider endpoints are not written to logs or response diagnostics. Provider secrets are sent only by the API service.
- Provider endpoints, API keys, and credentials must stay in server-side environment settings. Never put them in `NEXT_PUBLIC_*` variables.
