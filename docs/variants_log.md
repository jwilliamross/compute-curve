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

Engine-validation runs on synthetic data are not variants and are not counted.
