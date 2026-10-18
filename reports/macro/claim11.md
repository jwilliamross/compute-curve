# Claim 11 results: AI-economy signals vs GPU rental prices

Plan: docs/macro_drivers_plan.md. H100 weeks 2024-08-05 to 2026-10-12 (GetDeploying API, aggregates only; credit: GetDeploying). One shot, Holm over 5. No trade is simulated, so no cost assumption applies.

| Test | Predictor | n | Slope | 95% CI | corr | HAC p | Holm p | Verdict |
|---|---|---|---|---|---|---|---|---|
| MD-1 | AI-hardware basket excess return | 111 | -0.0199 | [-0.0878, 0.0276] | -0.08 | 0.748 | 1.000 | not confirmed |
| MD-2 | Neocloud basket excess return | 111 | -0.0161 | [-0.0329, -0.0003] | -0.17 | 0.977 | 1.000 | not confirmed |
| MD-3 | Hyperscaler basket excess return | 111 | -0.1856 | [-0.3161, -0.0410] | -0.42 | 0.996 | 1.000 | not confirmed |
| MD-4 | Change in the 2-year Treasury yield (pp) | 111 | 0.0278 | [0.0086, 0.0508] | 0.29 | 0.007 | 0.035 | confirmed |
| MD-5 | Power and capacity basket excess return | 111 | -0.0398 | [-0.0928, -0.0006] | -0.25 | 0.957 | 1.000 | not confirmed |

Target: 4-week provider-mean log change, n 111, mean -0.0000, sd 0.0215, exactly zero in 23% of weeks.

## Descriptive (exploratory)

Lead-lag: corr(AI-hardware weekly excess return at t, H100 weekly change at t+k).

| k (weeks) | -8 | -7 | -6 | -5 | -4 | -3 | -2 | -1 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corr | -0.17 | 0.12 | 0.02 | 0.09 | 0.04 | 0.24 | -0.04 | 0.03 | -0.03 | -0.09 | -0.02 | 0.02 | -0.23 | 0.12 | 0.10 | 0.04 | -0.03 |

Granger (lag 4, n 114): AI hardware -> H100 p 0.167; H100 -> AI hardware p 0.104.

NVIDIA earnings (7 verified dates): mean H100 4-week change from the next Monday 0.0035 vs -0.0003 in other weeks; share up 0.57 vs 0.42.

B200 (descriptive only):

- MD-1: n 62, slope 0.0583, corr 0.20, HAC p 0.093
- MD-2: n 62, slope 0.0165, corr 0.14, HAC p 0.171
- MD-3: n 62, slope -0.0852, corr -0.18, HAC p 0.892
- MD-4: n 62, slope 0.0575, corr 0.39, HAC p 0.003
- MD-5: n 62, slope 0.0005, corr 0.00, HAC p 0.493
