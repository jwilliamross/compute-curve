# Claim 10: modern strategies on the SA2 universe (results)

_2026-10-16. Plan: docs/modern_plan.md (commit 5abf008, written before any return).
Exploration frozen in commit f5cd828 before the confirmation ran. Full tables:
`reports/statarb/modern/exploration.md` and `confirmation.md`. Simulation only:
no orders._

## Bottom line

**None of the four modern ideas beat plain SA2-M, and none passed its one-shot
confirmation.**

- Three of the seven variants survived the lenient exploration screen: MX2a,
  MX2b and MX3-k2.
- All three failed the Holm-corrected confirmation.
- The simple strategy already trading on paper remains the best thing we have.

| Strategy | Idea | Exploration mean (bps/day), p | Confirmation mean (bps/day), raw p → Holm p | Verdict |
|---|---|---|---|---|
| SA2-M (reference) | Residual reversal vs XLK | +1.66 | +11.17 | Frozen; paper trading |
| MX1 | Volatility-managed SA2-M (Moreira–Muir) | Alpha −0.6 bps, p 0.81 | Alpha +0.1 bps, p 0.46 | Stops: adds nothing |
| MX2a | Reversal on **quiet** (low-volume) moves only | +2.84, p 0.098 | +6.94, 0.036 → 0.107 | Not confirmed (closest) |
| MX2b | **Momentum** on loud (high-volume) moves (Medhat–Schmeling) | +4.62, p 0.078 | −2.88, 0.74 | Not confirmed; sign flipped |
| MX3-k1/k2/k3 | Residuals on 1–3 statistical factors (Avellaneda–Lee PCA) | +0.33 / +2.15 / +1.63 | +2.43 / +3.21 / +0.97 | k2 not confirmed; k1 and k3 stop |
| MX4 | Walk-forward ridge forecast, 7 features (Gu–Kelly–Xiu) | IC 0.033 vs baseline 0.055 | IC 0.020 vs baseline 0.100 | Fails "baselines first" in both windows |

**Costs** (ASSUMPTIONS):

- per symbol, half the median quoted spread plus 2 bps per side;
- a 1 bp sell fee and 3% a year borrow;
- stress case: costs ×2 and borrow at 10% a year.

Books are pooled weights, as the paper account holds them. 95% bootstrap Sharpe
intervals are in the report tables.

## What each result says

**1. Volatility management (MX1) does not help a reversal strategy here.**

- Scaling down after volatile weeks cut exposure exactly when reversal paid.
- Nagel (2012) predicts this: reversal is paid for providing liquidity, and it
  pays most when markets are stressed.
- The Moreira–Muir alpha is about zero in both windows.

**2. Volume matters, but not robustly (MX2).**

- **Exploration.** Quiet-move reversal (MX2a) earned about three times SA2-M's
  return per unit of gross exposure. This is descriptive: 2.84/0.18 against
  1.66/0.31 bps per unit.
- **Confirmation.** The two were equal: about 21 against 22 bps per unit.
- **MX2b, loud-move momentum.** It made +4.6 bps a day in 2024–25, then lost
  2.9 bps a day in 2026. Medhat and Schmeling's short-term momentum did not
  carry over to 2026's AI selloff.
- **Reading.** "Quiet moves revert" is the more plausible half. It was the
  closest to passing (raw p 0.036), but after Holm it is not a finding.

**3. Statistical factors (MX3) did worse than the plain XLK hedge.**

- k = 1 is roughly "the AI trade". Removing it removed some of what SA2-M
  earns.
- k = 2 was best in both windows, but far from significant.

**4. Machine learning (MX4) lost to its own naive baseline.**

- The ridge model's rank IC (0.02–0.03) was below that of the single feature
  "minus the last 5 days' residual return" (0.05, then 0.10).
- With 20 names and about 300 training days, seven features add noise to one
  good signal.
- This is the "baselines first" rule doing its job: the model is not used.

## What it means for trading

- **SA2-M stays as it is.** No overlay improved it out of sample, so nothing
  changes on the paper account.
- **The edge is simple short-term reversal against the sector.** Every
  elaboration either matched it or diluted it.
- **What remains a risk:** SA2-M's 2026 strength is regime-dependent. MX2b's
  sign flip shows how fast a neighbouring effect can reverse.

## Forward shadow (running)

- `compute-curve statarb lab` runs nightly. It writes
  `reports/statarb/lab/latest.md`: every MX book's simulated return since
  2026-10-19, next to SA2-M.
- Because nothing was confirmed, these numbers are descriptive only and decide
  nothing.
- After 60 sessions, about mid-January 2027, the lab writes a one-time
  `forward.md`.

## Variants

- **Declared in the plan: 8.** MX1, MX2a, MX2b, MX3 with k = 1–3, MX4 and
  MX4's IC gate.
- **Post-hoc and descriptive: 1.** The return-per-unit-gross comparison in
  point 2.
- **Project total: 350.**
