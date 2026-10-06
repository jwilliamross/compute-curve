# Variants log

Every model, index method or strategy variant is declared here and in
`src/compute_curve/backtest/variants.py` **before** it is run. Reports print
the total count so the multiple-testing burden stays visible. Entries are
never deleted.

| Key | Claim | Description | Declared | Primary | Run on real data? |
|---|---|---|---|---|---|
| index.provider_weighted_median | index | Primary own-index aggregate | 2026-10-05 | yes | yes, as construction (no test) |
| index.pooled_median | index | Listing-level median | 2026-10-05 | no | no |
| index.trimmed_mean_10 | index | 10% trimmed mean | 2026-10-05 | no | no |
| nowcast.own_bridge | claim 1 | Own-index bridge, no fitted parameters | 2026-10-05 | yes | no (no settlement-index history) |
| ss.spot_only | claim 2 | Schwartz-Smith real-world fit on index | 2026-10-05 | yes | no (history below 180 days) |
| ss.panel | claim 2 | Schwartz-Smith panel fit with launch jumps | 2026-10-05 | yes | no (no futures) |
| rv.ar1_spread | H4 | AR(1) on performance-normalized log spread | 2026-10-05 | yes | no (history below 120 days) |
| strategy.nowcast_front | claim 3 | Front month on nowcast edge above 2x cost | 2026-10-05 | yes | no (no futures) |
| strategy.rv_fade | claim 3 | Fade abs(z) > 2 on second-month spread | 2026-10-05 | yes | no (no futures) |
| claim4.leadlag (18 tests) | claim 4 | Family P: 6 signals × horizons 1, 5, 20; category-balanced basket minus XLK; HAC t and circular-shift permutation; Holm | 2026-10-06 | yes | see docs/claim4_results.md |
| claim4.event (6 tests) | claim 4 | Family E: signed CAR after a level move of 2% or more; H100 and B200 × 3 horizons; sign-flip test; Holm | 2026-10-06 | no | see docs/claim4_results.md |
| claim4.walkforward (18 tests) | claim 4 | Family W: expanding-window OLS against zero and mean baselines; Clark-West; Holm | 2026-10-06 | yes | see docs/claim4_results.md |
| claim4.buckets (54 tests) | claim 4 | Family S: lead-lag per bucket basket; Benjamini-Hochberg at 10%; cannot open the gate | 2026-10-06 | no | see docs/claim4_results.md |
| claim4.strategy_pair (18 evaluations) | claim 4 | Gate G3: long-short basket against XLK on each walk-forward forecast, net of costs | 2026-10-06 | no | see docs/claim4_results.md |
| claim4.crosscorr (descriptive) | claim 4 | Cross-correlogram, leads and lags −5 to +5; not a test | 2026-10-06 | no | see docs/claim4_results.md |

## Design changes made before any result existed

These were decided on 2026-10-05 after new facts arrived, before any test was
run on real data, so they are not post-hoc tuning:

- Index restricted to US, North America or unknown regions, and hyperscalers
  excluded, after the CFTC filing showed "Geography: United States" and the
  neocloud scope.
- Coverage minimum raised from 2 providers and 3 listings to 3 and 5 when
  more sources became available.
- Settlement averaging switched from calendar days to Business Days, per the
  filed rule.
- Throughput ratio central value moved from 2.3 to 2.5 after Bandi and Su's
  Table 2 was read (range unchanged).
- Fixed-panel history series added to remove composition breaks.

Claim 4 entries stand for several tests each. The total declared for claim 4
is 114: 96 hypothesis tests plus 18 strategy evaluations used only inside
gate G3. Per-stock tests were deliberately not declared (docs/claim4_plan.md
6.6).

## Changes after the first claim-4 run

On 2026-10-06, after the first real-data run, five computational guards were
added (docs/decisions.md D34). They stop degenerate intervals and p-values
from appearing on tiny samples. Each can only make a test stricter. The only
outcomes that changed were two G3 "passes" that were artifacts, both now
fails. No definition or threshold changed, so no new variant was declared.

Engine-validation runs on synthetic data are not variants and are not counted.
