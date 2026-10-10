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

## 5. Variants

- Round 3 adds 6: 4 confirmation tests and 2 descriptive thresholds.
- The project total is 231.
