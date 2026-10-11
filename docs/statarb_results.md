# Claim 6: statistical arbitrage on compute-linked equities (results)

_2026-10-10. Plan: docs/statarb_plan.md (commit c86c7ec, written before any
strategy return). Full tables: reports/statarb/exploration.md. Simulation only._

## Bottom line

**Neither strategy survived the exploration rules, so no strategy goes to
confirmation.** The confirmation set (2026-02-20 to 10-05) stays unspent.
This is a clean "no significant edge" after costs.

| | SA1 pairs (cointegration) | SA2 residual reversal vs XLK |
|---|---|---|
| Pooled net Sharpe (non-IID SE) | −1.55 (1.11) | +0.18 (0.80) |
| 95% bootstrap CI of the Sharpe | [−3.28, 1.20] | [−1.05, 1.25] |
| Mean daily net return, 95% CI | −2.8 bps [−8.9, 1.2] | +0.9 bps [−4.6, 6.4] |
| Deflated Sharpe (K = 21) | 0.03 | 0.07 |
| Break-even stock cost per side | negative (loses before costs) | 23 bps (assumed 15) |
| Mean at double costs | −3.5 bps a day | −1.6 bps a day |
| Max drawdown, 95th percentile (bootstrap) | 27% | 19% |
| Trades / sessions | 699 / 367 | 1,746 / 367 |
| Survives | no | no |

Costs are ASSUMPTIONS: 15 bps per side for stocks, 3 bps for XLK, a 1 bp
sell fee and 3% a year borrow. There are 21 grid cells; the project total is
256 variants.

## What the numbers say

**1. Pairs trading loses money here, even before costs.**

- In this universe, stocks that looked tied together over the formation
  window kept drifting apart.
- 2024 to 2026 was a period of strong, news-driven trends in AI stocks:
  earnings, contracts, capacity deals. A spread that widens on news does not
  come back.
- The surface is negative everywhere. The least bad cells use the longest
  lookback (250 sessions).

**2. Residual reversal has a little timing information, but no tradable
edge.**

- After costs it is about break-even: Sharpe +0.18, with an interval from −1
  to +1.25.
- The pooled region is all 12 cells. With 1.5 years of data the Sharpe
  standard error is about 0.8 to 1, so the whole surface sits inside one SE
  of its best cell. The parameter ranking is noise. This is exactly the case
  the quant-research skill warns about.
- **Random-entry Monte Carlo** (descriptive):
  - each trade keeps its stocks, direction and holding length, but is moved
    to a random date;
  - the real entry dates did better than 99.3% of 300 random-date versions
    before costs, and than all of them after costs.
  - So the s-score picks better-than-random moments to trade. The edge is
    just too small to beat costs and the 21-trial penalty: the deflated
    Sharpe is 0.07 against a required 0.90.
- **Caveat on that Monte Carlo.**
  - The frozen exploration report's null (1,000 paths, "1.000") could place
    random trades before a stock listed, which biases it downward.
  - A post-hoc diagnostic restricted placements to listed periods. It is
    logged as variant `statarb.null_valid`, and the conclusion held.
  - The code now always does this (D53).
- **Not a signal.** This is a lead about timing. Under the plan it cannot be
  traded, and it is not re-tuned on the same data.

## What would change the answer

- **Lower costs.** The break-even is 23 bps per side. Large liquid names
  (NVDA, AMD, AVGO, TSM, MU) trade far below 15 bps, but the small miners
  and power names do not. A pre-registered liquid-only version with measured
  spreads is a fair next test.
  - Even then it would need the confirmation set, and the confirmation set
    is short: 158 sessions.
- **More data.** With 1.5 years, only a Sharpe above about 2.5 can be told
  apart from zero. Every extra year narrows the interval by about a third.

## Disclosures

- **Survivorship and selection.** The universe was picked in 2026 for its AI
  exposure.
- **Earlier use of the returns.** Equity returns were used earlier, with
  GPU-price signals, in claims 4 and 5 and in H11/H12.
- **Pair weights.** Pairs use hedge-ratio weights, (1, β) scaled to the
  pair's gross. That is dollar-neutral only when β = 1. The plan said
  "dollar-neutral, hedge-ratio weighted", and only one of the two can hold;
  the Engle-Granger hedge ratio was used.
- **Rebalancing approximation.** Weights are target weights each session.
  Drift between rebalances is not charged as turnover, which is a small
  approximation.
