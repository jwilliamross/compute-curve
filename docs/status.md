# Status

_Last updated: 2026-10-05, Phase 0 in progress._

## Done

- Step 0 environment check (`docs/env_check.md`), committed and pushed.
- uv project, dependencies, ruff and pytest configuration.
- CLAUDE.md with project standards.
- Core modules: normalized schema, typed config, rate-limited robots-aware
  HTTP client, append-only Parquet store, DuckDB warehouse views, own-index
  aggregation, tracking-error statistics, block bootstrap.
- Vast.ai collector (offline tests only so far).

## In progress

- Phase 0 data source audit (`docs/data_sources.md`).
- Contract facts and literature review.

## Blocked

See `docs/blockers.md`: CME website (terms prohibit automation), SSRN
(Cloudflare + TDM reservation), FLOPS Index (login), no allowlist active.

## Needs you

- Decide on the network allowlist (see `docs/env_check.md`).
- Provide CME settlements and published index values by hand when available.
