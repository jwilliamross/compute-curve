# Exploration round 1: plan

_Written 2026-10-06, before any analysis in this round. Every hypothesis,
split date, test and decision rule below was fixed before any test was run.
Results will be labelled **exploratory**. The report will be
`docs/exploration_round1.md`._

## 1. Purpose and limits

The aim is to find candidate signals for GPU rental prices, honestly.

- **Priority target.** Our own GPU rental index and its components, because
  compute futures and prediction markets pay out on those prices.
- **Simulation only.** No orders of any kind.
- **Data.** Only data already in the repository, or already approved in
  `docs/data_sources.md`: our listings, CGI, GetDeploying, the AWS spot
  archive and the cached Alpaca bars. Nothing new is fetched.
- **Outcomes.** A result that survives exploration is a **survivor**. One
  that also passes confirmation is a **candidate**. Neither is a finding.
  Only the existing validation gate, run on future data, can turn a
  candidate into a tradable signal.

## 2. Datasets and split dates

Each dataset is split by time on its own observations. The earliest 70% is
the **exploration set**; the latest 30% is the **confirmation set**.

| Dataset | Observations | Exploration set | Confirmation set |
|---|---|---|---|
| L: our listings (`gpurentalprices_hist`, `gpurentalprices`), index days | 80 days | 2026-07-19 to 2026-09-12 (56 days) | 2026-09-13 to 2026-10-06 (24 days) |
| C: CGI 15-minute index history (H100, B200) | 37 days, about 3,530 values per GPU | 2026-08-30 00:00 to 2026-09-24 23:45 UTC (26 days) | 2026-09-25 00:00 to 2026-10-05 18:30 UTC (11 days) |
| G: GetDeploying weekly medians (Monday-dated weeks) | 53 weeks | weeks of 2025-10-06 to 2026-06-15 (37) | weeks of 2026-06-22 to 2026-10-05 (16) |
| A: AWS spot archive, daily pool prices (`var/aws_spot/pool_daily.parquet`) | 608 days | 2024-10-01 to 2025-11-30 (426 days) | 2025-12-01 to 2026-02-28 and 2026-07-01 to 2026-09-30 (182 days) |
| E: Alpaca daily bars (cached in `var/`, not committed) | 524 sessions | 2024-09-03 to 2026-02-19 (367 sessions) | 2026-02-20 to 2026-10-05 (157 sessions) |

The AWS archive has no data for 2026-03 to 2026-06. Its confirmation set
therefore comes in two blocks.

**Rules for using the splits**

- **Whole windows only.** An observation is in a set only if every input it
  uses lies in that set: its signal window and its outcome window.
- **The boundary gap.** Observations whose windows straddle a split date
  are in neither set.
- **Hypotheses that join two datasets.** An observation is in the
  exploration sample only if its inputs lie in the exploration sets of
  *both* datasets. The same applies to confirmation.
- **Truncation in code.** The exploration code truncates each dataset to
  its exploration set before computing anything. No confirmation-set
  outcome can then be computed by accident. Tests check this.

## 3. What was already seen before this plan (contamination)

The rules can stop new looks at the data, but not undo earlier ones. These
are disclosed so the reader can discount affected hypotheses.

1. **Our index (claim 4).**
   - Earlier runs showed our H100 and B200 history-panel index from
     2026-08-20 to 2026-10-05. That spans both this round's exploration and
     confirmation sets.
   - Facts already known:
     - the H100 index moved on 5 of 32 sessions;
     - the index is unchanged on 88% of days (`docs/data_sources.md`);
     - two B200 moves drove claim 4's only secondary pattern;
     - the 2026-10-05 levels.
2. **CGI and GetDeploying.** Only their 2026-10-05 levels, and
   GetDeploying's back-filled early weeks, were looked at. No dynamics.
3. **AWS spot (claim 5).** Already known:
   - the monthly A100 and H100 medians through 2026-09: A100 roughly
     doubled from early 2026 to July–September 2026, and H100 fell from
     3.84 to about 2.1 and then rose to 2.63;
   - the share of days with a move;
   - the 2026-07-06 dispersion outlier.

   No lead-lag or autocorrelation between AWS series was computed.
4. **Equities (claims 4 and 5).** Already known, over the full sample:
   - the basket's excess-return scale;
   - its multi-day outperformance of XLK from 2024-10 to 2026-10;
   - each bucket's lead-lag against AWS A100 and H100 one-day changes at 1,
     5 and 20 sessions (none passed);
   - claim 5's reverse-direction diagnostic: correlations between the
     basket's excess returns and AWS one-day level changes, at leads and
     lags up to 5 sessions, were all within ±0.09.

   The last two bear on H11 and H12 below.
5. **None of the 12 statistics below** (no correlation, regression or
   autocorrelation for any hypothesis) has been computed on any data before
   this plan.

## 4. Ideas considered but not testable this round

These are not among the 12 and are not tested.

| Idea | Why it cannot be tested now |
|---|---|
| AWS spot leads neocloud list prices (our index) | The AWS exploration set ends 2025-11-30 and our listings start 2026-07-19, so there is no joint exploration data. The archive is also published monthly, so the signal could not run live |
| Compute-stock returns lead our index | The equity exploration set ends 2026-02-19, before our listings begin. It is tested against AWS spot instead (H11) |
| CGI leads our index (an intraday index catching price changes first) | The joint exploration window is 2026-08-30 to 09-12: 14 days, too few for a multi-day horizon |
| Availability flags or stock-outs in our listings | 98% of rows have availability "unknown". The median provider has one H100 listing, and 90% of listings are present on at least 48 of the 56 exploration days, so listing counts barely vary. Availability is tested with GetDeploying offer counts instead (H07) |
| AWS pool counts as a supply measure | In the archive, pools appear only at month starts (D37), so the count is not a daily supply measure |
| GetDeploying with AWS, or GetDeploying with our index | The joint exploration windows are 8 weeks and none |

## 5. Definitions used by the hypotheses

### 5.1 Our listings (L)

- **Rows.** Only the history sources (`gpurentalprices_hist`,
  `gpurentalprices`) are used, filtered with the index's eligibility rules:
  - on-demand term (spot term for H03's signal);
  - US, North American or unknown region;
  - an allowed variant;
  - not a hyperscaler;
  - not flagged unavailable;
  - a positive price.

  The latest snapshot per source-day and the index's source preference
  apply. The direct provider collectors exist only from 2026-10-05, so they
  are left out to avoid a source switch inside the window.
- **Listing price** `p_i(d)`: the price in USD per GPU-hour of listing `i`
  (a stable `listing_id`) on index day `d`.
- **Matched provider change** `c_p(d1, d2)`: the median, over provider
  `p`'s listings priced on both days, of `ln p_i(d2) − ln p_i(d1)`. This
  removes composition effects when a listing appears or disappears.
- **Group change** `M_G(d1, d2)`: the equal-weighted mean of `c_p` over
  the providers in group `G` with at least one matched listing.
  - It is NaN if fewer than 3 providers match (2 for H03's spot group).
  - Weighting each provider equally mirrors the index's one-provider,
    one-vote rule.
  - A mean, unlike our median index, moves whenever any provider reprices.
    The settlement index's methodology also averages provider means
    (`docs/data_sources.md`).
- **Provider level** `P_p(d)`: the median of provider `p`'s eligible
  listing prices on day `d`.
- **Timing.** Day `d`'s snapshot is usable from the claim-4 time, the later
  of its observation time plus 60 minutes and 23:30 UTC on `d` (D31).
  Signals use days up to `d`; outcomes run from `d` to `d + h`.

### 5.2 Other datasets

| Dataset | Definition |
|---|---|
| C: CGI | `v(τ)`: the latest CGI value at or before hourly stamp `τ`, no older than 30 minutes. Changes are `ln v(τ2) − ln v(τ1)` |
| G: GetDeploying | Weekly `value` (the published median) and `n_listings` (offering count) per series. Week `w`'s value is treated as known only after the week ends. ASSUMPTION, unverified: back-filled histories were not revised after the fact |
| A: AWS spot | Claim 5's pool prices, per GPU-hour, at 23:30 UTC (D36, D37). Classes: H100 (`p5.48xlarge`, `p5.4xlarge`) and H200 (`p5e.48xlarge`, `p5en.48xlarge`), in US zones on Linux. Matched-pool change `a_g(d1, d2)`: the median over pools priced on both days of the log change, NaN with fewer than 3 matched pools. A window that touches the 2026-03 to 06 gap has no value |
| E: equities | Claim 4's buckets and coverage rule. Bucket excess return `R_b(t, h)` is the equal-weight bucket return minus XLK, from the open of session `t` to the close of `t + h − 1`. Claim 5's member start dates apply (D38). Sessions come from the cached bars, at 09:30 and 16:00 New York time. That is conservative for early closes |

## 6. The 12 hypotheses

**Count.** At most 12 hypotheses were allowed; there are exactly 12, each
with one exact test.

**Equity targets.** Only one hypothesis (H12) targets equities, against an
allowed four. Claims 4 and 5 already ran the natural equity tests, and only
AWS data overlap the equity exploration set. H12 uses a signal construction
(a 20-day trend) and a target (the spread between two buckets) that neither
claim tested.

**Other rental series.** Eight hypotheses (H05 to H12) draw on CGI,
GetDeploying or AWS spot, because those have the history our own listings
lack. A signal found there is a lead to test on
our index later, not evidence about our index.

**Notation.** `h` is the forecast horizon. "Lag" is the Newey-West lag in
observation units. Every test is two-sided; the expected sign is the one the
mechanism predicts.

| ID | Mechanism | Signal at `t` | Target | Horizon and sampling | Expected sign |
|---|---|---|---|---|---|
| H01 | **Convergence to the market.** Providers priced far above (below) the cross-provider median face lost (unused) demand and reprice toward it | `s_p(d) = ln P_p(d) − median_q ln P_q(d)`, H100 on-demand, providers present on `d` | provider's own `c_p(d, d+5)` | 5 days; daily cross-sections (Fama-MacBeth) | − |
| H02 | **Price leadership.** The largest neoclouds (CoreWeave, Lambda, Nebius, Crusoe, Together, chosen before testing) move first and smaller providers follow | `M_leaders(d−5, d)` | `M_followers(d, d+5)`, all other H100 providers | 5 days; daily, lag 5 | + |
| H03 | **Neocloud spot leads list prices.** Spot prices clear continuously; on-demand list prices adjust later | `M_spot(d−5, d)`: H100 spot listings | `M_all(d, d+5)`: H100 on-demand | 5 days; daily, lag 5 | + |
| H04 | **Older chips reprice after newer ones.** B200 repricing, driven by supply growth, spreads to H100 | `M_B200(d−5, d)`, on-demand | `M_H100(d, d+5)` | 5 days; daily, lag 5 | + |
| H05 | **Transient moves revert.** A provider dropping out of CGI's sample, or a temporary promotion, moves the index briefly | CGI H100 `ln v(τ) − ln v(τ−6h)` | `ln v(τ+6h) − ln v(τ)` | 6 hours; hourly, lag 6 | − (+ if CGI is smoothed) |
| H06 | **Spot leads on-demand.** As H03, on a 53-week multi-provider series | GD H100 spot `Δ ln value(w)` | GD H100 on-demand `Δ ln value(w+1)` | 1 week; weekly, lag 1 | + |
| H07 | **Stock-outs precede price rises.** Fewer offers mean tighter supply, and prices follow | GD H100 on-demand `Δ ln n_listings(w)` | GD H100 on-demand `Δ ln value(w+1)` | 1 week; weekly, lag 1 | − |
| H08 | **Newer supply cheapens older chips.** Growth in B200 offers pulls H100 demand away | GD B200 on-demand `Δ ln n_listings(w)` | GD H100 on-demand `Δ ln value(w+1)` | 1 week; weekly, lag 1 | − |
| H09 | **Spot trends persist.** AWS adjusts spot prices gradually toward supply and demand, so moves continue | `a_H100(d−7, d)` | `a_H100(d, d+7)` | 7 days; daily, lag 7 | + |
| H10 | **The older generation catches up.** When H200 spot reprices relative to H100, H100 follows | `a_H200(d−7, d) − a_H100(d−7, d)` | `a_H100(d, d+7)` | 7 days; daily, lag 7 | + |
| H11 | **Compute stocks lead rental prices.** Equity markets price AI-compute demand news before sticky rental prices adjust | neocloud `R(t−4, 5)`, known at close plus 20 minutes | `a_H100(t, t+7)`, from the 23:30 UTC price on the session date | about 5 sessions; per session, lag 5 | + |
| H12 | **Renters gain on chip makers when rental prices trend up.** Rental-price rises reach neocloud margins directly, chip makers only through later orders | `a_H100(d*−20, d*)`, where `d*` is the calendar day before session `t` (claim-5 timing) | `R_neocloud(t, 5) − R_gpu_semis(t, 5)` | 5 sessions; per session, lag 5 | + |

### Data and power

| ID | Data | Exploration sample | Power: smallest detectable correlation |
|---|---|---|---|
| H01 | L | about 51 daily cross-sections of 13 to 19 providers | too few price changes to state reliably |
| H02 | L | about 46 days | 0.49 to 0.89 |
| H03 | L | about 46 days | 0.49 to 0.89 |
| H04 | L | about 46 days | 0.49 to 0.89 |
| H05 | C | about 600 hours | 0.14 to 0.34 |
| H06 | G | about 35 weeks | 0.55 |
| H07 | G | about 35 weeks | 0.55 |
| H08 | G | about 35 weeks | 0.55 |
| H09 | A | about 410 days | 0.17 to 0.44 |
| H10 | A, from 2024-12 | about 340 days | 0.18 to 0.48 |
| H11 | A and E | about 280 sessions | 0.21 to 0.52 |
| H12 | A and E | about 280 sessions | 0.20 to 0.46 |

The power column is the smallest correlation that the BH threshold for a
single discovery (0.10/12) would detect with 80% power (Fisher z). The
first figure counts every overlapping observation; the second counts
non-overlapping windows only. The true value lies in between.

**Honest power.** The four hypotheses on our own index (H01 to H04) can
only detect very strong effects. Their confirmation sets have 14 to 19
windows, so even a true effect of moderate size would very likely fail
there. They are tested because they target the priority, not because they
are likely to pass.

## 7. Exploration tests

All tests use `compute_curve.claim4.stats`, with seed 20261005 and 2,000
bootstrap resamples.

**Time-series hypotheses (H02 to H12)**

- **Slope test.** `ols_hac(x, y, lag)`: the slope, its Newey-West standard
  error, and the two-sided p-value, `p_HAC`.
- **Permutation check.** `circular_shift_pvalue(x, y, min_shift)`, with
  `min_shift` equal to the signal window plus the outcome window. This
  keeps every shifted pair free of overlap.
- **Interval.** `block_bootstrap_corr_ci`, with the block length equal to
  the larger of 5 and `min_shift`: a 95% interval for the correlation.

**Panel hypothesis (H01)**

- **Daily slopes.** For each day `d` with at least 5 providers and some
  variation in `s`, the cross-sectional OLS slope `b_d` of `c_p(d, d+5)` on
  `s_p(d)`.
- **Slope test.** The test statistic is the mean of `b_d`, with
  `hac_mean_se` at lag 5 and a t(n−1) p-value.
- **Permutation check.** The exact sign-flip test (`sign_flip_pvalue`) on
  the non-overlapping slopes `b_d`, `b_{d+5}`, and so on, starting from the
  first day.
- **Interval.** A circular block bootstrap of the mean slope, with block
  length 5.

**False-discovery control across the whole round.** Benjamini-Hochberg over
the 12 primary p-values `p_HAC`. A hypothesis that cannot be computed
counts as p = 1.

**Sufficiency.** Each hypothesis needs:

- `n ≥ 3 × lag` (claim 4's rule);
- at least 10 non-zero signal values;
- at least 5 distinct periods in which the signal's underlying one-period
  series changes. A trailing window repeats one change over several days,
  and this rule counts each change once;
- H01 also needs at least 20 daily cross-sections and at least 10 non-zero
  provider changes in the target.

A hypothesis that fails any of these is reported as **not testable**, not
as a failure of the idea.

**Echo check, for hypotheses whose signal can echo the target's own
momentum** (H02, H03, H04, H06, H07, H08, H10, H11, H12):

- re-estimate the slope after partialling out the target's own change over
  the signal window, by Frisch-Waugh-Lovell residualization of both `x` and
  `y` on it;
- for H12, the control is the spread's change over the previous 5
  sessions.

This is a diagnostic used only as a survival filter, not an extra test.

**A hypothesis survives exploration only if all of these hold:**

| | Condition |
|---|---|
| S1 | BH q ≤ 0.10 |
| S2 | permutation or sign-flip p ≤ 0.05 |
| S3 | every sufficiency rule holds |
| S4 | where the echo check applies, the partial slope has the same sign with \|t\| ≥ 1 |

Every exploration result carries the label "exploratory", with its
interval, its power, and the number of hypotheses in the round.

## 8. Confirmation (one shot)

**Selection.** At most the top 3 survivors go to confirmation, ranked by
q-value and then by `p_HAC`. If more than 3 survive, the rest are reported
and carried to round 2 untested.

**Freezing.** Before confirmation, each one's exact specification is frozen
and committed. That specification covers:

- the signal, target, horizon and sampling;
- the sign;
- the intercept and slope fitted on the exploration sample; for H01, the
  mean daily intercept and slope.

**The test.** The frozen specification runs once on its confirmation
sample. It passes only if both conditions hold:

| | Condition |
|---|---|
| C1 | A one-sided Newey-West test of the slope in the exploration direction passes at 5%, Holm-adjusted across the hypotheses confirmed. For H01, the mean of the confirmation-period daily slopes |
| C2 | The frozen forecast `a + b·x` beats both naive baselines out of sample: out-of-sample R² above 0 against a zero change and against the exploration-sample mean of the target |

**After the test.**

- Nothing is adjusted afterwards.
- The confirmation command refuses to run a second time once its result
  file exists.
- A failure is reported as "not confirmed" and, where the confirmation
  sample had less than 50% power against the exploration estimate, as "not
  confirmed (underpowered)".

## 9. Forward test for candidates

A hypothesis that passes confirmation becomes a **candidate**, not a
finding.

**Shadow mode.** It is added to `.github/workflows/daily.yml` in shadow mode
only. The step logs the frozen forecast for each new decision point,
under `reports/exploration/`, and sends no orders.

**Length: 60 future US equity sessions,** stated now. For a daily
rental-price target this means every decision point in those 60 sessions,
about 87 calendar days. A candidate whose input arrives late, such as the
monthly AWS archive, counts a session only once its data and outcome
exist.

**The pass test.** After 60 sessions with known outcomes, the frozen
specification must pass C1 (one-sided 5%, Holm across live candidates)
and C2 on forward data only. Only then is the existing gate evaluated, on
forward data and unchanged:

- **Equity target:** claim 4's gate, G1 to G4, including at least 120
  out-of-sample forecasts.
- **Rental-price target:** the same statistical conditions. But no
  instrument trades until GPU1 or GPU2 lists. So the strategy condition
  cannot be met before then (D26), and the candidate stays in shadow mode.

**Failure.** A candidate that fails the forward test is dropped and
reported. The gate is never loosened.

## 10. Costs, uncertainty, variants

**Costs.**

- **H01 to H11:** forecasts of rental prices that cannot be traded yet, so
  no trading cost applies. That is a limitation, not a finding.
- **H12:** claim 4's equity cost assumptions apply:
  - 15 bps per side on stocks;
  - 3 bps on XLK;
  - 1 bp of fees on sells;
  - borrow at 5% and 0.5% a year.

  A long-short bucket spread costs about 0.4% per round trip, which is the
  hurdle reported next to any effect.

**Uncertainty.** Every result is reported with a 95% bootstrap interval.

**Variants.**

- **This round:** 12 primary tests, at most 3 confirmation tests, and the
  forward tests of any candidates.
- **Diagnostics:** the echo checks and power figures are diagnostics, not
  tests.
- **Where they are logged:** all of this is declared in
  `docs/variants_log.md` and `compute_curve.backtest.variants` before
  anything runs.
- **Project total:** the project-wide count is printed in the report.

## 11. Commands

```bash
uv run compute-curve explore round1 exploration    # exploration set only
uv run compute-curve explore round1 freeze         # freeze top <= 3 survivors
uv run compute-curve explore round1 confirmation   # one shot, refuses a rerun
```

Outputs go to `reports/exploration/`. Split dates and parameters are in
`config/default.toml` under `[exploration]`.
