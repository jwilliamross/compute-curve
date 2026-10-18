# CLAUDE.md

Research and paper-trading codebase for a relative-value strategy on CME
compute futures: GPU1 (Silicon Data H100 Rental Index) and GPU2 (B200).

## Scope (hard limits)

- Research and simulation only. No brokerage connectivity, no order routing,
  no real money, no account sign-ups, no purchases.
- The paper trading engine is a local simulation. It must never contain code
  that talks to an exchange, broker or payment system.
- Single exception (owner request, 2026-10-05; docs/decisions.md D30): the
  claim-4 adapter in `compute_curve.claim4` may call Alpaca's **paper**
  trading API (`https://paper-api.alpaca.markets`) and its market data API.
  Every Alpaca client must hard-fail unless `APCA_API_BASE_URL` is exactly
  the paper endpoint. Paper orders only when the claim-4 validation gate
  passes; otherwise shadow mode. Never a live endpoint or real money.
- Second paper exception (owner request, 2026-10-16; D63): SA2-M stock
  stat-arb may trade the same Alpaca **paper** account (`statarb/paper.py`)
  with the readiness doc's sizing and kill criteria. Claim 4 stays in shadow
  mode while it runs. Fake money only.
- Alpaca market data is never committed (D29); it is cached under `var/`.
- GetDeploying API raw data is never committed in plain form (D60); only the
  encrypted archive under `data/private/`, and aggregates in reports.
- Kalshi market data is public and read-only: no account, no orders; raw data
  stays in `var/kalshi/` (D62).

## Commands

```bash
uv sync                                   # install
uv run pytest                             # offline suite (network/slow excluded); run before every commit
uv run pytest -m slow                     # estimator recovery checks (minutes)
uv run ruff check . && uv run ruff format --check .
uv run compute-curve snapshot             # collect today's raw prices (idempotent)
uv run compute-curve backfill gpurentalprices --start YYYY-MM-DD --end YYYY-MM-DD
uv run compute-curve index                # rebuild our H100/B200 index from raw data
uv run compute-curve status               # paper account status
uv run compute-curve daily                # daily cycle: ingest, signal, fill, report
uv run compute-curve evaluate             # claim tests on real data + validation gate
uv run compute-curve backtest --synthetic-engine-check
uv run compute-curve claim4 check         # Alpaca paper endpoint + data check (names only)
uv run compute-curve claim4 evaluate      # claim-4 tests + gate (docs/claim4_plan.md)
uv run compute-curve claim4 daily         # shadow log, or gated PAPER orders
uv run compute-curve statarb paper        # SA2-M Alpaca PAPER orders for the next open (D63; kill switches)
uv run compute-curve statarb signals      # SA2-M practice sheet for the next session (reports/statarb/practice/; no orders)
uv run compute-curve statarb lab          # claim 10: MX1-MX4 forward shadow next to SA2-M (docs/modern_plan.md; no orders)
uv run compute-curve claim5 fetch         # AWS spot archive (Zenodo, CC BY 4.0) -> daily GPU series
uv run compute-curve claim5 evaluate      # claim 4's battery on the AWS spot signals
uv run compute-curve index-gap            # claim 1b: our index vs Silicon Data's (licensed SD CSVs; B7)
uv run compute-curve futures-premium      # claim 7: GPU1/GPU2 premium shadow log (manual CME CSVs; no orders)
uv run compute-curve spread               # claim 8: GPU2/GPU1 spread shadow + own-index forward check (docs/spread_plan.md)
uv run compute-curve fair-value           # GPU1/GPU2 balance-of-month fair value sheet + FP-C (docs/bom_plan.md)
uv run compute-curve carry                # FP-D: long the backwardation on GPU1/GPU2 (docs/carry_plan.md)
uv run compute-curve macro                # claim 11: AI-economy signals vs GPU rents, one shot (docs/macro_drivers_plan.md)
uv run compute-curve replicate            # claim 12: SA2-M 2019-24 + rates on AWS spot, one shot (docs/replication_plan.md)
uv run compute-curve regime               # claim 13: volatility-regime test on universe B, one shot (docs/regime_plan.md)
uv run compute-curve crossvenue           # FP-K: GPU1 vs Kalshi H100 monthly-average implied curve (docs/crossvenue_plan.md)
uv run compute-curve kalshi               # claim 9: Kalshi GPU binaries, public data (docs/kalshi_plan.md; D62)
uv run compute-curve getdeploying-api check     # GetDeploying API key check (D60; needs GETDEPLOYING_API_KEY)
uv run compute-curve getdeploying-api download  # full per-provider history -> var/ (encrypted copy via workflow)
uv run compute-curve explore round7 api         # one-shot round 7 on the API history (docs/exploration_round7_plan.md)
uv run compute-curve wayback --dry-run    # archived pricing pages: count captures (D58; real runs via the manual workflow)
uv run compute-curve explore round1 exploration   # exploration sets only (docs/exploration_plan.md)
uv run compute-curve explore round1 shadow        # daily: candidates' shadow forecasts, no orders
```

## Standards (non-negotiable)

- Python 3.11+, uv, full type hints on every function, pytest, ruff.
  Small pure functions. Config-driven (`config/*.toml`). Fixed random seeds.
  Reproducible runs.
- **No look-ahead.** Every record carries `ts_observed`, the UTC time it was
  observed. Models see only data with `ts_observed <= decision time`.
  Evaluation is walk-forward only. Tests enforce this.
- **Raw data is immutable and append-only.** Raw snapshots are Parquet files
  under `data/raw/listings/<source>/` and `data/raw/indices/<source>/`. A file
  is never rewritten or deleted. DuckDB (git-ignored, under `var/`) is a
  derived view, rebuildable from raw Parquet.
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
  Vast.ai and RunPod terms prohibit automated collection and index use: their
  rows are dropped everywhere, and the Vast collector needs a licence flag.
  Silicon Data content may not be stored. Do not store host-identifying
  fields (IP addresses, hostnames).
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
data/raw/listings/      immutable listing snapshots (Parquet, committed)
data/raw/indices/       immutable third-party index snapshots (Parquet, committed)
data/raw/archive/       research-only rows from archived pricing pages (D58; not in the index)
data/private/           encrypted archives of licensed data (D60; GetDeploying API)
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
  collectors/           one collector per approved source (docs/data_sources.md)
  snapshot.py           idempotent daily snapshot + archive backfills
  pipeline.py           daily cycle orchestration
  evaluation.py         claim tests, validation gate, backtest reports
  storage/              raw Parquet store + DuckDB warehouse
  index/                our own robust H100/B200 index + tracking error
  contracts.py          contract months, settlement averaging
  paper/                simulated account, fills, risk limits, ledger
  models/               nowcast (+ baselines), Schwartz-Smith Kalman, term-structure
                        walk-forward, relative value
  backtest/             walk-forward runner, bootstrap, tearsheet
  claim4/               claim 4: Alpaca paper/data clients (paper-only guard),
                        index signals, tests, gate, paper strategy, risk, daily cycle
  claim5/               claim 5: AWS spot archive download/filter, spot signals,
                        evaluation with claim 4's battery
  explore/              exploration rounds: split-truncated data, hypothesis builders,
                        BH screen, one-shot confirmation, shadow forward tests
  futures_premium.py    claim 7: GPU1/GPU2 futures risk premium (outright vs index, calendar
                        spread), shadow log and one-shot evaluation (docs/futures_premium_plan.md)
  spread.py             claim 8: GPU2/GPU1 relative value (B200/H100 ratio), shadow + SP-0
  bom.py                balance-of-month fair value for monthly-average contracts; FP-C
  carry.py              FP-D: long the backwardation (hedging-pressure carry), shadow
  crossvenue.py         FP-K: GPU1 vs Kalshi's H100 monthly-average market, shadow
  kalshi.py             claim 9: Kalshi GPU price binaries (public API, var/kalshi only)
  macro.py              claim 11: AI-economy and rates signals vs GPU rents (FRED cache in var/fred)
  replication.py        claims 12-13: out-of-time SA2-M, rates on AWS spot, volatility regime
  synthetic.py          TEST-ONLY synthetic generators (labelled)
  cli.py                command-line entry point
tests/
.claude/skills/          agent skills: compute-curve-research (start here), nonstorable-futures
                        (power-market methods for GPU1/GPU2), plus reviewed, pinned copies of
                        third-party skills (D43, D61)
.github/workflows/daily.yml   daily cycle after the US close (default branch only)
```
