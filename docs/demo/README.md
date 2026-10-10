# Synthetic demo file

[`pocketorbit-sample-balances.csv`](pocketorbit-sample-balances.csv) contains invented quantities for demonstrating the current-balance CSV import flow. It is not an exchange export, proof of holdings, price quote, or investment record.

In PocketOrbit's import form, choose **Current account balances** and map:

- `asset` to the asset/symbol column;
- `balance` to the quantity column;
- `network` to the network column.

The rows cover SOL on Solana, ETH on Ethereum L1, and ETH on Base. Imported values remain user-provided and marked for review; a successful import does not verify them on-chain.

## Synthetic transaction review flow

[`pocketorbit-sample-exchange-transactions.csv`](pocketorbit-sample-exchange-transactions.csv) and [`pocketorbit-sample-wallet-transactions.csv`](pocketorbit-sample-wallet-transactions.csv) contain invented Ethereum activity. Import them into separate account sources named `Demo Exchange` and `Demo Wallet`. Map the date, asset, amount, type, network, exchange record ID, transaction value, quote currency, and transaction hash columns.

Leave **full available history** unchecked because these fixtures are only a few sample rows. Review the activity rows, then the matching withdrawal and deposit should produce a transfer suggestion. Confirming it shows how PocketOrbit preserves human review. Reports should continue to label performance partial because the synthetic history is incomplete. Do not use these files as evidence of real holdings or performance.
