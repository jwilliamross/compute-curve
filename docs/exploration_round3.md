# Exploration round 3: what drives the CGI reversal (interim report)

_2026-10-10. The plan is `docs/exploration_round3_plan.md` (commit 80aaaa7), and it
was committed before any round-3 statistic was computed. This report covers
the exploration window only. The one-shot confirmation runs automatically
once the CGI window 2026-10-11 to 12-31 is complete (on or after 2027-01-01
05:55 UTC). Until then nothing is confirmed._

## 1. Bottom line

- **No finding yet.** The exploration window is contaminated (D49), so its
  numbers count for nothing.
- **R2-02 was followed up, not ignored.** It was re-specified at 15-minute
  resolution as R3-01, the provider-count channel. It still shows nothing:
  c = −0.002, one-sided p 0.50. Moves made while CGI's seat count changes
  revert no more than other moves. The hourly sampling in R2-02 was a real
  flaw, but fixing it did not reveal an effect.
- **The jump story weakens in a joint model.** A research agent's
  descriptive look suggested the reversal sits in large 15-minute jumps.
  Here jumps and other moves are put in one model, with the past move as a
  control, and jumps do not revert significantly more:
  - H100: c −0.16, p 0.18;
  - B200: c is +0.15, the wrong sign.
- **What this leaves.** The reversal looks broad-based across the past
  6-hour move, not tied to a channel visible in the index. It is
  consistent with CGI's own aggregation (EWMA of seat prices, weights
  recomputed every 15 minutes) acting on all moves. That cannot be tested
  without per-provider receipts, which are blocked (B12).

## 2. Exploration window (EXPLORATORY, contaminated)

Setup:

- CGI first-observed vintages, published within 15 minutes;
- stamps 2026-09-01 00:15 to 09-24 23:45 UTC;
- hourly decision points;
- whole-window rule: no missing stamp and no methodology change in
  [τ−6h, τ+6h].

How to read the table:

- Model: y = a + b·past + c·x.
- c is estimated by Frisch-Waugh-Lovell with Newey-West errors (lag 12).
- p is one-sided in the pre-registered direction.
- The CI is a block-bootstrap 95% interval for corr(x, y) after FWL.
- Costs do not apply: these are forecasts of an index, not trades.

| ID | GPU | Channel | n | Events | Channel windows | c | t | p | Circular-shift p | corr CI | Past-only slope |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R3-01 | H100 | n_passing changes | 539 | 189 | 59 | −0.002 | −0.01 | 0.496 | 0.985 | [−0.19, 0.16] | −0.350 |
| R3-02 | H100 | jumps ≥ 25 bp | 539 | 214 | 61 | −0.157 | −0.92 | 0.180 | 0.257 | [−0.27, 0.11] | −0.350 |
| R3-03 | B200 | jumps ≥ 25 bp | 551 | 291 | 54 | +0.151 | 1.22 | 0.888 | 0.531 | [−0.02, 0.12] | −0.347 |
| R3-04 | H100 | lower band edge | 539 | 401 | 38 | +0.020 | 0.31 | 0.379 | 0.723 | [−0.11, 0.15] | −0.350 |

**Two descriptive jump thresholds, not tested.** At 10 bp, c is −0.08 for
H100 and +0.05 for B200. At 50 bp it is −0.06 and +0.08. No threshold gives
a strong jump effect.

### Frozen slopes (from reports/exploration/round3_frozen.json)

The frozen fit splits the past move into jump and non-jump parts:

| GPU | Non-jump moves (b) | Jump moves (b + c) |
|---|---|---|
| H100 | −0.24 | −0.40 |
| B200 | −0.49 | −0.34 |

Both parts revert for both GPUs.

**Why this differs from the agent's descriptive look.** The agent zeroed
the largest 1% of moves and found the remaining slope near 0 for B200. That
was a one-variable slope. Here both parts are in one model, and the
mechanism notes say jumps are followed by a slow partial giveback inside
the same window. That makes the two parts negatively correlated. A
one-variable slope on either part then mixes the two effects, and the joint
model separates them. This explanation is unverified.

## 3. What happens next

- **2027-01-01.** The daily workflow runs `explore round3 confirmation` once
  the window is complete. It applies:
  - C1: the Holm-adjusted one-sided p over the 4 tests is at most 0.05;
  - C2: the frozen two-regressor model beats the frozen past-only model and
    a zero forecast out of sample.

  Each test runs once. Until then the stage reports only how many stamps
  have accumulated.
- **Power is low.** The exploration window's effects are small, so a
  confirmation is unlikely. A failure will be reported as such, and these
  channels will not be re-tested on the same window.
- **H05 and R2-03 are unaffected.** Their forward test and confirmation
  continue as planned. Round 3 asks only why the reversal happens.

## 4. Data gathered this round

- **gpurentalprices.com backfill from Zenodo** (D48): 14 days,
  2026-07-05 to 07-18, CC BY 4.0, md5-checked, one request. The days fall
  before the listing split, so earlier rounds are unchanged.
- **Daily collection continues on every turn:**
  - the UserPromptSubmit hook;
  - a manual snapshot each work session;
  - the daily workflow.
- **The data-source agent found no free H100/B200 price history older than
  2026-07-05.** New candidates, which collect from today forward, are listed
  in docs/data_sources.md under "Candidates (2026-10-10)".

## 6. Addendum: what can produce the reversal (plan section 9)

Pre-registered in commit 5caf536 before running. No real data is tested
here and the confirmation window is untouched.

### 6.1 How much of a 6-hour move must be transient (derivation)

Model the log index as a random walk plus a stationary transient part. The
6-hour-on-6-hour slope is then

  β = −γ₀(1 − ρ)² / (σ² + 2γ₀(1 − ρ)),

where:

- σ² is the random walk's variance over 6 hours;
- γ₀ is the transient part's variance;
- ρ is the transient part's 6-hour autocorrelation.

β cannot go below −0.5. For β ≈ −0.35, at least about 70% of the variance
of a 6-hour CGI change must be transient.

### 6.2 Simulation of CGI's vote rule (SYNTHETIC)

Full table: `reports/exploration/round3_mechanism_simulation.md`.

CGI's published vote rule is applied to simulated seat prices:

- three votes per seat at c ± sd;
- the weighted mean of the middle third of the votes.

20 seeds × 60 days per row, ranges across seeds in brackets.

| Scenario | β, 17 seats | β, 9 seats | VR(24) | ACF(1) of 15-min changes |
|---|---|---|---|---|
| S0 vote rule only, seats are random walks | −0.02 [−0.08, 0.06] | −0.02 [−0.09, 0.08] | ≈ 1.0 | ≈ 0 |
| S1 + one-stamp seat drop-outs (2% per seat per stamp) | −0.38 [−0.42, −0.32] | −0.40 [−0.46, −0.33] | 0.05 | −0.50 |
| S2 + seat price deviations lasting hours (3h half-life) | −0.31 [−0.35, −0.26] | −0.34 [−0.39, −0.30] | 0.57 | −0.03 |
| S3 = S2 + CGI's 1-hour EWMA | −0.20 [−0.26, −0.15] | −0.24 [−0.30, −0.19] | 5.5 | +0.79 |

The sd floor (3% or 6%) made no material difference; the rows above are
the 3% runs.

**Pre-registered reading, reported as written.** The rule printed "the
aggregation rule alone can produce a reversal of the observed size" for
every panel. That wording is misleading:

- It was triggered by **S1 (seat drop-outs)**, because the rule grouped S0
  and S1.
- The vote rule on its own (S0) produces **no** reversal.
- The rule is not changed after the fact. This paragraph explains it.

**What the simulation shows (synthetic, so a mechanism check rather than a
finding):**

1. **CGI's construction is not the cause.** A trimmed vote mean of seats
   whose prices are random walks has no reversal.
2. **Two mechanisms can each produce a reversal of the observed size.**
   They leave different fingerprints:
   - **Drop-outs (S1).** Moves at stamps where the seat count changes
     reverse at once. 15-minute changes then have ACF(1) near −0.5. This is
     exactly the channel R3-01 measures.
   - **Seat price deviations lasting hours (S2).** The reversal is
     broad-based, with ACF(1) near 0 before smoothing. With CGI's EWMA the
     ACF(1) turns strongly positive while the 6-hour reversal remains (S3).
3. **Comparison with real CGI** (descriptive, contaminated exploration
   window):
   - R3-01's coefficient was −0.002. Moves at seat-count changes did not
     reverse more than other moves.
   - After CGI added the EWMA on 2026-09-15, the ACF(1) of 15-minute changes
     flipped from about −0.3 to +0.16 (H100) and +0.25 (B200), and the
     6-hour reversal persisted.

   Both fit S2/S3 better than S1.

**Current best explanation.** Seat-level price deviations that last hours
are the explanation most consistent with all of the above: a cheaper
listing appearing for a while, or order-book noise. **Unconfirmed.** Only
CGI's per-provider receipts could attribute them to seats, and those are
blocked (B12). Asking Computable is now the most useful single step for
this question.

### 6.3 Power of the four confirmations

These are planning numbers only:

- standard errors come from the contaminated exploration window, scaled to
  about 1,950 confirmation points;
- the effect sizes are the exploration estimates.

| Test | Exploration c | Expected SE on confirmation | Power (α 0.0125, first Holm step) | 80%-power MDE |
|---|---|---|---|---|
| R3-01 | −0.002 | 0.081 | 0.01 | 0.25 |
| R3-02 | −0.157 | 0.090 | 0.31 | 0.28 |
| R3-03 | +0.151 (wrong sign) | 0.066 | 0.00 | 0.20 |
| R3-04 | +0.020 | 0.034 | 0.05 | 0.11 |

A confirmation is unlikely; only R3-02 has a real chance. A null result
on 2027-01-01 will be read as "no evidence", not "no effect".

## 5. Variants

- Round 3 adds 6: 4 confirmation tests and 2 descriptive thresholds.
- The project total is 231.
