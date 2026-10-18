# Claim 11 results: do AI-economy signals lead GPU rental prices?

_Run once on 2026-10-18. Plan: docs/macro_drivers_plan.md (commit 5af143b, written
before any predictor was joined to a GPU price). Tables:
`reports/macro/claim11.md`; robustness: `reports/macro/claim11_posthoc.json`._

**Data.**

- GetDeploying API per-provider H100 on-demand prices, weekly, 2024-08-05 to
  2026-10-12. Aggregates only; credit: GetDeploying.
- Alpaca daily closes.
- FRED DGS2 and DGS10 (US Treasury, public domain).

**Costs.** No trade is simulated, so no cost assumption applies. The cost
arithmetic for a possible trade is in §4.

## Bottom line

**Equity prices do not lead GPU rents, but interest rates do, a little.**

- Of five pre-registered predictors, only the **2-year Treasury yield** passed.
  When it rose over the past month, H100 rents rose slightly over the next month
  (Holm p 0.035).
- This is what the user-cost-of-capital model predicts: GPUs are financed
  capital, so higher rates mean higher rent.
- **The effect is real but small and recent.**
  - It explains about 8% of the variance.
  - Almost all of it comes from the last year.
  - It is far smaller than futures trading costs.

| Test | Predictor (past 20 sessions) | n | Slope | 95% CI | corr | Holm p | Verdict |
|---|---|---|---|---|---|---|---|
| MD-1 | AI-hardware stocks minus SPY | 111 | −0.020 | [−0.088, 0.028] | −0.08 | 1.000 | not confirmed |
| MD-2 | Neocloud stocks minus SPY | 111 | −0.016 | [−0.033, −0.000] | −0.17 | 1.000 | not confirmed |
| MD-3 | Hyperscaler stocks minus SPY | 111 | −0.186 | [−0.316, −0.041] | −0.42 | 1.000 | not confirmed (sign opposite to the plan) |
| **MD-4** | **Change in the 2-year yield (pp)** | 111 | **+0.028** | **[0.009, 0.051]** | **0.29** | **0.035** | **confirmed** |
| MD-5 | Power and capacity stocks minus SPY | 111 | −0.040 | [−0.093, −0.001] | −0.25 | 1.000 | not confirmed |

**Target.** The 4-week provider-mean log change in H100 rent:

- standard deviation 2.15%;
- exactly zero in 23% of weeks.

**Power.** About 26 independent 4-week blocks, so only correlations of about 0.45
or more are reliably detectable after Holm.

## 1. What each result says

**Rates (MD-4).**

- **Size.** A 0.25 pp rise in the 2-year yield over a month goes with about
  +0.7% H100 rent over the next month (CI +0.2% to +1.3%).
- **Theory.**
  - The user cost of capital, with r + δ ≈ 0.6 (an ASSUMPTION, plan §1),
    predicts a full pass-through of about +1.7% per pp in the long run.
  - Our slope of +2.8% per pp is in the same range; its CI includes the theory
    value.
  - Neoclouds borrow well above Treasury rates, and their credit spreads move
    with rates, so a larger effect is plausible.
- **B200 agrees** (descriptive): corr 0.39 over 62 weeks.

**AI stocks (MD-1, MD-2).**

- **No lead.** Chip and neocloud stock moves say nothing about the next month's
  list rents.
- **The correlogram is flat in both directions,** with all lags between −0.23
  and +0.24.
- **Granger tests find nothing either way:** p 0.17 for AI hardware → H100, and
  p 0.10 for H100 → AI hardware.
- **This matches claims 4 and 5,** which found no link from GPU prices to
  stocks.
- **Reading.** Equities price long-run chip and contract profits. Spot list
  rents are a sticky corner of the market.

**Hyperscalers (MD-3): a post-hoc flag, not a finding.**

- When hyperscaler stocks outperformed, H100 rents tended to **fall** the next
  month (corr −0.42). This is the opposite of the plan's sign, so the
  pre-registered test fails.
- **Possible stories,** all unverified:
  - hyperscaler capex adds supply;
  - hyperscalers gain when compute gets cheaper.
- It needs its own forward test (§3).

**Power-capacity stocks (MD-5).**

- Slightly negative, the opposite of the plan's sign.
- Power is about 3% of the cost of a GPU-hour (plan §1, ASSUMPTION), so its
  price matters little. Its availability could matter, but this basket does not
  measure availability.

**NVIDIA earnings** (7 verified dates, descriptive):

- The mean 4-week H100 change after earnings was +0.35%, against −0.03% in other
  weeks. 57% of post-earnings windows were up, against 42%.
- Too few events to test.

## 2. Robustness of MD-4 (post-hoc, exploratory; 5 variants)

| Check | n | Slope | corr | One-sided p |
|---|---|---|---|---|
| 10-year yield instead of 2-year | 111 | +0.014 | 0.13 | 0.073 |
| 8-week horizon | 107 | +0.034 | 0.25 | 0.025 |
| First half (2024-08 to 2025-09) | 57 | +0.008 | 0.10 | 0.18 |
| Second half (2025-09 to 2026-10) | 54 | +0.054 | 0.48 | <0.001 |
| Five largest rate moves dropped | 106 | +0.033 | 0.29 | 0.005 |
| Median target (round 7's definition) | 111 | degenerate | – | – |

**What this shows:**

- **Robust to:** the horizon, and dropping the largest rate moves.
- **Weaker with the 10-year yield.** Short rates fit the financing story.
- **Concentrated in the last year.** In the first year the slope has the same
  sign but is small.
- **The same regime caution as SA2-M applies.** One year of data cannot tell a
  lasting mechanism from a regime.

## 3. Forward checks (pre-registered now, data not yet in existence)

These are checked on data collected after 2026-10-18, so their outcome is unknown
today.

**Data.**

- **Main series: our own H100 index.** Weekly Monday values from
  `data/raw/listings/`, rebuilt by `compute-curve index`.
- **Supplementary:**
  - GetDeploying API weeks after 2026-10-12, while access lasts (to
    2026-12-14);
  - Ornn's weekly H100 values from Kalshi settlements.

**Window.** Mondays from 2026-10-19 to 2027-10-18. The evaluation runs once, on
or after 2027-10-25.

| Check | Test | Sign |
|---|---|---|
| MD-4F | MD-4 exactly as specified: 4-week index change on the 20-session DGS2 change, HAC lag 6, one-sided α 0.05 | + |
| MD-3R | MD-3's predictor, with the sign reversed, one-sided α 0.05 | − |

MD-4F confirming would make the rates effect a candidate input for GPU1. MD-3R is
a test of the post-hoc flag, not of the plan.

## 4. What it means for trading GPU1/GPU2

**Not a standalone trade.**

- Futures costs are about 2.8% of an H100 contract per leg (strategy book §2).
- Even a large 0.5 pp monthly rate move predicts only about +1.4% of rent.

**Possible uses, all shadow and all judged forward:**

1. **Rule FP-M: a rates filter on FP-D, long the backwardation.**
   - Take FP-D's long only when the 2-year yield has not fallen by more than
     0.10 pp over the past 20 sessions.
   - The rule is fixed here. It is judged forward once GPU1 lists, against
     unfiltered FP-D, with the same tests as FP-D (docs/carry_plan.md).
2. **A diversifier, not an AI-stock proxy.** GPU rents do not move with AI
   equities in either direction. If GPU1 tracks its index, a long GPU1 position
   adds little AI-equity risk. That would make it a hedge against compute costs,
   not a leveraged AI-stock bet.
3. **Watch the rate path.** For the fair-value sheet, a rising-rate month
   argues for a slightly higher balance-of-month estimate. This is noted, not
   modelled, until MD-4F confirms.

## 5. Variants

- **Plan:** 5 tests and 4 descriptive measures.
- **Post-hoc robustness:** 5.
- **Forward checks:** 2 (MD-4F, MD-3R).
- **FP-M:** 1.
- **Added: 17. Project total: 367.**
