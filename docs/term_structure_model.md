# Term-structure model: derivation

Code: `src/compute_curve/models/schwartz_smith.py` and
`src/compute_curve/models/term_structure.py`. Research notes with sources:
`docs/audit/2026-10-05_contract_and_literature.md`.

## 1. Sources and what each contributes

| Reference | Read? | Used for |
|---|---|---|
| Schwartz, E. and Smith, J. E. (2000), "Short-Term Variations and Long-Term Dynamics in Commodity Prices", *Management Science* 46(7):893-911, doi:10.1287/mnsc.46.7.893.12034 | Yes, the author-hosted PDF | The two-factor model, futures formula (eq. 9), state-space form (eqs. 14-16) |
| Bandi, F. M. and Su, Y. (2026), "(Early) AI Compute Asset Pricing", arXiv:2607.12156 (v3) | Yes, full PDF | Non-storability; futures as expected spot minus a risk premium; synthetic futures from term-rental curves. It contains **no** state-space, depreciation or launch-jump model |
| Assody, A. (2026), "Pricing Compute Futures: Forward Curve and Volatility for a Non-Storable, Depreciating Commodity", SSRN 6926798 | Abstract only (Crossref); ssrn.com blocks automation | The idea of Schwartz-Smith plus scheduled launch jumps; prior jump size about -0.22 log per generation; incumbent depreciation 15-20% a year |
| Lee, S. J. and Nagaraj, S. (2026), "Pricing, Hedging, and Securitizing AI Compute", SSRN 7342241 | Abstract only | Seasonal Schwartz-Smith with upward spikes; not used |

The brief attributed the launch-jump model to arXiv 2607.12156. That paper
does not contain it; SSRN 6926798 does, and only its abstract could be read.
The extension below is therefore our own specification, guided by that
abstract, and its parameter values are priors, not findings.

## 2. Model

Let `S_t` be the daily index (USD per GPU-hour) and `t` time in years.

```
ln S_t = g(t) + chi_t + xi_t

d chi_t = -kappa chi_t dt + sigma_chi dZ_chi            (short-term deviation)
d xi_t  =  mu_xi dt + sigma_xi dZ_xi + sum_k J_k dN_k(t) (long-run level)
dZ_chi dZ_xi = rho dt
```

- `g(t) = -delta t` is a deterministic depreciation drift.
- `N_k(t) = 1{t >= tau_k}` is a scheduled jump at the k-th hardware launch
  window `tau_k` (config `[[launches]]`). Its size is uncertain:
  `J_k ~ N(m_J, s_J^2)`, independent of the diffusions. The timing is known
  and the effect is permanent, so the jump enters the long-run factor.

Under the pricing measure Q (Schwartz and Smith 2000, eq. 7), constant risk
premia shift the drifts: `chi` drifts at `-kappa chi - lambda_chi` and `xi`
at `mu_xi* = mu_xi - lambda_xi`. We assume no premium on jump size, so `J_k`
has the same law under Q. This is an assumption that only futures data around
a launch could test.

## 3. Distribution of the state

From Schwartz and Smith (eqs. 3a, 3b), plus the jumps that fall in `(t, t+h]`:

```
E[chi_{t+h} | chi_t] = e^{-kappa h} chi_t
E[xi_{t+h}  | xi_t]  = xi_t + mu_xi h + n(t,h) m_J

Var(chi_{t+h}) = (1 - e^{-2 kappa h}) sigma_chi^2 / (2 kappa)
Var(xi_{t+h})  = sigma_xi^2 h + n(t,h) s_J^2
Cov            = (1 - e^{-kappa h}) rho sigma_chi sigma_xi / kappa
```

where `n(t,h)` counts launch dates in `(t, t+h]`.

## 4. Futures on the daily index

A futures price under deterministic interest rates equals the Q-expectation of
the settlement value. For a single-day settlement at `T = t + tau`, `ln S_T`
is normal under Q given the state, so `ln F = E*[ln S_T] + Var*[ln S_T] / 2`:

```
ln F(t, T) = g(T) + e^{-kappa tau} chi_t + xi_t + A(tau) + sum_{t < tau_k <= T} (m_J + s_J^2 / 2)

A(tau) = mu_xi* tau - (1 - e^{-kappa tau}) lambda_chi / kappa
         + 1/2 [ (1 - e^{-2 kappa tau}) sigma_chi^2 / (2 kappa)
                 + sigma_xi^2 tau
                 + 2 (1 - e^{-kappa tau}) rho sigma_chi sigma_xi / kappa ]
```

Without `g` and jumps this is exactly Schwartz and Smith's eq. 9. Two checks
are in the tests: `A(0) = 0`, and for large `tau` the slope of `A` tends to
`mu_xi* + sigma_xi^2 / 2`.

## 5. Monthly average-price contracts

GPU1/GPU2 settle on the mean of the index over the `N` business days of month
`M`. By linearity of expectation, for a month that has not started:

```
F_avg(t, M) = (1/N) sum_{d in M} F(t, T_d)
```

The Kalman filter needs a measurement that is linear in the state. We use

```
ln F_avg(t, M) ~= (1/N) sum_{d in M} ln F(t, T_d)
```

which is linear in `(chi_t, xi_t)`: intercept `mean_d [g(T_d) + A(tau_d) + jumps_d]`,
loading `mean_d e^{-kappa tau_d}` on `chi`, and 1 on `xi`.

**Size of the error.** The neglected term is the Jensen gap of averaging
`F` across days, about half the cross-day variance of `ln F(t, T_d)`. If the
curve has slope `b` per year, `ln F` spans about `b/12` over a month; a uniform
spread of that width has variance `(b/12)^2 / 12`, so the gap is about
`(b/12)^2 / 24`. At an extreme slope `b = 1` this is `3e-4`, a few basis
points, while one tick at USD 2.80 is about `36e-4`. The approximation is
therefore far below price resolution.

The current contract month mixes published index values with expectations;
it is excluded from the filter and handled by the nowcast model instead.

## 6. State-space form (Schwartz and Smith eqs. 14-16)

Transition on a calendar-day grid (`dt = 1/365`):

```
x_t = c_t + G x_{t-1} + w_t,   x_t = (chi_t, xi_t)'
G   = diag(e^{-kappa dt}, 1)
c_t = (0, mu_xi dt + 1{launch in step} m_J)'
W_t = Cov from section 3 with h = dt, plus s_J^2 on xi in launch steps
```

Measurement, one slot per listed month not yet averaging:

```
y_t = d_t + Z_t x_t + v_t,   v_t ~ N(0, s^2 I)
```

with `d_t` and `Z_t` from section 5. Days without settlements are rows of
missing values: the filter predicts but does not update. The log-likelihood
is the prediction-error decomposition, maximized with Nelder-Mead on
transformed parameters (log for positive values, `atanh` for `rho`).

Note on notation: Schwartz and Smith label their loading matrix `F_t` as
`n x 2`, but their recursions need it `2 x n`. We write `Z_t` (`n x 2`).

## 7. Identification

These limits shape what can be estimated and when.

1. **Constant depreciation is not separately identified.** In the real-world
   transition, `-delta` and `mu_xi` both add a linear trend to `ln S`. In the
   futures cross-section, `-delta` and `mu_xi*` both add slope in `tau`. A
   constant `delta` is therefore absorbed by the two drifts. We fix `delta` at
   a prior (0.175 a year, from the SSRN 6926798 abstract) and read the
   estimated drifts as deviations from it. Forecasts do not depend on the
   prior while `delta` is constant. A time-varying depreciation schedule would
   be identified only by history spanning several launches.
2. **Jump size needs launches in the sample.** `m_J` is identified from level
   shifts at launch dates in index history, or from kinks in the futures
   curve at launch windows. Neither is available yet. The prior is `-0.22`
   with standard deviation `0.10`.
3. **Spot data alone identify the factors weakly.** On simulated data with
   known parameters (about 2.7 years daily, measurement noise 1%), the
   spot-only maximum-likelihood fit drove `sigma_xi` from 0.20 to about 0
   while beating the true parameters' likelihood (1926.3 vs 1921.8). A sum of
   a slow OU process and a random walk is hard to separate without the
   cross-section that futures provide.
4. **Short panels leave drifts and premia imprecise.** On a simulated 500-day,
   6-contract panel, the panel fit recovered `kappa` (4.14 vs 4.0),
   `sigma_chi` (0.503 vs 0.5), `sigma_xi` (0.205 vs 0.2), `rho` (0.34 vs 0.3),
   `mu_xi*` (-0.203 vs -0.2) and the noise level, but not `mu_xi` (0.007 vs
   -0.15) or `lambda_chi` (0.005 vs 0.1). Schwartz and Smith also report wide
   standard errors on these. Claim 2 depends on the real-world drift, so it
   needs a long sample.

Items 3 and 4 come from runs on simulated data. They describe the estimator,
not the market.

## 8. Forecasting the final settlement

From the filtered state `(m_t, P_t)` at decision time `t`, iterate the
transition to get the real-world mean `m_d` and variance `v_d` of `ln S_d` for
each business day `d` of month `M`, including launch jumps. Then

```
E[F_M | info_t] = (1/N) sum_d exp(m_d + v_d / 2)
```

because each `S_d` is lognormal given the state.

## 9. Walk-forward protocol (claim 2)

At the last trade date of each month: build the panel from settlements
available then, fit by maximum likelihood with an expanding window, filter to
`t`, forecast months 1 to 6 ahead, and score against realized final
settlements. The baselines are the futures settlement itself and the latest
index value. The pipeline is exercised on labelled synthetic data whose
futures embed a known risk premium (`tests/test_term_structure.py`, slow
marker). On that data the model's mean squared log error at horizons of 3
months or more is below the futures price's, as it should be when the
futures carry a premium the model can learn. The test passed on 2026-10-05.
This validates the code path only; it says nothing about real markets.

## 10. What can be estimated today

Nothing on real data. There are no futures settlements, licensed settlement
index history is not available, and our own index has 49 out-of-sample days
on a fixed panel, against a minimum of 180 for even the descriptive spot-only
fit.
