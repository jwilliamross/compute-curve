# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-20T02:04:49.426431+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `4e862818472c4959...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 22 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 42 | 2026-08-20 | 2026-10-19 | 0.42 | 0.55 |
| 5 | 38 | 2026-08-20 | 2026-10-13 | 0.44 | 0.57 |
| 20 | 23 | 2026-08-20 | 2026-09-22 | 0.56 | 0.69 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 42 | 13 | -0.983 | -0.333 | [-0.55, 0.07] | 0.008 | 0.123 | 0.048 | False |  |
| level_h100 | 5 | 38 | 9 | -1.065 | -0.135 | [-0.32, 0.17] | 0.098 | 1.000 | 0.500 | False | insufficient variation (9 non-zero < 10) |
| level_h100 | 20 | 23 | 3 | n/a | -0.037 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 42 | 20 | -0.334 | -0.308 | [-0.56, -0.09] | 0.082 | 1.000 | 0.095 | False |  |
| level_b200 | 5 | 38 | 16 | -0.531 | -0.183 | [-0.40, -0.01] | 0.062 | 0.926 | 0.300 | False |  |
| level_b200 | 20 | 23 | 6 | n/a | -0.204 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 42 | 35 | -0.065 | -0.077 | [-0.27, 0.16] | 0.495 | 1.000 | 0.643 | False |  |
| disp_h100 | 5 | 38 | 32 | 0.036 | 0.014 | [-0.28, 0.22] | 0.891 | 1.000 | 0.867 | False |  |
| disp_h100 | 20 | 23 | 18 | n/a | -0.080 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 42 | 7 | 0.168 | 0.349 | [-0.03, 0.55] | 0.002 | 0.028 | 0.024 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 38 | 7 | 0.241 | 0.188 | [0.02, 0.35] | 0.000 | 0.001 | 0.267 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 23 | 1 | n/a | 0.097 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 42 | 9 | -0.005 | -0.066 | [-0.36, 0.35] | 0.757 | 1.000 | 0.690 | False | insufficient variation (9 non-zero < 10) |
| avail_h100 | 5 | 38 | 6 | -0.010 | -0.033 | [-0.42, 0.19] | 0.764 | 1.000 | 0.633 | False | insufficient variation (6 non-zero < 10) |
| avail_h100 | 20 | 23 | 2 | n/a | -0.216 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 42 | 7 | -0.005 | -0.069 | [-0.34, 0.34] | 0.744 | 1.000 | 0.667 | False | insufficient variation (7 non-zero < 10) |
| avail_b200 | 5 | 38 | 4 | -0.008 | -0.029 | [-0.29, 0.19] | 0.779 | 1.000 | 0.767 | False | insufficient variation (4 non-zero < 10) |
| avail_b200 | 20 | 23 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 22 | -0.009 | -0.018 | 0.041 | 0.031 | 0.591 | 0.744 | False | 22 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 14 | 0.157 | 0.012 | n/a | n/a | 0.929 | n/a | False | 14 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 22 | -0.494 | -0.509 | 0.103 | 0.108 | 0.636 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 14 | 0.230 | 0.097 | n/a | n/a | 0.929 | n/a | False | 14 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 22 | 0.001 | -0.009 | 0.412 | 0.892 | 0.591 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 14 | 0.115 | -0.036 | n/a | n/a | 0.714 | n/a | False | 14 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 22 | -0.023 | -0.033 | 0.092 | 0.104 | 0.636 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 14 | 0.216 | 0.081 | n/a | n/a | 0.786 | n/a | False | 14 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 22 | -2.629 | -2.663 | 0.305 | 0.401 | 0.545 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 14 | -65.838 | -77.309 | n/a | n/a | 0.714 | n/a | False | 14 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 22 | -0.292 | -0.305 | 0.779 | 0.832 | 0.545 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 14 | 0.209 | 0.074 | n/a | n/a | 0.786 | n/a | False | 14 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 22 | 3 | 5.310 | [0.00, 8.12] | False | 0.227 | 0.200 | 0.172 | 0.118 | 0.009 |
| level_h100 | 5 | 14 | 8 | 5.813 | [2.34, 11.45] | True | 3.471 | 3.334 | 3.197 | 2.923 | 2.375 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 22 | 6 | 0.557 | [-5.34, 7.31] | False | 0.138 | 0.084 | 0.029 | -0.080 | -0.298 |
| level_b200 | 5 | 14 | 8 | 6.823 | [2.73, 18.76] | True | 4.015 | 3.878 | 3.741 | 3.468 | 2.920 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 22 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 14 | 8 | 3.531 | [-3.29, 13.92] | False | 2.791 | 2.661 | 2.530 | 2.269 | 1.747 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 22 | 3 | 4.141 | [-3.38, 6.73] | False | 0.123 | 0.096 | 0.070 | 0.016 | -0.092 |
| disp_b200 | 5 | 14 | 7 | 6.261 | [1.90, 16.85] | True | 3.780 | 3.661 | 3.541 | 3.301 | 2.822 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 22 | 5 | -2.935 | [-5.76, 4.39] | False | -0.150 | -0.195 | -0.240 | -0.329 | -0.507 |
| avail_h100 | 5 | 14 | 8 | 3.004 | [1.23, 7.23] | True | 2.449 | 2.315 | 2.181 | 1.914 | 1.379 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 22 | 4 | -3.733 | [-6.39, 0.00] | False | -0.224 | -0.260 | -0.295 | -0.366 | -0.508 |
| avail_b200 | 5 | 14 | 8 | 6.823 | [2.73, 18.76] | True | 4.015 | 3.878 | 3.741 | 3.468 | 2.920 |
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
| neocloud | level_h100 | 1 | 42 | 13 | -1.558 | -0.336 | [-0.53, 0.12] | 0.005 | 0.053 | 0.071 | False |  |
| neocloud | level_h100 | 5 | 38 | 9 | -2.506 | -0.205 | [-0.37, -0.01] | 0.000 | 0.000 | 0.267 | False | insufficient variation (9 non-zero < 10) |
| neocloud | level_h100 | 20 | 23 | 3 | n/a | -0.102 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 42 | 20 | -0.613 | -0.359 | [-0.55, -0.10] | 0.017 | 0.116 | 0.071 | False |  |
| neocloud | level_b200 | 5 | 38 | 16 | -1.088 | -0.243 | [-0.41, -0.02] | 0.007 | 0.060 | 0.267 | False |  |
| neocloud | level_b200 | 20 | 23 | 6 | n/a | -0.262 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 42 | 35 | -0.123 | -0.092 | [-0.31, 0.16] | 0.389 | 1.000 | 0.619 | False |  |
| neocloud | disp_h100 | 5 | 38 | 32 | 0.024 | 0.006 | [-0.29, 0.20] | 0.952 | 1.000 | 0.967 | False |  |
| neocloud | disp_h100 | 20 | 23 | 18 | n/a | -0.082 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 42 | 7 | 0.293 | 0.388 | [-0.00, 0.56] | 0.000 | 0.000 | 0.024 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 38 | 7 | 0.436 | 0.220 | [0.03, 0.39] | 0.000 | 0.000 | 0.167 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 23 | 1 | n/a | 0.154 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 42 | 9 | -0.019 | -0.169 | [-0.43, 0.23] | 0.391 | 1.000 | 0.333 | False | insufficient variation (9 non-zero < 10) |
| neocloud | avail_h100 | 5 | 38 | 6 | -0.034 | -0.076 | [-0.45, 0.12] | 0.507 | 1.000 | 0.367 | False | insufficient variation (6 non-zero < 10) |
| neocloud | avail_h100 | 20 | 23 | 2 | n/a | -0.261 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 42 | 7 | -0.020 | -0.181 | [-0.43, 0.23] | 0.357 | 1.000 | 0.238 | False | insufficient variation (7 non-zero < 10) |
| neocloud | avail_b200 | 5 | 38 | 4 | -0.035 | -0.081 | [-0.35, 0.11] | 0.452 | 1.000 | 0.533 | False | insufficient variation (4 non-zero < 10) |
| neocloud | avail_b200 | 20 | 23 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 42 | 13 | -0.700 | -0.373 | [-0.66, 0.04] | 0.010 | 0.077 | 0.048 | True |  |
| gpu_semis | level_h100 | 5 | 38 | 9 | -0.533 | -0.102 | [-0.32, 0.24] | 0.354 | 1.000 | 0.700 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 23 | 3 | n/a | -0.100 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 42 | 20 | -0.150 | -0.217 | [-0.66, 0.09] | 0.370 | 1.000 | 0.214 | False |  |
| gpu_semis | level_b200 | 5 | 38 | 16 | -0.332 | -0.172 | [-0.40, 0.11] | 0.043 | 0.212 | 0.367 | False |  |
| gpu_semis | level_b200 | 20 | 23 | 6 | n/a | -0.254 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 42 | 35 | -0.030 | -0.056 | [-0.31, 0.12] | 0.703 | 1.000 | 0.810 | False |  |
| gpu_semis | disp_h100 | 5 | 38 | 32 | -0.032 | -0.018 | [-0.28, 0.21] | 0.860 | 1.000 | 0.867 | False |  |
| gpu_semis | disp_h100 | 20 | 23 | 18 | n/a | 0.020 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 42 | 7 | 0.105 | 0.344 | [-0.10, 0.66] | 0.088 | 0.395 | 0.024 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 38 | 7 | 0.189 | 0.222 | [0.02, 0.38] | 0.000 | 0.001 | 0.267 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 23 | 1 | n/a | 0.141 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 42 | 9 | 0.004 | 0.086 | [-0.26, 0.50] | 0.703 | 1.000 | 0.571 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 38 | 6 | -0.004 | -0.023 | [-0.36, 0.18] | 0.830 | 1.000 | 0.767 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 23 | 2 | n/a | -0.085 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 42 | 7 | 0.004 | 0.095 | [-0.22, 0.51] | 0.674 | 1.000 | 0.548 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 38 | 4 | -0.005 | -0.025 | [-0.31, 0.18] | 0.814 | 1.000 | 0.867 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 23 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 42 | 13 | -0.691 | -0.213 | [-0.38, 0.11] | 0.030 | 0.182 | 0.214 | False |  |
| power_capacity | level_h100 | 5 | 38 | 9 | -0.155 | -0.020 | [-0.25, 0.42] | 0.862 | 1.000 | 0.867 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | level_h100 | 20 | 23 | 3 | n/a | 0.180 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 42 | 20 | -0.239 | -0.200 | [-0.39, -0.03] | 0.123 | 0.511 | 0.238 | False |  |
| power_capacity | level_b200 | 5 | 38 | 16 | -0.172 | -0.062 | [-0.40, 0.20] | 0.566 | 1.000 | 0.533 | False |  |
| power_capacity | level_b200 | 20 | 23 | 6 | n/a | 0.021 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 42 | 35 | -0.042 | -0.045 | [-0.24, 0.21] | 0.700 | 1.000 | 0.738 | False |  |
| power_capacity | disp_h100 | 5 | 38 | 32 | 0.115 | 0.046 | [-0.27, 0.28] | 0.688 | 1.000 | 0.767 | False |  |
| power_capacity | disp_h100 | 20 | 23 | 18 | n/a | -0.157 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 42 | 7 | 0.105 | 0.199 | [-0.19, 0.36] | 0.034 | 0.184 | 0.167 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 38 | 7 | 0.098 | 0.080 | [-0.15, 0.26] | 0.238 | 0.916 | 0.600 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 23 | 1 | n/a | -0.097 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 42 | 9 | 0.001 | 0.013 | [-0.31, 0.34] | 0.942 | 1.000 | 1.000 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 38 | 6 | 0.010 | 0.034 | [-0.39, 0.29] | 0.706 | 1.000 | 0.667 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 23 | 2 | n/a | -0.196 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 42 | 7 | 0.001 | 0.016 | [-0.21, 0.34] | 0.929 | 1.000 | 0.881 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 38 | 4 | 0.016 | 0.058 | [-0.15, 0.32] | 0.487 | 1.000 | 0.500 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 23 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.06 [-0.23, 0.19] | 0.12 [-0.16, 0.27] |
| -4 | -0.01 [-0.21, 0.18] | -0.15 [-0.31, 0.13] |
| -3 | -0.17 [-0.33, 0.06] | -0.16 [-0.38, -0.01] |
| -2 | -0.16 [-0.41, 0.17] | -0.14 [-0.36, 0.25] |
| -1 | -0.08 [-0.34, 0.19] | -0.30 [-0.44, 0.02] |
| 0 | -0.31 [-0.56, -0.09] | -0.33 [-0.55, 0.07] |
| 1 | 0.06 [-0.26, 0.40] | -0.05 [-0.25, 0.38] |
| 2 | 0.03 [-0.39, 0.28] | 0.03 [-0.30, 0.31] |
| 3 | -0.10 [-0.36, 0.38] | 0.09 [-0.20, 0.31] |
| 4 | -0.06 [-0.27, 0.02] | -0.09 [-0.44, 0.04] |
| 5 | -0.14 [-0.30, 0.02] | -0.07 [-0.36, 0.29] |

