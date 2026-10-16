# Claim 10 exploration, 2024-09-03 to 2026-02-19

Costs (ASSUMPTIONS): per symbol, half the median quoted spread + 2 bps per side (reports/statarb/claim6c_spreads.json); sell fee 1 bp; borrow 3%/yr. Stress: all x2, borrow 10%/yr. Books are pooled weights, entries from the first eligible session, data truncated at the window end. Simulation only; no orders. Plan: docs/modern_plan.md. Screen: test p <= 0.2, mean > 0, effective N >= 30 (MX4 also IC gate p <= 0.2).

| Strategy | Sessions | Trades | Mean (bps/day) | Sharpe (ann.) | 95% CI Sharpe | Test p | Stress mean (bps) | Avg gross | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| SA2-M | 367 | 1746 | +1.66 | +0.35 | [-0.88, +1.40] | 0.302 | +0.07 | 0.31 |  |
| MX1 | 367 | 1746 | +1.02 | +0.22 | [-1.08, +1.40] | 0.806 | -0.58 | 0.31 | stops here |
| MX2a | 367 | 1044 | +2.84 | +0.86 | [-0.21, +1.84] | 0.098 | +1.81 | 0.18 | survives the screen |
| MX2b | 367 | 898 | +4.62 | +0.95 | [-0.26, +2.24] | 0.078 | +3.23 | 0.33 | survives the screen |
| MX3-k1 | 367 | 1746 | +0.33 | +0.09 | [-1.44, +1.46] | 0.453 | -0.93 | 0.32 | stops here |
| MX3-k2 | 367 | 1773 | +2.15 | +0.75 | [-0.72, +1.99] | 0.144 | +0.86 | 0.31 | survives the screen |
| MX3-k3 | 367 | 1740 | +1.63 | +0.58 | [-0.77, +1.79] | 0.201 | +0.35 | 0.31 | stops here |
| MX4 | 367 | 612 | +2.48 | +0.66 | [-0.43, +2.14] | 0.177 | +1.79 | 0.16 | stops here |

Tests:

- SA2-M: reference (SA2-M, frozen; not a claim-10 variant)
- MX1: Moreira-Muir alpha > 0 (HAC) (alpha_daily -5.78e-05)
- MX2a: net mean > 0 (HAC)
- MX2b: net mean > 0 (HAC)
- MX3-k1: net mean > 0 (HAC)
- MX3-k2: net mean > 0 (HAC)
- MX3-k3: net mean > 0 (HAC)
- MX4: net mean > 0 (HAC); gate: IC(ridge) - IC(baseline) > 0 (ic_days 98, ic_model 0.03291, ic_baseline 0.05471, ic_p 0.6151)
