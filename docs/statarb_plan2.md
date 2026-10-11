# Claim 6b: residual reversal with measured trading costs (plan)

_Written 2026-10-11, before any 6b statistic was computed. It follows
docs/statarb_plan.md and docs/statarb_results.md. Simulation only._

## 1. Why

In claim 6, SA2 (Avellaneda-Lee residual reversal) did three things:

- it beat random entry timing in 99% of Monte Carlo draws;
- it broke even at 23 bps per side;
- it lost at the flat 15 bps assumed for every stock.

A flat cost is crude. Mega-caps trade far below 15 bps, and small miners
trade above it.

Claim 6b replaces the flat assumption with a **measured per-stock cost**. It
also tests a liquid subset.

**Contamination, disclosed.**

- The idea comes from claim 6's exploration result, so the SA2 surface on the
  exploration set has been seen.
- The confirmation set (2026-02-20 to 10-05) has **not** been used by any
  stat-arb test, because nothing survived claim 6.

## 2. Cost model (fixed now)

**Effective spread per stock.** The Corwin and Schultz (2012, *Journal of
Finance* 67(2)) high-low estimator, with their overnight adjustment, computed
on daily bars of the **exploration set only** (2024-09-03 to 2026-02-19):

- β = [ln(H_t/L_t)]² + [ln(H_{t+1}/L_{t+1})]²;
- γ = [ln(max(H_t, H_{t+1}) / min(L_t, L_{t+1}))]²;
- α = (√(2β) − √β)/(3 − 2√2) − √(γ/(3 − 2√2));
- S = 2(e^α − 1)/(1 + e^α).

Two-day estimates below zero are set to zero. A stock's spread is the median
over the window.

**Cost per side for a stock.** S/2 plus 2 bps slippage (ASSUMPTION), plus the
1 bp sell fee and 3% a year borrow, as in claim 6. XLK stays at 3 bps per
side.

**Stress (C2).** Every cost is doubled, and borrow is 10% a year, as in
claim 6.

## 3. Strategies (24 cells)

| ID | Universe | Grid |
|---|---|---|
| SA2-M | all 20 stocks, measured costs | W ∈ {40, 60, 90} × e ∈ {1.0, 1.25, 1.5, 2.0} |
| SA2-L | the 10 stocks with the lowest estimated spread on the exploration set, measured costs | same grid |

Everything else is claim 6's SA2 unchanged: entry and exit rules, XLK hedge,
10 positions, 20-day maximum hold, timing, region pooling and survival rules.

**Deflated Sharpe.** It uses K = 45 trials: all claim-6 and claim-6b cells.

## 4. Confirmation (one shot, survivors only)

- **Set.** Sessions 2026-02-20 to 10-05, with the frozen pooled region and
  the exploration-set spread estimates.
- **C1.** A one-sided Newey-West p (lag 10) of the mean daily net return,
  Holm-adjusted across survivors, of at most 0.05.
- **C2.** The mean is still above 0 at stress costs.

A confirmed strategy goes to a 60-session shadow test with no orders.

## 5. Variants

- 24 cells;
- 2 confirmations;
- 1 spread-estimation step (descriptive).

The project total rises from 262 to 289.
