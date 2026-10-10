# Exploration round 3: plan

_Written 2026-10-10, before any round-3 test statistic was computed. Round 1's
protocol (`docs/exploration_plan.md`) and round 2's split rules
(`docs/exploration_round2_plan.md`, D45) apply unless this document says
otherwise. The report will be `docs/exploration_round3.md`._

## 1. Purpose: find what drives the CGI reversal

H05 (H100) and R2-03 (B200) show that CGI's past 6-hour move partly reverses
over the next 6 hours. Round 2's R2-02 asked whether the reversal comes from
providers entering and leaving CGI's sample. It found no effect: the
interaction was +0.06, p 0.56.

**R2-02 is not ignored here.** A p-value of 0.56 is what noise produces, so it
is not evidence of an effect. But the test may have been mis-specified, and
that is worth fixing:

- R2-02 compared the provider count (`n_passing`) at the decision hour τ with
  the count at τ − 6h, at hourly resolution.
- CGI publishes every 15 minutes. Its seat drop-outs usually last 15 minutes
  (median drop-to-return 15 minutes, H100 and B200). A drop and return inside
  the window leaves the two hourly counts equal, so R2-02 marked most such
  windows as "no change".

Round 3 re-specifies that test at 15-minute resolution. It adds two other
explanations taken from CGI's published methodology:
https://github.com/getcomputable/gpu-index at commit 528b639, METHODOLOGY.md
sections 5 to 8.

### Disclosure: the CGI exploration window is contaminated

Before this plan, a research agent looked descriptively at CGI's exploration
window (2026-08-30 to 09-24). It computed no p-values. Its findings shaped
these hypotheses, so the exploration window cannot test them:

- moves are lumpy jumps;
- the top 5% of 15-minute moves carry 90% (H100) and 76% (B200) of the
  variance;
- 88% of H100's largest 1% of moves sit on a stamp where `n_passing`
  changed;
- zeroing the largest 1% of moves shrinks the descriptive 6-hour slope from
  −0.33 to −0.17 (H100) and from −0.36 to −0.03 (B200);
- the lower edge of the H100 stability band (value − band) and the upper
  edge of the B200 band are mostly pinned.

All are descriptive and unverified. Notes are in the session scratchpad and
are summarised in the round-3 report.

So round 3 has **no exploration screen**:

- Every pre-registered hypothesis goes to confirmation exactly once, on
  future CGI data, with Holm across the family.
- The exploration window is used only to freeze coefficients for the
  out-of-sample criterion C2. Its statistics are reported as **exploratory,
  contaminated**, and they count for nothing.

## 2. Data

| Item | Value |
|---|---|
| Source | CGI 15-minute history (approved source; collector `cgi`, backfill `cgi_hist`) |
| Fields used | `value`, `n_providers` (CGI's `coverage.n_passing`), `methodology_id`, `stability_band_usd_gpu_hr` (from `raw_json`) |
| Exploration window (coefficients only) | 2026-09-01 00:15 to 2026-09-24 23:45 UTC |
| Confirmation window (future) | **2026-10-11 00:00 to 2026-12-31 23:45 UTC** |
| Point-in-time rule | first-observed vintage per stamp; `generated_at` within 15 minutes of the stamp (as R2-03) |

Notes on the windows:

- **Exploration start.** Stamps before 2026-09-01 00:15 are left out. They
  carry methodology versions that took effect only on 09-01, so they look
  back-calculated (unverified).
- **Confirmation start.** The window starts on 10-11, one day after this
  plan. CGI values from 10-07 onward have been seen through H05's shadow log,
  but none of the round-3 decompositions has been computed on them.

No per-provider receipts are used (section 6).

## 3. Variables

Notation:

- 15-minute stamps s, log value v_s.
- 15-minute change r_s = v_s − v_{s−1}.
- Decision points τ are on the full hour, as in H05 and R2-03.

| Symbol | Definition |
|---|---|
| y(τ) | v_{τ+6h} − v_τ (the next 6-hour change) |
| past(τ) | v_τ − v_{τ−6h} = Σ r_s over the 24 stamps in (τ−6h, τ] |
| x_np(τ) | Σ r_s · 1{n_s ≠ n_{s−1}} over the same 24 stamps |
| x_jump(τ) | Σ r_s · 1{\|r_s\| ≥ 0.0025} over the same 24 stamps (25 bp, fixed) |
| x_edge(τ) | log L_τ − log L_{τ−6h}, where L = value − band (H100's lower band edge) |

**Whole-window rule.** A decision point is dropped if any of the following
holds:

- any of the 49 stamps from τ−6h to τ+6h is missing;
- `n_providers` is missing at any stamp needed for x_np;
- `methodology_id` changes anywhere in [τ−6h, τ+6h].

**Jump threshold.** The 25 bp threshold was chosen from the agent's
descriptive quantiles: the median absolute 15-minute change was 1.4 bp
(H100) and 0.4 bp (B200), and the 99th percentile was 149 and 187 bp. That
choice is contaminated and is disclosed. Two other thresholds, 10 bp and
50 bp, are reported descriptively only. They are logged as variants and are
not tested.

## 4. Hypotheses (family of 4, Holm)

Each model is y = a + b·past + c·x, where x is the channel; c is the
coefficient tested.

- With x = x_np or x_jump, c is the difference between the slope on moves
  inside the channel and the slope on all other moves.
- With x = x_edge, c is the extra slope on moves that the band edge shares.

| ID | GPU | Channel x | Mechanism (CGI METHODOLOGY.md) | Expected sign of c |
|---|---|---|---|---|
| R3-01 | H100 | x_np | **R2-02 at 15-minute resolution.** Moves made while seats drop out or return revert. Carried votes and attendance fade the change back (sections 7 and 8). | c < 0 |
| R3-02 | H100 | x_jump | Large 15-minute moves (a cheapest-offer change, a book-median seat, a vote crossing the inter-quantile cut) are partly transient (sections 6 and 7). | c < 0 |
| R3-03 | B200 | x_jump | As R3-02, for B200. | c < 0 |
| R3-04 | H100 | x_edge | A move the pinned band edge does not share is internal to the trimmed vote mean (a vote crossing the 1/3 or 2/3 cut) and reverts. A move the edge shares is a broad repricing and persists (section 7). | c > 0 |

R2-02 also ran on H100 only. B200 gets no x_np test: only 16% of its large
moves sat on an `n_passing` change.

### Test

The model is fitted by OLS on hourly decision points. Overlapping 6-hour
windows are handled with Newey-West errors, lag 12, the same lag as H05 and
R2-03. The test is one-sided in the expected direction.

As in R2-02, c is estimated by Frisch-Waugh-Lovell: x and y are each
residualized on a constant and past, then the univariate HAC slope is taken.
The circular-shift p-value and the block-bootstrap CI are reported beside it.

### Confirmation criteria (fixed now)

- **C1.** The Holm-adjusted one-sided p-value over the 4 tests is at most
  0.05 (`confirm_alpha`).
- **C2.** Coefficients are frozen from the exploration window: the
  two-regressor model (a, b, c) and the past-only model (a′, b′). On the
  confirmation window, the frozen two-regressor forecast must have a lower
  mean squared error than the frozen past-only forecast, so its
  out-of-sample R² against that baseline is above 0. It must also have an
  out-of-sample R² above 0 against a zero forecast.
- **Confirmed** = C1 and C2.

**Sufficiency.** A test that is not sufficient counts as not confirmed. A
test is sufficient only if it has at least:

- 120 decision points;
- 10 distinct 6-hour windows where the channel is non-zero;
- the round-1 minimums `min_nonzero` and `min_events`.

### Meaning of each outcome

| Outcome | Meaning | Next step |
|---|---|---|
| R3-01 confirmed | Part of the reversal comes from CGI's sample measurement | Not a market signal. It makes H05 a forecast of CGI's measurement. That is still what GPU1 would settle on, if GPU1 used CGI, which it does not. |
| R3-02 or R3-03 confirmed | The reversal is concentrated in large moves | The frozen two-regressor forecast joins H05's shadow test from 2027-01-01, 60 sessions, then the D26 gate |
| R3-04 confirmed | Moves inside the trimmed mean revert | Same as R3-02 |
| Nothing confirmed | The cause stays unknown | Say so. Do not re-test these channels on the same window. |

None of these outcomes leads to an order. D26 still holds: rental-price
targets cannot trade before GPU1 and GPU2 list.

### Timing

- The window closes at 2026-12-31 23:45 UTC.
- The confirmation runs once, automatically, in the daily workflow:
  `explore round3 confirmation`, once the window plus 6 hours 10 minutes has
  passed.
- Until then the stage only reports how much data has accumulated. It does
  not compute any statistic on the window.

## 5. Not tested this round

- **H01 re-test on the backfilled listings.** H01 is a 5-day panel test.
  The Zenodo backfill (D48) adds 14 days, 2026-07-05 to 07-18, with 0 to 3
  H100 or B200 price changes a day, almost all from one provider. That is
  too little to test anything, so H01 is not re-run.
- **Time-of-day and weekend splits.** Contaminated by the agent's look.
- **Methodology-version effects.** Only 3 version switches in the window.

## 6. Blocked: per-provider receipts (B12)

The mechanism agent proposed three hypotheses that need CGI's per-provider
receipts: seat prices, weights, filter verdicts and carried votes. They are:

- M1: a weighted seat-deviation signal;
- M2: order-book seats compared with list-price seats;
- M3: weight-driven giveback after a jump.

They would show directly which seats move the index.

Receipts are blocked:

- CGI's LICENSE-DATA says receipts are included "solely for verification and
  provenance". Reading that conservatively, receipts are not used for
  research until Computable confirms otherwise.
- The day-file host `data.getcomputable.com` is not in
  `docs/data_sources.md`.
- The day files carry `restatements` fields, so they may not be
  point-in-time.
- Vast and RunPod seats must be dropped everywhere, which rules out an exact
  recomputation of the index.

This is recorded in `docs/blockers.md` as B12. The owner can ask Computable
whether research use of receipts is permitted.

## 7. Equity hypotheses

None this round (allowed: at most 4; used: 0).

## 8. Variants

Round 3 counts 6 variants:

- 4 tests;
- 2 descriptive thresholds for x_jump.

The project total rises from 225 to 231 (`docs/variants_log.md`).

## 9. Addendum (2026-10-10, before running): what can produce the reversal?

This addendum adds no test on real data and does not touch the confirmation
window. It asks which kinds of mechanism can produce a 6-hour slope near
−0.35 at all.

### 9.1 Derivation: how much of a 6-hour move must be transient

Write the log index as a random walk W plus a stationary transient part T:

- one 6-hour step of W has variance σ²;
- T has variance γ₀;
- ρ is T's autocorrelation at 6 hours.

Past and future are adjacent 6-hour changes, so

  Cov(past, future) = 2γ₆ − γ₀ − γ₁₂,  with γ_k the autocovariance of T.

For T an AR(1) at the 6-hour step (γ₆ = ργ₀, γ₁₂ = ρ²γ₀):

  β = −γ₀(1 − ρ)² / (σ² + 2γ₀(1 − ρ)).

**Bound.** β is never below −1/2. It reaches −1/2 only with no random walk
and transients that die within 6 hours (ρ = 0).

**What β = −0.35 implies.** With ρ = 0 the transient part T must carry
about 70% of the variance of a 6-hour change. With ρ > 0 it must carry
more. The agent's descriptive look found retracement that lasts many hours,
which means ρ > 0.

Standard algebra; see e.g. Campbell, Lo and MacKinlay (1997), *The
Econometrics of Financial Markets*, ch. 2 (variance ratios and
autocorrelation of sums).

### 9.2 Simulation of CGI's aggregation (SYNTHETIC, mechanism check only)

A simulator of the aggregation published in CGI's METHODOLOGY.md, sections
6 and 7:

- each passing seat casts its weight three times, at c − sd, c and c + sd;
- sd is the 3% floor, with a 6% variant;
- the index is the weight-weighted mean of the votes between the 1/3 and
  2/3 cumulative-weight quantiles;
- weights are equal.

**Seats.** 17 (H100-like) and 9 (B200-like). Seat log price is

  p_i,t = m_t + o_i + u_i,t (+ d_i,t).

- **m_t:** a common random walk, σ_m = 0.001 per 15 minutes.
- **o_i:** a fixed offset, drawn from N(0, 0.15²).
- **u_i,t:** an idiosyncratic random walk, σ_u = 0.002 per 15 minutes.
- **d_i,t** (S2 and S3 only): an AR(1) seat deviation with a 3-hour
  half-life. Its stationary sd is 0.03.

**Scenarios.**

| Scenario | Adds |
|---|---|
| S0 | Aggregation only |
| S1 | S0 plus seat drop-outs: each seat is absent with probability 0.02 at each stamp, for one stamp, and not carried. This is the R3-01 channel |
| S2 | S0 plus the transient seat deviations d |
| S3 | S2 plus CGI's 1-hour-half-life EWMA on seat prices (calc_v16) |

**Runs.** 20 seeds per scenario. Each run is 60 days of 15-minute stamps.

**Reported.** The mean and the 5th to 95th percentile across seeds of:

- the hourly 6-hour-on-6-hour slope β;
- the 6-hour variance ratio VR(24);
- the ACF(1) of 15-minute changes.

**Interpretation, fixed now:**

- If S0 and S1 both give mean β in [−0.10, 0], aggregation and drop-outs
  alone cannot produce the observed reversal. The cause must then be
  seat-level price deviations that last hours. Only per-provider receipts
  (B12) can attribute those to seats.
- If S0 or S1 gives mean β ≤ −0.25, the aggregation rule alone can produce
  a reversal of the observed size.
- Anything between is inconclusive.

**Labelling.** Output is built by `compute_curve.synthetic` with
`is_synthetic=True`, written to
`reports/exploration/round3_mechanism_simulation.md` under a SYNTHETIC
banner, and is never presented as a finding about CGI.

### 9.3 Power of the four confirmations

The expected power of each test on the confirmation window is computed
from the exploration window's standard errors, scaled by √(n_explore /
n_confirm). Those standard errors are contaminated estimates, so this is
planning arithmetic only.

**Variants.** None added. No hypothesis test is run on real data. The
project total stays at 231.
