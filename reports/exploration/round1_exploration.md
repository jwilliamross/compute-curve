# Exploration round 1: exploration-set results (EXPLORATORY)

Generated 2026-10-06 22:56 UTC. Every number here is **exploratory**: it comes from the
exploration set only (docs/exploration_plan.md section 2) and is not a finding.
12 hypotheses, one test each; Benjamini-Hochberg across the round at q = 0.1. Project-wide declared tests and evaluations: 216.

| ID | Data | Sample (first to last t) | n | Non-zero signal | Distinct changes | Slope | Correlation (95% CI) | p (Newey-West) | p (permutation) | q (BH) | Echo t | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H01 | L | 2026-07-19 00:00 to 2026-09-07 00:00 | 958 provider-days, 51 days | 108 | 46 | -0.0363 | pooled -0.12; mean slope CI -0.055 to -0.019 | <0.001 | 0.087 | 0.003 | n/a | fails a robustness filter |
| H02 | L | 2026-07-24 00:00 to 2026-09-07 00:00 | 46 | 5 | 1 | 0.0495 | 0.10 (-0.07 to 0.21) | 0.200 | 0.750 | 1.000 | 2.00 | not testable |
| H03 | L | 2026-07-24 00:00 to 2026-09-07 00:00 | 46 | 46 | 48 | 0.0448 | 0.15 (-0.07 to 0.39) | 0.069 | 0.643 | 0.207 | 2.45 | not significant |
| H04 | L | 2026-07-24 00:00 to 2026-09-07 00:00 | 46 | 23 | 12 | 0.0643 | 0.09 (-0.25 to 0.38) | 0.428 | 0.607 | 0.642 | 1.54 | not significant |
| H05 | C | 2026-08-30 06:00 to 2026-09-24 17:00 | 612 | 612 | 617 | -0.3450 | -0.34 (-0.44 to -0.25) | <0.001 | 0.002 | <0.001 | n/a | survivor |
| H06 | G | 2025-10-13 00:00 to 2026-06-08 00:00 | 35 | 15 | 15 | 0.0258 | 0.16 (-0.01 to 0.51) | 0.260 | 0.364 | 0.521 | 1.16 | not significant |
| H07 | G | 2025-10-13 00:00 to 2026-06-08 00:00 | 35 | 27 | 27 | 0.0114 | 0.06 (-0.15 to 0.44) | 0.602 | 0.576 | 0.802 | 0.48 | not significant |
| H08 | G | 2025-10-13 00:00 to 2026-06-08 00:00 | 35 | 24 | 24 | -0.0028 | -0.02 (-0.20 to 0.16) | 0.790 | 0.909 | 0.861 | -0.46 | not significant |
| H09 | A | 2024-10-08 00:00 to 2025-11-23 00:00 | 412 | 403 | 396 | 0.6606 | 0.66 (0.45 to 0.80) | <0.001 | 0.003 | <0.001 | n/a | survivor |
| H10 | A | 2024-12-19 00:00 to 2025-11-23 00:00 | 340 | 340 | 344 | -0.1060 | -0.12 (-0.44 to 0.20) | 0.406 | 0.487 | 0.642 | 0.20 | not significant |
| H11 | A+E | 2024-10-25 00:00 to 2025-11-21 00:00 | 270 | 270 | 274 | 0.0403 | 0.04 (-0.25 to 0.33) | 0.761 | 0.694 | 0.861 | 0.62 | not significant |
| H12 | A+E | 2024-10-22 00:00 to 2025-12-01 00:00 | 278 | 275 | 403 | -0.0400 | -0.09 (-0.26 to 0.13) | 0.232 | 0.575 | 0.521 | -1.16 | not significant |

## Hypotheses

- **H01**: provider premium over the cross-provider median (H100 on-demand) → provider's own matched 5-day change (5 days). Expected sign −, observed −. Smallest detectable correlation at this n: 0.46. Notes: passes the false-discovery screen but fails a robustness filter.
- **H02**: leaders' 5-day mean change → followers' next 5-day mean change (5 days). Expected sign +, observed +. Smallest detectable correlation at this n: 0.49. Notes: insufficient: 5 non-zero signal values (need 10), 1 distinct changes (need 5).
- **H03**: H100 spot listings' 5-day mean change → H100 on-demand next 5-day mean change (5 days). Expected sign +, observed +. Smallest detectable correlation at this n: 0.49.
- **H04**: B200 on-demand 5-day mean change → H100 on-demand next 5-day mean change (5 days). Expected sign +, observed +. Smallest detectable correlation at this n: 0.49.
- **H05**: CGI H100 past 6-hour change → CGI H100 next 6-hour change (6 hours). Expected sign −, observed −. Smallest detectable correlation at this n: 0.14.
- **H06**: GetDeploying H100 spot weekly change → GetDeploying H100 on-demand next-week change (1 week). Expected sign +, observed +. Smallest detectable correlation at this n: 0.55.
- **H07**: GetDeploying H100 on-demand offer-count change → GetDeploying H100 on-demand next-week change (1 week). Expected sign −, observed +. Smallest detectable correlation at this n: 0.55.
- **H08**: GetDeploying B200 on-demand offer-count change → GetDeploying H100 on-demand next-week change (1 week). Expected sign −, observed −. Smallest detectable correlation at this n: 0.55.
- **H09**: AWS H100 spot 7-day change → AWS H100 spot next 7-day change (7 days). Expected sign +, observed +. Smallest detectable correlation at this n: 0.17.
- **H10**: AWS H200 minus H100 7-day change → AWS H100 spot next 7-day change (7 days). Expected sign +, observed −. Smallest detectable correlation at this n: 0.19.
- **H11**: neocloud 5-session excess return over XLK → AWS H100 spot change over the next 7 days (about 5 sessions). Expected sign +, observed +. Smallest detectable correlation at this n: 0.21.
- **H12**: AWS H100 20-day spot change → neocloud minus GPU-semis excess return, next 5 sessions (5 sessions). Expected sign +, observed −. Smallest detectable correlation at this n: 0.21.

## Survivors

Ranked by q, then p (at most 3 go to confirmation): H09, H05.
