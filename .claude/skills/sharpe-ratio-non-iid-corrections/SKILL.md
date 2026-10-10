---
name: sharpe-ratio-non-iid-corrections
description: >-
  Sharpe ratio inference for non-Normal, serially correlated returns, following
  López de Prado, Lipton & Zoonekynd (2026): variance of the Sharpe estimate with
  skew, kurtosis and AR(1) corrections, PSR, minimum track record length, power,
  pFDR, oFDR, deflated Sharpe and SFDR. Use when testing whether a Sharpe ratio
  from a short or autocorrelated return series is significant, how long a track
  record must be, or what false discovery rate a selected strategy carries.
---

# Sharpe Ratio Non-IID Corrections

> **compute-curve note.** Vendored from terrylica/cc-skills at commit
> `b592ad8d044a` (see `PROVENANCE.md`). CLAUDE.md wins on any conflict: no
> look-ahead, pre-registration before tests, variants logged in
> `docs/variants_log.md` (that log is the trial counter K), bootstrap intervals
> beside every analytic interval, no new dependency without a
> `docs/decisions.md` entry. No implementation is vendored: the upstream Numba
> script, paper PDF and paper transcription were left out. Any function built
> from these formulas goes into `compute_curve` with full type hints, numpy and
> scipy only, and tests that reproduce the Exhibit 1 values below. The formulas
> are asymptotic; with the few dozen observations this repository usually has,
> report them as approximate and say when the sample is too short to conclude
> anything. Do not cite a result from them as a finding until the method is
> derived in `docs/` with the citation.

Generalized Sharpe ratio inference framework for non-Normal, serially correlated
returns, after López de Prado, Lipton & Zoonekynd (2026).

## Paper Metadata

| Field           | Value                                                                         |
| --------------- | ----------------------------------------------------------------------------- |
| **Title**       | How to Use the Sharpe Ratio                                                   |
| **Authors**     | Marcos López de Prado, Alexander Lipton, Vincent Zoonekynd                    |
| **Series**      | ADIA Lab Research Paper Series, No. 19                                        |
| **Date**        | March 7, 2026                                                                 |
| **SSRN**        | 5520741                                                                       |
| **Replication** | <https://github.com/zoonek/2025-sharpe-ratio> (no licence file; read only)    |

The authors' replication repository titles SSRN 5520741 "Sharpe Ratio
Inference: A New Standard for Reporting and Decision-Making". The title and
date above are as upstream gives them and are unverified here; check the SSRN
page before citing.

## References

| Topic                               | Reference File                                             |
| ----------------------------------- | ---------------------------------------------------------- |
| Equation map (paper equation, page) | [equation-map.md](./references/equation-map.md)            |

## Preflight: Experimentation Context Assessment (CRITICAL)

Before computing DSR or SFDR, assess the experimentation context to determine
the correct parameters. These inputs require judgment that cannot be derived
from code alone. In compute-curve, fix them in the pre-registration, before the
statistic is computed.

### Decision: DSR vs SFDR

| Situation                                                                 | Use      | Why                                                      |
| ------------------------------------------------------------------------- | -------- | -------------------------------------------------------- |
| You have return series for all K strategies tested                        | **DSR**  | Can compute K_eff from eigenvalues of correlation matrix |
| Strategy is the survivor of a long, unrecoverable experimentation history | **SFDR** | K is unknowable; SFDR sets a threshold without needing K |
| Evaluating a single strategy with no selection involved                   | **PSR**  | No multiple-testing correction needed (K=1)              |

**compute-curve default:** K is recoverable, because every variant is logged in
`docs/variants_log.md`. Use **DSR** with that K (or K_eff when the variants'
return series exist). Report SFDR only as a sensitivity check, with its prior
stated.

### Parameters Requiring Judgment

| Parameter                                                       | What to assess                                                                          | How to assess it                                                                                                    |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **P[H₁]** (prior: fraction of genuine strategies)               | "Out of all ideas ever tried in this project, what fraction were genuinely profitable?" | Count ideas tried and confirmed in `docs/variants_log.md` and the exploration reports. Conservative default: **0.05**. |
| **SR₁** (alternative: what a real strategy's Sharpe looks like) | "When a strategy IS real, what Sharpe does it typically achieve?"                       | Published benchmarks for the asset class, stated per observation period. Label it as an assumption.                  |
| **q** (false discovery tolerance)                               | "What false positive rate can I tolerate?"                                              | Research: **0.05**. Exploratory screening: **0.10**.                                                                 |
| **γ₃, γ₄, ρ** (return distribution shape)                       | Skewness, Pearson kurtosis, lag-1 autocorrelation                                       | Compute directly from the return series under evaluation, using only data available at the decision time.           |
| **T** (sample length)                                           | Number of return observations                                                           | Count from data.                                                                                                     |

### Preflight Checklist

1. **Identify the evaluation context**: Is this a single new strategy, a fold comparison, or a survivor from a search?
2. **Determine DSR vs SFDR**: If return series for all candidates exist → DSR with K_eff. Otherwise → DSR with K from the variants log.
3. **Elicit P[H₁]**: From the variants log and exploration reports. If unknowable, use 0.05.
4. **Estimate SR₁**: From published benchmarks; label it unverified.
5. **Set q**: Based on the decision's consequence.
6. **Compute objective parameters**: γ₃, γ₄, ρ, T directly from the return series.
7. **Report the assessment**: State all parameter choices and reasoning before computing, so the user can override.

### Example Preflight Output (illustrative; the numbers are the paper's Exhibit 1)

```
SFDR Preflight Assessment:
  Context:    Survivor of a search whose full history is not recoverable
  Method:     SFDR
  P[H₁]:     0.05 (conservative)
  SR₁:       0.4 (assumed alternative, per observation period)
  q:         0.05 (research-grade threshold)
  γ₃:        -2.448 (computed from return series)
  γ₄:        10.164 (Pearson kurtosis, computed from return series)
  ρ:         0.20 (lag-1 autocorrelation, computed from return series)
  T:         24 months
  → SFDR threshold: SR_c = 0.862
  → Observed SR: 0.456
  → VERDICT: FAIL (observed SR below SFDR threshold)
```

compute-curve check: upstream printed SR_c = 0.760 here. Solving
pFDR(SR_c) = q with the formulas below and these inputs gives 0.862 (numpy and
scipy, 2026-10-10), and no nearby combination of the inputs gives 0.760, so the
upstream figure is treated as unverified. The verdict is the same either way.
For some inputs pFDR never falls to q (for example ρ=0 with SR₁=0.4 here): then
no SFDR threshold exists, and a root finder must report that rather than return
a bracket end.

The user may override any parameter. If they disagree with P[H₁] or SR₁, recompute with their values.

## Key Formulas

All equations use the paper's non-IID variance (Eq 2-3) with Pearson kurtosis
convention (γ₄=3 for Gaussian). SR is per observation period, not annualized.

| Eq    | Name        | Formula                                                            | Suggested function      |
| ----- | ----------- | ------------------------------------------------------------------ | ----------------------- |
| 2-3   | SR Variance | V[SR̂] = (1/T)·(a − b·γ₃·SR + c·(γ₄−1)/4·SR²)                       | `sr_variance()`         |
| 9     | PSR         | Φ((SR̂ − SR₀) / σ[SR₀])                                             | `psr()`                 |
| 11    | MinTRL      | (a − b·γ₃·SR₀ + c·(γ₄−1)/4·SR₀²) · (z\_{1−α}/(SR̂−SR₀))²            | `min_trl()`             |
| 13    | Critical SR | SR₀ + σ[SR₀]·z\_{1−α}                                              | `critical_sr()`         |
| 15    | Power       | 1 − Φ((SR_c − SR₁) / σ[SR₁])                                       | `power()`               |
| 17    | β (Type II) | Φ((z\_{1−α}·√(a(ρ)) − SR₁·√T) / √(a − b·γ₃·SR₁ + c·(γ₄−1)/4·SR₁²)) | `power()` → `1 - power` |
| 21    | pFDR        | (1 + (1−β)·P[H₁]/(α·P[H₀]))⁻¹                                      | `pfdr()`                |
| 24    | oFDR        | p·P[H₀] / (p·P[H₀] + (1−Φ[z*(SR₁)])·P[H₁])                         | `ofdr()`                |
| 28    | E[max SR]   | SR₀ + √V · ((1−γ)·Φ⁻¹[1−1/K] + γ·Φ⁻¹[1−1/(Ke)])                    | `expected_max_sr()`     |
| 29-31 | DSR         | PSR with SR₀ = E[max{SR̂_k}], σ = √V[max{SR̂_k}]                     | `dsr()`                 |
| 32-33 | SFDR        | Find SR_c such that pFDR(SR_c) = q                                 | `sfdr_threshold()`      |

Where a = (1+ρ)/(1−ρ), b = (1+ρ+ρ²)/(1−ρ²), c = (1+ρ²)/(1−ρ²) are AR(1)
variance coefficients, γ is the Euler-Mascheroni constant, and V in Eq 28 is
the variance of the Sharpe estimates across the K trials.

## Numerical Example (Paper Exhibit 1)

Hedge fund: T=24 months, γ₃=−2.448, γ₄=10.164 (Pearson), SR=0.036/0.079≈0.456, ρ=0.2.
Use these as test vectors for any implementation. The rows marked † were
recomputed independently with numpy and scipy on 2026-10-10 and agree to three
decimals.

| Quantity             | Equation | Value             | Notes                                           |
| -------------------- | -------- | ----------------- | ----------------------------------------------- |
| σ[SR̂] (non-Gaussian) | Eq 3     | **0.379** †       | vs 0.214 Gaussian — 77% wider                   |
| PSR (SR₀=0)          | Eq 9     | **0.966** †       | Still significant despite wider CI              |
| PSR (SR₀=0.1)        | Eq 9+5   | **0.900** †       | Harder benchmark reduces confidence             |
| MinTRL (SR₀=0)       | Eq 11    | **19.543** months † | T=24 > 19.5 → sufficient                      |
| MinTRL (SR₀=0.1)     | Eq 11    | **39.369** months † | More than doubles for SR₀ closer to SR̂        |
| β (power, SR₁=0.5)   | Eq 17    | **0.411** †       | vs 0.224 IID Normal — 84% higher                |
| pFDR (P[H₁]=0.1)     | Eq 21    | **0.433** †       | 43.3% false discovery when true strategies rare |
| oFDR (SR₁=0.5)       | Eq 24    | **0.361** †       | Even 3.4% p-value → 36% observed FDR            |
| Power (1−β)          | Eq 15    | **0.589** †       | Low for 24-month track record                   |

## Related Skills

| Skill                                                         | Relationship                                                                    |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| [quant-research](../quant-research/SKILL.md)                  | Trial counting, effective sample size, simplified deflated Sharpe, PBO          |
| [compute-curve-research](../compute-curve-research/SKILL.md)  | Pre-registration, time splits, multiple testing and reporting rules (start here) |
