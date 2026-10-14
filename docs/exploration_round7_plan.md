# Round 7 plan: per-provider GPU price history from the GetDeploying API

Pre-registered 2026-10-14. Committed **before any API row was downloaded**: no
GetDeploying API key existed in this repository or session when this file was
written. Decision record: docs/decisions.md D60.

## 1. Data

- **Source.** GetDeploying API, `GET /api/gpu-price-history`, granted free by
  GetDeploying for research until 2026-12-14. GetDeploying allows publishing
  aggregate results with charts and asks for credit.
- **Request shape.** One series per (provider, GPU), with `interval=daily`.
  Before 2026-07-30 this returns the Monday snapshots; daily snapshots start
  2026-07-30.
- **GPUs.** `nvidia-h100`, `nvidia-b200`; `nvidia-h200` is downloaded for
  descriptives only.
- **Providers.** All providers returned by `/api/providers`, except three that
  are never requested:
  - `vast-ai` and `runpod`: their terms prohibit automated collection and index
    use.
  - `together-ai`: excluded under D16.
- **Rows used.**
  - `billing_type = ON_DEMAND` and `reservation_months` null.
  - Price: `median_price`, the provider's median per-GPU hourly price that day.
  - Rows with a missing or non-positive price are dropped.
- **Grid.**
  - Mondays only, so that the weekly history and the daily series are on one
    grid.
  - Last Monday used: **2026-10-12**, the last Monday before this plan was
    committed. Later snapshots never enter these tests.
  - First Monday: the first one on which at least `MIN_CS = 8` providers have
    an H100 price.
- **Timing.**
  - A snapshot dated d is treated as observed at 00:00 UTC on d + 1.
  - The tests use only Monday-to-Monday changes, so this convention changes
    nothing in them.
  - The API's dating is taken as given. It cannot be verified, and early weeks
    of the free CSV look back-filled (docs/data_sources.md).
- **Storage.**
  - Raw responses go to git-ignored `var/getdeploying_api/`.
  - The durable copy is committed **encrypted** (D60).
  - Reports carry aggregates and test statistics only, never a provider's price
    row.

Notation: `p(i,t)` is the log H100 price of provider i on Monday t.

## 2. Tests (one shot, Holm over the four tests at 5%)

### R7-01. Do provider price gaps close?

This repeats round 2's H01 and round 5's R5-01 on a larger cross-section.

- **Premium.** `s(i,t) = p(i,t) − median_j p(j,t)`, the median taken over
  providers priced on Monday t.
- **Outcome.** `c(i,t) = p(i,t+4) − p(i,t)`, the change over the next 4 weeks.
- **Cross-sections.**
  - One OLS slope of c on s each Monday on which at least 8 providers are priced
    at both t and t+4.
  - A Monday with no premium variation gives no slope.
- **Statistic.**
  - Mean slope, with Newey-West SE at lag 6 (the outcomes overlap).
  - One-sided t test, H1: mean slope < 0 (gaps close).
  - At least 26 slopes, otherwise "too little history to conclude".
- **Uncertainty.** 95% circular block bootstrap CI for the mean slope (block 8,
  2000 draws, project seed).

### R7-02. Do price changes spread across providers? (trading-relevant)

- **Breadth.** `x(t) = (n_up − n_down) / n` over the past 4 weeks, where:
  - n is the number of providers priced at both t−4 and t;
  - n_up and n_down count those whose price rose or fell by more than 0.5%.
- **Outcome.** `y(t)` = the median over providers of `p(i,t+4) − p(i,t)`,
  taken over providers priced at both t and t+4.
- x uses only data up to t and y only data from t onwards; they do not overlap.
- **Statistic.**
  - OLS slope of y on x, Newey-West SE at lag 6.
  - One-sided test, H1: slope > 0 (cuts are followed by more cuts).
  - At least 26 observations with n ≥ 8.
- **Uncertainty.** Paired circular block bootstrap CI for the slope (block 8,
  2000 draws).
- **Why it matters.** If this passes, the breadth of recent price cuts predicts
  the next month's market move. That is a candidate signal for the H100 index
  and for GPU1. The SD index itself is not available (B7), so this would be
  only a candidate.

### R7-03. Is the weekly market move predictable from the last one?

- **Series.** `d(t)` = the median over providers priced at t−1 and t of
  `p(i,t) − p(i,t−1)`.
- **Forecast.** Walk-forward AR(1) with an intercept on an expanding window.
  - The fit at t uses `d(1..t)` only.
  - At least 26 changes before the first forecast.
- **Benchmark.** A zero forecast (random walk in levels).
- **Test.** Clark-West, Newey-West lag 1, one-sided (the model is better).
  - At least 26 out-of-sample forecasts.

### R7-04. Does the B200/H100 price ratio mean-revert?

This repeats R6-01 on more providers.

- **Ratio.** `L(t)` = the median over providers with both prices on Monday t of
  `ln(B200/H100)`, using Mondays with at least 3 such providers.
- **Deviation.** `D(t) = L(t)` minus the mean of all earlier `L`; at least 8
  earlier weeks.
- **Outcome.** `L(t+8) − L(t)`.
- **Statistic.**
  - OLS slope, Newey-West SE at lag 10.
  - One-sided test, H1: slope < 0.
  - At least 20 observations.

## 3. Descriptive (not tests)

- **D7-1. Coverage and price stickiness.**
  - Providers priced per Monday, per GPU.
  - The share of provider-weeks with a price change (|Δp| > 0.5%).
  - The annualised volatility of `d(t)`.
- **D7-2. Back-fill check.** The share of provider-weeks before 2025-10-06
  whose price equals the previous week's exactly, against the share after.

## 4. What counts as a result

- A test is **confirmed** only if its Holm-adjusted p is ≤ 0.05 and the point
  estimate has the declared sign.
- None of these is a strategy:
  - No trade is simulated, so no cost assumption applies.
  - Any confirmed effect would need its own plan with costs before it could
    feed a signal ("baselines first").
- **Forward check.** Only nine Mondays fall between 2026-10-19 and the end of
  access on 2026-12-14. That is too few to test anything, so no forward test is
  declared.

## 5. Variants

Four tests and two descriptive measures: six variants (project total 315).
