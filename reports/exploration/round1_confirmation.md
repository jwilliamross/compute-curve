# Exploration round 1: confirmation (one shot)

Generated 2026-10-06 22:59 UTC. Frozen specifications from `round1_frozen.json`, run once on
the confirmation set only. C1: one-sided Newey-West test in the exploration direction,
Holm across the 2 confirmed, at 0.05. C2: the frozen forecast
beats a zero change and the exploration mean out of sample (R² above 0 against both).

| ID | Sample | n | Slope | p one-sided | p Holm | OOS R² vs zero | OOS R² vs mean | Power | C1 | C2 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H09 | 2025-12-08 00:00 to 2026-09-23 00:00 | 154 | 0.2649 | 0.010 | 0.010 | -0.080 | -0.078 | 1.00 | yes | no | not confirmed |
| H05 | 2026-09-25 06:00 to 2026-10-05 12:00 | 247 | -0.3167 | <0.001 | 0.001 | 0.109 | 0.107 | 1.00 | yes | yes | confirmed: candidate for the forward test |
