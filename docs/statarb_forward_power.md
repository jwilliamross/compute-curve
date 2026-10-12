# Claim 6c forward test: how much can 60 sessions tell us?

_2026-10-12. A design calculation on already-spent confirmation data. It
tests no hypothesis and computes no forward-session statistic (4 forward
sessions existed, none evaluated). Code: `compute_curve.statarb.power`;
output: `reports/statarb/forward_power.md` (`compute-curve statarb power`).
Decision: D57._

## 1. Question

The 60-session forward shadow test (docs/statarb_plan3.md, sections 6 and 7)
decides whether SA2-M or SA2-L goes forward. Before any forward result
exists: if the edge is real, how likely is the test to pass? And if there is
no edge, how likely is it to pass by luck?

## 2. Method

- **Input.** The four pooled daily net-return series of the one-shot
  confirmation (SA2-M, SA2-L × engine weights, fixed shares; 157 sessions),
  rebuilt from cached bars exactly as `confirm_strategy` pools them. The
  rebuild reproduces the recorded means (10.56 and 4.93 bps a day).
- **Scenarios.** Each series is shifted so its true mean is θ × the observed
  mean, θ ∈ {0, 0.25, 0.5, 0.75, 1}. The stress series gets the same shift,
  so the cost gap is unchanged. θ = 1 is optimistic: the confirmation's mean
  is itself the best of a selection and fell to about 1 bp a day without its
  5 best days.
- **Resampling.** A joint circular block bootstrap (block 20, the project's
  `boot_block`), with the same indices for all four series. This keeps
  volatility, fat tails, serial correlation and the correlation between
  strategies and accountings. 2,000 resamples per cell, seed 20261005.
- **Rule.** The frozen forward rule on each resample:
  - one-sided Newey-West p (lag 10);
  - Holm over the 2 strategies within each accounting, at 0.05;
  - mean > 0 and stress mean > 0;
  - a pass under **both** accountings (D56).
- **Lengths.** 60 (declared), 120 and 250 sessions.

Holm is computed locally (`power.holm`). It equals `claim4.stats.holm` (a
test checks this); the statsmodels version runs `gc.collect` on every call,
too slow for 120,000 resamples.

## 3. Results

P(forward pass under both accountings):

| Sessions | Strategy | θ = 0 | 0.25 | 0.5 | 0.75 | 1 |
|---|---|---|---|---|---|---|
| 60 | SA2-M | 0.015 | 0.042 | 0.093 | 0.167 | 0.279 |
| 60 | SA2-L | 0.057 | 0.097 | 0.151 | 0.227 | 0.301 |
| 120 | SA2-M | 0.006 | 0.041 | 0.118 | 0.273 | 0.493 |
| 120 | SA2-L | 0.043 | 0.098 | 0.170 | 0.275 | 0.393 |
| 250 | SA2-M | 0.004 | 0.045 | 0.224 | 0.562 | 0.845 |
| 250 | SA2-L | 0.036 | 0.099 | 0.221 | 0.411 | 0.602 |

Monte Carlo standard error: at most about 0.011 per cell.

## 4. What this means

1. **The 60-session test is badly underpowered.** Even if SA2-M's full
   confirmation edge persists, it passes only about 28% of the time. At half
   the edge, about 9%. A fail at 60 sessions is therefore weak evidence
   against the edge, not a refutation.
2. **A pass at 60 sessions would be strong evidence.** With no edge, SA2-M
   passes about 1.5% of the time.
3. **SA2-L's test is slightly oversized.** With no edge it passes about 5.7%
   of the time at 60 sessions, above the nominal 5%. That is the
   Newey-West t on short, fat-tailed samples. One more reason to treat SA2-L
   as borderline.
4. **About 250 sessions (a year) are needed** for good power on SA2-M, and
   only if most of the edge is real.

## 5. A caveat on the confirmation itself

The confirmation's significance leans on negative serial correlation in the
daily book returns:

| Series | t (iid) | t (Newey-West) | t (5/10/20-day block means) | Σ autocorrelations, lags 1-10 |
|---|---|---|---|---|
| SA2-M (weights) | 1.42 | 2.30 | 2.19 / 2.38 / 2.08 | −0.39 |
| SA2-M (shares) | 1.43 | 2.35 | 2.28 / 2.40 / 2.46 | −0.45 |
| SA2-L (weights) | 1.37 | 1.66 | 1.52 / 1.71 / 1.32 | −0.27 |
| SA2-L (shares) | 1.26 | 1.58 | 1.40 / 1.52 / 1.14 | −0.28 |

- An iid t of 1.42 would give a one-sided p of about 0.08, which fails.
- The non-overlapping block-mean t-statistics agree with Newey-West, so the
  standard error is not a coding artefact. A reversal book can plausibly
  have negatively autocorrelated daily P&L: a loss today often means a
  wider spread that pays back as it closes.
- But each autocorrelation has a standard error of about 0.08 at 157
  sessions. Whether the negative dependence persists is itself unverified.
  The forward test uses the same Newey-West rule, so it inherits this.

## 6. Decision (D57)

Fixed now, before any forward-session statistic is computed:

- **The 60-session test runs unchanged** and is reported as declared.
- **Interpretation.** A 60-session fail is reported as "not confirmed at 60
  sessions (power about 0.28 even at the full edge)". It is not reported as
  evidence that the edge is absent.
- **Extension (SA2-M only).** The same frozen rule on the first **250**
  forward sessions from 2026-10-06 (to about 2027-10-01):
  `compute-curve statarb forward-extended`, run daily by the workflow. Both
  strategies are computed under the same Holm family, but only SA2-M's
  verdict counts. SA2-L gets no second chance; its 60-session test is
  already oversized.
- **Paper-trading precondition (docs/statarb_paper_readiness.md).** SA2-M
  passes either at 60 sessions or at 250, plus the owner's written approval.
  With no edge, the chance of either pass is at most about 1.9% (union
  bound on the bootstrap null).
- **Variants.** +2: this power calculation (descriptive) and the extension
  (1 test). Project total 297.

## References

- Newey, W. K. and West, K. D. (1987). A simple, positive semi-definite,
  heteroskedasticity and autocorrelation consistent covariance matrix.
  *Econometrica* 55(3), 703–708.
- Politis, D. N. and Romano, J. P. (1992). A circular block-resampling
  procedure for stationary data. In *Exploring the Limits of Bootstrap*,
  Wiley, 263–270.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure.
  *Scandinavian Journal of Statistics* 6(2), 65–70.
