# Claim 10 confirmation (one shot), 2026-02-20 to 2026-10-05

Costs (ASSUMPTIONS): per symbol, half the median quoted spread + 2 bps per side (reports/statarb/claim6c_spreads.json); sell fee 1 bp; borrow 3%/yr. Stress: all x2, borrow 10%/yr. Books are pooled weights, entries from the first eligible session, data truncated at the window end. Simulation only; no orders. Plan: docs/modern_plan.md. Holm across the survivors, alpha 0.05. This window was already used for SA2-M, so it is not blind for reversal; the forward shadow decides.

| Strategy | Sessions | Trades | Mean (bps/day) | Sharpe (ann.) | 95% CI Sharpe | Test p | Stress mean (bps) | Avg gross | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| SA2-M | 157 | 2906 | +11.17 | +1.89 | [+0.56, +3.29] | 0.008 | +8.30 | 0.51 |  |
| MX1 | 157 | 2906 | +10.67 | +1.83 | [+0.34, +3.64] | 0.464 | +7.54 | 0.55 | descriptive (did not survive the screen) |
| MX2a | 157 | 1808 | +6.94 | +1.61 | [+0.15, +3.36] | 0.036 | +4.89 | 0.33 | not confirmed |
| MX2b | 157 | 1490 | -2.88 | -0.45 | [-2.11, +0.97] | 0.741 | -4.84 | 0.57 | not confirmed |
| MX3-k1 | 157 | 2899 | +2.43 | +0.57 | [-0.45, +1.66] | 0.198 | +0.22 | 0.52 | descriptive (did not survive the screen) |
| MX3-k2 | 157 | 2950 | +3.21 | +0.80 | [-0.53, +2.39] | 0.163 | +0.93 | 0.53 | not confirmed |
| MX3-k3 | 157 | 2921 | +0.97 | +0.27 | [-1.14, +1.51] | 0.370 | -1.21 | 0.55 | descriptive (did not survive the screen) |
| MX4 | 157 | 1554 | -3.99 | -0.62 | [-2.24, +1.12] | 0.750 | -7.21 | 0.58 | descriptive (did not survive the screen) |

Tests:

- SA2-M: reference (SA2-M, frozen; not a claim-10 variant)
- MX1: Moreira-Muir alpha > 0 (HAC) (alpha_daily 1.484e-05)
- MX2a: net mean > 0 (HAC)
- MX2b: net mean > 0 (HAC)
- MX3-k1: net mean > 0 (HAC)
- MX3-k2: net mean > 0 (HAC)
- MX3-k3: net mean > 0 (HAC)
- MX4: net mean > 0 (HAC); gate: IC(ridge) - IC(baseline) > 0 (ic_days 152, ic_model 0.02021, ic_baseline 0.09976, ic_p 0.9967)
