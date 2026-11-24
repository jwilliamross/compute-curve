# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-24T07:05:27.798707+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `dc4a1fa294bd71ab...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 8 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 47 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 67 | 2026-08-20 | 2026-11-23 | 0.34 | 0.45 |
| 5 | 63 | 2026-08-20 | 2026-11-17 | 0.35 | 0.46 |
| 20 | 48 | 2026-08-20 | 2026-10-27 | 0.39 | 0.52 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 67 | 30 | 0.008 | 0.006 | [-0.30, 0.20] | 0.957 | 1.000 | 0.910 | False |  |
| level_h100 | 5 | 63 | 27 | 0.252 | 0.073 | [-0.21, 0.25] | 0.309 | 1.000 | 0.473 | False |  |
| level_h100 | 20 | 48 | 17 | n/a | -0.135 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 67 | 26 | -0.392 | -0.318 | [-0.50, -0.13] | 0.014 | 0.243 | 0.015 | False |  |
| level_b200 | 5 | 63 | 25 | -0.366 | -0.119 | [-0.31, 0.04] | 0.125 | 1.000 | 0.291 | False |  |
| level_b200 | 20 | 48 | 23 | n/a | -0.257 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 67 | 52 | 0.064 | 0.081 | [-0.12, 0.30] | 0.474 | 1.000 | 0.448 | False |  |
| disp_h100 | 5 | 63 | 49 | -0.209 | -0.108 | [-0.36, 0.12] | 0.303 | 1.000 | 0.364 | False |  |
| disp_h100 | 20 | 48 | 40 | n/a | -0.113 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 67 | 15 | 0.147 | 0.256 | [-0.07, 0.45] | 0.015 | 0.255 | 0.030 | False |  |
| disp_b200 | 5 | 63 | 14 | 0.107 | 0.076 | [-0.17, 0.24] | 0.365 | 1.000 | 0.600 | False |  |
| disp_b200 | 20 | 48 | 10 | n/a | 0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 67 | 21 | -0.004 | -0.053 | [-0.26, 0.21] | 0.700 | 1.000 | 0.672 | False |  |
| avail_h100 | 5 | 63 | 18 | -0.007 | -0.044 | [-0.20, 0.09] | 0.432 | 1.000 | 0.436 | False |  |
| avail_h100 | 20 | 48 | 12 | n/a | -0.028 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 67 | 16 | -0.003 | -0.048 | [-0.26, 0.21] | 0.735 | 1.000 | 0.746 | False |  |
| avail_b200 | 5 | 63 | 15 | -0.008 | -0.049 | [-0.20, 0.10] | 0.360 | 1.000 | 0.473 | False |  |
| avail_b200 | 20 | 48 | 10 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 47 | -0.162 | -0.179 | 0.610 | 0.785 | 0.532 | 1.000 | False | 47 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 39 | 0.082 | -0.077 | 0.039 | 0.485 | 0.795 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 9 | 0.895 | 0.013 | n/a | n/a | 1.000 | n/a | False | 9 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 47 | -0.109 | -0.125 | 0.033 | 0.038 | 0.574 | 0.688 | False | 47 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 39 | 0.163 | 0.018 | 0.003 | 0.077 | 0.795 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 9 | 0.927 | 0.308 | n/a | n/a | 1.000 | n/a | False | 9 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 47 | -0.002 | -0.016 | 0.394 | 0.840 | 0.532 | 1.000 | False | 47 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 39 | 0.123 | -0.028 | 0.024 | 0.910 | 0.718 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 9 | 0.900 | 0.058 | n/a | n/a | 1.000 | n/a | False | 9 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 47 | -0.004 | -0.019 | 0.115 | 0.158 | 0.553 | 1.000 | False | 47 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 39 | 0.136 | -0.013 | 0.010 | 0.408 | 0.744 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 9 | 0.900 | 0.052 | n/a | n/a | 1.000 | n/a | False | 9 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 47 | -0.981 | -1.010 | 0.281 | 0.425 | 0.532 | 1.000 | False | 47 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 39 | -25.184 | -29.701 | 0.508 | 0.631 | 0.692 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 9 | -78.168 | -746.109 | n/a | n/a | 0.556 | n/a | False | 9 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 47 | -0.112 | -0.128 | 0.691 | 0.838 | 0.532 | 1.000 | False | 47 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 39 | 0.156 | 0.011 | 0.014 | 0.128 | 0.718 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 9 | 0.894 | 0.000 | n/a | n/a | 1.000 | n/a | False | 9 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 47 | 9 | -1.269 | [-5.24, 3.85] | False | -0.006 | -0.044 | -0.082 | -0.157 | -0.309 |
| level_h100 | 5 | 39 | 32 | 3.416 | [0.09, 8.09] | True | 2.718 | 2.521 | 2.325 | 1.931 | 1.145 |
| level_h100 | 20 | 9 | 9 | 10.100 | n/a | False | 7.250 | 6.861 | 6.473 | 5.696 | 4.143 |
| level_b200 | 1 | 47 | 8 | 2.513 | [-1.62, 5.87] | False | 0.194 | 0.160 | 0.126 | 0.058 | -0.079 |
| level_b200 | 5 | 39 | 33 | 3.841 | [0.40, 9.15] | True | 3.036 | 2.833 | 2.630 | 2.225 | 1.414 |
| level_b200 | 20 | 9 | 9 | 10.100 | n/a | False | 7.250 | 6.861 | 6.473 | 5.696 | 4.143 |
| disp_h100 | 1 | 47 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 39 | 33 | 3.019 | [-0.34, 7.81] | False | 2.596 | 2.396 | 2.195 | 1.794 | 0.993 |
| disp_h100 | 20 | 9 | 9 | 10.100 | n/a | False | 7.250 | 6.861 | 6.473 | 5.696 | 4.143 |
| disp_b200 | 1 | 47 | 7 | 0.799 | [-3.44, 4.99] | False | 0.099 | 0.069 | 0.040 | -0.019 | -0.137 |
| disp_b200 | 5 | 39 | 32 | 3.722 | [0.31, 9.03] | True | 2.951 | 2.755 | 2.558 | 2.165 | 1.379 |
| disp_b200 | 20 | 9 | 9 | 10.100 | n/a | False | 7.250 | 6.861 | 6.473 | 5.696 | 4.143 |
| avail_h100 | 1 | 47 | 9 | -1.971 | [-4.33, 1.02] | False | -0.077 | -0.114 | -0.152 | -0.228 | -0.378 |
| avail_h100 | 5 | 39 | 33 | 2.354 | [-0.07, 5.56] | False | 2.166 | 1.965 | 1.765 | 1.364 | 0.562 |
| avail_h100 | 20 | 9 | 9 | 0.382 | n/a | False | 1.446 | 1.137 | 0.828 | 0.210 | -1.027 |
| avail_b200 | 1 | 47 | 8 | -2.341 | [-4.77, 0.45] | False | -0.111 | -0.145 | -0.178 | -0.245 | -0.379 |
| avail_b200 | 5 | 39 | 33 | 3.271 | [0.12, 7.65] | True | 2.728 | 2.526 | 2.325 | 1.922 | 1.115 |
| avail_b200 | 20 | 9 | 9 | 10.100 | n/a | False | 7.250 | 6.861 | 6.473 | 5.696 | 4.143 |

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
| neocloud | level_h100 | 1 | 67 | 30 | 0.087 | 0.042 | [-0.30, 0.28] | 0.729 | 1.000 | 0.731 | False |  |
| neocloud | level_h100 | 5 | 63 | 27 | 0.198 | 0.038 | [-0.25, 0.23] | 0.683 | 1.000 | 0.727 | False |  |
| neocloud | level_h100 | 20 | 48 | 17 | n/a | -0.189 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 67 | 26 | -0.655 | -0.326 | [-0.47, -0.17] | 0.001 | 0.062 | 0.015 | True |  |
| neocloud | level_b200 | 5 | 63 | 25 | -0.814 | -0.174 | [-0.33, -0.00] | 0.024 | 0.327 | 0.182 | False |  |
| neocloud | level_b200 | 20 | 48 | 23 | n/a | -0.286 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 67 | 52 | 0.049 | 0.038 | [-0.15, 0.24] | 0.712 | 1.000 | 0.821 | False |  |
| neocloud | disp_h100 | 5 | 63 | 49 | -0.392 | -0.133 | [-0.39, 0.10] | 0.208 | 0.989 | 0.309 | False |  |
| neocloud | disp_h100 | 20 | 48 | 40 | n/a | -0.127 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 67 | 15 | 0.246 | 0.263 | [-0.07, 0.45] | 0.002 | 0.062 | 0.045 | True |  |
| neocloud | disp_b200 | 5 | 63 | 14 | 0.274 | 0.128 | [-0.12, 0.28] | 0.076 | 0.680 | 0.291 | False |  |
| neocloud | disp_b200 | 20 | 48 | 10 | n/a | 0.228 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 67 | 21 | -0.011 | -0.095 | [-0.31, 0.17] | 0.497 | 1.000 | 0.418 | False |  |
| neocloud | avail_h100 | 5 | 63 | 18 | -0.008 | -0.033 | [-0.18, 0.11] | 0.557 | 1.000 | 0.691 | False |  |
| neocloud | avail_h100 | 20 | 48 | 12 | n/a | -0.039 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 67 | 16 | -0.010 | -0.091 | [-0.32, 0.17] | 0.520 | 1.000 | 0.463 | False |  |
| neocloud | avail_b200 | 5 | 63 | 15 | -0.010 | -0.040 | [-0.19, 0.10] | 0.461 | 1.000 | 0.636 | False |  |
| neocloud | avail_b200 | 20 | 48 | 10 | n/a | -0.048 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 67 | 30 | -0.021 | -0.026 | [-0.33, 0.17] | 0.818 | 1.000 | 0.881 | False |  |
| gpu_semis | level_h100 | 5 | 63 | 27 | 0.276 | 0.113 | [-0.19, 0.29] | 0.102 | 0.716 | 0.473 | False |  |
| gpu_semis | level_h100 | 20 | 48 | 17 | n/a | -0.158 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 67 | 26 | -0.173 | -0.228 | [-0.53, 0.03] | 0.197 | 0.989 | 0.060 | False |  |
| gpu_semis | level_b200 | 5 | 63 | 25 | -0.219 | -0.100 | [-0.28, 0.07] | 0.163 | 0.976 | 0.455 | False |  |
| gpu_semis | level_b200 | 20 | 48 | 23 | n/a | -0.292 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 67 | 52 | 0.042 | 0.087 | [-0.15, 0.36] | 0.504 | 1.000 | 0.299 | False |  |
| gpu_semis | disp_h100 | 5 | 63 | 49 | -0.122 | -0.088 | [-0.33, 0.13] | 0.359 | 1.000 | 0.436 | False |  |
| gpu_semis | disp_h100 | 20 | 48 | 40 | n/a | -0.079 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 67 | 15 | 0.091 | 0.257 | [-0.09, 0.53] | 0.106 | 0.716 | 0.060 | False |  |
| gpu_semis | disp_b200 | 5 | 63 | 14 | 0.070 | 0.070 | [-0.21, 0.26] | 0.483 | 1.000 | 0.618 | False |  |
| gpu_semis | disp_b200 | 20 | 48 | 10 | n/a | 0.241 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 67 | 21 | -0.001 | -0.017 | [-0.25, 0.28] | 0.905 | 1.000 | 0.970 | False |  |
| gpu_semis | avail_h100 | 5 | 63 | 18 | -0.006 | -0.052 | [-0.17, 0.07] | 0.299 | 1.000 | 0.418 | False |  |
| gpu_semis | avail_h100 | 20 | 48 | 12 | n/a | 0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 67 | 16 | -0.000 | -0.004 | [-0.24, 0.30] | 0.980 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 63 | 15 | -0.007 | -0.060 | [-0.18, 0.07] | 0.226 | 0.989 | 0.345 | False |  |
| gpu_semis | avail_b200 | 20 | 48 | 10 | n/a | -0.008 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 67 | 30 | -0.043 | -0.032 | [-0.21, 0.08] | 0.670 | 1.000 | 0.821 | False |  |
| power_capacity | level_h100 | 5 | 63 | 27 | 0.281 | 0.083 | [-0.12, 0.27] | 0.238 | 0.989 | 0.509 | False |  |
| power_capacity | level_h100 | 20 | 48 | 17 | n/a | 0.070 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 67 | 26 | -0.349 | -0.270 | [-0.43, -0.10] | 0.022 | 0.327 | 0.015 | False |  |
| power_capacity | level_b200 | 5 | 63 | 25 | -0.065 | -0.021 | [-0.29, 0.13] | 0.765 | 1.000 | 0.836 | False |  |
| power_capacity | level_b200 | 20 | 48 | 23 | n/a | -0.033 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 67 | 52 | 0.101 | 0.122 | [-0.08, 0.33] | 0.283 | 1.000 | 0.343 | False |  |
| power_capacity | disp_h100 | 5 | 63 | 49 | -0.114 | -0.059 | [-0.32, 0.18] | 0.591 | 1.000 | 0.618 | False |  |
| power_capacity | disp_h100 | 20 | 48 | 40 | n/a | -0.070 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 67 | 15 | 0.104 | 0.174 | [-0.11, 0.33] | 0.066 | 0.680 | 0.164 | False |  |
| power_capacity | disp_b200 | 5 | 63 | 14 | -0.022 | -0.016 | [-0.21, 0.17] | 0.851 | 1.000 | 0.927 | False |  |
| power_capacity | disp_b200 | 20 | 48 | 10 | n/a | 0.018 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 67 | 21 | 0.000 | 0.004 | [-0.18, 0.23] | 0.974 | 1.000 | 0.985 | False |  |
| power_capacity | avail_h100 | 5 | 63 | 18 | -0.007 | -0.044 | [-0.22, 0.14] | 0.508 | 1.000 | 0.418 | False |  |
| power_capacity | avail_h100 | 20 | 48 | 12 | n/a | -0.027 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 67 | 16 | 0.001 | 0.008 | [-0.17, 0.23] | 0.949 | 1.000 | 0.970 | False |  |
| power_capacity | avail_b200 | 5 | 63 | 15 | -0.007 | -0.044 | [-0.21, 0.15] | 0.515 | 1.000 | 0.382 | False |  |
| power_capacity | avail_b200 | 20 | 48 | 10 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.04 [-0.13, 0.21] | -0.03 [-0.23, 0.25] |
| -4 | -0.01 [-0.12, 0.12] | -0.30 [-0.45, -0.12] |
| -3 | -0.11 [-0.24, 0.03] | 0.04 [-0.16, 0.32] |
| -2 | -0.23 [-0.42, -0.01] | -0.16 [-0.32, 0.03] |
| -1 | 0.05 [-0.31, 0.38] | -0.24 [-0.37, -0.08] |
| 0 | -0.32 [-0.50, -0.13] | 0.01 [-0.30, 0.20] |
| 1 | -0.04 [-0.27, 0.25] | -0.01 [-0.28, 0.23] |
| 2 | 0.08 [-0.11, 0.22] | 0.03 [-0.14, 0.30] |
| 3 | 0.02 [-0.21, 0.29] | 0.15 [-0.01, 0.25] |
| 4 | -0.02 [-0.12, 0.06] | 0.18 [-0.24, 0.37] |
| 5 | -0.02 [-0.16, 0.15] | 0.09 [-0.24, 0.28] |

