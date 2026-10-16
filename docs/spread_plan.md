# Claim 8 plan: GPU2/GPU1 relative value (the B200/H100 spread)

Pre-registered 2026-10-15. GPU1 and GPU2 are not listed, so no futures price
exists. No Silicon Data history is held (B7). The only evidence behind this
plan is round 7's R7-04 (docs/exploration_round7.md): the median
ln(B200/H100) list-price ratio across providers mean-reverts.

- Slope −0.577 over 8 weeks, CI [−1.04, −0.19], Holm p 0.002, on 50 weekly
  observations.
- With a stable set of providers: slope −0.547.

Research and simulation only: shadow decisions, never orders.

## 1. Idea (power analogue: an inter-commodity spread)

GPU2 (B200) and GPU1 (H100) rent the same kind of service, one generation
apart. Their price ratio is like a spark spread or a peak/off-peak spread.
It can move, but substitution pulls it back. R7-04 says a deviation from its
running average is about 58% undone within 8 weeks.

**Hypothesis.** If the futures market prices the ratio for the contract
month two months ahead as if it were a random walk (no reversion), then a
spread position that bets on the reversion earns money after costs.

## 2. Notation

- t: decision day, the first business day of each month (as in claim 7).
- M2: the contract month two months after t's month.
  - R7-04's 8-week horizon is roughly the gap from t to the middle of M2.
- I1(d), I2(d): Silicon Data H100 and B200 index values on day d, usable
  only from `ts_available`.
- F1, F2: the latest GPU1 and GPU2 settlements for M2, usable before 00:00
  UTC on t (claim 7's `curve_before`).
- S1, S2: the final settlements of M2. Proxy: the settlement on M2's last
  trading day (claim 7's assumption).

## 3. Rules (fixed; no estimated parameters)

- **Reversion factor φ = 0.5.**
  - R7-04 implies 1 − 0.577 = 0.42; the stable-provider version implies
    0.45.
  - Rounded to 0.5, the more conservative side: less predicted reversion.
- **Threshold θ = 0.05** in log ratio.
- **Size.**
  - Long or short 1 GPU2 against k GPU1 on the other side, with
    k = round(F2/F1) clipped to {1, 2, 3}. This is roughly notional-neutral.
  - Inside the risk limits in `config/default.toml` (at most 5 contracts per
    month, 10 gross).
- **Costs per contract per leg:** claim 7's `leg_cost`, USD 60.45 at the
  configured assumptions. Stress at 2×.
- **Holding.** Hold to final settlement. No early exit.
- **P&L, position p ∈ {+1, −1} in GPU2:**

  `p · [(S2 − F2) − k·(S1 − F1)] · 730 − (1 + k) · leg_cost`

### SP-I: index-based (needs licensed SD history)

- **Inputs.**
  - R(t) = ln I2 − ln I1 on the latest day available for both.
  - R̄(t) = the mean of R over all earlier days with both values. At least
    40 such days, otherwise no decision.
- **Forecast.** `R̂ = R̄ + φ·(R(t) − R̄)`.
- **Market.** The futures-implied ratio `f = ln F2(M2) − ln F1(M2)`.
- **Signal.** `g = R̂ − f`.
  - g > θ: buy GPU2 and sell k GPU1 (the market ratio is too low).
  - g < −θ: the reverse.

### SP-F: futures only (fallback if SD history is never obtained)

- **Inputs.**
  - R(t) = the front-month log ratio `ln F2(M1) − ln F1(M1)`. This is the
    market's own near-term level.
  - R̄(t) = the mean of the daily front-month log ratio over all earlier
    trading days. At least 60 such days.
- **Forecast, market and signal.** As SP-I.

## 4. Tests (one-shot)

**Trigger.** The first date on which either variant has 12 settled traded
decisions, or 2028-07-01, whichever comes first.

- **C0, baseline first (forecast).**
  - On every decision day with a settled M2, traded or not, R̂ must beat the
    random-walk forecast R(t) at predicting the realised
    `ln(S2/S1)`.
  - Clark-West, Newey-West lag 1, one-sided, α = 0.05.
  - A variant that fails C0 fails, whatever its P&L.
- **C1, profit.** Mean net P&L per traded decision is above zero.
  - One-sided Newey-West lag 1 (the holding periods overlap by about one
    decision).
  - Holm over SP-I and SP-F, α = 0.05.
- **C2, costs.** Mean P&L is still above zero at 2× costs.

A variant **passes** only if C0, C1 (Holm) and C2 all hold. With fewer than
12 settled trades at the deadline it reads "too little history to
conclude".

## 5. SP-0: forward replication of R7-04 on our own daily index (starts now)

- **Why.** Our index (`reports/own_index.csv`, `history_panel`, coverage
  met) is built from our own collectors, not GetDeploying. Its B200/H100
  ratio is a check on the same market from independent data.
- **Series.** `R_own(d) = ln J2(d) − ln J1(d)` on days where both indices
  meet coverage.
- **Forecast at d.** `R̂ = R̄ + φ·(R_own(d) − R̄)`.
  - R̄ is the mean over all earlier days, at least 20.
  - Horizon: 40 business days.
  - Benchmark: the random walk `R_own(d)`.
- **Test.** Clark-West, Newey-West lag 40, one-sided, α = 0.05. Run once on
  or after 2027-07-01, with at least 60 forecasts whose 40-day outcome has
  been seen.
- **Status.** A forecast check only; no position.

## 6. What this can and cannot show

- Before listing nothing here is a result: the code logs "waiting".
- A pass in SP-I or SP-F is needed before any paper position, plus the
  owner's approval. Live trading is outside this project's scope.
- **The main risk is basis.** R7-04 is a list-price result. Silicon Data's
  indices are built differently (round 7 section 3.1). If SP-0 or C0 fails,
  the idea is dropped.

## 7. Variants

Four: SP-I, SP-F, SP-0 and the C0 forecast gate. Project total 328.
