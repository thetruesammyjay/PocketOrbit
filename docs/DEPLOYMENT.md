# Review Demo Deployment

This guide prepares a hosted PocketOrbit demo for hackathon judges. It does not make the service production-safe by itself. The API's Railway configuration is in [`apps/api/railway.toml`](../apps/api/railway.toml); the Next.js app is in `apps/web`.

## How requests reach the API

The browser calls the web origin at `/api/v1`. Next.js rewrites those requests to the server-only `API_INTERNAL_URL`. This keeps browser API requests same-origin, which is important for the signed session cookie and the API's same-origin mutation check.

Set `API_INTERNAL_URL` on the web deployment to a URL reachable from its server runtime, including `/api/v1`, for example:

```text
https://<api-host>/api/v1
```

Do not put provider credentials in this value or in any `NEXT_PUBLIC_*` variable.

## API service

1. Create a PostgreSQL database and an API service with the repository subdirectory `apps/api` as its working/root directory.
2. Use the existing Railway configuration. It applies Alembic migrations before starting Uvicorn and checks `/api/v1/ready`.
3. Add the following values through the hosting provider's secret/environment settings. Do not upload `.env` files or commit these values.

| Variable | Requirement |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | PostgreSQL URL supported by SQLAlchemy/psycopg |
| `SECRET_KEY` | Unique random value of at least 32 characters |
| `WEB_ORIGIN` | Exact HTTPS origin of the web app, with no path or trailing slash |
| `ADMIN_EMAILS` | Comma-separated allowlist; also configure the matching web value if judges need the admin area |
| `ADMIN_PASSWORD` | Admin login password, at least 12 characters; store in Railway/API secrets only |
| `MAX_REQUEST_BODY_BYTES` | At least `5308416` bytes and no more than `67108864` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM_EMAIL` | Optional; needed only for password recovery email |
| `SMTP_SECURITY` | `starttls` or `ssl`, matching the SMTP service and port, if SMTP is configured |
| `SMTP_USERNAME`, `SMTP_PASSWORD` | Set both when the SMTP service requires authentication |
| `SOLANA_RPC_URL` | HTTPS RPC endpoint for Solana mainnet |
| `SOLANA_RPC_FALLBACK_URL` | Defaults to PublicNode; retries failed Solana reads |
| `ETHEREUM_RPC_URL` | HTTPS RPC endpoint for Ethereum mainnet; `EVM_RPC_URL` is an Ethereum fallback |
| `BASE_RPC_URL` | HTTPS RPC endpoint for Base mainnet |
| `ALCHEMY_API_KEY` | Optional; enables indexed EVM token discovery and the Portfolio API fallback |
| `COINGECKO_API_KEY` | Optional; enables authenticated market-price requests |

Email confirmation is disabled, so SMTP is not needed for registration or sign-in. Add SMTP settings later if you want password recovery emails. The local `apps/api/.env` is ignored by Git and is not copied to a hosted service.

`AUTH_COOKIE_NAME`, `AUTH_COOKIE_SAMESITE`, and `AUTH_SESSION_DAYS` have safe defaults for the same-origin web proxy. Keep the web app and API on the configured origin relationship; do not change the cookie domain or `SameSite` value without testing login, refresh, and logout in a browser.

## Web service

1. Deploy the Next.js application from `apps/web` using the repository's pnpm workspace and lockfile.
2. Set `API_INTERNAL_URL` to the reachable API base URL shown above for both the build and runtime environments. The production build fails if this variable is missing.
3. Set `AUTH_COOKIE_NAME` to the API cookie name. If the admin area is part of the review, set `ADMIN_EMAILS` to the same allowlist as the API. Do not set `ADMIN_PASSWORD` in Vercel; the API validates it from Railway's secret settings.
4. Use the final HTTPS web origin as the API's `WEB_ORIGIN`, then redeploy the API if that value changes.

## Verify before sharing

- Confirm `https://<api-host>/api/v1/ready` reports `ready`, `database: connected`, and `schema: current`.
- Open the web app over HTTPS. Register a controlled test account and confirm registration creates a session, then sign out and sign in again.
- Sign in, sign out, and sign back in to confirm the cookie works through the same-origin proxy.
- Add a wallet you control on each selected network (Solana, Ethereum L1, and Base); verify the result records a source, retrieval time, and any partial-coverage warnings.
- Import a non-sensitive sample CSV and confirm the app labels transaction history separately from current-balance statements.
- Confirm the public sample portfolio is still identified as sample data and never appears as live wallet data.
- Check browser console and server logs for failed requests, secret values, personal data, or wallet addresses before recording the demo.
- Use only test accounts and addresses that you own or have permission to display in a recording.

## Remaining launch operations

Before inviting public users, configure backups and restore drills, monitoring and alerting, retention and deletion policies, incident response, and reviewed privacy/terms pages. See [`SECURITY.md`](SECURITY.md) for the current security and launch gaps.
