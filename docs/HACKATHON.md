# PocketOrbit Hackathon MVP

PocketOrbit is being built for the **2026 Crypto World's Fair by Colosseum**. This document defines the hackathon-sized product slice. The longer-term architecture and product roadmap are in [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md); the visual specification is in [DESIGN.md](DESIGN.md).

## Competition scope and current build

The selected networks for this submission are **Solana, Ethereum L1, and Base**. The API also recognizes Arbitrum, but Arbitrum is outside the competition scope we are presenting. Hyperliquid is not an integration.

The working prototype includes account registration and sign-in, account-owned portfolios, read-only public wallet sources with saved snapshots, generic CSV transaction and current-balance imports, price lookups for identified assets, and a dashboard backed by saved portfolio data. Source, timestamp, coverage, and data-quality information travel with portfolio values. The unauthenticated sample portfolio is illustrative; it is not live account data.

Keep these limitations explicit in the pitch and demo:

- Wallet reads cover supported native assets and fungible tokens. They do not represent NFTs, DeFi positions, or complete on-chain transaction history.
- EVM indexed discovery is bounded. Provider omissions, unsupported assets, and partial reads are labeled; an incomplete portfolio total is withheld.
- CSV transaction history does not establish current holdings. A current-balance CSV can populate holdings, but it is user-provided and remains marked for review.
- Cost basis, realized/unrealized P&L, reliable internal-transfer matching, direct exchange API connections, and verified full-history performance are not implemented.
- The public sample dashboard is not a deployed live-account demo. A live demo requires a reachable web app and API, a production database, and working provider configuration.

The submission-ready product description, pitch and demo scripts, and outstanding portal fields are collected in [HACKATHON_SUBMISSION.md](HACKATHON_SUBMISSION.md).

## MVP goal

Demonstrate that someone can bring supported crypto records together in a single, read-only portfolio view and understand where the important numbers came from.

The MVP should complete one clear loop:

```text
Create portfolio
      ↓
Add supported source
      ↓
Import or retrieve records
      ↓
Validate and normalize
      ↓
Identify assets and resolve prices
      ↓
Calculate portfolio deterministically
      ↓
Review data quality and provenance
      ↓
Understand the portfolio
```

## MVP scope

### 1. Portfolio setup

- Create a portfolio.
- Choose a reporting currency.
- Make clear that reporting currency changes displayed values, not native crypto quantities.

### 2. Exchange CSV import

Allow import of supported exchange transaction or account-history files. State supported formats and file limits before upload.

Process each import through:

```text
Upload → Validate → Normalize → Identify assets → Match prices
       → Calculate portfolio → Present a review
```

Before accepting the results, show accepted and rejected rows, validation warnings, unmatched assets, and the resulting balances. Do not silently discard records that cannot be processed.

### 3. Public wallet tracking

- Allow the user to add a public address for a supported network.
- Clearly label the connection as read-only.
- Retrieve supported balances and public activity through an available data provider or RPC service.
- Never request a seed phrase, private key, recovery phrase, or signing permission.

### 4. Portfolio overview

The dashboard should answer: **What do I own right now, where is it held, and how reliable is this view?**

Show the information that is available for the selected sources:

- total portfolio value in the reporting currency;
- change over a selected period when history supports it;
- allocation by asset, source, and network;
- accounts and wallets with their balances;
- recent supported activity, including transfers and fees;
- source, price, and calculation freshness;
- incomplete, stale, estimated, unmatched, or conflicting records.

Do not display a chart or percentage change as authoritative when the underlying history is unavailable. Label partial results and explain which records are excluded.

## Data quality and provenance

Keep enough context for the user to inspect an important balance or valuation:

- source name and type;
- wallet/network or imported-file reference;
- asset identifier where applicable;
- balance retrieval time;
- price provider and retrieval time;
- portfolio calculation time;
- quality state and known limitations.

Use clear states such as **Fresh**, **Delayed**, **Partial**, **Needs review**, **Unmatched**, **Offline**, and **Estimated**. A status must include a short explanation. Do not guess an asset from its symbol alone when identity is uncertain.

## Suggested demonstration path

1. Create a portfolio and choose a reporting currency.
2. Add a supported public wallet or import a supported exchange file.
3. Show the processing stages and at least one useful validation or matching result.
4. Review the normalized balances and activity before they are included.
5. Open the overview and show value, allocation, and source grouping.
6. Open a source/freshness detail and trace a displayed value to its source and timestamps.
7. Point out any incomplete or unmatched data and how it affects the displayed total.

Use a clearly identified demo portfolio or fixture data if a live provider is unavailable. Demo data must not be presented as a user's live wallet data.

## MVP acceptance target (not a claim that every item is complete)

- A new portfolio can be created without granting control over assets.
- At least one supported exchange CSV format can be imported and reviewed.
- A public address on at least one supported network can be tracked without signing access.
- The portfolio view can represent imported and wallet data as distinct sources.
- Imported or retrieved records pass through validation and normalization before calculation.
- The user can see review outcomes, including warnings and unmatched records where present.
- Portfolio totals are produced by deterministic application logic, not generated by an AI model.
- A displayed value can be traced to a source and relevant timestamps.
- The interface marks partial, stale, or estimated information instead of presenting it as certain.
- The experience works on mobile and desktop for the demonstrated path.

## Explicitly out of scope for the hackathon MVP

- Custody or initiating trades, swaps, transfers, bridges, staking, or withdrawals.
- Private-key, seed-phrase, recovery-word, or wallet-signing access.
- Guaranteed price predictions or buy/sell recommendations.
- Broad coverage of every exchange, blockchain, wallet, or CSV format.
- Direct exchange API credentials unless a later, explicitly read-only integration is added.
- Tax advice or jurisdiction-specific tax claims.
- AI-generated portfolio balances, prices, or transactions.

## Product statement

PocketOrbit is not another trading screen. It is a calm place to understand a fragmented crypto portfolio, with the source and limits of its data visible alongside the result.
