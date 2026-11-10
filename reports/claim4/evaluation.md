# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-10T04:48:14.251751+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `b2e9db4d93d9b02d...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 4 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 37 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 57 | 2026-08-20 | 2026-11-09 | 0.36 | 0.48 |
| 5 | 53 | 2026-08-20 | 2026-11-03 | 0.38 | 0.49 |
| 20 | 38 | 2026-08-20 | 2026-10-13 | 0.44 | 0.57 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 57 | 24 | -0.347 | -0.139 | [-0.44, 0.14] | 0.436 | 1.000 | 0.228 | False |  |
| level_h100 | 5 | 53 | 20 | -1.225 | -0.154 | [-0.32, 0.07] | 0.049 | 0.741 | 0.267 | False |  |
| level_h100 | 20 | 38 | 9 | n/a | -0.141 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 57 | 24 | -0.390 | -0.340 | [-0.52, -0.14] | 0.013 | 0.215 | 0.018 | False |  |
| level_b200 | 5 | 53 | 23 | -0.543 | -0.170 | [-0.39, 0.01] | 0.080 | 1.000 | 0.289 | False |  |
| level_b200 | 20 | 38 | 16 | n/a | -0.265 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 57 | 47 | 0.087 | 0.117 | [-0.11, 0.35] | 0.359 | 1.000 | 0.351 | False |  |
| disp_h100 | 5 | 53 | 44 | -0.098 | -0.049 | [-0.32, 0.16] | 0.640 | 1.000 | 0.778 | False |  |
| disp_h100 | 20 | 38 | 32 | n/a | -0.157 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 57 | 13 | 0.163 | 0.303 | [-0.04, 0.49] | 0.003 | 0.053 | 0.018 | False |  |
| disp_b200 | 5 | 53 | 11 | 0.261 | 0.183 | [0.05, 0.34] | 0.000 | 0.002 | 0.200 | False |  |
| disp_b200 | 20 | 38 | 7 | n/a | 0.210 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 57 | 17 | -0.004 | -0.058 | [-0.30, 0.23] | 0.704 | 1.000 | 0.667 | False |  |
| avail_h100 | 5 | 53 | 15 | -0.008 | -0.052 | [-0.24, 0.12] | 0.441 | 1.000 | 0.311 | False |  |
| avail_h100 | 20 | 38 | 6 | n/a | 0.025 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 57 | 14 | -0.003 | -0.052 | [-0.29, 0.23] | 0.740 | 1.000 | 0.719 | False |  |
| avail_b200 | 5 | 53 | 13 | -0.008 | -0.049 | [-0.24, 0.12] | 0.450 | 1.000 | 0.356 | False |  |
| avail_b200 | 20 | 38 | 4 | n/a | 0.010 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 3 | -1.287 | n/a | 0.750 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 3 | -6.126 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 37 | -0.157 | -0.149 | 0.482 | 0.557 | 0.541 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 29 | 0.231 | 0.023 | 0.001 | 0.015 | 0.828 | 0.277 | False | 29 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 37 | -0.180 | -0.172 | 0.051 | 0.043 | 0.568 | 0.769 | False | 37 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 29 | 0.262 | 0.062 | 0.000 | 0.040 | 0.828 | 0.647 | False | 29 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 37 | -0.018 | -0.011 | 0.631 | 0.705 | 0.541 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 29 | 0.176 | -0.047 | 0.007 | 0.990 | 0.724 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 37 | -0.011 | -0.004 | 0.126 | 0.121 | 0.568 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 29 | 0.259 | 0.059 | 0.000 | 0.022 | 0.759 | 0.375 | False | 29 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 37 | -1.332 | -1.317 | 0.350 | 0.425 | 0.514 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 29 | -36.252 | -46.331 | 0.520 | 0.632 | 0.690 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 37 | -0.175 | -0.167 | 0.805 | 0.840 | 0.514 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 29 | 0.225 | 0.015 | 0.006 | 0.128 | 0.724 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 37 | 7 | 0.168 | [-3.59, 5.58] | False | 0.086 | 0.049 | 0.011 | -0.064 | -0.214 |
| level_h100 | 5 | 29 | 22 | 4.890 | [1.66, 8.80] | True | 3.180 | 2.998 | 2.816 | 2.453 | 1.726 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 37 | 7 | 2.044 | [-3.74, 6.33] | False | 0.185 | 0.147 | 0.109 | 0.033 | -0.118 |
| level_b200 | 5 | 29 | 23 | 5.615 | [2.02, 10.93] | True | 3.607 | 3.417 | 3.227 | 2.847 | 2.087 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 37 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 29 | 23 | 4.057 | [0.10, 9.15] | True | 3.017 | 2.830 | 2.643 | 2.269 | 1.521 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 37 | 5 | 1.237 | [-3.51, 5.05] | False | 0.112 | 0.085 | 0.059 | 0.005 | -0.102 |
| disp_b200 | 5 | 29 | 22 | 5.389 | [1.84, 10.40] | True | 3.494 | 3.312 | 3.131 | 2.767 | 2.040 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 37 | 9 | -2.219 | [-4.95, 0.96] | False | -0.097 | -0.145 | -0.193 | -0.289 | -0.481 |
| avail_h100 | 5 | 29 | 23 | 2.985 | [0.92, 5.51] | True | 2.437 | 2.250 | 2.063 | 1.689 | 0.942 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 37 | 8 | -2.639 | [-5.34, 0.37] | False | -0.141 | -0.184 | -0.226 | -0.311 | -0.481 |
| avail_b200 | 5 | 29 | 23 | 4.517 | [1.38, 9.14] | True | 3.194 | 3.005 | 2.817 | 2.440 | 1.686 |
| avail_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |

## Gate

| pair | G1 | G2 | G3 | G4 | validated |
|---|---|---|---|---|---|
| level_h100|h1 | False | False | False | False | False |
| level_h100|h5 | False | False | True | False | False |
| level_h100|h20 | False | False | False | False | False |
| level_b200|h1 | False | False | False | False | False |
| level_b200|h5 | False | False | True | False | False |
| level_b200|h20 | False | False | False | False | False |
| disp_h100|h1 | False | False | False | False | False |
| disp_h100|h5 | False | False | True | False | False |
| disp_h100|h20 | False | False | False | False | False |
| disp_b200|h1 | False | False | False | False | False |
| disp_b200|h5 | False | False | True | False | False |
| disp_b200|h20 | False | False | False | False | False |
| avail_h100|h1 | False | False | False | False | False |
| avail_h100|h5 | False | False | True | False | False |
| avail_h100|h20 | False | False | False | False | False |
| avail_b200|h1 | False | False | False | False | False |
| avail_b200|h5 | False | False | True | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 57 | 24 | -0.508 | -0.129 | [-0.43, 0.15] | 0.464 | 1.000 | 0.228 | False |  |
| neocloud | level_h100 | 5 | 53 | 20 | -2.638 | -0.215 | [-0.35, -0.07] | 0.000 | 0.000 | 0.111 | False |  |
| neocloud | level_h100 | 20 | 38 | 9 | n/a | -0.195 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 57 | 24 | -0.648 | -0.356 | [-0.50, -0.19] | 0.001 | 0.008 | 0.018 | True |  |
| neocloud | level_b200 | 5 | 53 | 23 | -1.123 | -0.228 | [-0.41, -0.02] | 0.010 | 0.090 | 0.111 | False |  |
| neocloud | level_b200 | 20 | 38 | 16 | n/a | -0.292 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 57 | 47 | 0.095 | 0.081 | [-0.13, 0.30] | 0.497 | 1.000 | 0.526 | False |  |
| neocloud | disp_h100 | 5 | 53 | 44 | -0.168 | -0.054 | [-0.34, 0.16] | 0.624 | 1.000 | 0.822 | False |  |
| neocloud | disp_h100 | 20 | 38 | 32 | n/a | -0.161 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 57 | 13 | 0.281 | 0.330 | [0.03, 0.50] | 0.000 | 0.000 | 0.018 | True |  |
| neocloud | disp_b200 | 5 | 53 | 11 | 0.466 | 0.213 | [0.08, 0.36] | 0.000 | 0.000 | 0.089 | False |  |
| neocloud | disp_b200 | 20 | 38 | 7 | n/a | 0.234 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 57 | 17 | -0.011 | -0.106 | [-0.37, 0.19] | 0.503 | 1.000 | 0.404 | False |  |
| neocloud | avail_h100 | 5 | 53 | 15 | -0.012 | -0.051 | [-0.23, 0.12] | 0.430 | 1.000 | 0.311 | False |  |
| neocloud | avail_h100 | 20 | 38 | 6 | n/a | -0.021 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 57 | 14 | -0.010 | -0.104 | [-0.37, 0.19] | 0.521 | 1.000 | 0.474 | False |  |
| neocloud | avail_b200 | 5 | 53 | 13 | -0.013 | -0.053 | [-0.24, 0.12] | 0.400 | 1.000 | 0.333 | False |  |
| neocloud | avail_b200 | 20 | 38 | 4 | n/a | -0.037 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 57 | 24 | -0.274 | -0.178 | [-0.51, 0.19] | 0.353 | 1.000 | 0.140 | False |  |
| gpu_semis | level_h100 | 5 | 53 | 20 | -0.569 | -0.101 | [-0.31, 0.21] | 0.377 | 1.000 | 0.489 | False |  |
| gpu_semis | level_h100 | 20 | 38 | 9 | n/a | -0.173 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 57 | 24 | -0.180 | -0.253 | [-0.57, 0.03] | 0.194 | 0.873 | 0.035 | False |  |
| gpu_semis | level_b200 | 5 | 53 | 23 | -0.270 | -0.119 | [-0.35, 0.23] | 0.182 | 0.873 | 0.489 | False |  |
| gpu_semis | level_b200 | 20 | 38 | 16 | n/a | -0.305 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 57 | 47 | 0.049 | 0.107 | [-0.19, 0.39] | 0.461 | 1.000 | 0.333 | False |  |
| gpu_semis | disp_h100 | 5 | 53 | 44 | -0.122 | -0.086 | [-0.31, 0.11] | 0.341 | 1.000 | 0.467 | False |  |
| gpu_semis | disp_h100 | 20 | 38 | 32 | n/a | -0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 57 | 13 | 0.098 | 0.295 | [-0.09, 0.58] | 0.083 | 0.495 | 0.035 | False |  |
| gpu_semis | disp_b200 | 5 | 53 | 11 | 0.194 | 0.192 | [0.01, 0.35] | 0.000 | 0.002 | 0.200 | False |  |
| gpu_semis | disp_b200 | 20 | 38 | 7 | n/a | 0.255 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 57 | 17 | -0.001 | -0.018 | [-0.27, 0.31] | 0.908 | 1.000 | 0.965 | False |  |
| gpu_semis | avail_h100 | 5 | 53 | 15 | -0.008 | -0.069 | [-0.23, 0.07] | 0.251 | 0.905 | 0.222 | False |  |
| gpu_semis | avail_h100 | 20 | 38 | 6 | n/a | -0.047 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 57 | 14 | -0.000 | -0.004 | [-0.26, 0.32] | 0.978 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 53 | 13 | -0.008 | -0.072 | [-0.24, 0.06] | 0.230 | 0.905 | 0.244 | False |  |
| gpu_semis | avail_b200 | 20 | 38 | 4 | n/a | -0.069 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 57 | 24 | -0.258 | -0.095 | [-0.30, 0.11] | 0.484 | 1.000 | 0.386 | False |  |
| power_capacity | level_h100 | 5 | 53 | 20 | -0.468 | -0.060 | [-0.24, 0.21] | 0.525 | 1.000 | 0.600 | False |  |
| power_capacity | level_h100 | 20 | 38 | 9 | n/a | 0.107 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 57 | 24 | -0.343 | -0.272 | [-0.44, -0.08] | 0.026 | 0.201 | 0.018 | False |  |
| power_capacity | level_b200 | 5 | 53 | 23 | -0.237 | -0.076 | [-0.41, 0.10] | 0.460 | 1.000 | 0.667 | False |  |
| power_capacity | level_b200 | 20 | 38 | 16 | n/a | -0.045 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 57 | 47 | 0.116 | 0.143 | [-0.07, 0.36] | 0.243 | 0.905 | 0.281 | False |  |
| power_capacity | disp_h100 | 5 | 53 | 44 | -0.005 | -0.002 | [-0.26, 0.20] | 0.982 | 1.000 | 0.978 | False |  |
| power_capacity | disp_h100 | 20 | 38 | 32 | n/a | -0.172 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 57 | 13 | 0.109 | 0.185 | [-0.15, 0.34] | 0.057 | 0.384 | 0.140 | False |  |
| power_capacity | disp_b200 | 5 | 53 | 11 | 0.122 | 0.088 | [-0.07, 0.29] | 0.147 | 0.793 | 0.533 | False |  |
| power_capacity | disp_b200 | 20 | 38 | 7 | n/a | 0.008 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 57 | 17 | 0.000 | 0.004 | [-0.17, 0.23] | 0.973 | 1.000 | 0.982 | False |  |
| power_capacity | avail_h100 | 5 | 53 | 15 | -0.004 | -0.028 | [-0.24, 0.19] | 0.734 | 1.000 | 0.578 | False |  |
| power_capacity | avail_h100 | 20 | 38 | 6 | n/a | 0.262 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 57 | 14 | 0.001 | 0.011 | [-0.17, 0.23] | 0.930 | 1.000 | 0.965 | False |  |
| power_capacity | avail_b200 | 5 | 53 | 13 | -0.002 | -0.016 | [-0.23, 0.20] | 0.854 | 1.000 | 0.844 | False |  |
| power_capacity | avail_b200 | 20 | 38 | 4 | n/a | 0.262 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.15, 0.21] | 0.12 [-0.05, 0.24] |
| -4 | -0.03 [-0.14, 0.10] | -0.31 [-0.48, -0.08] |
| -3 | -0.11 [-0.26, 0.05] | 0.14 [-0.21, 0.44] |
| -2 | -0.23 [-0.43, 0.01] | -0.20 [-0.38, 0.18] |
| -1 | 0.08 [-0.26, 0.41] | -0.25 [-0.40, -0.02] |
| 0 | -0.34 [-0.52, -0.14] | -0.14 [-0.44, 0.14] |
| 1 | -0.05 [-0.29, 0.24] | -0.07 [-0.41, 0.29] |
| 2 | 0.07 [-0.17, 0.24] | 0.19 [-0.18, 0.46] |
| 3 | 0.02 [-0.25, 0.33] | 0.09 [-0.09, 0.25] |
| 4 | -0.06 [-0.23, 0.01] | -0.17 [-0.44, -0.03] |
| 5 | -0.11 [-0.24, 0.03] | -0.06 [-0.28, 0.16] |

