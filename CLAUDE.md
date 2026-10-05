# CLAUDE.md

Research and paper-trading codebase for a relative-value strategy on CME
compute futures: GPU1 (Silicon Data H100 Rental Index) and GPU2 (B200).

## Scope (hard limits)

- Research and simulation only. No brokerage connectivity, no order routing,
  no real money, no account sign-ups, no purchases.
- The paper trading engine is a local simulation. It must never contain code
  that talks to an exchange, broker or payment system.

## Commands

```bash
uv sync                                   # install
uv run pytest -m "not network"            # offline test suite (run before every commit)
uv run ruff check . && uv run ruff format --check .
uv run compute-curve snapshot             # collect today's raw prices (idempotent)
uv run compute-curve index                # rebuild our H100/B200 index from raw data
uv run compute-curve status               # paper account status
uv run compute-curve daily                # daily cycle: ingest, signal, fill, report
uv run compute-curve backtest --config config/default.toml
```

## Standards (non-negotiable)

- Python 3.11+, uv, full type hints on every function, pytest, ruff.
  Small pure functions. Config-driven (`config/*.toml`). Fixed random seeds.
  Reproducible runs.
- **No look-ahead.** Every record carries `ts_observed`, the UTC time it was
  observed. Models see only data with `ts_observed <= decision time`.
  Evaluation is walk-forward only. Tests enforce this.
- **Raw data is immutable and append-only.** Raw snapshots are Parquet files
  under `data/raw/<source>/`. A file is never rewritten or deleted. DuckDB
  (`var/warehouse.duckdb`, git-ignored) is a derived view, rebuildable from
  raw Parquet.
- **Baselines first.** Every model must beat a naive baseline out of sample
  before it is used in a signal. If it does not, it is not used.
- **Uncertainty always.** Every reported result includes bootstrap confidence
  intervals, the cost assumptions used, and the number of variants tried
  (logged in `docs/variants_log.md`).
- **Math in docs.** Derivations live in `docs/` with citations. Never present
  an assumption as a finding. Label every unverified number as such.
- **Secrets** come from environment variables only. There is no `.env` file.
  Never print, log or commit a secret.
- **Sources:** respect robots.txt and each source's terms. Rate limit every
  request. If a source prohibits collection, skip it and record that in
  `docs/blockers.md`. Do not scrape cmegroup.com (its terms prohibit it).
  Do not store host-identifying fields (IP addresses, hostnames).
- **Never fabricate data.** Synthetic data lives only in tests and in
  clearly labelled engine-validation output, built by
  `compute_curve.synthetic`, and every synthetic frame carries
  `is_synthetic=True`. Synthetic data never appears in results.
- When there is too little history to conclude anything, say so instead of
  fitting.

## Working rules

- Conservative choice when a decision is needed; record it in
  `docs/decisions.md` with reasoning.
- Blocked items go in `docs/blockers.md`. Keep `docs/status.md` current.
- Small commits with clear messages. Tests and ruff pass before every commit.
- Core stack: numpy, pandas, scipy, statsmodels, duckdb, httpx, pydantic,
  pytest, matplotlib. Any other dependency needs a recorded reason in
  `docs/decisions.md`.
- Do not call MCP connector tools from autonomous runs; a pending approval
  stalls the run.

## Layout

```
config/                 TOML configs (contract specs, costs, limits, models)
data/raw/<source>/      immutable raw snapshots (Parquet, committed)
data/manual/            files the user downloads by hand (CME settlements,
                        published index values); read-only inputs
var/                    git-ignored local state (DuckDB warehouse, paper ledger)
reports/                generated reports (daily, tearsheets)
docs/                   research plan, derivations, decisions, blockers, status
src/compute_curve/
  schema.py             normalized observation schema (pydantic)
  config.py             typed config loading
  timeutil.py           UTC helpers, month calendars
  http.py               rate-limited, robots-aware HTTP client
  collectors/           one module per approved source
  storage/              raw Parquet store + DuckDB warehouse
  index/                our own robust H100/B200 index + tracking error
  contracts.py          contract months, settlement averaging
  paper/                simulated account, fills, risk limits, ledger
  models/               baselines, nowcast, Schwartz-Smith Kalman, relative value
  backtest/             walk-forward runner, bootstrap, tearsheet
  synthetic.py          TEST-ONLY synthetic generators (labelled)
  cli.py                command-line entry point
tests/
```
