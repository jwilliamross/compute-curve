# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-19T01:37:54.277607+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `b5b4571f7daea011...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 21 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 3 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 41 | 2026-08-20 | 2026-10-16 | 0.43 | 0.55 |
| 5 | 37 | 2026-08-20 | 2026-10-12 | 0.45 | 0.58 |
| 20 | 22 | 2026-08-20 | 2026-09-21 | 0.57 | 0.71 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 41 | 12 | -0.958 | -0.330 | [-0.55, 0.11] | 0.008 | 0.135 | 0.024 | False |  |
| level_h100 | 5 | 37 | 9 | -1.073 | -0.137 | [-0.31, 0.16] | 0.081 | 1.000 | 0.483 | False | insufficient variation (9 non-zero < 10) |
| level_h100 | 20 | 22 | 3 | n/a | -0.027 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 41 | 19 | -0.324 | -0.303 | [-0.55, -0.05] | 0.080 | 1.000 | 0.073 | False |  |
| level_b200 | 5 | 37 | 15 | -0.524 | -0.183 | [-0.40, -0.01] | 0.053 | 0.788 | 0.310 | False |  |
| level_b200 | 20 | 22 | 6 | n/a | -0.214 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 41 | 34 | 0.008 | 0.009 | [-0.21, 0.21] | 0.930 | 1.000 | 1.000 | False |  |
| disp_h100 | 5 | 37 | 31 | 0.049 | 0.019 | [-0.28, 0.23] | 0.852 | 1.000 | 0.931 | False |  |
| disp_h100 | 20 | 22 | 17 | n/a | -0.053 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 41 | 7 | 0.167 | 0.354 | [-0.03, 0.56] | 0.001 | 0.020 | 0.049 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 37 | 7 | 0.240 | 0.189 | [0.02, 0.36] | 0.000 | 0.000 | 0.276 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 22 | 1 | n/a | 0.086 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 41 | 8 | -0.008 | -0.112 | [-0.44, 0.36] | 0.608 | 1.000 | 0.439 | False | insufficient variation (8 non-zero < 10) |
| avail_h100 | 5 | 37 | 5 | 0.022 | 0.063 | [-0.45, 0.30] | 0.488 | 1.000 | 0.448 | False | insufficient variation (5 non-zero < 10) |
| avail_h100 | 20 | 22 | 2 | n/a | -0.236 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 41 | 6 | -0.008 | -0.115 | [-0.43, 0.35] | 0.595 | 1.000 | 0.415 | False | insufficient variation (6 non-zero < 10) |
| avail_b200 | 5 | 37 | 3 | 0.021 | 0.065 | [-0.24, 0.31] | 0.487 | 1.000 | 0.586 | False | insufficient variation (3 non-zero < 10) |
| avail_b200 | 20 | 22 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 3 | -2.614 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 5 | 3 | -6.126 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 21 | -0.035 | -0.031 | 0.071 | 0.046 | 0.571 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 13 | 0.146 | 0.014 | n/a | n/a | 0.923 | n/a | False | 13 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 21 | -0.558 | -0.553 | 0.119 | 0.116 | 0.619 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 13 | 0.223 | 0.103 | n/a | n/a | 0.923 | n/a | False | 13 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 21 | -0.009 | -0.006 | 0.550 | 0.805 | 0.571 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 13 | 0.100 | -0.038 | n/a | n/a | 0.692 | n/a | False | 13 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 21 | -0.039 | -0.036 | 0.110 | 0.106 | 0.619 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 13 | 0.209 | 0.087 | n/a | n/a | 0.769 | n/a | False | 13 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 21 | -2.823 | -2.810 | 0.296 | 0.373 | 0.571 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 13 | -70.206 | -81.180 | n/a | n/a | 0.692 | n/a | False | 13 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 21 | -0.307 | -0.302 | 0.764 | 0.798 | 0.571 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 13 | 0.129 | -0.006 | n/a | n/a | 0.769 | n/a | False | 13 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 21 | 2 | 4.497 | [0.00, 7.79] | False | 0.117 | 0.098 | 0.079 | 0.041 | -0.035 |
| level_h100 | 5 | 13 | 7 | 5.295 | [1.88, 10.98] | True | 3.190 | 3.061 | 2.932 | 2.674 | 2.158 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 21 | 5 | -1.576 | [-8.49, 7.51] | False | 0.025 | -0.023 | -0.071 | -0.166 | -0.356 |
| level_b200 | 5 | 13 | 7 | 6.311 | [1.97, 16.12] | True | 3.776 | 3.647 | 3.518 | 3.260 | 2.744 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 21 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 13 | 7 | 3.052 | [-3.47, 10.87] | False | 2.458 | 2.336 | 2.214 | 1.970 | 1.481 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 21 | 3 | 4.241 | [-3.46, 6.89] | False | 0.129 | 0.101 | 0.073 | 0.017 | -0.096 |
| disp_b200 | 5 | 13 | 6 | 5.754 | [1.97, 13.91] | True | 3.524 | 3.413 | 3.302 | 3.081 | 2.639 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 21 | 5 | -3.003 | [-5.69, 3.46] | False | -0.157 | -0.204 | -0.251 | -0.344 | -0.531 |
| avail_h100 | 5 | 13 | 7 | 2.512 | [0.66, 6.98] | True | 2.089 | 1.964 | 1.838 | 1.587 | 1.085 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 21 | 4 | -3.822 | [-6.56, 0.00] | False | -0.235 | -0.272 | -0.309 | -0.384 | -0.533 |
| avail_b200 | 5 | 13 | 7 | 6.311 | [1.97, 16.12] | True | 3.776 | 3.647 | 3.518 | 3.260 | 2.744 |
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
| disp_h100|h5 | False | False | False | False | False |
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
| neocloud | level_h100 | 1 | 41 | 12 | -1.526 | -0.332 | [-0.54, 0.16] | 0.005 | 0.049 | 0.024 | True |  |
| neocloud | level_h100 | 5 | 37 | 9 | -2.521 | -0.210 | [-0.37, -0.02] | 0.000 | 0.000 | 0.276 | False | insufficient variation (9 non-zero < 10) |
| neocloud | level_h100 | 20 | 22 | 3 | n/a | -0.097 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 41 | 19 | -0.600 | -0.355 | [-0.55, -0.06] | 0.016 | 0.093 | 0.049 | True |  |
| neocloud | level_b200 | 5 | 37 | 15 | -1.077 | -0.244 | [-0.41, -0.03] | 0.004 | 0.048 | 0.207 | False |  |
| neocloud | level_b200 | 20 | 22 | 6 | n/a | -0.276 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 41 | 34 | -0.036 | -0.024 | [-0.26, 0.22] | 0.822 | 1.000 | 0.878 | False |  |
| neocloud | disp_h100 | 5 | 37 | 31 | 0.047 | 0.012 | [-0.30, 0.22] | 0.906 | 1.000 | 0.862 | False |  |
| neocloud | disp_h100 | 20 | 22 | 17 | n/a | -0.056 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 41 | 7 | 0.293 | 0.391 | [-0.01, 0.57] | 0.000 | 0.000 | 0.049 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 37 | 7 | 0.434 | 0.222 | [0.03, 0.40] | 0.000 | 0.000 | 0.207 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 22 | 1 | n/a | 0.148 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 41 | 8 | -0.024 | -0.213 | [-0.51, 0.23] | 0.292 | 0.877 | 0.171 | False | insufficient variation (8 non-zero < 10) |
| neocloud | avail_h100 | 5 | 37 | 5 | 0.015 | 0.028 | [-0.47, 0.28] | 0.776 | 1.000 | 0.793 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_h100 | 20 | 22 | 2 | n/a | -0.283 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 41 | 6 | -0.025 | -0.225 | [-0.53, 0.23] | 0.264 | 0.839 | 0.195 | False | insufficient variation (6 non-zero < 10) |
| neocloud | avail_b200 | 5 | 37 | 3 | 0.009 | 0.017 | [-0.31, 0.29] | 0.871 | 1.000 | 0.828 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_b200 | 20 | 22 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 41 | 12 | -0.683 | -0.370 | [-0.67, 0.04] | 0.011 | 0.086 | 0.049 | True |  |
| gpu_semis | level_h100 | 5 | 37 | 9 | -0.538 | -0.104 | [-0.31, 0.25] | 0.335 | 0.952 | 0.690 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 22 | 3 | n/a | -0.097 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 41 | 19 | -0.143 | -0.211 | [-0.65, 0.12] | 0.379 | 1.000 | 0.220 | False |  |
| gpu_semis | level_b200 | 5 | 37 | 15 | -0.328 | -0.172 | [-0.39, 0.10] | 0.037 | 0.166 | 0.448 | False |  |
| gpu_semis | level_b200 | 20 | 22 | 6 | n/a | -0.279 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 41 | 34 | 0.023 | 0.039 | [-0.26, 0.22] | 0.748 | 1.000 | 0.854 | False |  |
| gpu_semis | disp_h100 | 5 | 37 | 31 | -0.025 | -0.014 | [-0.29, 0.21] | 0.891 | 1.000 | 0.862 | False |  |
| gpu_semis | disp_h100 | 20 | 22 | 17 | n/a | 0.066 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 41 | 7 | 0.105 | 0.350 | [-0.10, 0.66] | 0.083 | 0.321 | 0.049 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 37 | 7 | 0.189 | 0.224 | [0.04, 0.39] | 0.000 | 0.001 | 0.241 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 22 | 1 | n/a | 0.136 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 41 | 8 | 0.002 | 0.044 | [-0.34, 0.51] | 0.852 | 1.000 | 0.805 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 37 | 5 | 0.014 | 0.059 | [-0.38, 0.30] | 0.562 | 1.000 | 0.483 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 22 | 2 | n/a | -0.096 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 41 | 6 | 0.002 | 0.053 | [-0.33, 0.52] | 0.822 | 1.000 | 0.780 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 37 | 3 | 0.012 | 0.053 | [-0.30, 0.31] | 0.614 | 1.000 | 0.655 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 22 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 41 | 12 | -0.666 | -0.208 | [-0.38, 0.13] | 0.034 | 0.164 | 0.220 | False |  |
| power_capacity | level_h100 | 5 | 37 | 9 | -0.160 | -0.021 | [-0.24, 0.42] | 0.854 | 1.000 | 0.828 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | level_h100 | 20 | 22 | 3 | n/a | 0.196 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 41 | 19 | -0.229 | -0.194 | [-0.39, -0.01] | 0.120 | 0.433 | 0.171 | False |  |
| power_capacity | level_b200 | 5 | 37 | 15 | -0.168 | -0.060 | [-0.39, 0.20] | 0.563 | 1.000 | 0.586 | False |  |
| power_capacity | level_b200 | 20 | 22 | 6 | n/a | 0.027 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 41 | 34 | 0.037 | 0.035 | [-0.17, 0.26] | 0.754 | 1.000 | 0.829 | False |  |
| power_capacity | disp_h100 | 5 | 37 | 31 | 0.124 | 0.049 | [-0.26, 0.29] | 0.667 | 1.000 | 0.759 | False |  |
| power_capacity | disp_h100 | 20 | 22 | 17 | n/a | -0.142 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 41 | 7 | 0.105 | 0.201 | [-0.18, 0.37] | 0.029 | 0.157 | 0.195 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 37 | 7 | 0.098 | 0.080 | [-0.14, 0.27] | 0.226 | 0.764 | 0.586 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 22 | 1 | n/a | -0.114 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 41 | 8 | -0.002 | -0.025 | [-0.33, 0.35] | 0.889 | 1.000 | 0.878 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 37 | 5 | 0.037 | 0.112 | [-0.43, 0.36] | 0.066 | 0.274 | 0.379 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 22 | 2 | n/a | -0.204 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 41 | 6 | -0.002 | -0.022 | [-0.28, 0.34] | 0.901 | 1.000 | 0.854 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 37 | 3 | 0.044 | 0.137 | [-0.07, 0.39] | 0.013 | 0.086 | 0.345 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 22 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.07 [-0.25, 0.20] | 0.12 [-0.17, 0.28] |
| -4 | -0.01 [-0.20, 0.19] | -0.15 [-0.32, 0.14] |
| -3 | -0.19 [-0.35, 0.02] | -0.17 [-0.38, -0.01] |
| -2 | -0.16 [-0.42, 0.13] | -0.15 [-0.37, 0.23] |
| -1 | -0.09 [-0.34, 0.18] | -0.30 [-0.44, 0.01] |
| 0 | -0.30 [-0.55, -0.05] | -0.33 [-0.55, 0.11] |
| 1 | 0.06 [-0.25, 0.40] | -0.05 [-0.26, 0.38] |
| 2 | 0.03 [-0.39, 0.29] | 0.03 [-0.31, 0.32] |
| 3 | -0.10 [-0.37, 0.42] | 0.09 [-0.21, 0.29] |
| 4 | -0.06 [-0.25, 0.02] | -0.09 [-0.47, 0.03] |
| 5 | -0.11 [-0.25, 0.07] | -0.07 [-0.38, 0.33] |

