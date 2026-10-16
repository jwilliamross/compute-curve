# Balance-of-month fair value and FP-C (pre-registered 2026-10-15)

Pre-registered before GPU1/GPU2 list, with no futures or Silicon Data history
held. Methods: the `nonstorable-futures` skill, section 3. Research and
simulation only.

## 1. Fair-value sheet (descriptive; runs nightly)

For each product (GPU1, GPU2) and each of the current month M0 and the next
three months M1–M3, as of day t:

- **Index L.** The latest settlement-index value usable at t:
  - Silicon Data's published index, if a licensed CSV is present in
    `data/manual/published_index/`;
  - otherwise our own index, labelled **proxy** (basis risk; round 7
    section 3.1).
- **M0, balance of month.**
  - k averaging (business) days have been observed, with average A_k; m
    days remain, out of N in total.
  - Fair value: `FV = (k·A_k + m·L) / N`.
- **M1–M3.** `FV = L`: a driftless random walk, supported by R6-03 and the
  sticky-price results of rounds 5–7.
- **Uncertainty.** Under a random walk with daily log volatility σ, the
  variance of the average of the remaining values at horizons
  h_1, …, h_m business days ahead is
  `σ² · (1/m²) · Σ_i Σ_j min(h_i, h_j)`.
  - For M0 it is scaled by `(m/N)²`.
  - The band is FV·exp(±1.645·sd), a 90% interval.
- **σ estimate.** The sample standard deviation of the index's daily log
  changes over the last 60 observations, floored at 0.001. The sheet
  reports it with the number of observations behind it.
- **Market comparison.** When CME settlement CSVs are present, the sheet
  shows each month's latest settlement F and `F − FV`, in USD per GPU-hour
  and in band widths.

## 2. FP-C: balance-of-month trade on the current month

Needs licensed SD daily values for A_k. Never run on the proxy.

- **Decision.** Once per contract month, on the first business day on which
  at least half the month's averaging days have been observed (k ≥ N/2).
- **Market.** F is the latest M0 settlement usable before 00:00 UTC on the
  decision day.
- **Band.** `b = 2 · leg_cost / 730` (USD per GPU-hour), where `leg_cost`
  is claim 7's cost (entry spread, slippage and fees), plus `1.0 · sd` of
  FV.
- **Rule.**
  - Sell one M0 contract if F > FV + b.
  - Buy one if F < FV − b.
  - Hold to final settlement.
- **P&L.** `pos · (S − F) · 730 − leg_cost`. Stress at 2× costs.
- **Test, one-shot.** Triggered by 12 settled traded decisions or by
  2028-01-01.
  - Mean net P&L > 0, Newey-West lag 1, one-sided, α = 0.05.
  - Mean P&L still > 0 at 2× costs.
  - Otherwise "not confirmed", or "too little history to conclude".

## 3. Why this might earn money

- Once half the month is averaged, most of M0's settlement is already known.
  On H100 list-price medians the monthly average stayed within 0.23% of its
  first Monday value (median; round 7 section 3.2).
- A new, thin contract may still trade M0 off the latest index level or off
  stale quotes, not off the locked-in average.
- In power, balance-of-month mispricing after a mid-month price move is a
  standard desk trade.
- It is low-risk by construction, because the remaining-days variance is
  small.

## 4. Variants

One test (FP-C) and one descriptive sheet: 2 variants. Project total 330.
