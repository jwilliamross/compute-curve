# Round 5: provider gaps and the price trend in archived list prices (plan)

_Written 2026-10-13 at about 03:50 UTC. The Wayback backfill (D58) pilot was
running and **no archived row had been read by anyone**. This plan is
committed before any archived price is looked at. Simulation and research
only._

## 1. Data (frozen)

- **Rows.** `data/raw/archive/wayback_*`, the verified rows only (D58).
  - GPU `H100`, term `on_demand`, per-GPU price.
  - Providers: lambda, coreweave, nebius, hyperstack, verda.
- **Capture price.** The **median** per-GPU H100 on-demand price over the
  verified rows of one capture.
- **Month-end price** `P_p(m)`. The capture price of provider p's latest
  capture with `ts_observed` at or before the end of month m. It is used
  only if that capture is at most 92 days old; otherwise it is missing.
- **Months.** 2023-01 to the last complete month covered by the archive.
- **Truncation.** Rows are truncated to that range before anything is
  computed.

## 2. R5-01: do provider gaps close? (one test)

This is H01's idea at monthly frequency, on independent data (archived
pages, 2023 onwards). It is a new variant, not a replication of H01's
frozen daily specification.

| Item | Value |
|---|---|
| Premium | `s_p(m) = ln P_p(m) − median_q ln P_q(m)`, over providers present in month m |
| Outcome | `c_p(m) = ln P_p(m+3) − ln P_p(m)`, both present |
| Cross-section | needs at least **4** providers with premium and outcome (only 5 exist, so H01's 5 would leave almost none) |
| Estimator | Fama-MacBeth: OLS slope of `c` on `s` per month, then the mean slope |
| Inference | one-sided p (slope < 0) with Newey-West lag 3, because the 3-month outcomes overlap |
| Pass | p ≤ 0.05 |
| Minimum data | at least 12 cross-sections, else reported as "too little history to conclude", with no p |

**Expected sign.** Negative: an expensive provider cuts, a cheap one
raises.

**Honest power.** Very low. There are at most 5 providers, list prices
change rarely, and many outcomes will be zero. A non-pass will be weak
evidence.

## 3. R5-02: the list-price trend (descriptive, no test)

- **Estimate.** The OLS slope of `median_p ln P_p(m)` on time in years,
  for months with at least 3 providers present.
- **Interval.** A 95% circular block-bootstrap CI (block 6 months, 2,000
  resamples, project seed).
- **Comparison.** Reported beside the GetDeploying drift used in the Monte
  Carlo fair value (+0.135 per year, CI [−0.33, 0.60]; D55). It is a
  calibration input, not a finding.

## 4. When it runs

- **Once,** after the backfill run(s) that the owner's USD 20 budget allows
  have finished.
- **Never repeated** on the same rows. More archived rows bought later would
  be a new, separately declared test.

## 5. Variants

+2: R5-01 (1 test) and R5-02 (1 descriptive estimate). The project total
rises from 297 to 299.
