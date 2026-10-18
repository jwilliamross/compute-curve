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
| claim4.posthoc_drop_large_moves (descriptive, post hoc) | claim 4 | Correlation without the two sessions with level moves of 2% or more, for neocloud vs level_b200 and basket vs level_h100 at h = 1. Run after seeing results, to check whether two days drove them; not a test | 2026-10-06 | no | yes: −0.42 to −0.12 and −0.41 to −0.06 |
| claim5.leadlag (12 tests) | claim 5 | Family P: AWS spot signals (A100 and H100 level and dispersion) × horizons 1, 5, 20; claim 4's basket minus XLK; HAC t and circular-shift permutation; Holm | 2026-10-06 | yes | see docs/claim5_results.md |
| claim5.event (6 tests) | claim 5 | Family E: signed CAR after a spot level move of 2% or more; A100 and H100 × 3 horizons; sign-flip test; Holm | 2026-10-06 | no | see docs/claim5_results.md |
| claim5.walkforward (12 tests) | claim 5 | Family W: expanding-window OLS against zero and mean baselines; Clark-West; Holm | 2026-10-06 | yes | see docs/claim5_results.md |
| claim5.buckets (36 tests) | claim 5 | Family S: lead-lag per bucket basket; Benjamini-Hochberg at 10%; cannot open the gate | 2026-10-06 | no | see docs/claim5_results.md |
| claim5.strategy_pair (12 evaluations) | claim 5 | Gate G3: long-short basket against XLK on each walk-forward forecast, claim 4's costs | 2026-10-06 | no | see docs/claim5_results.md |
| claim5.crosscorr (descriptive) | claim 5 | Cross-correlogram for the two level signals; not a test | 2026-10-06 | no | see docs/claim5_results.md |
| claim5.posthoc_outlier (descriptive, post hoc) | claim 5 | disp_h100 correlations without the 2026-07-06 session, as the plan required; not a test | 2026-10-06 | no | yes: correlations move slightly away from zero; nothing would pass |
| claim5.posthoc_mean_only (descriptive, post hoc) | claim 5 | 20-session strategy run on the running-mean forecast alone, to explain the G3 table; not a test | 2026-10-06 | no | yes: 3.6% per window, the same as with the spot signals |
| explore1.H01 | exploration 1 | Convergence: provider premium over the cross-provider median → the provider's own matched 5-day price change; our H100 listings; Fama-MacBeth with Newey-West, sign-flip check. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H02 | exploration 1 | Leadership: CoreWeave, Lambda, Nebius, Crusoe and Together's 5-day mean change → other H100 providers' next 5-day mean change. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H03 | exploration 1 | Neocloud H100 spot listings' 5-day change → H100 on-demand next 5-day change. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H04 | exploration 1 | B200 on-demand 5-day change → H100 on-demand next 5-day change. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H05 | exploration 1 | CGI H100: past 6-hour change → next 6-hour change (reversal). One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H06 | exploration 1 | GetDeploying H100 spot weekly change → H100 on-demand change the next week. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H07 | exploration 1 | GetDeploying H100 on-demand offer-count change → H100 on-demand change the next week. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H08 | exploration 1 | GetDeploying B200 on-demand offer-count change → H100 on-demand change the next week. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H09 | exploration 1 | AWS H100 spot 7-day matched-pool change → next 7-day change (persistence). One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H10 | exploration 1 | AWS H200 minus H100 7-day change → H100 next 7-day change (catch-up). One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H11 | exploration 1 | Neocloud bucket 5-session excess return over XLK → AWS H100 spot change over the next 7 days. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.H12 | exploration 1 | Equity target: AWS H100 20-day spot trend → neocloud minus GPU-semis excess return over the next 5 sessions. One test; Benjamini-Hochberg across the round's 12 | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore1.echo (filter, not a test) | exploration 1 | Partial slope after removing the target's own past change; survival filter for 9 hypotheses | 2026-10-06 | no | see docs/exploration_round1.md |
| explore1.posthoc_stability (descriptive, post hoc) | exploration 1 | Survivors' correlation in each half of the exploration sample and without the 1% largest signal values. Added after seeing which hypotheses survived, on the exploration set only; changes nothing in the frozen specifications; not a test | 2026-10-06 | no | see reports/exploration/round1_descriptive.md |
| explore1.confirm (up to 3 tests) | exploration 1 | One shot per survivor on the confirmation set: one-sided Newey-West (Holm) and out-of-sample R² above 0 against both naive baselines | 2026-10-06 | yes | see docs/exploration_round1.md |
| explore2.R2-01 (1 test) | exploration 2 | Confirmatory replication of H01 with its frozen round-1 specification on the listings confirmation set (2026-09-13 to 10-06); C1 and C2 | 2026-10-09 | yes | see docs/exploration_round2.md |
| explore2.R2-02 (1 test) | exploration 2 | Mechanism test: CGI H100 6-hour reversal stronger in windows where CGI's provider count changed (interaction slope, Frisch-Waugh-Lovell); cannot become a candidate | 2026-10-09 | yes | see docs/exploration_round2.md |
| explore2.R2-03 (1 test) | exploration 2 | CGI B200 past 6-hour change → next 6-hour change | 2026-10-09 | yes | see docs/exploration_round2.md |
| explore2.R2-04 (1 test) | exploration 2 | AWS H100 spot 7-day persistence with an expanding-window coefficient; Clark-West against zero change | 2026-10-09 | yes | see docs/exploration_round2.md |
| explore2.R2-06 (1 test) | exploration 2 | GetDeploying H100 on-demand premium over the 12-month reservation price (weekly change) → next week's on-demand change | 2026-10-09 | yes | see docs/exploration_round2.md |
| explore2.confirm (up to 3 tests) | exploration 2 | Round-2 one-shot confirmations; CGI and AWS ones on future data | 2026-10-09 | yes | see docs/exploration_round2.md |
| explore1.forward.H05 (1 test) | exploration 1 | Forward test of the confirmed candidate H05 (CGI H100 6-hour reversal) in shadow mode: every hourly decision point in the 60 US equity sessions from 2026-10-07 to 2026-12-31, then C1 and C2 once on forward data only. Declared when the candidate was added | 2026-10-06 | yes | runs daily; result in reports/exploration/round1_forward_H05.json after 2027-01-01 |

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

Claim 5 declares 78 more: 66 hypothesis tests plus 12 strategy
evaluations, with the same battery and gate as claim 4.

Exploration round 1 (docs/exploration_plan.md) declares 16 more: 12
exploratory tests, one per hypothesis, at most 3 one-shot confirmation
tests (2 were run), and the forward test of the one candidate, H05. The
project total is now 217.

Exploration round 2 (docs/exploration_round2_plan.md) declares 8 more: one
replication, four exploratory tests and up to three confirmations. The
project total is now 225.

Exploration round 3 (docs/exploration_round3_plan.md) declares 6 more: four
one-shot confirmation tests on future CGI data (Holm across the four) and
two descriptive jump thresholds. The project total is now 231.

Claim 6, statistical arbitrage on compute-linked equities
(docs/statarb_plan.md), declares 24 more: 21 grid cells (9 pairs, 12
residual-reversal), up to 2 confirmations and 1 forward test. The project
total is now 255. One post-hoc descriptive diagnostic of the random-entry null
(D53) brings it to 256. The proxy-calibrated Monte Carlo fair-value strip
(D55, descriptive) brings it to 257.

Exploration round 4 (docs/exploration_round4_plan.md) declares one forward
one-shot replication of H01 (R4-01). The project total is now 258. Its
addendum adds R4-02 (AWS scarcity leading neocloud prices): 2 confirmation
tests and 2 descriptive exploration fits. The project total is now 262.

Claim 6b (docs/statarb_plan2.md) declares 27 more: 24 grid cells, 2
confirmations and 1 descriptive spread estimation. The project total is now
289. Claim 6c (docs/statarb_plan3.md) declares 3 more: 2 one-shot
confirmations and 1 descriptive quoted-spread measurement. The project total
is now 292. The descriptive paper-readiness diagnostics
(docs/statarb_paper_readiness.md) bring it to 293. Claim 6d
(docs/statarb_plan4.md, out-of-universe replication) adds 2: 295.
The forward-test power calculation (descriptive) and the 250-session SA2-M
extension (1 test, D57, docs/statarb_forward_power.md) add 2: 297.
Round 5 on archived list prices (docs/exploration_round5_plan.md) adds 2:
R5-01 (monthly provider-gap test) and R5-02 (descriptive trend). Total 299.
Round 6 (docs/exploration_round6_plan.md) adds 5: R6-01 to R6-03 (tests, Holm
over 3) and two descriptive measures. Total 304.
Claim 7, the futures premium (docs/futures_premium_plan.md), adds 3: FP-A, FP-B
and the descriptive premium series. Total 307.
Claim 1b, the index gap (docs/index_gap_plan.md), adds 2: GAP-1 (lead-lag) and
GAP-2 (error correction). Total 309.
Round 7 on GetDeploying API per-provider history (docs/exploration_round7_plan.md)
adds 6: R7-01 to R7-04 (tests, Holm over 4) and D7-1, D7-2 (descriptive).
Total 315.
Round 7 post-hoc (docs/exploration_round7.md section 3, exploratory) adds 9:
seven robustness variants (six of R7-01, one of R7-04), index-construction
comparison and monthly settlement risk. Total 324.
Claim 8, the GPU2/GPU1 spread (docs/spread_plan.md), adds 4: SP-I, SP-F, SP-0 and
the C0 forecast gate. Total 328.
The balance-of-month plan (docs/bom_plan.md) adds 2: FP-C and the descriptive
fair-value sheet. Total 330.
Claim 9, the Kalshi GPU binaries (docs/kalshi_plan.md), adds 3: KB-1R, KB-1F and
KB-2. Total 333.
FP-D, long the backwardation (docs/carry_plan.md), adds 3: FP-D-I, FP-D-F and the
descriptive list-price drift study. Total 336.
The exploratory Ornn-vs-list-price basis comparison (docs/kalshi_results.md section 5)
adds 1. Total 337.
FP-K, GPU1 against Kalshi's H100 monthly average (docs/crossvenue_plan.md), adds 2:
the rule and its forecast gate. Total 339.
The SA2-M paper-trading risk review (2026-10-16, descriptive) adds 2: the exploration
period re-run at quoted costs, and the bootstrapped P&L ranges. Total 341.
Claim 10, modern strategies on the SA2 universe (docs/modern_plan.md), adds 8: MX1,
MX2a, MX2b, MX3-k1/k2/k3, MX4 and MX4's IC gate. One post-hoc descriptive comparison
(return per unit gross, docs/modern_results.md) adds 1. Total 350.
Claim 11, AI-economy signals vs GPU rents (docs/macro_drivers_plan.md, docs/macro_drivers.md),
adds 17: MD-1 to MD-5 (Holm over 5), 4 descriptive measures, 5 post-hoc robustness checks
of MD-4, forward checks MD-4F and MD-3R, and rule FP-M. Total 367.

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
