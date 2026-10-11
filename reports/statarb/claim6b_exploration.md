# Claim 6b: residual reversal with measured costs, exploration set

Sessions 2024-09-03 to 2026-02-19. Plan: docs/statarb_plan.md. Variants: 45 grid cells (project total 255). Simulation only.

Costs (ASSUMPTIONS): stocks 15 bps per side, XLK 3 bps, sell fee 1 bp, borrow 3%/yr on shorts. Stress: costs x2, borrow 10%/yr.

The universe was chosen in 2026 for its AI exposure (survivorship and selection, disclosed). Equity returns were used before in claims 4 and 5 with GPU signals; no stat-arb signal had been computed.

## SA2-M: residual reversal, all names, measured costs

Annualized net Sharpe by cell (window W down, entry |s| across):

| | 1 | 1.25 | 1.5 | 2 |
|---|---|---|---|---|
| 40 | 0.33 | -0.12 | -0.81 | -1.31 |
| 60 | 0.10 | 0.23 | 0.64 | -0.12 |
| 90 | -0.09 | -0.41 | -0.15 | -0.66 |

Region (within one SE of the best smoothed cell): (40, 1), (40, 1.25), (40, 1.5), (40, 2), (60, 1), (60, 1.25), (60, 1.5), (60, 2), (90, 1), (90, 1.25), (90, 1.5), (90, 2). The pooled candidate is the equal-weight average of these cells.

| Pooled candidate | Value |
|---|---|
| Sessions / trades | 367 / 1746 |
| Mean daily net return | -0.72 bps |
| 95% block-bootstrap CI of the mean | [-6.26, 4.84] bps |
| Annualized net Sharpe (non-IID SE) | -0.15 (0.81) |
| 95% block-bootstrap CI of the Sharpe | [-1.41, 0.95] |
| Deflated Sharpe (K = 45) | 0.013 |
| One-sided Newey-West p (descriptive here) | 0.589 |
| Skew / kurtosis / lag-1 autocorrelation | 1.35 / 11.63 / -0.03 |
| Effective observations | 391 |
| Random-entry Monte Carlo: share of 1000 null Sharpes below the real one | 1.000 |
| Max drawdown, 95th percentile of 10000 bootstrap paths | 22.9% |
| Break-even stock cost per side | 0.8 bps |
| Mean daily return at stress costs | -4.75 bps |

**Does not survive.** fails: pooled net Sharpe > 0; fails: deflated Sharpe >= 0.9

## SA2-L: residual reversal, 10 lowest-spread names, measured costs

Annualized net Sharpe by cell (window W down, entry |s| across):

| | 1 | 1.25 | 1.5 | 2 |
|---|---|---|---|---|
| 40 | -0.88 | -1.16 | -1.05 | -2.10 |
| 60 | -0.04 | 0.12 | 0.47 | 0.29 |
| 90 | 0.12 | -0.47 | 0.19 | 0.98 |

Region (within one SE of the best smoothed cell): (60, 1), (60, 1.25), (60, 1.5), (60, 2), (90, 1), (90, 1.25), (90, 1.5), (90, 2). The pooled candidate is the equal-weight average of these cells.

| Pooled candidate | Value |
|---|---|
| Sessions / trades | 367 / 499 |
| Mean daily net return | 0.42 bps |
| 95% block-bootstrap CI of the mean | [-1.91, 2.70] bps |
| Annualized net Sharpe (non-IID SE) | 0.21 (0.81) |
| 95% block-bootstrap CI of the Sharpe | [-1.07, 1.23] |
| Deflated Sharpe (K = 45) | 0.033 |
| One-sided Newey-West p (descriptive here) | 0.361 |
| Skew / kurtosis / lag-1 autocorrelation | 3.10 / 27.22 / -0.00 |
| Effective observations | 370 |
| Random-entry Monte Carlo: share of 1000 null Sharpes below the real one | 0.983 |
| Max drawdown, 95th percentile of 10000 bootstrap paths | 6.6% |
| Break-even stock cost per side | 1.4 bps |
| Mean daily return at stress costs | -0.89 bps |

**Does not survive.** fails: deflated Sharpe >= 0.9


## Measured costs (Corwin-Schultz, exploration set only)

Per-side cost = half the median spread + 2 bps slippage (ASSUMPTION). With measured costs the 'break-even stock cost' row is the multiple of these costs at which the mean net return reaches zero.

| Symbol | Median spread (bps) | Per-side cost (bps) | Liquid 10 |
|---|---|---|---|
| MU | 13.0 | 8.5 | yes |
| TSM | 25.4 | 14.7 | yes |
| VRT | 26.1 | 15.0 | yes |
| AMD | 36.0 | 20.0 | yes |
| CRWV | 40.6 | 22.3 | yes |
| AVGO | 42.8 | 23.4 | yes |
| SMCI | 52.1 | 28.0 | yes |
| NVDA | 53.2 | 28.6 | yes |
| TLN | 61.8 | 32.9 | yes |
| VST | 66.1 | 35.1 | yes |
| CEG | 68.0 | 36.0 |  |
| MRVL | 69.1 | 36.6 |  |
| APLD | 76.0 | 40.0 |  |
| CORZ | 76.9 | 40.5 |  |
| CIFR | 80.1 | 42.1 |  |
| NBIS | 88.8 | 46.4 |  |
| BE | 93.7 | 48.8 |  |
| IREN | 124.5 | 64.2 |  |
| WULF | 144.3 | 74.1 |  |
| WYFI | 156.4 | 80.2 |  |
