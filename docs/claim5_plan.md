# Claim 5 pre-registration: do AWS GPU spot prices lead compute-linked equities?

> **DRAFT.** The signal-side numbers marked `{{...}}` are filled in once the
> spot download finishes. The plan is final only in the commit that removes
> this note, and that commit precedes any stock-return fetch for claim 5.

**Pre-registered on 2026-10-06, before any stock return for the claim-5
window was fetched.** The commit that adds this file timestamps the plan.
Only signal-side data had been examined: the AWS spot series, its timing
and coverage, and the trading calendar.

**One overlap to disclose.** Claim 4 already computed aggregate statistics
of the same basket for 2026-08-20 to 2026-10-05: its daily excess-return
volatility, its mean, and its correlation with claim 4's own index signals.
Those sessions are the last part of this window. No relation between AWS
spot prices and returns has been looked at.

After results exist, changing any choice below is a new variant
(`docs/variants_log.md`). The settings live in `config/default.toml` under
`[claim5]`. Everything not named there is claim 4's, unchanged: universe,
benchmark, horizons, tests, costs, risk limits and the gate.

## 0. What is known before any return is seen

{{BOTTOM_LINE}}

## 1. Signal data

| Item | Choice |
|---|---|
| Dataset | "AWS Spot Price History", Eric Pauley (University of Wisconsin-Madison), Zenodo version 2026-09, DOI 10.5281/zenodo.23082767, licence CC BY 4.0 (audit: `docs/data_sources.md`) |
| Months | 2024-10 to 2026-02 and 2026-07 to 2026-09. 2026-03 to 2026-06 are absent from the dataset; the sessions they cover get no signal |
| Rows kept | Instance types with A100 or newer data-center GPUs; availability zones in `us-east-1`, `us-east-2`, `us-west-1` and `us-west-2` (zone IDs `use1`, `use2`, `usw1`, `usw2`); product `Linux/UNIX` |
| Pool | One availability zone × one instance type |
| Daily value | The price in effect at 23:30 UTC: the latest record at or before the cutoff in that month's file, divided by the instance's GPU count, in USD per GPU-hour |
| Timing | Day `d`'s value is usable from 00:30 UTC on `d + 1`, the claim-4 rule (D31), so it reaches the market at the next session's open |
| Assumption | AWS published each price in real time through its API and never revised it. The archive was collected monthly. This is plausible but unverified, and it is the condition for treating the backtest as tradable |

## 2. Universe, benchmark and missing history

The universe and benchmark are claim 4's, unchanged (`docs/claim4_plan.md`
section 2): 21 stocks in three buckets, the category-balanced basket,
against XLK.

Several members lack history for part of the window. The dates below come
from public listing information. The report verifies them against the first
bar actually used for each member.

| Member | History in the window | Handling |
|---|---|---|
| NBIS | Nasdaq trading resumed on 2024-10-21. Before that the ticker was Yandex N.V., a different business, suspended since February 2022 | Returns used only from 2024-10-21 (`[claim5.member_start]`, D38) |
| CRWV | IPO on 2025-03-28 | Absent before its first bar |
| WYFI | IPO in August 2025 | Absent before its first bar |
| CBRS | Listed in 2026 | Absent for most of the window |
| The other 17 | Expected to trade throughout | Used throughout |

The handling is claim 4's own rule, unchanged:

- within a bucket, members that have a return for the window are equally
  weighted;
- a bucket counts only if at least half its members have a return;
- the basket needs all three buckets.

The neocloud bucket has two of its four members (IREN and NBIS) from
2024-10-21. **So the sample starts on 2024-10-21.** Before then the basket
does not exist under claim 4's rule.

**Hindsight bias.** The universe was chosen in October 2026 from current
business descriptions. Applying it to 2024–2026 returns includes companies
partly because they later became AI plays. This mainly affects mean excess
returns, which the walk-forward's mean baseline absorbs, less so the
predictive slope. It is disclosed, not corrected.

## 3. Signals

There are two GPU classes. These two have US spot prices throughout the
window.

| Class | Instance types |
|---|---|
| A100 | `p4d.24xlarge` (8 × A100 40 GB), `p4de.24xlarge` (8 × A100 80 GB) |
| H100 | `p5.48xlarge` (8 × H100), `p5.4xlarge` (1 × H100) |

H200, B200 and B300 rows are kept for description but not tested.

For session `t`:

- `d*(t)` is the latest price day usable before the open. It must be the
  calendar day before the session (`max_age_days = 1`), because the data
  cover every calendar day. A missing day means a gap, and the session gets
  no signal.
- Matched pools are the pools priced on both `d*(t-1)` and `d*(t)`. At
  least 3 are required (`min_pools`).

| Signal | Definition |
|---|---|
| `level_a100`, `level_h100` | Median over matched pools of `ln p(d*(t)) - ln p(d*(t-1))`. A matched-pool change cannot jump when AWS adds or drops a zone |
| `disp_a100`, `disp_h100` | `IQR(ln p(d*(t))) - IQR(ln p(d*(t-1)))` over the matched pools |

There is **no availability signal**. Within a month a pool can only appear,
never disappear, so a pool count would mostly mark month starts (D37).
Claim 4 had 6 signals; claim 5 has 4.

### Signal-side facts at registration

{{SIGNAL_FACTS}}

## 4. Outcome

Claim 4's outcome, unchanged. `R(t,h)` is the category-balanced basket's
simple return minus XLK's, from the open of `t` to the close of `t+h-1`,
for `h` in {1, 5, 20}. Bars are Alpaca SIP daily bars, adjusted for splits
and dividends, usable from the close plus 20 minutes. They are fetched at
run time and never committed (D29).

## 5. Tests

Claim 4's battery runs unchanged, through the same code
(`compute_curve.claim4.analysis`):

- **Family P, primary: 12 tests.** Lead-lag for 4 signals × 3 horizons.
  Newey-West t-test at lag `h`, Holm across the 12 tests, circular-shift
  permutation p-value, and at least 10 non-zero signal values.
- **Family E: 6 tests.** Event study on spot level moves of 2% or more, for
  A100 and H100 × 3 horizons. Sign-flip test, Holm, at least 10 events.
- **Family W: 12 tests.** Walk-forward OLS against zero and mean baselines.
  `R2_OS > 0` against both, Clark-West with Holm, at least 120
  out-of-sample forecasts.
- **Family S, secondary: 36 tests.** Bucket baskets, Benjamini-Hochberg at
  10%. These cannot open the gate.
- **Gate G3: 12 strategy evaluations**, net of claim 4's costs.
- **A descriptive cross-correlogram** for the two level signals.

The bootstrap is the circular block bootstrap with 2,000 resamples and seed
20261005, with claim 4's small-sample guards (D34). In total 78 tests and
evaluations are declared (`docs/variants_log.md`).

## 6. Costs

Claim 4's assumptions, unchanged: 15 bps per side on stocks, 3 bps on XLK,
1 bp of fees on sells, borrow at 5% a year on short stocks and 0.5% on
short XLK. A round trip of the pair costs about 0.38%. Results are shown at
0×, 0.5×, 1×, 2× and 4× costs.

## 7. Validation gate

Claim 4's gate, **unchanged and not loosened**:

- **G1:** family P passes.
- **G2:** family W passes.
- **G3:** the net Sharpe's 95% lower bound is above 0 at 1× costs, and the
  mean is positive at 2× costs.
- **G4:** at least 120 out-of-sample forecasts and at least 30 non-zero
  signal values out of sample.
- **G5:** checked at trading time.

If several pairs pass, the one with the smallest Holm-adjusted G1 p-value
is selected.

## 8. If the gate passes

**Shadow mode only.** The signal is added to the daily workflow to log
predictions, never orders. Two limits apply even then:

- **The data is monthly.** The archive arrives monthly, so a daily signal
  would lag by up to a month unless same-day AWS spot prices are read from
  AWS's API, which needs the owner's AWS account and decision. A lagged
  signal is a different strategy from the one tested, so the backtest's
  economics would not carry over.
- **The shadow log must confirm the result.** If, over its first 120
  realized sessions, the logged forecasts do not beat both naive baselines
  out of sample, claim 5 reverts to "not supported".

## 9. Kill criteria

| Code | Criterion | Consequence |
|---|---|---|
| K1 | No family P test passes on this window | Claim 5 is "not supported" on 2024-10 to 2026-09 data |
| K2 | After at least 250 new sessions (about the 2027-09 Zenodo version), a re-run under this plan still has no family P pass | Claim 5 is rejected |
| K3 | The gate passed but the shadow log fails (section 8) | Back to "not supported" |

## 10. Statistical power for the actual sample

{{POWER}}

## 11. Changes after registration

Any change to a definition, threshold, member, weighting, cost or test is a
new variant with a dated entry. A bug fix that changes no definition goes in
`docs/decisions.md`.
