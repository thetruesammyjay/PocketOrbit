# Colosseum Submission Draft

This is a factual draft for PocketOrbit's 2026 Crypto World's Fair submission. Replace every **Needs founder input** item before submitting. The official Colosseum page asks for the product and integrations, team backgrounds and location, logo, repository, a 2–3 minute presentation video, a product demo video of at most 3 minutes, and a go-to-market plan with demand validation and distribution. It also says the submission should explain the venture, not only the code. See the [official hackathon FAQ](https://colosseum.com/hackathon?year=fall2026).

## Portal fields

| Field | Draft |
|---|---|
| Product name | PocketOrbit |
| Tagline | Your crypto, in one clear view. |
| Short description | PocketOrbit gives people who hold crypto across wallets and exchange exports one read-only portfolio. It brings supported Solana, Ethereum L1, and Base wallet balances together with CSV records, while showing the source, update time, and data-quality warnings behind the numbers. It never asks for private keys or permission to move assets. |
| Selected blockchains | Solana, Ethereum L1, Base |
| Integrations and tools | Solana JSON-RPC; EVM JSON-RPC for Ethereum and Base; optional Alchemy-compatible indexed token discovery; optional CoinGecko pricing; Next.js/TypeScript web app; FastAPI/Python API; PostgreSQL. Provider configuration is server-side. |
| Product graphic | `apps/web/public/brand/PocketOrbit-Logo.png` |
| GitHub repository | `https://github.com/thetruesammyjay/PocketOrbit` — confirm that judges can access it. |
| Team members and backgrounds | Team Leader/Backend Engineer: Samuel Justin Ifiezibe, Frontend Engineer: Ugwumba MacAnointed, Product Design: Ehonor Joshua |
| Team location | Nigeria |
| Public product URL | **Needs deployment:** the current public sample is illustrative, not a live portfolio connection. Follow [DEPLOYMENT.md](DEPLOYMENT.md) to prepare a review demo. |
| License / open-source status | MIT |

## Product pitch

Crypto holders often spread assets across wallets, networks, and exchange exports. A single total can look precise while hiding stale prices, missing tokens, or data that came from an unverified file.

PocketOrbit gives people a read-only view across Solana, Ethereum L1, and Base. Users add a public address or import a CSV. PocketOrbit saves wallet snapshots, organizes supported records, and keeps the source, timestamp, and data-quality status visible beside the result. If coverage is incomplete, it says so instead of presenting a guess as the full portfolio.

The product's wedge is **provenance and honest confidence**: help a user see not only a number, but what supports that number and what is still missing. PocketOrbit does not custody assets, sign transactions, trade, or request private keys.

## What judges can verify in the current prototype

- Create an account with email and password; registration signs the user in immediately.
- Add a public wallet on a supported network and save timestamped balance snapshots.
- Import generic CSV transaction history or a current-balance statement, review validation results, and retain source/import records.
- Review imported transaction rows, inspect date coverage and duplicate counts, and accept or reject rows before using them in performance calculations.
- Review conservative internal-transfer suggestions; the app never confirms a transfer automatically and leaves equally strong candidate matches unresolved.
- View FIFO cost basis and realized/unrealized P&L for supported reviewed records. The API withholds total P&L and explains gaps when history, identity, prices, fees, or balances do not reconcile.
- View saved holdings, supported activity, prices when an asset is identified, source grouping, timestamps, and quality warnings.
- Explore an unauthenticated sample portfolio that is labeled as illustrative.

The product cannot verify that an exchange export contains every record, index complete activity history for public wallets, connect directly to exchange APIs, value transaction fees, or convert historical quote currencies. Token coverage also depends on the configured RPC/indexing provider. Do not describe these areas as complete.

## Business and distribution draft

**Initial customer hypothesis:** people who actively hold crypto across multiple self-custody wallets and exchange accounts, and who need a trustworthy overview without granting trading or custody access.

**Problem hypothesis:** current portfolio tools can make aggregation convenient, but users still need to understand which source produced each balance, how fresh a price is, and whether missing coverage changes the total. PocketOrbit focuses its first experience on explaining that evidence clearly.

**Possible business model — needs founder approval and validation:** free read-only portfolio tracking, with a paid tier for longer history, richer reconciliation and export tools, and multi-portfolio workflows. A later advisor or treasury offering is a separate hypothesis, not a current product commitment.

**Initial distribution hypothesis — needs founder input:** recruit early testers from Solana and EVM wallet communities, crypto meetups, and creator/operator networks; use guided onboarding and feedback sessions to learn which sources and explanations users need most. Name the actual channels and owner before submission.

**Demand validation — needs founder input:** no customer interviews, waitlist, active-user count, letters of intent, or revenue evidence is documented in this repository. Add only evidence the team can substantiate, including dates, sample size, and what changed in the product. If there is no evidence yet, state that plainly and describe the next validation step.

## Presentation video script (target: about 2 minutes)

> People who hold crypto across wallets and exchanges have a basic problem: there is no easy way to see what they own and know whether the numbers can be trusted. Balances can be stale, assets can be missed, and a CSV may show activity without proving what someone holds today.
>
> PocketOrbit is a read-only portfolio tracker for Solana, Ethereum L1, and Base. Add a public wallet or import an exchange CSV. PocketOrbit saves the source and update time, organizes the records, and shows data-quality warnings alongside the portfolio. Users can review imported activity, check possible internal transfers, and inspect FIFO cost basis and performance when the available history supports it. If coverage is incomplete, PocketOrbit explains that instead of pretending the total is complete.
>
> Our focus is provenance and confidence. A user can inspect where a balance came from, when it was retrieved, and what the app could not verify. We never ask for seed phrases or private keys, and we cannot move a user's assets.
>
> Today, the prototype supports public wallet snapshots, saved portfolios, reviewable CSV transaction history, conservative transfer suggestions, and explainable FIFO performance for supported records. Direct exchange connections and complete wallet transaction history remain work to do; user-provided history can still be incomplete.
>
> We are testing whether crypto holders with assets across wallets and exchanges will use a clearer, more honest portfolio view. **[Founder: add the team's relevant experience, verified customer evidence if available, and the next distribution step.]** PocketOrbit: your crypto, in one clear view.

Record this with a founder on camera or voiceover and show the product briefly. Replace the bracketed sentence with verified facts; do not invent traction or founder credentials.

## Product demo run-of-show (target: 2:30; maximum 3:00)

1. **0:00–0:15 — Set the promise.** Show PocketOrbit and say it is read-only, with source and data quality attached to the numbers.
2. **0:15–0:45 — Add a source.** In a working deployed or local environment, add a public address on Solana, Ethereum L1, or Base. Show that the flow asks for a public address only.
3. **0:45–1:15 — Inspect the saved wallet result.** Show the asset, balance, network, retrieval time, provider/source, and any coverage warning.
4. **1:15–1:45 — Import a CSV.** Use the clearly synthetic [`demo/pocketorbit-sample-balances.csv`](demo/pocketorbit-sample-balances.csv). Choose current-balance mode, map its three columns, and show the review warning. Explain that these example balances are not live or verified.
5. **1:45–2:15 — Review records and performance.** Import the two transaction fixtures described in [`demo/README.md`](demo/README.md), review the activity rows, then show the possible transfer suggestion and its manual confirmation. Open Reports to show FIFO cost basis and the reasons the sample remains partial. Do not claim that the fixture history is complete.
6. **2:15–2:30 — Close with the boundary.** Reiterate no custody, no trading, and no private keys; state the one next feature the team is validating.

Use only an account and addresses you control or have permission to display. Hide credentials, email addresses, and any private account data in the recording. If the live provider is unavailable, use clearly labeled sample data and do not call it a live wallet result.

## Final submission checklist

- [ ] Add relevant backgrounds for the listed teammates and confirm they are registered on the portal.
- [ ] Confirm repository visibility and give judges access if it is private.
- [x] Add the MIT license and contribution instructions.
- [ ] Add substantiated user research or explicitly say validation is early / not yet done.
- [ ] Deploy and verify a public demo, or clearly explain that the videos show a local prototype.
- [ ] Record and upload the 2–3 minute presentation video and the <=3 minute product demo.
- [ ] Confirm the selected chain list is Solana, Ethereum L1, Base.
- [ ] Disclose any relevant pre-hackathon product/code work. The visible Git history in this checkout begins on 2026-10-05; that alone does not establish when every current file was created.
- [ ] Complete the portal submission before its deadline. The official page currently lists submissions due October 12, 2026; verify the portal's displayed cutoff and timezone before the final upload.
