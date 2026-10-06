# Claim 5 results: do AWS GPU spot prices lead compute-linked equities?

First evaluation, run 2026-10-06 with spot data through 2026-09-30 and stock
data through the 2026-10-05 close. The plan (`docs/claim5_plan.md`) was
committed before any stock return for this window was fetched. Full tables
are in `reports/claim5/evaluation.md`.

## Bottom line

**The gate does not pass. The evidence does not support claim 5.** The gate
was not loosened.

- **Nothing passed.** None of the 12 primary tests, 6 event tests or 12
  walk-forward forecasts passes, and none of the 36 secondary tests.
- **Correlations are near zero.** Every correlation between a spot signal
  and the basket's later excess return is between −0.16 and 0.11, and every
  95% interval includes zero.
- **Forecasts lose to naive guesses.** Every walk-forward forecast does
  worse out of sample than both naive baselines, "no difference" and "the
  average difference so far".
- **This sample has real power, unlike claim 4's.** 402 sessions with
  dense signals: correlations of about 0.18 or more (after the correction
  for 12 tests) would most likely have been found. None was.
- **What it does not show.** Small effects (correlations below about 0.14)
  are not ruled out.
- **Status.** Claim 5 is **"not supported"** on 2024-10 to 2026-09 data
  (kill criterion K1). A re-test under the same plan is due once about 250
  new sessions exist (about the 2027-09 Zenodo version). If that also fails,
  claim 5 is rejected (K2).
- **No workflow change.** Because the gate failed, nothing was added to the
  daily workflow.

## Data used

| Item | Detail |
|---|---|
| Signal data | "AWS Spot Price History" by Eric Pauley (University of Wisconsin-Madison), Zenodo version 2026-09, DOI 10.5281/zenodo.23082767, CC BY 4.0. 20 monthly files, 2024-10 to 2026-09 (2026-03 to 06 are absent from the dataset), 3.5 GB, MD5-verified, kept in git-ignored `var/aws_spot/raw/` |
| Rows kept | 90,915 spot price records: A100, H100, H200, B200 and B300 instance types in US availability zones on Linux/UNIX. US spot pools grew from 12 to 65 over the window |
| Signals | A100 and H100 level (median matched-pool log change) and dispersion (change in cross-pool IQR), per GPU-hour. Day `d`'s price at 23:30 UTC is used at the next session's open |
| Sample | 402 sessions with a signal, 2024-10-21 to 2026-10-01. Level moved on 99% (A100) and 81% (H100) of sessions. There were 58 and 64 moves of 2% or more |
| Stocks | Claim 4's 21-stock basket against XLK: Alpaca SIP daily bars, adjusted, not stored (D29), manifest hash `bd80ca5cf6d23869…` |
| Missing history | First bar used: NBIS 2024-10-21 (pre-registered start), CRWV 2025-03-28, WYFI 2025-08-07, CBRS 2026-05-14; the other 17 throughout. These match the plan. Claim 4's coverage rule kept the basket defined on every session from 2024-10-21 |
| Outcome scale (descriptive) | Basket excess return over XLK, open to close: daily standard deviation 2.49%, mean 0.01% |

## Results by family

### Family P, primary lead-lag: 0 of 12 pass

| Signal | 1 session: correlation (95% CI) | 5 sessions | 20 sessions | Smallest Holm p |
|---|---|---|---|---|
| level_a100 | 0.07 (−0.04 to 0.17) | 0.06 (−0.05 to 0.17) | 0.02 (−0.18 to 0.20) | 1.00 |
| level_h100 | −0.08 (−0.19 to 0.03) | −0.05 (−0.19 to 0.11) | −0.11 (−0.30 to 0.12) | 1.00 |
| disp_a100 | −0.01 (−0.10 to 0.08) | −0.11 (−0.21 to 0.00) | −0.16 (−0.33 to 0.02) | 0.75 |
| disp_h100 | −0.01 (−0.07 to 0.10) | 0.05 (−0.02 to 0.18) | 0.11 (−0.02 to 0.27) | 1.00 |

The strongest raw result, `disp_a100` at 20 sessions (correlation −0.16,
permutation p 0.023, Newey-West p 0.084), is far from surviving the Holm
correction (0.92).

### Family E, event study: 0 of 6 pass

At the 1-session horizon, the mean signed excess return after a move of 2%
or more:

- **A100:** +0.04% (95% CI −0.65 to 0.73), 58 events.
- **H100:** −0.34% (−0.97 to 0.29), 64 events.

The 5- and 20-session means are larger but have 11 to 32 events and wide
intervals. No Holm-adjusted p-value is below 1.00.

### Family W, walk-forward: 0 of 12 pass

There were 346 to 382 out-of-sample forecasts per model, which meets G4's
120. Every model's out-of-sample R² is negative against both baselines:
from −0.003 to −0.034 against the running mean, and from −0.021 to −0.119
against zero. Adding a spot signal made forecasts worse.

### Gate condition G3, strategy: 0 of 12 pass

At the 1-session horizon the strategy rarely trades (16 to 81 trades),
because forecasts seldom exceed the 0.38% round-trip cost, and loses a
little after costs.

The 20-session strategies show large mean gains per window, about 3 to 4%,
but their Sharpe intervals include zero. **Post-hoc check** (descriptive,
logged): these forecasts were "long the basket" in 97–98% of windows, and a
forecast using only the running mean, with no spot data, earns the same:
3.6% per window. The gains are the basket's average multi-day outperformance
in this window, not a spot-price effect. Two things explain why they show up
only at long horizons:

- Multi-day windows include overnight moves; the 1-session outcome, open to
  close, excludes them by design.
- The universe was picked in hindsight (D38).

### Family S, secondary: 0 of 36 pass

The lowest Benjamini-Hochberg q-value is 0.43. A few nominal permutation
p-values fall below 0.05, for example power and capacity against
`disp_h100` at 5 sessions, but no more than chance alone produces across 36
tests.

### The `disp_h100` outlier

The plan flagged one extreme value, the session of 2026-07-06 (−1.04). This
was a logged post-hoc check. Without it, `disp_h100` correlations move
slightly away from zero: basket at 5 sessions 0.05 → 0.09, and power and
capacity at 5 sessions 0.14 → 0.20. So the outlier diluted rather than
drove the results. The check is post hoc and opens no gate.

### Reverse direction (diagnostic)

Correlations between today's spot change and the basket's excess returns on
sessions before and after it are all within ±0.09. There is no sign of the
spot price lagging equities either.

## What the evidence supports

1. **No moderate predictive link** from AWS A100 or H100 spot price changes
   to next-day, next-week or next-month excess returns of compute-linked
   stocks over XLK, in 2024-10 to 2026-09. Unlike claim 4, the sample was
   large enough to find correlations of about 0.18 or more after
   correction.
2. **The test battery transfers.** Claim 4's battery, gate and safeguards
   ran unchanged on a second, independent signal source. The gate behaves
   as intended: data sufficiency (G4) was met, the other conditions failed,
   and the 20-session P&L that came from the mean alone was not mistaken
   for a signal.
3. **Spot GPU prices are informative in their own right** (descriptive):
   - The A100 median roughly doubled, from about USD 1.2 to about 2.3 per
     GPU-hour, between early 2026 and July to September 2026.
   - H100 fell from 3.84 (October 2024) to about 2.1 (mid-2025), then rose
     to 2.63.
   - US spot pools grew five-fold.

## What it does not support

- **That AWS spot prices lead these equities** at the horizons tested. Nor
  the opposite.
- **Small effects.** The absence of correlations below about 0.14 is not
  shown. Detecting 0.10 after correction would need about 1,370 sessions.
- **Other designs.** Prices on other clouds, other GPU types (H200, B200
  and B300 were kept but not tested), other outcomes such as overnight or
  close-to-close returns, and other universes are untested. Each would be
  a new, declared variant.
- **Real-time use.** The backtest assumes AWS spot prices were observable
  in real time, which is true through the AWS API but not through this
  monthly archive.

## Paper trading and automation

- **No change.** The gate failed for all 12 pairs, so no claim-5 signal was
  added to the daily workflow, not even in shadow mode. Claim 4's daily
  cycle is unchanged.
- **Re-running.** `uv run compute-curve claim5 fetch` and
  `uv run compute-curve claim5 evaluate` re-run the test. Add new months to
  `[claim5].months` once Zenodo publishes them. That counts as extending
  the sample under this plan, not as a new variant.

## Corrections made after the first run

The report's "Sample and power" table first counted outcome windows (490),
including sessions in the data gap that have no signal. It now counts
sessions with a signal (402), which matches the per-test counts and the
plan. This changed only the displayed numbers, not any test or result.

## Uncertainty, costs and variants

- **Bootstrap.** Circular block bootstrap, 2,000 resamples, seed 20261005,
  with claim 4's small-sample guards (D34).
- **Costs.** Claim 4's assumptions: 15 bps per side on stocks, 3 bps on
  XLK, 1 bp of fees on sells, borrow at 5% and 0.5% a year. Results are
  shown at 0× to 4× in the report.
- **Variants.** 78 tests and evaluations declared for claim 5; all were
  run. There were also two post-hoc descriptive checks: the outlier, and
  the mean-only strategy. All are in `docs/variants_log.md`. Project-wide
  there are 201 declared tests and evaluations.
