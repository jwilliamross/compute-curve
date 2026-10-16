# FP-K plan: GPU1 against Kalshi's H100 monthly-average market (cross-venue)

Pre-registered 2026-10-16, before GPU1 lists. Kalshi's implied-curve log
starts on the same day. Research and simulation only: no Kalshi account and
no orders.

## 1. Idea

GPU1 settles on the monthly average of Silicon Data's H100 index. Kalshi's
KXH100MS markets settle on the monthly average of **Ornn's** H100 index.
Both indices are built from transactions, and their levels were close in
October 2026: SD 2.81 on 10-05, Ornn 2.79 on 10-02 and 10-09.

If the two indices move together, two venues are pricing nearly the same
thing. A gap between GPU1's price and Kalshi's implied expectation for the
same month is then a relative-value signal, like the same power product
quoted on two exchanges.

**Main risk: basis.** The two indices have different methods and providers.
B200 shows how large the gap can be: Ornn about 7.5, SD reported at
5.5–6.0. So FP-K covers **H100 / GPU1 only**.

## 2. Kalshi implied curve (logged nightly from 2026-10-16; derived numbers only)

- **Snapshot.** For each active monthly-average event in KXH100MS (and, for
  description only, KXB200MS, KXH200MS and KXA100MS), at the nightly
  snapshot.
- **Inputs.** Take the "greater than K" markets that have both a bid and an
  ask, with the ask above 0 and below 1, and a spread of 0.20 or less.
  - Mid = (bid + ask)/2, made non-increasing in K.
- **Implied median.** The strike at which the mid crosses 0.5, by linear
  interpolation. It is recorded only if at least 3 quoted strikes exist
  and the mids bracket 0.5.
- **Log.** `reports/kalshi/implied_curve.csv`: date, series, month,
  implied median, number of strikes, median spread. Append-only.

## 3. Rule (fixed)

- **Decision day.** The first business day of each month (as in claim 7).
- **Inputs.**
  - F: the latest GPU1 settlement for M1 (next month), usable before 00:00
    UTC on the decision day.
  - Q: the latest Kalshi implied median for the same month, logged on or
    before the previous calendar day.
  - The decision is skipped if Q is more than 3 days old.
- **Signal.** `g = ln(F / Q)`.
  - g > 0.08: sell 1 GPU1 (M1).
  - g < −0.08: buy 1 GPU1 (M1).
  - The 8% band covers the basis between the indices plus costs.
- **Holding and costs.** Hold to final settlement, with claim 7's
  `leg_cost`, stressed at 2×.
- **No Kalshi leg.** GPU1 is the only position, so this is a forecast-based
  trade with Kalshi as the forecast, not an arbitrage.

## 4. Test (one-shot)

- **Trigger.** 12 settled trades, or 2028-07-01.
- **Pass.** Mean net P&L > 0, one-sided Newey-West lag 1, α = 0.05, and
  still > 0 at 2× costs.
- **Gate first.** Over every decision day with a settled M1, Q must forecast
  GPU1's final settlement better than F does (lower squared log error,
  Diebold-Mariano one-sided, α = 0.10). Otherwise the strategy fails
  whatever its P&L.

## 5. Variants

FP-K and its forecast gate: 2. Project total 339.
