# Claim 13: does residual reversal pay only in volatile markets? (plan)

_Written 2026-10-18, right after claim 12 and before the data below was fetched.
Simulation only: no orders._

## 1. Why

Claim 12 found that frozen SA2-M lost money from 2019 to 2024: −1.65 bps a day, with
5 of 6 years negative. It earned in 2026 (claim 6c).

**The theory.** Nagel (2012), *RFS* 25(7), shows that short-term reversal profits
are the returns to supplying liquidity. They rise with market volatility (VIX) and
are small or negative in calm markets.

**What it predicts:** SA2-type reversal pays when volatility is high and loses when
it is low.

**The year pattern in claim 12 is suggestive,** but this plan does not use it as
evidence:

- 2020 and 2022 (volatile) were the only positive years;
- 2019, 2021, 2023 and 2024 were negative.

That table was seen before this plan, so the AI universe's 2019–24 data is
**contaminated** for this question. The test uses data never fetched.

## 2. Data (never fetched before)

- **Universe:** universe B from claim 6d, the 20 large-cap tech names
  (`statarb.pipeline.UNIVERSE_6D`), plus XLK.
- **Window: 2019-01-02 to 2024-08-30.** Alpaca daily SIP bars, adjustment "all",
  from 2018-06-01, cached under `var/` (D29).
- **What was seen before:**
  - claim 6d used universe B for 2024-09-03 to 2026-10-05, aggregate only;
  - no universe-B session before 2024-09-03 has ever been fetched.

**Strategy.** Frozen SA2-M: the 12 pooled cells, weights accounting, `[statarb]`
parameters.

**Costs** (ASSUMPTIONS): claim 6d's universe-B quoted-spread costs
(`reports/statarb/claim6d_spreads.json`). Stress: ×2 and borrow at 10% a year.

## 3. The regime variable (no look-ahead)

- `v(d)`: the annualized realized volatility of XLK daily log returns over the
  60 sessions ending at the close of d−1. The book held on day d is decided at
  that close.
- **High regime:** `v(d)` is above the median of all `v` values up to d−1 (an
  expanding median, from at least 120 values, starting with the bars from
  2018-06).
- **Low regime:** otherwise. Days with too little history are excluded.

## 4. Tests (one shot, Holm over two, α = 0.05, one-sided)

| ID | Test | Sign |
|---|---|---|
| N13-1 | Mean net return on high days minus mean on low days: OLS of r(d) on the high dummy, Newey–West lag 10 | + |
| N13-2 | Mean net return on high days, Newey–West lag 10 | + |

**Descriptive** (contaminated, as §1 says): the same split on the AI universe,
2019–24 and 2026.

## 5. What the result means, fixed now

**If both pass:**

- "SA2-V", SA2-M traded only in the high regime, becomes a candidate for a
  forward shadow from 2026-10-19 on the AI universe.
- It is judged after 60 forward sessions in the high regime.
- The paper account does not change until then.

**If either fails:**

- Volatility does not rescue reversal in this setting.
- SA2-M stays a regime bet with no identified regime signal.
- No further variant of SA2 is explored on historical data. Every SA2 question
  is then forward-only.

## 5a. Variants

- **Tests: 2.**
- **Descriptive measures: 1.**
- **Total added: 3.**
