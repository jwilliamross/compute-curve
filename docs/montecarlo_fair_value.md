# Monte Carlo fair value of GPU1/GPU2 (monthly-average futures)

_2026-10-10. Derivation for `compute_curve.models.montecarlo`. This is a
model-building and engine document. It contains no hypothesis test, and its
proxy calibration is illustrative (D55)._

## 1. Why a Monte Carlo engine

GPU1 and GPU2 settle on the **arithmetic average** of the daily index over
the business days of the contract month (docs/contract_specs.md). Two things
follow from that.

**1. No storage, so no cash-and-carry arbitrage.**

- An unused GPU-hour cannot be stored, just as a megawatt-hour of electricity
  cannot.
- So the futures price is not pinned to spot by a financing argument.
- Under a pricing measure Q, F(t, M) = E^Q[A_M | F_t], with
  A_M = (1/N) Σ_{d∈M} S_d.
- The futures price is the market's expectation of the monthly average plus
  a risk premium. A model's real-world expectation E^P[A_M] gives a
  reference level. A quote far from that level is either a risk premium or
  information the model lacks. It is **not** automatically a mispricing.
  Power markets such as PJM West Hub monthly futures behave the same way.

**2. The average has no simple distribution.**

- A sum of lognormals is not lognormal.
- The expectation is analytic: E[A] = (1/N) Σ exp(m_d + v_d/2), already in
  `expected_average_level`.
- Quantiles, value-at-risk and the price of an option on the average
  (an "Asian" option) are not analytic. Monte Carlo provides them.

## 2. Model (Schwartz and Smith 2000, as in docs/term_structure_model.md)

  ln S_t = g(t) + χ_t + ξ_t,  g(t) = −δ t
  dχ = −κ χ dt + σ_χ dZ_χ          (short-term deviation, mean-reverting)
  dξ = μ_ξ dt + σ_ξ dZ_ξ + J dN    (long-term level, scheduled launch jumps)
  dZ_χ dZ_ξ = ρ dt

### Exact simulation over a step Δ

- χ_{t+Δ} = e^{−κΔ} χ_t + ε_χ, with Var ε_χ = σ_χ²(1 − e^{−2κΔ})/(2κ).
- ξ_{t+Δ} = ξ_t + μ_ξ Δ + ε_ξ, with Var ε_ξ = σ_ξ² Δ.
- Cov(ε_χ, ε_ξ) = ρ σ_χ σ_ξ (1 − e^{−κΔ})/κ.
- A scheduled jump adds N(m_J, s_J²) to ξ on its day.

There is no discretization bias: this is the same transition as
`schwartz_smith.transition`.

### Covariance of ln S between two dates s ≤ t, from a known state at 0

- Cov(χ_s, χ_t) = σ_χ² e^{−κ(t−s)} (1 − e^{−2κs}) / (2κ)
- Cov(ξ_s, ξ_t) = σ_ξ² s + s_J² · #jumps in (0, s]
- Cov(χ_a, ξ_b) = ρ σ_χ σ_ξ e^{−κa} (e^{κ min(a,b)} − 1) / κ

Cov(ln S_s, ln S_t) is the sum of the χχ and ξξ terms and both cross terms,
Cov(χ_s, ξ_t) + Cov(χ_t, ξ_s). With scheduled jumps of normal size, the
vector (ln S_d) over the averaging days is jointly Gaussian.

## 3. Control variate (Kemna and Vorst 1990; Glasserman 2004, §4.1)

The geometric average G = exp((1/N) Σ ln S_d) is lognormal:

- m_G = (1/N) Σ m_d;
- v_G = (1/N²) Σ_{d,e} Cov(ln S_d, ln S_e);
- E[G] = exp(m_G + v_G/2).

The controlled estimator of E[A] is

  Â = mean(A) − ĉ (mean(G) − E[G]),  ĉ = Cov(A, G) / Var(G).

A and G are almost perfectly correlated over a month of daily values, so the
variance falls by orders of magnitude. The same control prices an Asian call:

- payoff (A − K)⁺;
- control (G − K)⁺, whose expectation is a Black-style closed form.

Paths are also antithetic, with shocks Z and −Z.

## 4. What the engine reports per contract month

- **Mean of A.** Both the Monte Carlo estimate with its standard error, and
  the analytic E[A] as a check.
- **Distribution of A.** The 5, 25, 50, 75 and 95% quantiles.
- **Value-at-risk.** The 95% one-sided loss of one long contract held to
  settlement against a futures price F: 730 GPU-hours × (F − A) at the 5%
  quantile of A.
- **Asian calls.** E[(A − K)⁺] at chosen strikes, undiscounted and real-world.
  This is a model value, not a market price.

## 5. Proxy calibration (illustrative only)

The settlement index's history cannot be stored (B7). The engine is therefore
calibrated on proxies, and every output is labelled MODEL OUTPUT ON A PROXY.

- **Short-term factor (κ, σ_χ).** The CGI daily close, in log terms with a
  linear trend removed, fitted as AR(1) with exact OU mapping:
  - b = e^{−κΔ};
  - σ_χ² = Var(e) · 2κ / (1 − b²).
- **Long-term factor (μ_ξ, σ_ξ).** The GetDeploying weekly median, from its
  log changes. This is an approximation: weekly changes still contain some
  short-term noise.
- **Other parameters.** ρ = 0, δ = 0 and no launch jumps unless stated.
- **Reporting.** The strip is reported as F/S₀, the fair value relative to
  today's spot. It can then be applied to the settlement index's level once
  that is known.
- **Model risk.** A random-walk scenario (no mean reversion) is reported
  beside the fitted one. The gap between the two is the model risk.

## References

- Schwartz, E. and Smith, J. E. (2000). Short-term variations and long-term
  dynamics in commodity prices. *Management Science* 46(7), 893–911.
- Kemna, A. G. Z. and Vorst, A. C. F. (1990). A pricing method for options
  based on average asset values. *Journal of Banking and Finance* 14(1),
  113–129.
- Glasserman, P. (2004). *Monte Carlo Methods in Financial Engineering*.
  Springer, chapter 4 (variance reduction).
- Benth, F. E., Šaltytė Benth, J. and Koekebakker, S. (2008). *Stochastic
  Modelling of Electricity and Related Markets*. World Scientific. Covers
  non-storable commodities, futures with delivery periods, and the risk
  premium.
