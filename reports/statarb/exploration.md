# Claim 6: statistical arbitrage, exploration set

Sessions 2024-09-03 to 2026-02-19. Plan: docs/statarb_plan.md. Variants: 21 grid cells (project total 255). Simulation only.

Costs (ASSUMPTIONS): stocks 15 bps per side, XLK 3 bps, sell fee 1 bp, borrow 3%/yr on shorts. Stress: costs x2, borrow 10%/yr.

The universe was chosen in 2026 for its AI exposure (survivorship and selection, disclosed). Equity returns were used before in claims 4 and 5 with GPU signals; no stat-arb signal had been computed.

## SA1: pairs (cointegration)

Annualized net Sharpe by cell (lookback L down, entry |z| across):

| | 1.5 | 2 | 2.5 |
|---|---|---|---|
| 60 | -1.35 | -1.38 | -1.46 |
| 120 | -0.67 | -0.87 | -0.39 |
| 250 | -0.51 | -0.54 | -0.01 |

Region (within one SE of the best smoothed cell): (60, 1.5), (60, 2), (60, 2.5), (120, 1.5), (120, 2), (120, 2.5), (250, 1.5), (250, 2), (250, 2.5). The pooled candidate is the equal-weight average of these cells.

| Pooled candidate | Value |
|---|---|
| Sessions / trades | 367 / 699 |
| Mean daily net return | -2.80 bps |
| 95% block-bootstrap CI of the mean | [-8.88, 1.18] bps |
| Annualized net Sharpe (non-IID SE) | -1.55 (1.11) |
| 95% block-bootstrap CI of the Sharpe | [-3.28, 1.20] |
| Deflated Sharpe (K = 21) | 0.033 |
| One-sided Newey-West p (descriptive here) | 0.864 |
| Skew / kurtosis / lag-1 autocorrelation | -4.86 / 51.93 / 0.44 |
| Effective observations | 143 |
| Random-entry Monte Carlo: share of 1000 null Sharpes below the real one | 0.090 |
| Max drawdown, 95th percentile of 10000 bootstrap paths | 26.9% |
| Break-even stock cost per side | -52.7 bps |
| Mean daily return at stress costs | -3.52 bps |

**Does not survive.** fails: pooled net Sharpe > 0; fails: deflated Sharpe >= 0.9

## SA2: residual reversal vs XLK (Avellaneda-Lee)

Annualized net Sharpe by cell (window W down, entry |s| across):

| | 1 | 1.25 | 1.5 | 2 |
|---|---|---|---|---|
| 40 | 0.71 | 0.20 | -0.58 | -1.15 |
| 60 | 0.37 | 0.48 | 0.89 | 0.03 |
| 90 | 0.11 | -0.25 | 0.01 | -0.56 |

Region (within one SE of the best smoothed cell): (40, 1), (40, 1.25), (40, 1.5), (40, 2), (60, 1), (60, 1.25), (60, 1.5), (60, 2), (90, 1), (90, 1.25), (90, 1.5), (90, 2). The pooled candidate is the equal-weight average of these cells.

| Pooled candidate | Value |
|---|---|
| Sessions / trades | 367 / 1746 |
| Mean daily net return | 0.86 bps |
| 95% block-bootstrap CI of the mean | [-4.60, 6.43] bps |
| Annualized net Sharpe (non-IID SE) | 0.18 (0.80) |
| 95% block-bootstrap CI of the Sharpe | [-1.05, 1.25] |
| Deflated Sharpe (K = 21) | 0.070 |
| One-sided Newey-West p (descriptive here) | 0.394 |
| Skew / kurtosis / lag-1 autocorrelation | 1.38 / 11.68 / -0.03 |
| Effective observations | 388 |
| Random-entry Monte Carlo: share of 1000 null Sharpes below the real one | 1.000 |
| Max drawdown, 95th percentile of 10000 bootstrap paths | 19.4% |
| Break-even stock cost per side | 23.3 bps |
| Mean daily return at stress costs | -1.59 bps |

**Does not survive.** fails: deflated Sharpe >= 0.9

