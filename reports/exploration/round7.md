# Round 7: GetDeploying per-provider price history (one-shot)

Plan: docs/exploration_round7_plan.md (committed before the download). Holm over 4 tests at 5%. Mondays up to 2026-10-12, on-demand, Vast.ai, RunPod and Together excluded. No trade is simulated, so no cost assumption applies. Variants: 6 (project total 315).

Data: GetDeploying API, research access (vintage 20261014T172009Z). Source credit: GetDeploying, getdeploying.com. Aggregates only; no provider price rows are published.

| Test | n | Estimate | 95% CI | One-sided p | Holm p | Verdict |
|---|---|---|---|---|---|---|
| R7-01 Provider gaps close (mean 4-week Fama-MacBeth slope < 0) | 111 | -0.023 | [-0.039, -0.011] | 0.001 | 0.003 | confirmed |
| R7-02 Breadth of past cuts predicts next 4-week market move (slope > 0) | 107 | 0.000 | [+0.000, +0.000] | n/a | 1.000 | not confirmed |
| R7-03 AR(1) beats random walk for the weekly market move (Clark-West) | 87 | n/a | n/a | n/a | n/a | too little history to conclude |
| R7-04 B200/H100 ratio mean-reverts over 8 weeks (slope < 0) | 50 | -0.577 | n/a | 0.000 | 0.002 | confirmed |

## Descriptive

- H100: 115 Mondays (2024-08-05 to 2026-10-12), 54 providers ever, median 31 a week; share of provider-weeks with a move > 0.5%: 0.08; weekly market move volatility 0.000 a year; exactly unchanged before 2025-10-06 0.97 vs after 0.85.
- B200: 79 Mondays (2025-04-14 to 2026-10-12), 28 providers ever, median 10 a week; share of provider-weeks with a move > 0.5%: 0.09; weekly market move volatility 0.063 a year; exactly unchanged before 2025-10-06 0.96 vs after 0.89.
- H200: 105 Mondays (2024-10-14 to 2026-10-12), 43 providers ever, median 18 a week; share of provider-weeks with a move > 0.5%: 0.06; weekly market move volatility 0.060 a year; exactly unchanged before 2025-10-06 0.97 vs after 0.91.
