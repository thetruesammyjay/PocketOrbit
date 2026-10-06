# PocketOrbit

> **Your crypto, in one clear view.**

PocketOrbit is a read-only crypto portfolio companion. It brings assets from supported public wallets and exchange records into one portfolio view, then explains where the balances, prices, and activity came from.

## How PocketOrbit works

![Infographic: Add a public wallet or exchange file, organize the records, see the portfolio, and check where the information came from. PocketOrbit is read-only and never asks for private keys or seed phrases.](assets/PocketOrbit-Product-Flow.png)

Add a public wallet address or upload an exchange statement. PocketOrbit brings the records together so you can see your balances, portfolio value, and activity in one place. You can check where each number came from and when it was last updated. PocketOrbit can read and organize your records, but it cannot move your crypto.

## The problem

Crypto assets are spread across wallets, networks, and exchanges. Each service shows only part of the picture, and portfolio totals can hide stale prices, unmatched tokens, duplicated transfers, or incomplete history. PocketOrbit is designed to make those limits visible alongside the numbers.

## What we are building

PocketOrbit will let people combine supported portfolio sources and understand:

- what assets they track and where those assets are held;
- the value of the tracked portfolio in a chosen reporting currency;
- how balances and recorded activity change over time;
- which sources, prices, and calculation times support each result;
- which records are incomplete, stale, estimated, or awaiting review.

PocketOrbit is read-only. It does not custody assets, execute trades, request private keys or seed phrases, or predict investment returns. Portfolio calculations are deterministic; optional explanations may describe calculated results but do not produce authoritative balances.

## Product principles

- **Clear:** Explain crypto and portfolio terms in plain language.
- **Traceable:** Keep source and freshness information with important values.
- **Read-only:** Use public addresses and imported records for the initial product.
- **Honest:** Show missing, conflicting, stale, and uncertain data instead of hiding it.
- **Global:** Keep native asset quantities separate from reporting-currency values and avoid assuming one country, currency, network, or tax regime.

## Project status

This repository currently contains the product and design documentation plus brand assets. The application implementation is planned; the target repository layout and responsibilities are documented in [Project Structure](docs/PROJECT_STRUCTURE.md).

## Documentation

- [Design system and product UI specification](docs/DESIGN.md)
- [Project architecture and complete file map](docs/PROJECT_STRUCTURE.md)
- [2026 Crypto World's Fair hackathon MVP](docs/HACKATHON.md)

<p align="center">
  <strong>PocketOrbit</strong><br />
  Know what you own. Know where it is. Know where the numbers came from.
</p>
