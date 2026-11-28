# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-28T04:57:59.543780+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `5666096d5a38a0f9...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 9 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 50 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 70 | 2026-08-20 | 2026-11-27 | 0.33 | 0.44 |
| 5 | 66 | 2026-08-20 | 2026-11-20 | 0.34 | 0.45 |
| 20 | 51 | 2026-08-20 | 2026-10-30 | 0.38 | 0.50 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 70 | 32 | -0.005 | -0.004 | [-0.30, 0.18] | 0.973 | 1.000 | 0.957 | False |  |
| level_h100 | 5 | 66 | 29 | 0.136 | 0.040 | [-0.23, 0.20] | 0.599 | 1.000 | 0.690 | False |  |
| level_h100 | 20 | 51 | 19 | n/a | -0.138 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 70 | 26 | -0.388 | -0.302 | [-0.48, -0.12] | 0.014 | 0.257 | 0.014 | False |  |
| level_b200 | 5 | 66 | 25 | -0.334 | -0.105 | [-0.28, 0.05] | 0.173 | 1.000 | 0.310 | False |  |
| level_b200 | 20 | 51 | 23 | n/a | -0.247 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 70 | 54 | 0.046 | 0.056 | [-0.14, 0.27] | 0.603 | 1.000 | 0.571 | False |  |
| disp_h100 | 5 | 66 | 51 | -0.223 | -0.112 | [-0.37, 0.12] | 0.267 | 1.000 | 0.241 | False |  |
| disp_h100 | 20 | 51 | 43 | n/a | -0.082 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 70 | 15 | 0.147 | 0.245 | [-0.08, 0.44] | 0.016 | 0.267 | 0.043 | False |  |
| disp_b200 | 5 | 66 | 14 | 0.107 | 0.074 | [-0.17, 0.24] | 0.384 | 1.000 | 0.586 | False |  |
| disp_b200 | 20 | 51 | 11 | n/a | 0.204 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 70 | 21 | -0.004 | -0.051 | [-0.25, 0.20] | 0.700 | 1.000 | 0.657 | False |  |
| avail_h100 | 5 | 66 | 20 | -0.008 | -0.044 | [-0.18, 0.10] | 0.401 | 1.000 | 0.397 | False |  |
| avail_h100 | 20 | 51 | 14 | n/a | -0.025 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 70 | 16 | -0.003 | -0.046 | [-0.25, 0.21] | 0.736 | 1.000 | 0.700 | False |  |
| avail_b200 | 5 | 66 | 15 | -0.008 | -0.047 | [-0.18, 0.09] | 0.355 | 1.000 | 0.483 | False |  |
| avail_b200 | 20 | 51 | 12 | n/a | -0.034 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 9 | -0.426 | n/a | 0.672 | 1.000 | False | insufficient events (9 < 10); descriptive only |
| H100 | 5 | 5 | 2.801 | n/a | 0.375 | 1.000 | False | insufficient events (5 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 5 | -2.780 | n/a | 0.062 | 0.375 | False | insufficient events (5 < 10); descriptive only |
| B200 | 5 | 4 | -4.733 | n/a | 0.125 | 0.625 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 50 | -0.140 | -0.161 | 0.572 | 0.786 | 0.540 | 1.000 | False | 50 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 42 | 0.127 | -0.062 | 0.022 | 0.441 | 0.810 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 12 | 0.870 | 0.070 | n/a | n/a | 1.000 | n/a | False | 12 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 50 | -0.095 | -0.115 | 0.032 | 0.040 | 0.580 | 0.722 | False | 50 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 42 | 0.188 | 0.013 | 0.001 | 0.100 | 0.810 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 12 | 0.877 | 0.125 | n/a | n/a | 1.000 | n/a | False | 12 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 50 | -0.000 | -0.019 | 0.364 | 0.898 | 0.540 | 1.000 | False | 50 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 42 | 0.158 | -0.023 | 0.014 | 0.864 | 0.738 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 12 | 0.837 | -0.160 | n/a | n/a | 1.000 | n/a | False | 12 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 50 | 0.001 | -0.017 | 0.104 | 0.159 | 0.560 | 1.000 | False | 50 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 42 | 0.167 | -0.012 | 0.004 | 0.415 | 0.762 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 12 | 0.867 | 0.053 | n/a | n/a | 1.000 | n/a | False | 12 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 50 | -0.872 | -0.906 | 0.259 | 0.425 | 0.540 | 1.000 | False | 50 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 42 | -21.887 | -26.822 | 0.484 | 0.630 | 0.714 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 12 | -48.564 | -352.469 | n/a | n/a | 0.583 | n/a | False | 12 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 50 | -0.095 | -0.115 | 0.647 | 0.838 | 0.540 | 1.000 | False | 50 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 42 | 0.185 | 0.010 | 0.007 | 0.130 | 0.738 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 12 | 0.860 | 0.000 | n/a | n/a | 1.000 | n/a | False | 12 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 50 | 10 | -2.020 | [-5.78, 2.13] | False | -0.057 | -0.097 | -0.136 | -0.215 | -0.374 |
| level_h100 | 5 | 42 | 35 | 3.864 | [0.48, 8.59] | True | 3.059 | 2.859 | 2.659 | 2.260 | 1.461 |
| level_h100 | 20 | 12 | 12 | 8.303 | n/a | False | 8.775 | 8.386 | 7.998 | 7.221 | 5.668 |
| level_b200 | 1 | 50 | 8 | 2.437 | [-2.38, 6.14] | False | 0.182 | 0.150 | 0.118 | 0.054 | -0.074 |
| level_b200 | 5 | 42 | 36 | 4.269 | [0.72, 9.54] | True | 3.354 | 3.149 | 2.943 | 2.533 | 1.711 |
| level_b200 | 20 | 12 | 12 | 8.303 | n/a | False | 8.775 | 8.386 | 7.998 | 7.221 | 5.668 |
| disp_h100 | 1 | 50 | 1 | -2.245 | [-3.97, 0.00] | False | -0.052 | -0.056 | -0.059 | -0.067 | -0.083 |
| disp_h100 | 5 | 42 | 36 | 3.467 | [0.14, 8.15] | True | 2.946 | 2.743 | 2.540 | 2.133 | 1.320 |
| disp_h100 | 20 | 12 | 12 | 8.303 | n/a | False | 8.775 | 8.386 | 7.998 | 7.221 | 5.668 |
| disp_b200 | 1 | 50 | 8 | -0.400 | [-4.09, 3.57] | False | 0.041 | 0.010 | -0.022 | -0.085 | -0.212 |
| disp_b200 | 5 | 42 | 35 | 4.154 | [0.66, 9.34] | True | 3.276 | 3.076 | 2.876 | 2.477 | 1.678 |
| disp_b200 | 20 | 12 | 12 | 8.303 | n/a | False | 8.775 | 8.386 | 7.998 | 7.221 | 5.668 |
| avail_h100 | 1 | 50 | 10 | -2.565 | [-5.02, -0.06] | False | -0.124 | -0.163 | -0.202 | -0.281 | -0.439 |
| avail_h100 | 5 | 42 | 36 | 2.827 | [0.13, 6.15] | True | 2.546 | 2.343 | 2.140 | 1.733 | 0.920 |
| avail_h100 | 20 | 12 | 12 | 0.557 | n/a | False | 2.097 | 1.783 | 1.469 | 0.841 | -0.415 |
| avail_b200 | 1 | 50 | 9 | -2.914 | [-5.26, -0.38] | False | -0.156 | -0.192 | -0.227 | -0.298 | -0.440 |
| avail_b200 | 5 | 42 | 36 | 3.714 | [0.49, 8.14] | True | 3.068 | 2.864 | 2.660 | 2.251 | 1.434 |
| avail_b200 | 20 | 12 | 12 | 8.303 | n/a | False | 8.775 | 8.386 | 7.998 | 7.221 | 5.668 |

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
| neocloud | level_h100 | 1 | 70 | 32 | 0.060 | 0.029 | [-0.30, 0.25] | 0.807 | 1.000 | 0.786 | False |  |
| neocloud | level_h100 | 5 | 66 | 29 | 0.038 | 0.007 | [-0.27, 0.18] | 0.937 | 1.000 | 0.948 | False |  |
| neocloud | level_h100 | 20 | 51 | 19 | n/a | -0.197 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 70 | 26 | -0.648 | -0.313 | [-0.45, -0.16] | 0.001 | 0.066 | 0.014 | True |  |
| neocloud | level_b200 | 5 | 66 | 25 | -0.771 | -0.161 | [-0.31, 0.01] | 0.037 | 0.503 | 0.207 | False |  |
| neocloud | level_b200 | 20 | 51 | 23 | n/a | -0.274 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 70 | 54 | 0.023 | 0.018 | [-0.17, 0.21] | 0.860 | 1.000 | 0.886 | False |  |
| neocloud | disp_h100 | 5 | 66 | 51 | -0.412 | -0.137 | [-0.39, 0.09] | 0.179 | 1.000 | 0.069 | False |  |
| neocloud | disp_h100 | 20 | 51 | 43 | n/a | -0.091 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 70 | 15 | 0.245 | 0.255 | [-0.07, 0.44] | 0.002 | 0.066 | 0.043 | True |  |
| neocloud | disp_b200 | 5 | 66 | 14 | 0.273 | 0.124 | [-0.12, 0.27] | 0.084 | 0.755 | 0.241 | False |  |
| neocloud | disp_b200 | 20 | 51 | 11 | n/a | 0.226 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 70 | 21 | -0.011 | -0.092 | [-0.30, 0.15] | 0.496 | 1.000 | 0.386 | False |  |
| neocloud | avail_h100 | 5 | 66 | 20 | -0.009 | -0.035 | [-0.17, 0.11] | 0.523 | 1.000 | 0.672 | False |  |
| neocloud | avail_h100 | 20 | 51 | 14 | n/a | -0.030 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 70 | 16 | -0.010 | -0.088 | [-0.30, 0.16] | 0.519 | 1.000 | 0.400 | False |  |
| neocloud | avail_b200 | 5 | 66 | 15 | -0.010 | -0.038 | [-0.17, 0.10] | 0.455 | 1.000 | 0.621 | False |  |
| neocloud | avail_b200 | 20 | 51 | 12 | n/a | -0.039 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 70 | 32 | -0.023 | -0.029 | [-0.32, 0.15] | 0.786 | 1.000 | 0.814 | False |  |
| gpu_semis | level_h100 | 5 | 66 | 29 | 0.173 | 0.072 | [-0.24, 0.24] | 0.368 | 1.000 | 0.586 | False |  |
| gpu_semis | level_h100 | 20 | 51 | 19 | n/a | -0.165 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 70 | 26 | -0.172 | -0.214 | [-0.50, 0.04] | 0.199 | 1.000 | 0.086 | False |  |
| gpu_semis | level_b200 | 5 | 66 | 25 | -0.201 | -0.090 | [-0.27, 0.07] | 0.210 | 1.000 | 0.500 | False |  |
| gpu_semis | level_b200 | 20 | 51 | 23 | n/a | -0.275 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 70 | 54 | 0.028 | 0.056 | [-0.18, 0.31] | 0.655 | 1.000 | 0.629 | False |  |
| gpu_semis | disp_h100 | 5 | 66 | 51 | -0.134 | -0.095 | [-0.33, 0.11] | 0.310 | 1.000 | 0.293 | False |  |
| gpu_semis | disp_h100 | 20 | 51 | 43 | n/a | -0.049 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 70 | 15 | 0.091 | 0.242 | [-0.10, 0.50] | 0.106 | 0.821 | 0.043 | False |  |
| gpu_semis | disp_b200 | 5 | 66 | 14 | 0.070 | 0.068 | [-0.22, 0.26] | 0.493 | 1.000 | 0.672 | False |  |
| gpu_semis | disp_b200 | 20 | 51 | 11 | n/a | 0.236 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 70 | 21 | -0.001 | -0.016 | [-0.25, 0.28] | 0.905 | 1.000 | 0.914 | False |  |
| gpu_semis | avail_h100 | 5 | 66 | 20 | -0.006 | -0.053 | [-0.17, 0.07] | 0.264 | 1.000 | 0.362 | False |  |
| gpu_semis | avail_h100 | 20 | 51 | 14 | n/a | -0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 70 | 16 | -0.000 | -0.003 | [-0.24, 0.29] | 0.980 | 1.000 | 0.971 | False |  |
| gpu_semis | avail_b200 | 5 | 66 | 15 | -0.007 | -0.059 | [-0.17, 0.06] | 0.219 | 1.000 | 0.345 | False |  |
| gpu_semis | avail_b200 | 20 | 51 | 12 | n/a | -0.015 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 70 | 32 | -0.051 | -0.038 | [-0.21, 0.07] | 0.602 | 1.000 | 0.786 | False |  |
| power_capacity | level_h100 | 5 | 66 | 29 | 0.197 | 0.059 | [-0.14, 0.23] | 0.415 | 1.000 | 0.517 | False |  |
| power_capacity | level_h100 | 20 | 51 | 19 | n/a | 0.087 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 70 | 26 | -0.344 | -0.259 | [-0.41, -0.09] | 0.024 | 0.424 | 0.014 | False |  |
| power_capacity | level_b200 | 5 | 66 | 25 | -0.030 | -0.010 | [-0.26, 0.14] | 0.892 | 1.000 | 0.983 | False |  |
| power_capacity | level_b200 | 20 | 51 | 23 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 70 | 54 | 0.086 | 0.103 | [-0.10, 0.31] | 0.347 | 1.000 | 0.371 | False |  |
| power_capacity | disp_h100 | 5 | 66 | 51 | -0.122 | -0.062 | [-0.30, 0.17] | 0.561 | 1.000 | 0.603 | False |  |
| power_capacity | disp_h100 | 20 | 51 | 43 | n/a | -0.060 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 70 | 15 | 0.104 | 0.169 | [-0.11, 0.31] | 0.068 | 0.739 | 0.214 | False |  |
| power_capacity | disp_b200 | 5 | 66 | 14 | -0.023 | -0.016 | [-0.22, 0.16] | 0.855 | 1.000 | 0.879 | False |  |
| power_capacity | disp_b200 | 20 | 51 | 11 | n/a | 0.017 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 70 | 21 | 0.000 | 0.004 | [-0.16, 0.22] | 0.974 | 1.000 | 0.957 | False |  |
| power_capacity | avail_h100 | 5 | 66 | 20 | -0.008 | -0.044 | [-0.20, 0.15] | 0.493 | 1.000 | 0.431 | False |  |
| power_capacity | avail_h100 | 20 | 51 | 14 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 70 | 16 | 0.001 | 0.007 | [-0.16, 0.23] | 0.948 | 1.000 | 0.914 | False |  |
| power_capacity | avail_b200 | 5 | 66 | 15 | -0.007 | -0.043 | [-0.19, 0.16] | 0.520 | 1.000 | 0.483 | False |  |
| power_capacity | avail_b200 | 20 | 51 | 12 | n/a | -0.031 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.04 [-0.12, 0.21] | -0.08 [-0.25, 0.19] |
| -4 | -0.01 [-0.11, 0.12] | -0.33 [-0.46, -0.17] |
| -3 | -0.10 [-0.23, 0.05] | 0.02 [-0.18, 0.28] |
| -2 | -0.22 [-0.40, -0.02] | -0.19 [-0.37, -0.00] |
| -1 | 0.05 [-0.28, 0.34] | -0.18 [-0.33, 0.05] |
| 0 | -0.30 [-0.48, -0.12] | -0.00 [-0.30, 0.18] |
| 1 | -0.08 [-0.32, 0.18] | -0.08 [-0.35, 0.18] |
| 2 | 0.11 [-0.06, 0.26] | 0.12 [-0.05, 0.38] |
| 3 | 0.02 [-0.20, 0.27] | 0.05 [-0.23, 0.22] |
| 4 | -0.01 [-0.12, 0.06] | 0.20 [-0.16, 0.38] |
| 5 | -0.02 [-0.15, 0.15] | 0.07 [-0.23, 0.24] |

