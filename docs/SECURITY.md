# Security and privacy

## Product rules

- PocketOrbit is read-only. Never request seed phrases, private keys, recovery phrases, or wallet signing permission.
- Public addresses are public information, but the relationship between an address and an account is private application data.
- Any future exchange API integration must use the least-privileged read-only access available. Never request trading, transfer, or withdrawal permission.
- Keep provider credentials out of source control. Keep secrets separate from normalized portfolio records and never return full secret values to a client.
- Send portfolio data to an AI provider only when a user opts into a feature that needs it.
- Clearly label sample data, stale data, partial results, unmatched records, and estimates.

## Current scaffold limitations

This repository does not yet implement authentication, account isolation, stored provider credentials, production rate limiting, or admin authorization. The `/admin` pages are UI placeholders and must not be used as a production operations console. The CSV preview endpoint reads uploaded content into memory, limits input to 5 MB, returns only a small preview, and does not store the file.

## Before production

Choose and implement authentication and authorization; enforce portfolio ownership on every data endpoint; review upload handling and retention; configure HTTPS, secret storage, logging redaction, database backups, provider allowlists, and rate limits; and publish reviewed privacy and terms documents. Do not describe these controls as active until implemented.
