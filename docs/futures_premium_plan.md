# Claim 7: the GPU1/GPU2 futures risk premium (plan)

_Written 2026-10-13, before GPU1/GPU2 list. No futures price exists yet;
CFTC review runs to 2026-11-09 (B8). Owner request: "build the futures
premium model". Shadow log and simulation only. No orders, no broker, no
exchange connection._

## 1. Idea and evidence

**Non-storable goods.** An unused GPU-hour cannot be stored, just as a
megawatt-hour cannot. A futures price is therefore an expectation of the
monthly average plus a risk premium, not a cost-of-carry price
(docs/montecarlo_fair_value.md §1). In power markets, forward prices
deviate predictably from the spot later realised:

- Bessembinder, H. and Lemmon, M. L. (2002). Equilibrium pricing and
  optimal hedging in electricity forward markets. *Journal of Finance*
  57(3), 1347–1382.
- Longstaff, F. A. and Wang, A. W. (2004). Electricity forward prices: a
  high-frequency empirical analysis. *Journal of Finance* 59(4),
  1877–1900.

A new market with mostly one-sided hedgers may carry a premium. Its sign
for GPU1/GPU2 is unknown.

**What our own data says about fair value:**

- Round 5: list prices had no trend, −1.2% a year, CI [−15.6%, +11.8%].
- Round 6: a random walk beats AR(1) for monthly changes.

So the fair value of a fully future contract month is the **current index
level**. Every fully future month has the **same** fair value. A futures
price away from that, or a sloped curve, is premium plus error. This is a
model, not a finding: the settlement index may behave differently from
list prices (B7).

## 2. Data and timing (frozen)

- **Futures.** CME daily settlements, dropped by hand in
  `data/manual/cme_settlements/` (format in docs/data_sources.md). A
  settlement for trade date d is usable from the end of d.
- **Index level S** (FP-A only). Published values in
  `data/manual/published_index/`, `SDH100RT` for GPU1 and `SDB200RT` for
  GPU2. A value is usable after the configured publication lag. Without
  them (B7), FP-A is not computed.
- **Realised settlement A_M.** The contract's settlement price on its last
  trading day, which is its final settlement. This is an assumption: for an
  average-price contract, the last day's settle equals the final average
  (unverified).
- **Decision day.** The first business day of each calendar month m. It
  uses the latest settlement and index value usable before 00:00 UTC that
  day.
- **Licence.** Manual CSVs are git-ignored (D59). Logs store only derived
  numbers: log premia, positions and P&L. No prices.

## 3. Strategies (frozen)

**FP-A, outright** (needs S):

- Contract `M1 = m+1`.
- `π = ln F(M1) − ln S`.
- Short 1 if `π > 0.05`; long 1 if `π < −0.05`; else flat.
- Held to final settlement.
- P&L in USD: `pos × (A − F_fill) × 730 − fees`.

**FP-B, calendar** (futures only):

- Contracts `M1 = m+1` and `M2 = m+2`.
- `s = ln F(M2) − ln F(M1)`.
- If `s > 0.03`: short M2, long M1. If `s < −0.03`: the reverse. Else flat.
- Both legs held to their final settlements.
- Under the zero-drift model `E[A(M2) − A(M1)] = 0`, so a sloped curve is a
  premium to sell.

**Costs, per leg.**

- Fill = settle ± (half-spread 5 + slippage 2 ticks) × USD 0.01.
- Plus exchange fee USD 5.50, broker fee USD 2.50 and cash-settlement fee
  USD 1.35.
- These are the existing `[costs]` assumptions.

**Size.** One contract per leg per product per month. GPU1 and GPU2 are
pooled.

## 4. Evaluation (once)

- **Observation.** One traded decision: product × month × strategy, with
  net P&L in USD per contract-set.
- **C1.** The mean net P&L is above 0. One-sided t with Newey-West lag 1,
  since FP-B legs overlap one month. Holm over the 2 strategies, at 5%.
- **C2.** The mean P&L is still above 0 at 2× costs.
- **When.** It runs once, on the first daily run after **12 traded
  observations** of a strategy have settled, or on 2028-01-01, whichever
  comes first.
  - A strategy with fewer than 12 traded observations by then is reported
    as "too little history to conclude".
  - The rule is fixed now, so it is not optional stopping.
- **Pass.** A candidate for local paper trading in the existing futures
  engine, after the owner's approval. A real account is never used.
- **Descriptive (daily).** The log premia π and s for every product and
  day, with no position implied.

**Honest power.** Expect about 2 traded observations a month across both
products, so 12 take about 6 months or more. Each observation is noisy:
monthly index volatility is about 8% (round 6: 29% a year). Only a large
premium, above about 5% per month, is detectable in the first year.

## 5. Variants

+3: FP-A, FP-B and the descriptive premium series. Project total 304 → 307.
