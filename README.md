# compute-curve

Research and paper-trading code for a relative-value strategy on CME compute
futures: GPU1 (Silicon Data H100 Rental Index) and GPU2 (B200).

**Simulation only.** There is no broker connection, no order routing and no
real money. The paper account is a local DuckDB ledger.

**Status on 2026-10-05:** GPU1/GPU2 are **not trading**. The CFTC extended its
review to 2026-11-09 (docs/contract_specs.md). None of the three research
claims can be tested yet; see `docs/status.md` for what was built and what is
needed next.

## Setup

```bash
uv sync
uv run pytest                 # offline suite (network and slow tests excluded)
uv run pytest -m slow         # estimator recovery checks, a few minutes
uv run ruff check . && uv run ruff format --check .
```

Python 3.11+, uv. No secrets are needed: every approved source is keyless.

## Commands

| Command | What it does |
|---|---|
| `uv run compute-curve snapshot` | Collect today's prices from approved sources. Idempotent per UTC day; `--force` appends another snapshot |
| `uv run compute-curve backfill gpurentalprices --start 2026-07-19 --end 2026-10-04` | One-off import of a source's archived daily files (idempotent) |
| `uv run compute-curve backfill cgi --start 2026-08-30 --end 2026-10-05` | One-off import of Computable GPU Index history (last 90 days only) |
| `uv run compute-curve index` | Rebuild our H100/B200 index; writes `reports/own_index.md` and `.csv` |
| `uv run compute-curve status` | Show the forward paper account |
| `uv run compute-curve daily` | Daily cycle: snapshot, index, signals, simulated fills, report in `reports/daily/` |
| `uv run compute-curve evaluate` | Test the claims on real data; writes `reports/evaluation.md` and the validation file that gates trading |
| `uv run compute-curve backtest --synthetic-engine-check` | Engine validation on labelled synthetic data, plus the real-data backtest when settlements exist |

## Scheduling the daily cycle

This session cannot schedule anything. Run `scripts/daily.sh` once a day on a
machine with this repository checked out. It pulls, runs the daily cycle and
the evaluation, then commits the new raw data and reports and pushes them.

**cron (Linux or macOS).** 23:30 UTC is after gpurentalprices.com's daily
refresh (around 22:00 to 23:00 UTC) and before the UTC date changes:

```cron
CRON_TZ=UTC
30 23 * * * /path/to/compute-curve/scripts/daily.sh >> $HOME/compute-curve-daily.log 2>&1
```

If your cron does not support `CRON_TZ`, convert 23:30 UTC to local time.

**systemd timer (alternative):**

```ini
# ~/.config/systemd/user/compute-curve.service
[Service]
Type=oneshot
ExecStart=/path/to/compute-curve/scripts/daily.sh

# ~/.config/systemd/user/compute-curve.timer
[Timer]
OnCalendar=*-*-* 23:30:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
```

Then run `systemctl --user enable --now compute-curve.timer`.

The machine needs `uv` on its `PATH`, push access to this repository, and
outbound HTTPS to the hosts in docs/data_sources.md. Set
`COMPUTE_CURVE_PUSH=0` to commit without pushing. Missing a day loses that
day's live listings for good, because most sources publish no history.

## Files you add by hand

The pipeline reads these folders. Files are never modified by the code.

**CME settlements:** `data/manual/cme_settlements/*.csv`. Download them from
CME under your own account once GPU1/GPU2 list. Do not script cmegroup.com;
its terms prohibit it. Format (the values below are illustrative, not data):

```csv
product,contract_month,trade_date,settle_price,volume,open_interest
GPU1,2026-12,2026-11-16,2.745,12,140
```

`volume` and `open_interest` are optional. A settlement is treated as
available at 23:59:59 UTC on its trade date.

**Settlement index history:** `data/manual/published_index/*.csv`. Only with
a licence that permits storing it (docs/blockers.md B7). Use the
US-geography, business-day series that settles the contracts if you can get
it. Format (illustrative values, not data):

```csv
index_name,as_of_date,value
Silicon Data H100 Rental Index,2026-09-01,2.71
Silicon Data B200 Rental Index,2026-09-01,5.62
```

`index_name` must match `underlying_index` in `config/default.toml`. A value
for date `d` is treated as usable from 00:00 UTC on `d + 1` (an assumption,
`nowcast.publication_lag_days`).

## Layout

```
config/default.toml     every tunable number; verified terms are marked per field
data/raw/listings/      immutable listing snapshots (Parquet, committed)
data/raw/indices/       immutable third-party index snapshots (Parquet, committed)
data/manual/            files you add by hand (see above)
data/collection_log.jsonl  one line per collection attempt
var/                    git-ignored DuckDB warehouse, paper ledger, validation file
reports/                index, daily reports, evaluation, engine validation
docs/                   research plan, derivations, data sources, decisions, blockers, status
src/compute_curve/      the package (see CLAUDE.md)
tests/                  pytest suite; synthetic data lives only here and in synthetic.py
```

## Data licences

Stored third-party data keeps its licence: Computable GPU Index (CC BY-NC
4.0, non-commercial only), GetDeploying (CC BY 4.0), gpurentalprices.com
(CC BY 4.0). Attribution strings are in docs/data_sources.md. Re-check them
before making this repository public or using it commercially.

## Standards

See `CLAUDE.md`: no look-ahead, immutable raw data, baselines first,
uncertainty on every result, no fabricated data, secrets only from the
environment.
