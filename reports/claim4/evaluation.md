# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-26T05:25:05.430710+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `b8cae6ae1faff218...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 8 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 49 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 69 | 2026-08-20 | 2026-11-25 | 0.33 | 0.44 |
| 5 | 65 | 2026-08-20 | 2026-11-19 | 0.34 | 0.45 |
| 20 | 50 | 2026-08-20 | 2026-10-29 | 0.39 | 0.51 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 69 | 31 | 0.005 | 0.003 | [-0.31, 0.19] | 0.975 | 1.000 | 0.986 | False |  |
| level_h100 | 5 | 65 | 28 | 0.133 | 0.038 | [-0.25, 0.20] | 0.627 | 1.000 | 0.737 | False |  |
| level_h100 | 20 | 50 | 18 | n/a | -0.129 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 69 | 26 | -0.389 | -0.303 | [-0.48, -0.12] | 0.014 | 0.253 | 0.014 | False |  |
| level_b200 | 5 | 65 | 25 | -0.336 | -0.106 | [-0.29, 0.06] | 0.172 | 1.000 | 0.351 | False |  |
| level_b200 | 20 | 50 | 23 | n/a | -0.249 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 69 | 53 | 0.049 | 0.060 | [-0.14, 0.29] | 0.582 | 1.000 | 0.565 | False |  |
| disp_h100 | 5 | 65 | 50 | -0.225 | -0.113 | [-0.37, 0.11] | 0.263 | 1.000 | 0.246 | False |  |
| disp_h100 | 20 | 50 | 42 | n/a | -0.075 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 69 | 15 | 0.147 | 0.245 | [-0.09, 0.44] | 0.015 | 0.263 | 0.072 | False |  |
| disp_b200 | 5 | 65 | 14 | 0.107 | 0.074 | [-0.16, 0.23] | 0.383 | 1.000 | 0.632 | False |  |
| disp_b200 | 20 | 50 | 11 | n/a | 0.204 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 69 | 21 | -0.004 | -0.051 | [-0.26, 0.20] | 0.700 | 1.000 | 0.594 | False |  |
| avail_h100 | 5 | 65 | 19 | -0.008 | -0.045 | [-0.18, 0.09] | 0.399 | 1.000 | 0.386 | False |  |
| avail_h100 | 20 | 50 | 14 | n/a | -0.025 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 69 | 16 | -0.003 | -0.046 | [-0.26, 0.20] | 0.736 | 1.000 | 0.667 | False |  |
| avail_b200 | 5 | 65 | 15 | -0.008 | -0.047 | [-0.19, 0.09] | 0.356 | 1.000 | 0.491 | False |  |
| avail_b200 | 20 | 50 | 12 | n/a | -0.034 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 49 | -0.142 | -0.161 | 0.586 | 0.785 | 0.531 | 1.000 | False | 49 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 41 | 0.122 | -0.062 | 0.025 | 0.446 | 0.805 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 11 | 0.854 | 0.001 | n/a | n/a | 1.000 | n/a | False | 11 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 49 | -0.096 | -0.114 | 0.032 | 0.039 | 0.571 | 0.710 | False | 49 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 41 | 0.184 | 0.013 | 0.002 | 0.097 | 0.805 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 11 | 0.873 | 0.135 | n/a | n/a | 1.000 | n/a | False | 11 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 49 | -0.002 | -0.018 | 0.389 | 0.892 | 0.531 | 1.000 | False | 49 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 41 | 0.154 | -0.023 | 0.016 | 0.856 | 0.732 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 11 | 0.819 | -0.231 | n/a | n/a | 1.000 | n/a | False | 11 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 49 | -0.001 | -0.017 | 0.109 | 0.159 | 0.551 | 1.000 | False | 49 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 41 | 0.163 | -0.012 | 0.005 | 0.415 | 0.756 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 11 | 0.861 | 0.050 | n/a | n/a | 1.000 | n/a | False | 11 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 49 | -0.877 | -0.907 | 0.269 | 0.425 | 0.531 | 1.000 | False | 49 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 41 | -22.020 | -26.840 | 0.487 | 0.630 | 0.707 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 11 | -56.160 | -388.968 | n/a | n/a | 0.545 | n/a | False | 11 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 49 | -0.097 | -0.115 | 0.662 | 0.838 | 0.531 | 1.000 | False | 49 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 41 | 0.181 | 0.010 | 0.008 | 0.129 | 0.732 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 11 | 0.853 | 0.000 | n/a | n/a | 1.000 | n/a | False | 11 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 49 | 10 | -2.040 | [-5.74, 2.54] | False | -0.058 | -0.098 | -0.139 | -0.220 | -0.382 |
| level_h100 | 5 | 41 | 34 | 3.821 | [0.32, 8.59] | True | 3.060 | 2.862 | 2.663 | 2.266 | 1.471 |
| level_h100 | 20 | 11 | 11 | 7.965 | n/a | False | 8.496 | 8.108 | 7.720 | 6.943 | 5.389 |
| level_b200 | 1 | 49 | 8 | 2.461 | [-1.92, 5.98] | False | 0.186 | 0.153 | 0.120 | 0.055 | -0.075 |
| level_b200 | 5 | 41 | 35 | 4.232 | [0.59, 9.74] | True | 3.363 | 3.158 | 2.954 | 2.545 | 1.727 |
| level_b200 | 20 | 11 | 11 | 7.965 | n/a | False | 8.496 | 8.108 | 7.720 | 6.943 | 5.389 |
| disp_h100 | 1 | 49 | 1 | -2.268 | [-4.01, 0.00] | False | -0.053 | -0.057 | -0.061 | -0.069 | -0.085 |
| disp_h100 | 5 | 41 | 35 | 3.426 | [0.02, 8.13] | True | 2.945 | 2.743 | 2.540 | 2.135 | 1.326 |
| disp_h100 | 20 | 11 | 11 | 7.965 | n/a | False | 8.496 | 8.108 | 7.720 | 6.943 | 5.389 |
| disp_b200 | 1 | 49 | 8 | -0.404 | [-3.98, 3.91] | False | 0.042 | 0.010 | -0.023 | -0.087 | -0.216 |
| disp_b200 | 5 | 41 | 34 | 4.116 | [0.54, 9.45] | True | 3.283 | 3.084 | 2.885 | 2.488 | 1.693 |
| disp_b200 | 20 | 11 | 11 | 7.965 | n/a | False | 8.496 | 8.108 | 7.720 | 6.943 | 5.389 |
| avail_h100 | 1 | 49 | 10 | -2.591 | [-5.02, -0.05] | False | -0.126 | -0.166 | -0.207 | -0.287 | -0.448 |
| avail_h100 | 5 | 41 | 35 | 2.781 | [0.07, 6.12] | True | 2.535 | 2.333 | 2.130 | 1.726 | 0.916 |
| avail_h100 | 20 | 11 | 11 | 0.228 | n/a | False | 1.211 | 0.904 | 0.597 | -0.018 | -1.247 |
| avail_b200 | 1 | 49 | 9 | -2.944 | [-5.37, -0.48] | False | -0.159 | -0.195 | -0.232 | -0.304 | -0.449 |
| avail_b200 | 5 | 41 | 35 | 3.674 | [0.41, 8.23] | True | 3.070 | 2.867 | 2.663 | 2.256 | 1.443 |
| avail_b200 | 20 | 11 | 11 | 7.965 | n/a | False | 8.496 | 8.108 | 7.720 | 6.943 | 5.389 |

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
| neocloud | level_h100 | 1 | 69 | 31 | 0.083 | 0.038 | [-0.32, 0.27] | 0.743 | 1.000 | 0.754 | False |  |
| neocloud | level_h100 | 5 | 65 | 28 | 0.038 | 0.007 | [-0.29, 0.17] | 0.940 | 1.000 | 0.895 | False |  |
| neocloud | level_h100 | 20 | 50 | 18 | n/a | -0.183 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 69 | 26 | -0.650 | -0.314 | [-0.46, -0.16] | 0.001 | 0.064 | 0.014 | True |  |
| neocloud | level_b200 | 5 | 65 | 25 | -0.772 | -0.161 | [-0.31, 0.02] | 0.038 | 0.508 | 0.193 | False |  |
| neocloud | level_b200 | 20 | 50 | 23 | n/a | -0.277 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 69 | 53 | 0.029 | 0.022 | [-0.17, 0.22] | 0.828 | 1.000 | 0.797 | False |  |
| neocloud | disp_h100 | 5 | 65 | 50 | -0.414 | -0.137 | [-0.40, 0.08] | 0.178 | 1.000 | 0.070 | False |  |
| neocloud | disp_h100 | 20 | 50 | 42 | n/a | -0.081 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 69 | 15 | 0.245 | 0.255 | [-0.09, 0.44] | 0.002 | 0.064 | 0.058 | False |  |
| neocloud | disp_b200 | 5 | 65 | 14 | 0.273 | 0.124 | [-0.11, 0.27] | 0.084 | 0.756 | 0.246 | False |  |
| neocloud | disp_b200 | 20 | 50 | 11 | n/a | 0.227 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 69 | 21 | -0.011 | -0.092 | [-0.32, 0.14] | 0.496 | 1.000 | 0.362 | False |  |
| neocloud | avail_h100 | 5 | 65 | 19 | -0.009 | -0.035 | [-0.17, 0.10] | 0.523 | 1.000 | 0.649 | False |  |
| neocloud | avail_h100 | 20 | 50 | 14 | n/a | -0.030 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 69 | 16 | -0.010 | -0.088 | [-0.32, 0.15] | 0.519 | 1.000 | 0.391 | False |  |
| neocloud | avail_b200 | 5 | 65 | 15 | -0.010 | -0.038 | [-0.18, 0.10] | 0.455 | 1.000 | 0.649 | False |  |
| neocloud | avail_b200 | 20 | 50 | 12 | n/a | -0.039 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 69 | 31 | -0.024 | -0.029 | [-0.33, 0.15] | 0.791 | 1.000 | 0.812 | False |  |
| gpu_semis | level_h100 | 5 | 65 | 28 | 0.201 | 0.082 | [-0.22, 0.25] | 0.278 | 1.000 | 0.561 | False |  |
| gpu_semis | level_h100 | 20 | 50 | 18 | n/a | -0.148 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 69 | 26 | -0.172 | -0.214 | [-0.51, 0.03] | 0.199 | 1.000 | 0.130 | False |  |
| gpu_semis | level_b200 | 5 | 65 | 25 | -0.199 | -0.089 | [-0.27, 0.09] | 0.219 | 1.000 | 0.544 | False |  |
| gpu_semis | level_b200 | 20 | 50 | 23 | n/a | -0.278 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 69 | 53 | 0.029 | 0.056 | [-0.16, 0.32] | 0.653 | 1.000 | 0.667 | False |  |
| gpu_semis | disp_h100 | 5 | 65 | 50 | -0.131 | -0.093 | [-0.34, 0.12] | 0.322 | 1.000 | 0.333 | False |  |
| gpu_semis | disp_h100 | 20 | 50 | 42 | n/a | -0.038 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 69 | 15 | 0.091 | 0.242 | [-0.10, 0.51] | 0.106 | 0.821 | 0.087 | False |  |
| gpu_semis | disp_b200 | 5 | 65 | 14 | 0.069 | 0.068 | [-0.21, 0.25] | 0.495 | 1.000 | 0.684 | False |  |
| gpu_semis | disp_b200 | 20 | 50 | 11 | n/a | 0.236 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 69 | 21 | -0.001 | -0.016 | [-0.25, 0.29] | 0.905 | 1.000 | 0.942 | False |  |
| gpu_semis | avail_h100 | 5 | 65 | 19 | -0.006 | -0.052 | [-0.17, 0.06] | 0.269 | 1.000 | 0.404 | False |  |
| gpu_semis | avail_h100 | 20 | 50 | 14 | n/a | -0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 69 | 16 | -0.000 | -0.003 | [-0.24, 0.30] | 0.980 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 65 | 15 | -0.007 | -0.059 | [-0.17, 0.06] | 0.218 | 1.000 | 0.368 | False |  |
| gpu_semis | avail_b200 | 20 | 50 | 12 | n/a | -0.015 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 69 | 31 | -0.045 | -0.033 | [-0.21, 0.08] | 0.656 | 1.000 | 0.841 | False |  |
| power_capacity | level_h100 | 5 | 65 | 28 | 0.160 | 0.047 | [-0.19, 0.22] | 0.530 | 1.000 | 0.702 | False |  |
| power_capacity | level_h100 | 20 | 50 | 18 | n/a | 0.069 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 69 | 26 | -0.345 | -0.260 | [-0.41, -0.09] | 0.023 | 0.419 | 0.014 | False |  |
| power_capacity | level_b200 | 5 | 65 | 25 | -0.036 | -0.011 | [-0.27, 0.15] | 0.872 | 1.000 | 0.912 | False |  |
| power_capacity | level_b200 | 20 | 50 | 23 | n/a | -0.034 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 69 | 53 | 0.090 | 0.107 | [-0.10, 0.32] | 0.333 | 1.000 | 0.290 | False |  |
| power_capacity | disp_h100 | 5 | 65 | 50 | -0.131 | -0.066 | [-0.31, 0.16] | 0.534 | 1.000 | 0.491 | False |  |
| power_capacity | disp_h100 | 20 | 50 | 42 | n/a | -0.072 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 69 | 15 | 0.104 | 0.169 | [-0.13, 0.32] | 0.068 | 0.733 | 0.246 | False |  |
| power_capacity | disp_b200 | 5 | 65 | 14 | -0.022 | -0.016 | [-0.21, 0.16] | 0.854 | 1.000 | 0.842 | False |  |
| power_capacity | disp_b200 | 20 | 50 | 11 | n/a | 0.018 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 69 | 21 | 0.000 | 0.004 | [-0.17, 0.22] | 0.974 | 1.000 | 0.971 | False |  |
| power_capacity | avail_h100 | 5 | 65 | 19 | -0.008 | -0.045 | [-0.21, 0.14] | 0.484 | 1.000 | 0.439 | False |  |
| power_capacity | avail_h100 | 20 | 50 | 14 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 69 | 16 | 0.001 | 0.007 | [-0.17, 0.23] | 0.948 | 1.000 | 0.942 | False |  |
| power_capacity | avail_b200 | 5 | 65 | 15 | -0.007 | -0.043 | [-0.21, 0.15] | 0.519 | 1.000 | 0.474 | False |  |
| power_capacity | avail_b200 | 20 | 50 | 12 | n/a | -0.031 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.04 [-0.12, 0.21] | -0.03 [-0.21, 0.24] |
| -4 | -0.01 [-0.11, 0.11] | -0.29 [-0.44, -0.11] |
| -3 | -0.10 [-0.23, 0.04] | 0.04 [-0.13, 0.31] |
| -2 | -0.22 [-0.41, -0.02] | -0.15 [-0.32, 0.04] |
| -1 | 0.05 [-0.28, 0.36] | -0.23 [-0.35, -0.07] |
| 0 | -0.30 [-0.48, -0.12] | 0.00 [-0.31, 0.19] |
| 1 | -0.08 [-0.32, 0.18] | -0.08 [-0.35, 0.18] |
| 2 | 0.11 [-0.05, 0.26] | 0.12 [-0.06, 0.38] |
| 3 | 0.02 [-0.19, 0.28] | 0.06 [-0.27, 0.22] |
| 4 | -0.01 [-0.12, 0.06] | 0.20 [-0.17, 0.38] |
| 5 | -0.02 [-0.15, 0.15] | 0.08 [-0.24, 0.25] |

