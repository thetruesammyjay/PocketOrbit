# Contributing to PocketOrbit

Thanks for helping improve PocketOrbit. Contributions should make portfolio data easier to understand and keep its source, freshness, and limitations visible.

## Before you start

- Check the existing issues and documentation before starting a large change.
- For a substantial feature or change to the data model, open an issue or discuss the approach first.
- Do not include real wallet addresses, account emails, credentials, `.env` files, or user portfolio exports in commits, tests, screenshots, or sample data.
- Use synthetic values for fixtures and demos. Never request seed phrases, private keys, signing access, or permission to move assets.

## Development setup

Install the workspace dependencies from the repository root:

```powershell
pnpm install
```

Create local environment files from the checked-in examples, configure a local PostgreSQL database and a unique development `SECRET_KEY`, then apply API migrations:

```powershell
if (-not (Test-Path apps/api/.env)) { Copy-Item apps/api/.env.example apps/api/.env }
if (-not (Test-Path apps/web/.env.local)) { Copy-Item apps/web/.env.example apps/web/.env.local }
uv run --directory apps/api alembic upgrade head
```

Start the API and web app in separate terminals:

```powershell
pnpm dev:api
pnpm dev
```

See [README.md](README.md), [API.md](docs/API.md), and [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for more setup and architecture details.

## Code expectations

- Keep portfolio calculations deterministic. Do not use an AI model as the source of balances, prices, or transactions.
- Preserve provenance: attach source, retrieval time, provider time when available, and quality status to imported or fetched data.
- Label incomplete, stale, estimated, unmatched, and user-provided data. Do not present an incomplete subtotal as a complete portfolio value.
- Keep provider secrets on the API side. Never put them in `NEXT_PUBLIC_*` variables or log them.
- Scope portfolio operations to the authenticated owner. Keep admin data behind the API's admin allowlist.
- Keep the web app responsive, keyboard accessible, and respectful of reduced-motion preferences.
- Add an Alembic migration for schema changes. Keep migrations reversible when practical and avoid destructive data changes without a clear migration plan.

## Checks before opening a pull request

Run the checks relevant to your change. The CI workflow runs these checks:

```powershell
pnpm typecheck
pnpm lint
$env:API_INTERNAL_URL = "https://api.example.invalid/api/v1"
pnpm build
uv run --directory apps/api ruff check app tests
uv run --directory apps/api python -m unittest discover -s tests -v
```

The API CI job also applies migrations to PostgreSQL. The optional shared-rate-limit integration check uses `POCKETORBIT_POSTGRES_TEST_URL`.

## Pull request notes

Include:

- the user problem and the behavior changed;
- screenshots for visible interface changes, including mobile when relevant;
- migration, environment-variable, or provider changes;
- checks run and any known limitations.

Keep pull requests focused. Do not commit build output, installed dependencies, generated secrets, or private portfolio data.
