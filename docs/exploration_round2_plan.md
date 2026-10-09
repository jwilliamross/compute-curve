# Exploration round 2: plan

_Written 2026-10-09, before any round-2 analysis. Round 1's protocol
(`docs/exploration_plan.md`) applies unless this document says otherwise.
Every exploration number will be labelled **exploratory**. The report will be
`docs/exploration_round2.md`._

## 1. Why round 2 is small

Almost no new data exists since round 1. Our listings have three more days
(2026-10-07 to 10-09), and no new AWS month has been published. So round 2
does not repeat round 1 or retune its failures. It does four things:

1. **Replicates H01 once.** H01 was round 1's only lead for our own index.
   It runs once, with its frozen round-1 specification, on listing data it
   has never been run on.
2. **Tests why H05 works.** H05 is the CGI 6-hour reversal and the current
   candidate. The test asks whether the reversal comes from providers
   entering and leaving CGI's sample, which is a measurement effect.
3. **Tests whether H05 generalizes to B200.**
4. **Revisits AWS persistence with coefficients that update,** and adds one
   new GetDeploying idea about the term structure of reservation prices.

There is no equity hypothesis this round. Claims 4 and 5 and H11 and H12
found nothing, and no new equity-relevant data exists. Allowed: at most 4.
Used: 0.

## 2. Data and sets

Round 1's split dates stay fixed. Re-splitting would put data already seen
into a "new" confirmation set. A confirmation set already spent in round 1 is
not reused for a related idea; that idea is confirmed on future data instead.

| Dataset | Exploration set (as round 1) | Round-2 confirmation data | Why |
|---|---|---|---|
| Our listings | 2026-07-19 to 09-12 (not used this round) | 2026-09-13 to 10-06 (round 1's confirmation set; no outcome on it has been computed) | R2-01 replication only |
| CGI | 2026-08-30 to 09-24 | **Future:** 2026-10-10 00:00 to 2026-12-31 23:59 UTC | Round 1's CGI confirmation set was spent on H05 |
| GetDeploying | weeks of 2025-10-06 to 2026-06-15 | weeks of 2026-06-22 to 2026-10-05 (round 1's set; unspent) | R2-06 |
| AWS spot | 2024-10-01 to 2025-11-30 | **Future:** the 2026-10, 2026-11 and 2026-12 months, when Zenodo publishes them | Round 1's AWS confirmation set was spent on H09 |

The whole-window, joint-dataset and truncate-before-computing rules from
round 1 apply (D39). Future CGI values are imported daily by the existing
shadow step, which fetches both H100 and B200. Future AWS months arrive
through `compute-curve claim5 fetch` after adding them to `[claim5].months`.

## 3. Contamination (what was already seen)

- **Everything in `docs/exploration_round1.md`:**
  - H01's exploration result: mean slope −0.036, which passed BH but failed
    the sign-flip check;
  - H05's reversal on both CGI sets;
  - H09's persistence: 0.66 in exploration, 0.26 in its confirmation set;
  - every other round-1 statistic.
- **Claim 5:** AWS monthly medians through 2026-09.
- **Claim 4:** our index's levels through 2026-10-05.
- **The H05 forward log:** only its row count has been looked at (64 rows on
  2026-10-09, D44). No performance.
- **GetDeploying:** the reservation series' existence and length (53 weeks),
  and its 2026-10-05 level only.
- **Not seen:** CGI provider counts and any B200 CGI dynamics. Their
  coverage was checked: every value has a count.

## 4. Hypotheses

| ID | Type | Mechanism | Signal | Target | Horizon and sampling | Expected sign |
|---|---|---|---|---|---|---|
| R2-01 | **Confirmatory replication** | H01 convergence: providers priced far from the market reprice toward it | H01 exactly as frozen in round 1 | as H01 | 5 days; daily cross-sections (Fama-MacBeth), lag 5 | − |
| R2-02 | Exploratory, **mechanism test** (cannot become a candidate) | H05's reversal comes from changes in the set of providers CGI covers: a move that coincides with a provider entering or leaving is transient | interaction `z = x · D`, where `x` = CGI H100 past 6-hour log change and `D = 1` if `n_providers` at τ differs from τ−6h | CGI H100 next 6-hour log change; slope on `z` controlling for `x` (Frisch-Waugh-Lovell) | 6 hours; hourly, lag 6 | − |
| R2-03 | Exploratory | H05's mechanism also applies to B200 | CGI B200 past 6-hour log change | CGI B200 next 6-hour log change | 6 hours; hourly, lag 6 | − |
| R2-04 | Exploratory | AWS spot moves persist (H09), but the strength drifts, so only a coefficient re-estimated on past data can forecast | `a_H100(d−7, d)` | `a_H100(d, d+7)`, forecast by expanding-window OLS refitted daily on pairs whose outcome is known at `d` (at least 60) | 7 days; daily, lag 7 | + (forecast beats zero change) |
| R2-06 | Exploratory | Term structure: when on-demand rises relative to the 12-month reservation price (a scarcity premium), on-demand reverts | change in `ln OD(w) − ln R12(w)` from `w−1` to `w`, GetDeploying H100 | `Δ ln OD(w+1)` | 1 week; weekly, lag 1 | − |

(R2-05 was dropped before testing. AWS A100 persistence is contaminated:
claim 5 showed A100 roughly doubled over the confirmation period.)

**Tests**, all with `compute_curve.claim4.stats`, seed 20261005 and 2,000
bootstrap resamples:

- **R2-01:** round 1's confirmation rule exactly.
  - C1: one-sided Fama-MacBeth Newey-West test of the mean daily slope, at
    5%. A family of one.
  - C2: the round-1 frozen forecast (mean exploration intercept and slope)
    beats both a zero change and the exploration mean, with out-of-sample R²
    above 0 against each.
  - Pass needs both. It runs immediately after this plan is committed.
- **R2-02, R2-03, R2-06:**
  - test: `ols_hac` slope test (for R2-02, on residualized `z` and `y`);
  - permutation check: `circular_shift_pvalue` with min_shift = signal
    window + outcome window;
  - interval: `block_bootstrap_corr_ci`;
  - echo check for R2-06, controlling for on-demand's own change.
- **R2-04:**
  - the Clark-West test (`clark_west`, lag 7, one-sided) of the walk-forward
    forecast against a zero change;
  - the out-of-sample R² against zero and against the running training mean
    is reported, and both must be above 0 to survive.

**False-discovery control:** Benjamini-Hochberg at q = 0.10 across the four
exploratory tests (R2-02, R2-03, R2-04, R2-06). R2-01 is outside this family,
because it is a single pre-specified confirmation. The report also gives the
BH result across all 16 exploratory tests of rounds 1 and 2 together, for
context.

**Sufficiency** (as round 1): `n ≥ 3 × lag`, at least 10 non-zero signal
values, at least 5 distinct change periods. For R2-02, at least 10 windows
with `D = 1`. For R2-04, at least 120 out-of-sample forecasts.

**Survival** (as round 1):
- q ≤ 0.10;
- permutation p ≤ 0.05 (for R2-04: both out-of-sample R² above 0);
- sufficiency;
- the echo check where it applies.

### Power

| ID | Approximate n | Smallest detectable correlation (BH single, 0.10/4) |
|---|---|---|
| R2-01 | 14 to 19 daily cross-sections | only very large effects; likely underpowered |
| R2-02 | about 600 hours, but depends on how often `n_providers` changes | unknown until the sufficiency count |
| R2-03 | about 600 hours (about 100 non-overlapping) | 0.13 to 0.30 |
| R2-04 | about 350 out-of-sample days | moderate |
| R2-06 | about 34 weeks | about 0.5 |

## 5. Confirmation and forward test

- **Selection.** Up to three survivors are frozen first: the specification
  plus the exploration-fitted coefficients, committed before any
  confirmation data is used.
- **When each confirmation runs:**

  | Survivor | Confirmation data | When |
  |---|---|---|
  | R2-03 | CGI B200 future data | once, after 2026-12-31 |
  | R2-02 | CGI H100 future data | once, after 2026-12-31 |
  | R2-04 | the AWS 2026-10 to 12 months | once, after they are published |
  | R2-06 | GetDeploying confirmation set | at once, since it is unspent |

- **Rules.** The same C1 and C2 as round 1. R2-02 uses C1 only, because it
  explains H05 rather than forecasting.
- **Candidates.** A confirmed forecasting survivor becomes a candidate. It
  runs in shadow mode for 60 further US equity sessions before the existing
  gate is evaluated. The gate is unchanged, and D26 still applies to
  rental-price targets.

## 6. Variants

Round 2 declares 8 tests:

| Item | Tests |
|---|---|
| R2-01 replication | 1 |
| Exploratory tests (R2-02, R2-03, R2-04, R2-06) | 4 |
| Confirmations | up to 3 |

The project total becomes 225. They are logged in `docs/variants_log.md` and
`compute_curve.backtest.variants` before anything runs.

## 7. Commands

```bash
uv run compute-curve explore round2 exploration    # R2-02..R2-06 on exploration sets
uv run compute-curve explore round2 replicate      # R2-01, one shot
uv run compute-curve explore round2 freeze         # freeze survivors
uv run compute-curve explore round2 confirmation   # one shot per survivor whose data is complete
```
