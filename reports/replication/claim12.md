# Claim 12 results: out-of-sample replications

Plan: docs/replication_plan.md. One shot. Simulation only; no orders.

## R12-A: frozen SA2-M, 2019-01-02 to 2024-08-30 (never used before)

Costs (ASSUMPTIONS): claim-6c per-symbol quoted-spread costs (half the median NBBO spread + 2 bps), sell fee 1 bp, borrow 3%/yr; stress x2 and 10%/yr.

| Accounting | Sessions | Trades | Mean (bps/day) | 95% CI | Sharpe | 95% CI Sharpe | HAC p | Stress mean (bps) |
|---|---|---|---|---|---|---|---|---|
| weights | 1426 | 6028 | -1.65 | [-4.44, +1.08] | -0.42 | [-1.11, +0.28] | 0.861 | -3.03 |
| shares | 1426 | 6028 | -2.40 | [-5.53, +0.62] | -0.57 | [-1.27, +0.16] | 0.926 | -3.81 |

**Verdict: fails.**

By year (weights accounting, descriptive):

| Year | Names eligible | Sessions | Mean (bps/day) | Sharpe |
|---|---|---|---|---|
| 2019 | 9 | 252 | -2.57 | -1.33 |
| 2020 | 10 | 253 | +0.46 | +0.14 |
| 2021 | 11 | 252 | -1.50 | -0.73 |
| 2022 | 15 | 251 | +3.59 | +0.81 |
| 2023 | 15 | 250 | -5.84 | -1.04 |
| 2024 | 16 | 168 | -5.26 | -1.03 |

## R12-B: rates (20-session DGS2 change) vs AWS spot 4-week change

| Class | Weeks | n | Slope | 95% CI | corr | HAC p | Holm p | Pass |
|---|---|---|---|---|---|---|---|---|
| H100 | 2024-10-07 to 2026-09-28 | 72 | -0.1976 | [-0.8388, +0.4196] | -0.13 | 0.720 | 0.720 | False |
| A100 | 2024-10-07 to 2026-09-28 | 79 | +0.0706 | [-0.1842, +0.2532] | +0.09 | 0.218 | 0.437 | False |
