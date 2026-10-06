# Exploration round 1: results

_Run 2026-10-06. Protocol: `docs/exploration_plan.md`. Every exploration
number below is **exploratory**. A survivor is not a finding, and neither
is a candidate._

## Bottom line

**Our own index.** Nothing survived. Our index is too young and changes
too rarely for this round to find anything about it. One idea is worth
re-testing:

- H01: providers priced above the market tend to cut, and those below to
  raise. It passed the false-discovery screen.
- But it failed its pre-registered robustness check, so it did not go to
  confirmation.

**Other rental-price series.** One candidate came through:

- **H05:** the Computable GPU Index (CGI) for H100 tends to give back about
  a third of any 6-hour move over the next 6 hours.
- It survived exploration and then passed its one-shot confirmation.
- It now runs in shadow mode for 60 future sessions, to 2026-12-31. It
  sends no orders.
- It is a forecasting rule for a third-party index, not a trading signal.
  No instrument settles on CGI. Even if it passes the forward test, the
  existing gate keeps it in shadow mode until a tradable contract exists
  (D26).

**AWS spot.** H09, AWS H100 spot persistence, survived exploration. At
confirmation:

- the direction held;
- but the coefficient frozen from 2024–25 overshot, and the forecast lost
  to a naive "no change" guess.

So it was not confirmed. No adjustment was made after seeing that.

**Equities.** H12, the only equity hypothesis, found nothing. Neither did
H11, which tested whether compute stocks lead AWS spot.

## How the round was run

| Step | Commit | What it fixed in advance |
|---|---|---|
| Plan | `6a21706` | Split dates, 12 hypotheses, tests, survival filters, confirmation and forward-test rules, contamination disclosures. Before any analysis |
| Code | `0d0d126` | Loaders that cut every dataset to one set before computing anything; 16 synthetic-data tests (outcome poisoning, planted effects, null world) |
| Exploration and freeze | `90d2b62` | Exploration results; the two survivors' specifications and coefficients frozen before confirmation |
| Confirmation | `342f38b` | One run on the confirmation sets. The command refuses a second run |

**Split dates** (earliest 70% for exploration, latest 30% for confirmation):

| Dataset | Exploration | Confirmation |
|---|---|---|
| Our listings | 2026-07-19 to 09-12 | 2026-09-13 to 10-06 |
| CGI | 2026-08-30 to 09-24 | 2026-09-25 to 10-05 |
| GetDeploying | weeks of 2025-10-06 to 2026-06-15 | 2026-06-22 to 10-05 |
| AWS spot | 2024-10-01 to 2025-11-30 | 2025-12 to 2026-02, and 2026-07 to 09 |
| Equities | 2024-09-03 to 2026-02-19 | 2026-02-20 to 2026-10-05 |

## Every hypothesis

**Exploration statistics.**

- **The test.** A Newey-West slope test. The correlation's 95% interval
  comes from a block bootstrap.
- **False-discovery control.** Benjamini-Hochberg across all 12
  hypotheses (q).
- **Survival.** A hypothesis survives only if all hold:
  - q ≤ 0.10;
  - the permutation (or sign-flip) p ≤ 0.05;
  - enough distinct changes;
  - no echo of the target's own past.

| ID | Idea | Data | Correlation (95% CI) | p | q | Outcome |
|---|---|---|---|---|---|---|
| H01 | Providers converge to the market price | our listings | mean slope −0.036 (−0.055 to −0.019) | 0.0006 | 0.003 | **Fails robustness**: sign-flip p 0.087 |
| H02 | Large providers lead smaller ones | our listings | 0.10 | 0.20 | 1.00 | **Not testable**: the leaders changed price on one day |
| H03 | Neocloud spot leads on-demand | our listings | 0.15 (−0.07 to 0.39) | 0.069 | 0.21 | Not significant |
| H04 | B200 repricing spreads to H100 | our listings | 0.09 (−0.25 to 0.38) | 0.43 | 0.64 | Not significant |
| H05 | CGI 6-hour moves revert | CGI | −0.34 (−0.44 to −0.25) | <0.001 | <0.001 | **Survivor → confirmed → candidate** |
| H06 | Spot leads on-demand (weekly) | GetDeploying | 0.16 (−0.01 to 0.51) | 0.26 | 0.52 | Not significant |
| H07 | Fewer offers precede price rises | GetDeploying | 0.06 (−0.15 to 0.44) | 0.60 | 0.80 | Not significant; sign opposite to the idea |
| H08 | More B200 offers cheapen H100 | GetDeploying | −0.02 (−0.20 to 0.16) | 0.79 | 0.86 | Not significant |
| H09 | AWS H100 spot moves persist | AWS spot | 0.66 (0.45 to 0.80) | <0.001 | <0.001 | **Survivor → not confirmed** |
| H10 | AWS H100 catches up with H200 | AWS spot | −0.12 (−0.44 to 0.20) | 0.41 | 0.64 | Not significant; sign opposite |
| H11 | Compute stocks lead AWS spot | AWS and equities | 0.04 (−0.25 to 0.33) | 0.76 | 0.86 | Not significant |
| H12 | Spot trend favours neoclouds over chip makers (equity target) | AWS and equities | −0.09 (−0.26 to 0.13) | 0.23 | 0.52 | Not significant; sign opposite |

Full tables, sample windows and counts are in
`reports/exploration/round1_exploration.md`.

### Why each one ended where it did

- **H01, convergence.**
  - What was found:
    - A provider priced 10% above the cross-provider median changed its
      own H100 price by about −0.36% over the next 5 days, on average.
    - The mean of 51 daily slopes is clearly negative.
    - But the pre-registered sign-flip check on 11 non-overlapping days
      gives p = 0.087. So the effect rests on fewer independent days than
      the Newey-West test credits.
  - The rule says it does not survive.
  - It is the most promising lead for our own index. In about six months
    the listings will have several times more price changes; it should be
    re-tested then as a new hypothesis.
- **H02, leadership.** CoreWeave, Lambda, Nebius, Crusoe and Together
  changed their H100 list price on only one day in 56. With one event
  there is nothing to test.
- **H03 and H04, spot-to-list and B200-to-H100.**
  - Both point the expected way and are weak.
  - With 46 overlapping windows, only correlations above about 0.5 could
    have been detected. Our listings cannot answer these yet.
- **H05, CGI reversal.** See the next section.
- **H06 to H08, GetDeploying weekly.**
  - Thirty-five weeks can detect only correlations above about 0.55.
  - The early weeks are back-filled copies (`docs/data_sources.md`), which
    weakens the series further.
  - The availability idea (H07) points the wrong way.
- **H09, AWS persistence.** It survived exploration strongly and was
  stable in both halves (0.71 and 0.47). See the confirmation below.
- **H10, H200-to-H100 catch-up.**
  - Nothing beyond H100's own persistence. The echo check shows the
    signal adds nothing once H100's own past change is removed (t = 0.2).
- **H11, compute stocks → AWS spot.**
  - No sign that equity moves lead AWS spot prices over a week.
  - This agrees with claim 5's reverse-direction diagnostic.
- **H12, AWS spot trend → neocloud minus chip makers.**
  - Nothing, and the sign is opposite to the idea.
  - The 0.4% round-trip cost of a long-short bucket trade was never in
    play.

## Confirmation (one shot each)

Each frozen specification was run once on its confirmation set. A
specification passes only if both conditions hold:

| | Condition |
|---|---|
| C1 | A one-sided Newey-West test in the exploration direction, Holm-adjusted across the two |
| C2 | The frozen forecast beats both a zero change and the exploration mean out of sample |

| ID | Sample | n | Slope: exploration → confirmation | One-sided p (Holm) | OOS R² vs zero | OOS R² vs mean | Verdict |
|---|---|---|---|---|---|---|---|
| H05 | 2026-09-25 to 10-05, hourly | 247 | −0.345 → −0.317 | 0.001 | +0.109 | +0.107 | **Confirmed** |
| H09 | 2025-12-08 to 2026-09-23, daily | 154 | 0.661 → 0.265 | 0.010 | −0.080 | −0.078 | **Not confirmed**: C1 passed, C2 failed |

**H09.**

- AWS H100 spot moves still persisted in the confirmation period, but less
  than half as strongly.
- A forecast that assumes the 2024–25 strength overshoots and does worse
  than guessing no change. The rule cannot then be used, so it fails.
- A shrunken coefficient might work. Choosing one now would mean tuning on
  the confirmation data, so it is left for a future round on new AWS
  months.

**H05.**

- The reversal was about as strong in late September and early October as
  in the exploration weeks.
- The frozen rule explained about 11% of the variance of the next 6-hour
  change, against both baselines.

## The candidate: H05, CGI H100 6-hour reversal

**The rule.** At each hour, take the CGI H100 index's log change over the
past 6 hours. The forecast for the next 6 hours is
0.000267 − 0.345 × that change. In words, about a third of a 6-hour move
is given back.

**Why it may happen.** CGI recomputes every 15 minutes from provider price
checks. Its methodology also changed during the sample:

- calculation versions 8, 10 and 16 for H100;
- versions 14 and 17 for B200.

When a provider drops out of the check or shows a short-lived price, the
index jumps and then returns. The reversal is consistent with this kind
of transient measurement noise, not with a market reaction. This is a
hypothesis about the cause, not a finding.

**Point in time.**

- CGI published each value 1 to 8 minutes after its stamp (median 3), so
  the history was not regenerated later.
- The forward test treats each decision as made 10 minutes after the
  hour.
- It excludes any value published more than 15 minutes late (D42).

**What it is useful for.** Forecasting a CGI-like index over hours, for
example to avoid reading a transient jump as a new price level. It says
nothing about our own index, which is daily and sticky. Nor does it say
anything about the Silicon Data settlement index.

**Forward test, as pre-stated.**

- **Command:** `compute-curve explore round1 shadow`. It runs in the daily
  workflow after the tests pass, and in `scripts/daily.sh`.
- **Window:** every hourly decision point in the 60 US equity sessions
  from 2026-10-07 to 2026-12-31 (2,052 points).
- **Log:** `reports/exploration/round1_shadow_H05.csv`, with a summary in
  `round1_shadow.md`. No interim performance is shown.
- **Evaluation:** once, after the last outcome is known (from 2027-01-01),
  with C1 and C2 on forward data only.
- **If it passes:** the existing gate is evaluated, unchanged. For a
  rental-price target, the gate's strategy condition cannot be met before
  GPU1 or GPU2 lists (D26), so H05 would stay in shadow mode.
- **If it fails:** it is dropped.
- **It needs the merge.** The scheduled workflow runs only on the default
  branch, so this branch must be merged for the shadow log to start.

## What this round does not show

- That any of our index's components can be forecast. The data are too
  short and too sticky. The power figures in the plan said so in advance.
- That AWS spot prices lead neocloud list prices, or that compute stocks
  lead our index. The splits leave no joint exploration data, so neither
  was tested (plan section 4).
- That H05 is useful for trading. It is not tradable, and its cause is
  probably measurement.

## Most valuable new data

In order:

1. **Licensed history of the settlement index** (Silicon Data SD-H100 and
   SD-B200, US geography). This is the price that pays. It would let every
   idea here be tested on the real target, over years instead of weeks.
   It is still blocker B7.
2. **Per-provider price history with timestamps.**
   - Leadership (H02) and convergence (H01) need many repricing events.
   - Two sources:
     - CGI's per-provider receipts, if their history can be obtained under
       its CC BY-NC licence;
     - our own collection, kept running for 6 to 12 months.
3. **Real availability or utilization data**, such as Lium's
   listed/rented/idle counts, collected daily from now. Stock-out ideas
   (H07) failed for lack of a real availability measure, not for lack of
   a mechanism.
4. **Live AWS spot prices.** The monthly archive cannot drive a daily
   signal. Live prices would need an AWS account, which is the owner's
   decision.
5. **Time.** Each month of our own listings adds about 30 index days.
   About six months from now, H01, H03 and H04 can be re-asked with real
   power.

## Uncertainty, costs, variants, contamination

- **Uncertainty.** Every correlation has a 95% circular-block bootstrap
  interval (2,000 resamples, seed 20261005). The panel test (H01) uses a
  bootstrap of the mean daily slope.
- **Costs.**
  - None apply to H01–H11: they forecast prices that cannot be traded yet.
  - H12 used claim 4's equity cost assumptions: about 0.4% per long-short
    round trip.
- **Variants.**
  - **This round:** 16 tests declared before use. 12 were exploratory,
    one per hypothesis; 2 of the 3 allowed confirmation tests were used;
    and there is 1 forward test.
  - **Diagnostics, not tests:** a descriptive stability check, logged post
    hoc, plus the echo filter.
  - **Project:** 217 tests and evaluations declared in total. See
    `docs/variants_log.md`.
- **Contamination.** Earlier claims had already shown:
  - our index's levels through 2026-10-05;
  - AWS monthly medians;
  - equity basket statistics.

  None of the 12 statistics had been computed before the plan (plan
  section 3). H11 and H12 were the most exposed and both came out null.
