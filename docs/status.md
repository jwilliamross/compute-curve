# Status

_Last updated: 2026-10-05, end of the autonomous run._

## Final summary

**Bottom line.** The evidence neither supports nor rejects any of the three
claims. None of them can be tested yet. GPU1/GPU2 did not list on 2026-10-05:
the CFTC extended its review to 2026-11-09, so there are no futures prices.
History of the settlement index is paid, and its terms forbid storing it
without a licence. The research infrastructure is built, tested and
collecting real data. The tests can run as soon as those two inputs exist.

### What was built

- **Environment check** (docs/env_check.md). Tools, PyPI and git work. No
  allowlist is active (example.com is reachable). cmegroup.com and SSRN block
  automation.
- **Data layer.** Nine collectors for sources whose terms permit automated
  reading: Computable GPU Index, GetDeploying, gpurentalprices.com, Lium,
  Nebius, Lambda, CoreWeave, Hyperstack and Verda. Raw data is immutable
  Parquet with a collection log, and the daily snapshot is idempotent. The
  first live snapshot is stored. Backfills from licensed archives:
  - gpurentalprices.com daily offers, 2026-07-19 to 2026-10-04 (78 days);
  - Computable GPU Index, 15-minute values from 2026-08-30;
  - GetDeploying weekly medians, 53 weeks.
- **Excluded on terms.** Vast.ai and RunPod prohibit automated collection
  and index use; their rows are dropped everywhere. Silicon Data content is
  not stored. Together AI and FLOPS are not collected directly.
- **Our H100/B200 index** (docs/index_methodology.md). Provider-weighted
  median, neocloud-only, US or unknown region. Two series: a multi-source
  headline index, and a fixed-panel history series (from 2026-08-18) that
  the models use.
- **Paper trading engine.** Local DuckDB ledger. Fills at the next daily
  settlement plus half-spread, slippage and fees. Per-month and gross
  position limits, a daily loss halt and a drawdown kill switch. Backtest and
  forward modes share one daily function; forward mode is idempotent. A
  point-in-time view is the only way strategies see data.
- **Verified contract terms** from the NYMEX filing with the CFTC: 730
  GPU-hours, USD 0.01 tick, business-day averaging, 36 months, fees. Margins
  are not published.
- **Models.**
  - Nowcast with two naive baselines.
  - Schwartz-Smith two-factor model with depreciation drift and scheduled
    launch jumps: Kalman filter, panel maximum likelihood, and a walk-forward
    test against the futures price and a random walk.
  - Performance-normalized H100/B200 relative value.
  - Every signal stays in shadow mode until validated out of sample.
- **Reporting.** Tearsheets with block-bootstrap Sharpe intervals, cost
  sensitivity, capacity and the count of declared variants (9). Engine
  validation on labelled synthetic data passes all checks.
- **Docs.** Research plan with kill criteria, derivations, data-source audit,
  contract specs, launch calendar, 28 recorded decisions and 11 blockers.
- **Tests.** 92 fast tests and 2 slow estimator checks pass. Ruff is clean.

### What the evidence says so far

| Claim | Verdict | Why |
|---|---|---|
| 1. Nowcast edge | **Not testable** | Needs licensed settlement-index history; the pre-registered minimum is 6 complete months |
| 2. Model edge | **Not testable** | Needs futures settlements with realized finals, about 12 months after listing |
| 3. Survivability | **Not testable** | Needs futures prices |

Descriptive observations follow. None of them is a test result.

- **Listing-based indices disagree.** On 2026-10-05 the verified H100
  readings ranged from 2.81 to 3.62 USD per GPU-hour across four publishers.
  A fifth, Ornn, showed 2.59, but only in a search snippet. Our headline index
  read 3.20 against Silicon Data's public 2.81.
- **Our index barely tracks another index built from similar listings.** Over
  37 days our fixed-panel index sat 12% (H100) and 8% (B200) below the
  Computable GPU Index. The correlation of daily changes was −0.17 and 0.15.
  Listing-based indices therefore do not agree day to day, which is a warning
  sign for claim 1.
- **List prices are sticky.** Our H100 panel index was unchanged on 88% of
  days.
- **Costs are large relative to price.** At the default cost assumptions, a
  round trip costs about USD 0.16 per GPU-hour: 5.8% of the H100 index level
  and 2.8% of B200. Any edge must clear that.
- **Relative value is not robust.** The B200/H100 break-even throughput
  ratio was 1.92 to 2.19 across four sources, inside the assumed 1.8 to 3.0
  range. Whether B200 is the cheaper way to buy compute depends on the
  workload.

### Actions you need to take, in priority order

1. **Switch on the daily cycle.** Merge this branch into the default branch;
   the GitHub Actions workflow then runs at 23:30 UTC (README, option A). If
   you prefer cron on your own machine, use option B instead, not both. Live
   listings that are not collected on the day are lost for good.
2. **Get licensed settlement-index history** (docs/blockers.md B7). Ask
   Silicon Data for research access to the US-geography, business-day
   SD-H100/SD-B200 series, or export `SDH100RT Index` / `SDB200RT Index` from
   Bloomberg. Save it as CSV in `data/manual/published_index/`, then run
   `uv run compute-curve evaluate`. This unblocks claim 1.
3. **When GPU1/GPU2 list** (CFTC decision due by 2026-11-09), download daily
   settlements under your own CME account into `data/manual/cme_settlements/`.
   This unblocks claims 2 and 3 and the paper account.
4. **Decide the network policy.** No allowlist is active; the domain list is
   in docs/env_check.md.
5. **Review two conservative choices** you may want to relax. Vast.ai and
   RunPod rows are dropped even from aggregators (D13), and Together AI is not
   collected directly (D16). Both are config changes.
6. **Optional:**
   - ask data@vast.ai for a research licence and team@flopsindex.com about
     their terms;
   - put the two SSRN PDFs in `references/`;
   - backfill 2026-07-05 to 07-18 from Zenodo record 21435394;
   - remove `VAST_API_KEY` from the environment if nothing else uses it.
7. **Review and merge** branch `claude/quirky-allen-b87nkb`. No pull request
   was opened.

## Done

- Step 0 environment check; Phase 0 foundations (CLAUDE.md, data-source
  audit, research plan, contract specs); Phase 1 data layer and paper
  engine; Phase 2 models; Phase 3 tearsheet, engine validation and the
  real-data evaluation and backtest reports.

## In progress

- Daily data collection, once scheduled by you.

## Blocked

- B7 settlement-index history (licence); B8 contracts not listed; B2 CME
  website; B3 SSRN full texts; B5 and B6 Vast.ai and RunPod terms; B9 FLOPS
  terms; B10 Ornn unreachable. Details in docs/blockers.md.

## Needs you

- Items 1 to 7 above.
