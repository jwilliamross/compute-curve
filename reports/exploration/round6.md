# Round 6: archived list prices, trading-relevant tests (one-shot)

Plan: docs/exploration_round6_plan.md. Holm over 3 tests at 5%. Research only.

| Test | n | Estimate | One-sided p | Holm p | Verdict |
|---|---|---|---|---|---|
| R6-01 B200/H100 ratio mean reversion (slope) | 12 | -0.246 | 0.298 | 0.893 | not confirmed |
| R6-02 H100 price change -> next-month stock excess (slope) | 24 | -0.487 | 0.792 | 0.893 | not confirmed |
| R6-03 AR(1) vs random walk for monthly H100 change (Clark-West) | 27 | 0.384 | 0.351 | 0.893 | not confirmed |

## Descriptive

- H100 median list price: annualised volatility of monthly log changes 0.290; share of provider-months with a price change 0.17 (40 months).
- B200: volatility 0.288; change share 0.20 (17 months).
