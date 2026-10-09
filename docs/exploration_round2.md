# Exploration round 2: results

_Run 2026-10-09. Plan: `docs/exploration_round2_plan.md`, committed before
any analysis (`4d588a3`). Exploration numbers are **exploratory**. A survivor
is not a finding._

## Bottom line

- **Our own index: still nothing confirmed.** The one lead, H01, was
  replicated once on 19 unseen days. Providers priced above the market tend
  to cut, and those below to raise.
  - The effect size came out almost identical: slope −0.0367 against −0.0363
    in round 1.
  - The frozen forecast beat both naive baselines.
  - But the test was not significant (one-sided p 0.107), so the rule says
    "not confirmed".
  - It points the same way. There are too few days to tell. It is worth
    re-asking once a few more months of listings exist.
- **Two new survivors.** Both await confirmation on future data.
  - **R2-03:** the CGI B200 index gives back about a third of a 6-hour move,
    the same reversal as H05 but on B200.
  - **R2-04:** AWS H100 spot moves persist, forecast with a coefficient
    re-estimated each day. This fixes the failure that sank H09 in round 1.
- **H05's cause is still unknown.** Moves that coincide with providers
  entering or leaving CGI's sample do not revert more (R2-02, p 0.56). So
  provider churn does not explain the reversal.
- **The term-structure idea (R2-06) found nothing.**
- **No equity hypothesis was run.** No orders. The gate is unchanged.

## Housekeeping found on the way: H05's forward log was empty

The daily shadow step had failed on every scheduled run since 2026-10-07.
Two bugs were responsible:
- the CGI history request used bounds off the index's 15-minute grid
  (HTTP 400/404);
- an empty series crashed the step.

Both are fixed, with regression tests, and merged (PR 6, D44). The log was
rebuilt from published values since 2026-10-07 under unchanged
point-in-time rules. None of those values were published late or revised.
Only its row count was looked at.

## R2-01: one-shot replication of H01

| | Round 1 exploration | Replication (2026-09-13 to 10-01, 19 days) |
|---|---|---|
| Mean daily slope | −0.0363 | −0.0367 |
| Standard error (Newey-West) | — | 0.0285 |
| One-sided p (expected −) | — | 0.107 |
| Out-of-sample R², frozen forecast vs zero / vs mean | — | +0.024 / +0.017 |
| Verdict | passed BH, failed sign-flip | **not confirmed**: C1 failed, C2 passed |

A slope of −0.036 means a provider priced 10% above the cross-provider
median changed its own H100 price by about −0.36% over the next 5 days.
That is small, but it is the most stable pattern found so far in our own
data.

## Exploration (round 1's exploration sets)

All four tests are exploratory. Benjamini-Hochberg is applied across the
four at q = 0.10.

| ID | Idea | Result | p | q | Status |
|---|---|---|---|---|---|
| R2-02 | H05's reversal comes from provider churn | interaction slope +0.06; correlation 0.03 (−0.09 to 0.13); 147 windows with a provider-count change | 0.555 | 0.555 | not significant |
| R2-03 | CGI B200 6-hour reversal | correlation −0.37 (−0.49 to −0.23), slope −0.366, n 612 | <0.001 | <0.001 | **survivor** |
| R2-04 | AWS H100 7-day persistence, coefficient re-estimated daily | 346 out-of-sample forecasts; R² +0.17 vs zero, +0.24 vs running mean; Clark-West | 0.008 | 0.015 | **survivor** |
| R2-06 | Rise in the on-demand premium over 12-month reservations precedes on-demand falls | correlation 0.09 (−0.11 to 0.35), n 35 weeks, sign opposite to the idea | 0.438 | 0.555 | not significant |

Pooling all 16 exploratory tests from rounds 1 and 2 under one
Benjamini-Hochberg screen gives:
- R2-03 and R2-04 keep q ≤ 0.025;
- H05 and H09 keep q < 0.001;
- H01 keeps q 0.003.

Full tables are in `reports/exploration/round2_exploration.md`.

### Why each one ended where it did

- **R2-02.** If transient provider entry and exit caused H05, moves in
  windows where CGI's provider count changed would revert more. They don't.
  - The reversal is about as strong whether or not the count changed.
  - Other explanations remain:
    - CGI's smoothing ("stability band");
    - its calculation-version changes;
    - short-lived price checks that don't change the provider count.

  These are not tested.
- **R2-03.** Same index family and same construction as H05, so it is not
  independent evidence that the reversal is real. It does show that the
  reversal is not specific to H100.
- **R2-04.** H09 failed confirmation because a coefficient frozen from
  2024–25 overshot later, weaker persistence. Re-estimating the coefficient
  from past data each day is the standard fix.
  - Out-of-sample within the exploration period it beat both baselines.
  - Round 1's AWS confirmation set was already seen, so it is confirmed only
    on AWS months not yet published.
- **R2-06.** 35 weekly points can detect only correlations of about 0.5 or
  more. The estimate is small and points the wrong way.

## Confirmation: frozen, waiting for future data

Both specifications and coefficients were frozen and committed (`cb7866f`)
before any confirmation data existed (`reports/exploration/round2_frozen.json`).

| Survivor | Confirmation data | Earliest run | Pass rule |
|---|---|---|---|
| R2-03 | CGI B200, 2026-10-10 to 2026-12-31, point-in-time | 2027-01-01 (automatic, daily workflow) | one-sided Newey-West p × 2 ≤ 0.05, and the frozen forecast beats zero and the exploration mean |
| R2-04 | AWS H100 spot, months 2026-10 to 12 | once Zenodo publishes 2026-12; add the months to `[claim5].months` and run `compute-curve claim5 fetch` | Clark-West p × 2 ≤ 0.05, and out-of-sample R² above 0 against zero and the running mean |

The ×2 is a Bonferroni adjustment, because the two finish at different
times (D46). A survivor that confirms becomes a candidate. It then runs 60
more US equity sessions in shadow mode before the existing gate is
evaluated. D26 still applies: nothing trades before GPU1 or GPU2 lists.

## Uncertainty, costs, variants, contamination

- **Uncertainty.** 95% block-bootstrap intervals, with 2,000 resamples and
  seed 20261005. R2-04 is judged on out-of-sample R² and Clark-West.
- **Costs.** None apply. These are forecasts of indices that no instrument
  trades yet.
- **Variants.** Round 2 declared 8 tests:
  - 1 replication;
  - 4 exploratory tests;
  - up to 3 confirmations (2 to be used).

  The project total is 225.
- **Contamination.** Round 2 reused exploration sets that round 1 had
  already mined, for new questions only. Two survivors are relatives of
  round-1 survivors:
  - R2-03 of H05;
  - R2-04 of H09.

  That is why both are confirmed only on data no one has seen.
