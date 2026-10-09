# Exploration round 2: exploration-set results (EXPLORATORY)

Generated 2026-10-09 21:55 UTC. Exploration sets of round 1 only
(docs/exploration_round2_plan.md). Benjamini-Hochberg across the 4 tests at q = 0.10.

| ID | n | Non-zero signal | Distinct changes | Slope | Correlation (95% CI) | p | Robustness p | q (BH) | Echo t | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| R2-02 | 612 | 612 | 89 | 0.0607 | 0.03 (-0.09 to 0.13) | 0.555 | 0.629 | 0.555 | n/a | not significant |
| R2-03 | 612 | 612 | 617 | -0.3664 | -0.37 (-0.49 to -0.23) | <0.001 | 0.002 | <0.001 | n/a | survivor |
| R2-04 | 346 | 403 | 396 | 0.6610 | OOS R² 0.172 vs zero, 0.244 vs mean | 0.008 | both R² > 0 | 0.015 | n/a | survivor |
| R2-06 | 35 | 25 | 25 | 0.0252 | 0.09 (-0.11 to 0.35) | 0.438 | 0.636 | 0.555 | 0.59 | not significant |

## Hypotheses

- **R2-02**: CGI H100 past 6-hour change x (provider count changed in window) → CGI H100 next 6-hour change, controlling for the past change (6 hours); expected sign −.
- **R2-03**: CGI B200 past 6-hour change → CGI B200 next 6-hour change (6 hours); expected sign −.
- **R2-04**: AWS H100 spot 7-day change (expanding-window OLS forecast) → AWS H100 spot next 7-day change (7 days); expected sign +. Notes: OOS R2 vs zero 0.172, vs running mean 0.244.
- **R2-06**: GetDeploying H100 on-demand premium over 12-month reservation, weekly change → GetDeploying H100 on-demand next-week change (1 week); expected sign −.

Extra counts: {"R2-02_D_windows": 147, "R2-04_n_oos": 346}.

Survivors: R2-03, R2-04.
