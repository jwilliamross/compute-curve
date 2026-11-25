# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-25T05:40:47.544067+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `31babbcebae68a24...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 8 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 48 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 68 | 2026-08-20 | 2026-11-24 | 0.33 | 0.44 |
| 5 | 64 | 2026-08-20 | 2026-11-18 | 0.34 | 0.45 |
| 20 | 49 | 2026-08-20 | 2026-10-28 | 0.39 | 0.51 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 68 | 30 | 0.009 | 0.007 | [-0.30, 0.20] | 0.947 | 1.000 | 0.971 | False |  |
| level_h100 | 5 | 64 | 27 | 0.253 | 0.072 | [-0.20, 0.23] | 0.308 | 1.000 | 0.571 | False |  |
| level_h100 | 20 | 49 | 18 | n/a | -0.130 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 68 | 26 | -0.384 | -0.302 | [-0.48, -0.11] | 0.016 | 0.287 | 0.015 | False |  |
| level_b200 | 5 | 64 | 25 | -0.350 | -0.112 | [-0.30, 0.05] | 0.149 | 1.000 | 0.339 | False |  |
| level_b200 | 20 | 49 | 23 | n/a | -0.252 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 68 | 52 | 0.064 | 0.079 | [-0.11, 0.30] | 0.464 | 1.000 | 0.515 | False |  |
| disp_h100 | 5 | 64 | 49 | -0.208 | -0.106 | [-0.38, 0.12] | 0.304 | 1.000 | 0.393 | False |  |
| disp_h100 | 20 | 49 | 41 | n/a | -0.126 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 68 | 15 | 0.146 | 0.248 | [-0.08, 0.44] | 0.017 | 0.289 | 0.044 | False |  |
| disp_b200 | 5 | 64 | 14 | 0.107 | 0.075 | [-0.16, 0.24] | 0.375 | 1.000 | 0.625 | False |  |
| disp_b200 | 20 | 49 | 11 | n/a | 0.204 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 68 | 21 | -0.004 | -0.052 | [-0.26, 0.20] | 0.699 | 1.000 | 0.618 | False |  |
| avail_h100 | 5 | 64 | 18 | -0.007 | -0.043 | [-0.19, 0.10] | 0.428 | 1.000 | 0.429 | False |  |
| avail_h100 | 20 | 49 | 13 | n/a | -0.055 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 68 | 16 | -0.003 | -0.046 | [-0.26, 0.21] | 0.736 | 1.000 | 0.676 | False |  |
| avail_b200 | 5 | 64 | 15 | -0.008 | -0.048 | [-0.19, 0.09] | 0.357 | 1.000 | 0.482 | False |  |
| avail_b200 | 20 | 49 | 11 | n/a | -0.064 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 8 | -0.362 | n/a | 0.758 | 1.000 | False | insufficient events (8 < 10); descriptive only |
| H100 | 5 | 4 | 2.753 | n/a | 0.500 | 1.000 | False | insufficient events (4 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 5 | -2.780 | n/a | 0.062 | 0.375 | False | insufficient events (5 < 10); descriptive only |
| B200 | 5 | 4 | -4.733 | n/a | 0.125 | 0.625 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 48 | -0.137 | -0.166 | 0.541 | 0.785 | 0.542 | 1.000 | False | 48 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 40 | 0.099 | -0.073 | 0.032 | 0.488 | 0.800 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 10 | 0.865 | 0.001 | n/a | n/a | 1.000 | n/a | False | 10 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 48 | -0.093 | -0.122 | 0.029 | 0.042 | 0.583 | 0.760 | False | 48 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 40 | 0.174 | 0.015 | 0.002 | 0.088 | 0.800 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 10 | 0.889 | 0.180 | n/a | n/a | 1.000 | n/a | False | 10 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 48 | 0.011 | -0.015 | 0.253 | 0.837 | 0.542 | 1.000 | False | 48 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 40 | 0.138 | -0.027 | 0.019 | 0.910 | 0.725 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 10 | 0.886 | 0.159 | n/a | n/a | 1.000 | n/a | False | 10 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 48 | 0.008 | -0.018 | 0.093 | 0.159 | 0.562 | 1.000 | False | 48 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 40 | 0.150 | -0.013 | 0.007 | 0.412 | 0.750 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 10 | 0.871 | 0.046 | n/a | n/a | 1.000 | n/a | False | 10 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 48 | -0.890 | -0.939 | 0.242 | 0.425 | 0.542 | 1.000 | False | 48 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 40 | -23.374 | -28.052 | 0.497 | 0.631 | 0.700 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 10 | -61.940 | -464.018 | n/a | n/a | 0.600 | n/a | False | 10 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 48 | -0.091 | -0.119 | 0.613 | 0.838 | 0.542 | 1.000 | False | 48 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 40 | 0.170 | 0.010 | 0.010 | 0.128 | 0.725 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 10 | 0.865 | 0.000 | n/a | n/a | 1.000 | n/a | False | 10 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 48 | 9 | -1.256 | [-5.07, 4.08] | False | -0.006 | -0.043 | -0.080 | -0.154 | -0.303 |
| level_h100 | 5 | 40 | 33 | 3.627 | [0.29, 8.19] | True | 2.903 | 2.705 | 2.508 | 2.112 | 1.322 |
| level_h100 | 20 | 10 | 10 | 8.255 | n/a | False | 7.951 | 7.563 | 7.174 | 6.397 | 4.844 |
| level_b200 | 1 | 48 | 8 | 2.487 | [-1.90, 5.96] | False | 0.190 | 0.156 | 0.123 | 0.056 | -0.077 |
| level_b200 | 5 | 40 | 34 | 4.044 | [0.57, 9.38] | True | 3.213 | 3.009 | 2.806 | 2.398 | 1.584 |
| level_b200 | 20 | 10 | 10 | 8.255 | n/a | False | 7.951 | 7.563 | 7.174 | 6.397 | 4.844 |
| disp_h100 | 1 | 48 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 40 | 34 | 3.232 | [-0.07, 7.99] | False | 2.785 | 2.583 | 2.382 | 1.979 | 1.173 |
| disp_h100 | 20 | 10 | 10 | 8.255 | n/a | False | 7.951 | 7.563 | 7.174 | 6.397 | 4.844 |
| disp_b200 | 1 | 48 | 7 | 0.791 | [-3.26, 4.94] | False | 0.097 | 0.068 | 0.039 | -0.019 | -0.134 |
| disp_b200 | 5 | 40 | 33 | 3.927 | [0.48, 9.09] | True | 3.131 | 2.933 | 2.736 | 2.340 | 1.550 |
| disp_b200 | 20 | 10 | 10 | 8.255 | n/a | False | 7.951 | 7.563 | 7.174 | 6.397 | 4.844 |
| avail_h100 | 1 | 48 | 9 | -1.950 | [-4.27, 0.78] | False | -0.075 | -0.112 | -0.149 | -0.223 | -0.370 |
| avail_h100 | 5 | 40 | 34 | 2.580 | [-0.01, 5.82] | False | 2.365 | 2.163 | 1.962 | 1.559 | 0.753 |
| avail_h100 | 20 | 10 | 10 | 0.897 | n/a | False | 2.727 | 2.410 | 2.093 | 1.459 | 0.192 |
| avail_b200 | 1 | 48 | 8 | -2.317 | [-4.75, 0.34] | False | -0.109 | -0.142 | -0.174 | -0.240 | -0.371 |
| avail_b200 | 5 | 40 | 34 | 3.482 | [0.27, 8.08] | True | 2.913 | 2.710 | 2.508 | 2.103 | 1.293 |
| avail_b200 | 20 | 10 | 10 | 8.255 | n/a | False | 7.951 | 7.563 | 7.174 | 6.397 | 4.844 |

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
| disp_h100|h5 | False | False | False | False | False |
| disp_h100|h20 | False | False | False | False | False |
| disp_b200|h1 | False | False | False | False | False |
| disp_b200|h5 | False | False | True | False | False |
| disp_b200|h20 | False | False | False | False | False |
| avail_h100|h1 | False | False | False | False | False |
| avail_h100|h5 | False | False | False | False | False |
| avail_h100|h20 | False | False | False | False | False |
| avail_b200|h1 | False | False | False | False | False |
| avail_b200|h5 | False | False | True | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 68 | 30 | 0.090 | 0.042 | [-0.31, 0.27] | 0.720 | 1.000 | 0.662 | False |  |
| neocloud | level_h100 | 5 | 64 | 27 | 0.199 | 0.038 | [-0.25, 0.21] | 0.679 | 1.000 | 0.768 | False |  |
| neocloud | level_h100 | 20 | 49 | 18 | n/a | -0.185 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 68 | 26 | -0.643 | -0.313 | [-0.46, -0.15] | 0.002 | 0.072 | 0.015 | True |  |
| neocloud | level_b200 | 5 | 64 | 25 | -0.792 | -0.167 | [-0.32, 0.01] | 0.031 | 0.414 | 0.232 | False |  |
| neocloud | level_b200 | 20 | 49 | 23 | n/a | -0.281 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 68 | 52 | 0.050 | 0.038 | [-0.15, 0.23] | 0.704 | 1.000 | 0.721 | False |  |
| neocloud | disp_h100 | 5 | 64 | 49 | -0.390 | -0.131 | [-0.39, 0.11] | 0.208 | 0.997 | 0.196 | False |  |
| neocloud | disp_h100 | 20 | 49 | 41 | n/a | -0.139 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 68 | 15 | 0.245 | 0.257 | [-0.08, 0.44] | 0.003 | 0.072 | 0.044 | True |  |
| neocloud | disp_b200 | 5 | 64 | 14 | 0.273 | 0.126 | [-0.12, 0.27] | 0.080 | 0.719 | 0.268 | False |  |
| neocloud | disp_b200 | 20 | 49 | 11 | n/a | 0.227 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 68 | 21 | -0.011 | -0.093 | [-0.32, 0.15] | 0.496 | 1.000 | 0.353 | False |  |
| neocloud | avail_h100 | 5 | 64 | 18 | -0.008 | -0.033 | [-0.18, 0.11] | 0.553 | 1.000 | 0.696 | False |  |
| neocloud | avail_h100 | 20 | 49 | 13 | n/a | -0.064 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 68 | 16 | -0.010 | -0.089 | [-0.32, 0.16] | 0.519 | 1.000 | 0.397 | False |  |
| neocloud | avail_b200 | 5 | 64 | 15 | -0.010 | -0.039 | [-0.18, 0.10] | 0.458 | 1.000 | 0.643 | False |  |
| neocloud | avail_b200 | 20 | 49 | 11 | n/a | -0.074 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 68 | 30 | -0.019 | -0.024 | [-0.32, 0.16] | 0.828 | 1.000 | 0.838 | False |  |
| gpu_semis | level_h100 | 5 | 64 | 27 | 0.276 | 0.111 | [-0.18, 0.27] | 0.104 | 0.760 | 0.411 | False |  |
| gpu_semis | level_h100 | 20 | 49 | 18 | n/a | -0.150 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 68 | 26 | -0.167 | -0.214 | [-0.51, 0.05] | 0.215 | 0.997 | 0.103 | False |  |
| gpu_semis | level_b200 | 5 | 64 | 25 | -0.207 | -0.093 | [-0.28, 0.08] | 0.194 | 0.997 | 0.464 | False |  |
| gpu_semis | level_b200 | 20 | 49 | 23 | n/a | -0.284 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 68 | 52 | 0.042 | 0.085 | [-0.15, 0.35] | 0.493 | 1.000 | 0.397 | False |  |
| gpu_semis | disp_h100 | 5 | 64 | 49 | -0.121 | -0.086 | [-0.33, 0.14] | 0.362 | 1.000 | 0.429 | False |  |
| gpu_semis | disp_h100 | 20 | 49 | 41 | n/a | -0.101 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 68 | 15 | 0.090 | 0.249 | [-0.10, 0.51] | 0.113 | 0.760 | 0.044 | False |  |
| gpu_semis | disp_b200 | 5 | 64 | 14 | 0.070 | 0.068 | [-0.21, 0.26] | 0.490 | 1.000 | 0.679 | False |  |
| gpu_semis | disp_b200 | 20 | 49 | 11 | n/a | 0.238 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 68 | 21 | -0.001 | -0.017 | [-0.24, 0.28] | 0.905 | 1.000 | 0.897 | False |  |
| gpu_semis | avail_h100 | 5 | 64 | 18 | -0.006 | -0.051 | [-0.17, 0.07] | 0.292 | 1.000 | 0.411 | False |  |
| gpu_semis | avail_h100 | 20 | 49 | 13 | n/a | -0.043 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 68 | 16 | -0.000 | -0.003 | [-0.23, 0.29] | 0.982 | 1.000 | 0.971 | False |  |
| gpu_semis | avail_b200 | 5 | 64 | 15 | -0.007 | -0.059 | [-0.18, 0.06] | 0.222 | 0.997 | 0.339 | False |  |
| gpu_semis | avail_b200 | 20 | 49 | 11 | n/a | -0.055 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 68 | 30 | -0.042 | -0.031 | [-0.21, 0.09] | 0.679 | 1.000 | 0.765 | False |  |
| power_capacity | level_h100 | 5 | 64 | 27 | 0.282 | 0.082 | [-0.11, 0.27] | 0.247 | 1.000 | 0.482 | False |  |
| power_capacity | level_h100 | 20 | 49 | 18 | n/a | 0.069 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 68 | 26 | -0.341 | -0.259 | [-0.42, -0.08] | 0.025 | 0.414 | 0.015 | False |  |
| power_capacity | level_b200 | 5 | 64 | 25 | -0.050 | -0.016 | [-0.27, 0.14] | 0.820 | 1.000 | 0.929 | False |  |
| power_capacity | level_b200 | 20 | 49 | 23 | n/a | -0.033 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 68 | 52 | 0.101 | 0.120 | [-0.08, 0.33] | 0.277 | 1.000 | 0.353 | False |  |
| power_capacity | disp_h100 | 5 | 64 | 49 | -0.113 | -0.058 | [-0.33, 0.18] | 0.593 | 1.000 | 0.571 | False |  |
| power_capacity | disp_h100 | 20 | 49 | 41 | n/a | -0.068 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 68 | 15 | 0.104 | 0.170 | [-0.13, 0.32] | 0.070 | 0.719 | 0.206 | False |  |
| power_capacity | disp_b200 | 5 | 64 | 14 | -0.022 | -0.016 | [-0.21, 0.17] | 0.852 | 1.000 | 0.857 | False |  |
| power_capacity | disp_b200 | 20 | 49 | 11 | n/a | 0.018 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 68 | 21 | 0.000 | 0.004 | [-0.17, 0.23] | 0.974 | 1.000 | 0.956 | False |  |
| power_capacity | avail_h100 | 5 | 64 | 18 | -0.007 | -0.043 | [-0.21, 0.15] | 0.508 | 1.000 | 0.429 | False |  |
| power_capacity | avail_h100 | 20 | 49 | 13 | n/a | -0.023 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 68 | 16 | 0.001 | 0.008 | [-0.17, 0.23] | 0.947 | 1.000 | 0.956 | False |  |
| power_capacity | avail_b200 | 5 | 64 | 15 | -0.007 | -0.044 | [-0.21, 0.15] | 0.517 | 1.000 | 0.446 | False |  |
| power_capacity | avail_b200 | 20 | 49 | 11 | n/a | -0.025 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.04 [-0.12, 0.22] | -0.03 [-0.22, 0.25] |
| -4 | -0.00 [-0.12, 0.12] | -0.29 [-0.45, -0.10] |
| -3 | -0.10 [-0.24, 0.05] | 0.05 [-0.14, 0.33] |
| -2 | -0.22 [-0.40, -0.01] | -0.15 [-0.31, 0.04] |
| -1 | 0.05 [-0.28, 0.38] | -0.23 [-0.35, -0.07] |
| 0 | -0.30 [-0.48, -0.11] | 0.01 [-0.30, 0.20] |
| 1 | -0.08 [-0.32, 0.19] | -0.08 [-0.36, 0.17] |
| 2 | 0.08 [-0.09, 0.21] | 0.08 [-0.07, 0.32] |
| 3 | 0.03 [-0.19, 0.30] | 0.10 [-0.16, 0.23] |
| 4 | -0.01 [-0.11, 0.07] | 0.17 [-0.23, 0.36] |
| 5 | -0.01 [-0.15, 0.16] | 0.08 [-0.24, 0.25] |

