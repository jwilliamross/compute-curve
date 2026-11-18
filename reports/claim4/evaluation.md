# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-18T04:42:47.516316+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `1292b1bcbe219dfd...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 5 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 43 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 63 | 2026-08-20 | 2026-11-17 | 0.35 | 0.46 |
| 5 | 59 | 2026-08-20 | 2026-11-11 | 0.36 | 0.47 |
| 20 | 44 | 2026-08-20 | 2026-10-21 | 0.41 | 0.54 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 63 | 27 | 0.063 | 0.048 | [-0.35, 0.24] | 0.658 | 1.000 | 0.730 | False |  |
| level_h100 | 5 | 59 | 25 | -0.290 | -0.056 | [-0.26, 0.20] | 0.603 | 1.000 | 0.627 | False |  |
| level_h100 | 20 | 44 | 14 | n/a | -0.135 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 63 | 25 | -0.401 | -0.341 | [-0.51, -0.15] | 0.011 | 0.197 | 0.016 | False |  |
| level_b200 | 5 | 59 | 24 | -0.382 | -0.127 | [-0.31, 0.02] | 0.096 | 1.000 | 0.431 | False |  |
| level_b200 | 20 | 44 | 22 | n/a | -0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 63 | 49 | 0.069 | 0.093 | [-0.12, 0.32] | 0.460 | 1.000 | 0.540 | False |  |
| disp_h100 | 5 | 59 | 47 | -0.210 | -0.108 | [-0.39, 0.14] | 0.329 | 1.000 | 0.235 | False |  |
| disp_h100 | 20 | 44 | 37 | n/a | -0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 63 | 14 | 0.143 | 0.266 | [-0.08, 0.45] | 0.015 | 0.253 | 0.032 | False |  |
| disp_b200 | 5 | 59 | 13 | 0.162 | 0.115 | [-0.09, 0.25] | 0.063 | 1.000 | 0.333 | False |  |
| disp_b200 | 20 | 44 | 7 | n/a | 0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 63 | 18 | -0.004 | -0.055 | [-0.29, 0.22] | 0.712 | 1.000 | 0.698 | False |  |
| avail_h100 | 5 | 59 | 17 | -0.008 | -0.047 | [-0.21, 0.10] | 0.419 | 1.000 | 0.353 | False |  |
| avail_h100 | 20 | 44 | 11 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 63 | 15 | -0.003 | -0.047 | [-0.28, 0.22] | 0.760 | 1.000 | 0.762 | False |  |
| avail_b200 | 5 | 59 | 14 | -0.009 | -0.056 | [-0.21, 0.09] | 0.311 | 1.000 | 0.353 | False |  |
| avail_b200 | 20 | 44 | 9 | n/a | -0.038 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 5 | -0.081 | n/a | 1.000 | 1.000 | False | insufficient events (5 < 10); descriptive only |
| H100 | 5 | 3 | 0.974 | n/a | 1.000 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.733 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 43 | -0.220 | -0.203 | 0.687 | 0.744 | 0.488 | 1.000 | False | 43 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 35 | 0.009 | -0.102 | 0.079 | 0.579 | 0.771 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 5 | 0.832 | 0.016 | n/a | n/a | 1.000 | n/a | False | 5 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 43 | -0.165 | -0.149 | 0.051 | 0.038 | 0.535 | 0.924 | False | 43 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 35 | 0.121 | 0.023 | 0.012 | 0.065 | 0.771 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 5 | 0.883 | 0.313 | n/a | n/a | 1.000 | n/a | False | 5 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 43 | -0.031 | -0.017 | 0.788 | 0.810 | 0.488 | 1.000 | False | 43 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 35 | 0.068 | -0.036 | 0.068 | 0.982 | 0.686 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 5 | 0.860 | 0.181 | n/a | n/a | 1.000 | n/a | False | 5 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 43 | -0.043 | -0.029 | 0.194 | 0.175 | 0.512 | 1.000 | False | 43 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 35 | 0.105 | 0.005 | 0.028 | 0.244 | 0.714 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 5 | 0.841 | 0.066 | n/a | n/a | 1.000 | n/a | False | 5 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 43 | -1.249 | -1.218 | 0.370 | 0.426 | 0.488 | 1.000 | False | 43 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 35 | -29.060 | -32.406 | 0.535 | 0.631 | 0.657 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 5 | -136.440 | -804.710 | n/a | n/a | 0.400 | n/a | False | 5 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 43 | -0.172 | -0.155 | 0.828 | 0.841 | 0.488 | 1.000 | False | 43 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 35 | 0.112 | 0.013 | 0.040 | 0.120 | 0.686 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 5 | 0.829 | 0.000 | n/a | n/a | 1.000 | n/a | False | 5 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 43 | 9 | -1.326 | [-5.73, 4.34] | False | -0.006 | -0.048 | -0.089 | -0.172 | -0.338 |
| level_h100 | 5 | 35 | 28 | 2.792 | [-0.67, 7.26] | False | 2.308 | 2.117 | 1.925 | 1.542 | 0.775 |
| level_h100 | 20 | 5 | 5 | 7.038 | n/a | False | 6.570 | 6.181 | 5.793 | 5.016 | 3.462 |
| level_b200 | 1 | 43 | 7 | 1.898 | [-3.43, 6.13] | False | 0.159 | 0.126 | 0.094 | 0.029 | -0.102 |
| level_b200 | 5 | 35 | 29 | 3.246 | [-0.43, 8.61] | False | 2.663 | 2.464 | 2.266 | 1.869 | 1.074 |
| level_b200 | 20 | 5 | 5 | 7.038 | n/a | False | 6.570 | 6.181 | 5.793 | 5.016 | 3.462 |
| disp_h100 | 1 | 43 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 35 | 29 | 2.409 | [-1.09, 6.84] | False | 2.173 | 1.977 | 1.781 | 1.389 | 0.605 |
| disp_h100 | 20 | 5 | 5 | 7.038 | n/a | False | 6.570 | 6.181 | 5.793 | 5.016 | 3.462 |
| disp_b200 | 1 | 43 | 6 | -0.003 | [-4.27, 4.50] | False | 0.055 | 0.027 | -0.000 | -0.055 | -0.165 |
| disp_b200 | 5 | 35 | 28 | 3.122 | [-0.48, 8.30] | False | 2.569 | 2.377 | 2.185 | 1.802 | 1.035 |
| disp_b200 | 20 | 5 | 5 | 7.038 | n/a | False | 6.570 | 6.181 | 5.793 | 5.016 | 3.462 |
| avail_h100 | 1 | 43 | 9 | -2.060 | [-4.53, 0.93] | False | -0.084 | -0.125 | -0.166 | -0.249 | -0.414 |
| avail_h100 | 5 | 35 | 29 | 1.716 | [-0.91, 4.48] | False | 1.693 | 1.497 | 1.301 | 0.909 | 0.125 |
| avail_h100 | 20 | 5 | 5 | -0.338 | n/a | False | -0.173 | -0.454 | -0.736 | -1.298 | -2.423 |
| avail_b200 | 1 | 43 | 8 | -2.448 | [-5.02, 0.33] | False | -0.122 | -0.158 | -0.195 | -0.268 | -0.414 |
| avail_b200 | 5 | 35 | 29 | 2.663 | [-0.62, 7.04] | False | 2.320 | 2.122 | 1.925 | 1.531 | 0.742 |
| avail_b200 | 20 | 5 | 5 | 7.038 | n/a | False | 6.570 | 6.181 | 5.793 | 5.016 | 3.462 |

## Gate

| pair | G1 | G2 | G3 | G4 | validated |
|---|---|---|---|---|---|
| level_h100|h1 | False | False | False | False | False |
| level_h100|h5 | False | False | False | False | False |
| level_h100|h20 | False | False | False | False | False |
| level_b200|h1 | False | False | False | False | False |
| level_b200|h5 | False | False | False | False | False |
| level_b200|h20 | False | False | False | False | False |
| disp_h100|h1 | False | False | False | False | False |
| disp_h100|h5 | False | False | False | False | False |
| disp_h100|h20 | False | False | False | False | False |
| disp_b200|h1 | False | False | False | False | False |
| disp_b200|h5 | False | False | False | False | False |
| disp_b200|h20 | False | False | False | False | False |
| avail_h100|h1 | False | False | False | False | False |
| avail_h100|h5 | False | False | False | False | False |
| avail_h100|h20 | False | False | False | False | False |
| avail_b200|h1 | False | False | False | False | False |
| avail_b200|h5 | False | False | False | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 63 | 27 | 0.219 | 0.104 | [-0.35, 0.33] | 0.352 | 1.000 | 0.492 | False |  |
| neocloud | level_h100 | 5 | 59 | 25 | -1.190 | -0.151 | [-0.33, 0.08] | 0.134 | 0.803 | 0.255 | False |  |
| neocloud | level_h100 | 20 | 44 | 14 | n/a | -0.191 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 63 | 25 | -0.666 | -0.352 | [-0.49, -0.21] | 0.001 | 0.016 | 0.016 | True |  |
| neocloud | level_b200 | 5 | 59 | 24 | -0.841 | -0.185 | [-0.33, -0.02] | 0.015 | 0.200 | 0.255 | False |  |
| neocloud | level_b200 | 20 | 44 | 22 | n/a | -0.288 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 63 | 49 | 0.060 | 0.050 | [-0.14, 0.26] | 0.666 | 1.000 | 0.730 | False |  |
| neocloud | disp_h100 | 5 | 59 | 47 | -0.384 | -0.131 | [-0.42, 0.11] | 0.241 | 1.000 | 0.157 | False |  |
| neocloud | disp_h100 | 20 | 44 | 37 | n/a | -0.141 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 63 | 14 | 0.238 | 0.275 | [-0.07, 0.46] | 0.003 | 0.046 | 0.016 | True |  |
| neocloud | disp_b200 | 5 | 59 | 13 | 0.380 | 0.178 | [0.01, 0.30] | 0.000 | 0.001 | 0.157 | False |  |
| neocloud | disp_b200 | 20 | 44 | 7 | n/a | 0.231 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 63 | 18 | -0.010 | -0.100 | [-0.35, 0.16] | 0.514 | 1.000 | 0.397 | False |  |
| neocloud | avail_h100 | 5 | 59 | 17 | -0.009 | -0.037 | [-0.19, 0.11] | 0.536 | 1.000 | 0.529 | False |  |
| neocloud | avail_h100 | 20 | 44 | 11 | n/a | -0.051 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 63 | 15 | -0.009 | -0.094 | [-0.35, 0.17] | 0.547 | 1.000 | 0.429 | False |  |
| neocloud | avail_b200 | 5 | 59 | 14 | -0.012 | -0.049 | [-0.21, 0.09] | 0.393 | 1.000 | 0.471 | False |  |
| neocloud | avail_b200 | 20 | 44 | 9 | n/a | -0.061 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 63 | 27 | -0.010 | -0.012 | [-0.41, 0.18] | 0.919 | 1.000 | 0.952 | False |  |
| gpu_semis | level_h100 | 5 | 59 | 25 | 0.012 | 0.003 | [-0.23, 0.24] | 0.975 | 1.000 | 1.000 | False |  |
| gpu_semis | level_h100 | 20 | 44 | 14 | n/a | -0.166 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 63 | 25 | -0.188 | -0.259 | [-0.58, 0.02] | 0.173 | 0.850 | 0.032 | False |  |
| gpu_semis | level_b200 | 5 | 59 | 24 | -0.228 | -0.106 | [-0.29, 0.07] | 0.132 | 0.803 | 0.529 | False |  |
| gpu_semis | level_b200 | 20 | 44 | 22 | n/a | -0.304 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 63 | 49 | 0.044 | 0.095 | [-0.17, 0.37] | 0.506 | 1.000 | 0.413 | False |  |
| gpu_semis | disp_h100 | 5 | 59 | 47 | -0.121 | -0.088 | [-0.34, 0.15] | 0.392 | 1.000 | 0.294 | False |  |
| gpu_semis | disp_h100 | 20 | 44 | 37 | n/a | -0.102 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 63 | 14 | 0.091 | 0.273 | [-0.09, 0.56] | 0.096 | 0.744 | 0.048 | False |  |
| gpu_semis | disp_b200 | 5 | 59 | 13 | 0.109 | 0.108 | [-0.15, 0.28] | 0.154 | 0.830 | 0.392 | False |  |
| gpu_semis | disp_b200 | 20 | 44 | 7 | n/a | 0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 63 | 18 | -0.001 | -0.018 | [-0.27, 0.31] | 0.911 | 1.000 | 0.952 | False |  |
| gpu_semis | avail_h100 | 5 | 59 | 17 | -0.006 | -0.055 | [-0.18, 0.07] | 0.293 | 1.000 | 0.314 | False |  |
| gpu_semis | avail_h100 | 20 | 44 | 11 | n/a | -0.040 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 63 | 15 | -0.000 | -0.003 | [-0.26, 0.33] | 0.984 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 59 | 14 | -0.008 | -0.068 | [-0.19, 0.06] | 0.193 | 0.867 | 0.275 | False |  |
| gpu_semis | avail_b200 | 20 | 44 | 9 | n/a | -0.052 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 63 | 27 | -0.019 | -0.013 | [-0.24, 0.10] | 0.860 | 1.000 | 0.921 | False |  |
| power_capacity | level_h100 | 5 | 59 | 25 | 0.307 | 0.059 | [-0.16, 0.30] | 0.563 | 1.000 | 0.471 | False |  |
| power_capacity | level_h100 | 20 | 44 | 14 | n/a | 0.088 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 63 | 25 | -0.350 | -0.275 | [-0.43, -0.09] | 0.022 | 0.240 | 0.048 | False |  |
| power_capacity | level_b200 | 5 | 59 | 24 | -0.076 | -0.025 | [-0.30, 0.13] | 0.718 | 1.000 | 0.882 | False |  |
| power_capacity | level_b200 | 20 | 44 | 22 | n/a | -0.017 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 63 | 49 | 0.103 | 0.128 | [-0.09, 0.35] | 0.285 | 1.000 | 0.333 | False |  |
| power_capacity | disp_h100 | 5 | 59 | 47 | -0.124 | -0.063 | [-0.33, 0.19] | 0.576 | 1.000 | 0.569 | False |  |
| power_capacity | disp_h100 | 20 | 44 | 37 | n/a | -0.008 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 63 | 14 | 0.100 | 0.172 | [-0.11, 0.31] | 0.075 | 0.672 | 0.206 | False |  |
| power_capacity | disp_b200 | 5 | 59 | 13 | -0.003 | -0.002 | [-0.20, 0.17] | 0.979 | 1.000 | 0.980 | False |  |
| power_capacity | disp_b200 | 20 | 44 | 7 | n/a | -0.000 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 63 | 18 | 0.000 | 0.004 | [-0.18, 0.23] | 0.970 | 1.000 | 0.984 | False |  |
| power_capacity | avail_h100 | 5 | 59 | 17 | -0.007 | -0.045 | [-0.23, 0.15] | 0.500 | 1.000 | 0.392 | False |  |
| power_capacity | avail_h100 | 20 | 44 | 11 | n/a | 0.049 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 63 | 15 | 0.001 | 0.012 | [-0.18, 0.23] | 0.925 | 1.000 | 0.952 | False |  |
| power_capacity | avail_b200 | 5 | 59 | 14 | -0.008 | -0.047 | [-0.23, 0.15] | 0.491 | 1.000 | 0.412 | False |  |
| power_capacity | avail_b200 | 20 | 44 | 9 | n/a | 0.048 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.15, 0.21] | -0.10 [-0.26, 0.19] |
| -4 | -0.02 [-0.13, 0.10] | -0.33 [-0.49, -0.13] |
| -3 | -0.11 [-0.26, 0.04] | 0.08 [-0.15, 0.39] |
| -2 | -0.22 [-0.42, 0.02] | -0.12 [-0.33, 0.11] |
| -1 | 0.08 [-0.26, 0.42] | -0.23 [-0.36, -0.06] |
| 0 | -0.34 [-0.51, -0.15] | 0.05 [-0.35, 0.24] |
| 1 | -0.06 [-0.29, 0.22] | 0.02 [-0.30, 0.26] |
| 2 | 0.06 [-0.20, 0.22] | 0.06 [-0.10, 0.34] |
| 3 | 0.01 [-0.25, 0.30] | 0.10 [-0.05, 0.24] |
| 4 | -0.03 [-0.15, 0.05] | -0.01 [-0.27, 0.19] |
| 5 | -0.03 [-0.19, 0.15] | -0.08 [-0.25, 0.11] |

