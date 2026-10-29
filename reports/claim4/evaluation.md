# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-29T02:47:53.763595+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `d34344cd62024e85...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 29 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 3 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 49 | 2026-08-20 | 2026-10-28 | 0.39 | 0.51 |
| 5 | 45 | 2026-08-20 | 2026-10-22 | 0.41 | 0.53 |
| 20 | 30 | 2026-08-20 | 2026-10-01 | 0.49 | 0.63 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 49 | 18 | -0.997 | -0.312 | [-0.52, 0.03] | 0.004 | 0.069 | 0.061 | False |  |
| level_h100 | 5 | 45 | 15 | -1.089 | -0.132 | [-0.31, 0.16] | 0.120 | 1.000 | 0.378 | False |  |
| level_h100 | 20 | 30 | 4 | n/a | -0.127 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 49 | 23 | -0.349 | -0.297 | [-0.54, -0.11] | 0.069 | 1.000 | 0.061 | False |  |
| level_b200 | 5 | 45 | 23 | -0.553 | -0.183 | [-0.42, -0.02] | 0.080 | 1.000 | 0.324 | False |  |
| level_b200 | 20 | 30 | 10 | n/a | -0.238 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 49 | 41 | 0.018 | 0.021 | [-0.17, 0.24] | 0.862 | 1.000 | 0.878 | False |  |
| disp_h100 | 5 | 45 | 38 | -0.207 | -0.094 | [-0.39, 0.14] | 0.416 | 1.000 | 0.514 | False |  |
| disp_h100 | 20 | 30 | 24 | n/a | -0.121 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 49 | 11 | 0.171 | 0.328 | [0.02, 0.52] | 0.001 | 0.011 | 0.020 | True |  |
| disp_b200 | 5 | 45 | 7 | 0.243 | 0.181 | [0.02, 0.33] | 0.000 | 0.001 | 0.243 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 30 | 4 | n/a | 0.112 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 49 | 13 | -0.005 | -0.087 | [-0.34, 0.28] | 0.591 | 1.000 | 0.571 | False |  |
| avail_h100 | 5 | 45 | 11 | -0.010 | -0.054 | [-0.29, 0.14] | 0.459 | 1.000 | 0.297 | False |  |
| avail_h100 | 20 | 30 | 2 | n/a | -0.156 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 49 | 11 | -0.005 | -0.087 | [-0.33, 0.27] | 0.589 | 1.000 | 0.551 | False |  |
| avail_b200 | 5 | 45 | 9 | -0.009 | -0.051 | [-0.24, 0.13] | 0.472 | 1.000 | 0.351 | False | insufficient variation (9 non-zero < 10) |
| avail_b200 | 20 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 29 | -0.017 | -0.008 | 0.073 | 0.026 | 0.552 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 21 | 0.212 | 0.011 | 0.001 | 0.046 | 0.857 | 0.739 | False | 21 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 29 | -0.374 | -0.362 | 0.107 | 0.099 | 0.586 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 21 | 0.270 | 0.084 | 0.000 | 0.016 | 0.857 | 0.295 | False | 21 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 29 | -0.033 | -0.024 | 0.757 | 0.927 | 0.517 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 21 | 0.171 | -0.041 | 0.017 | 1.000 | 0.714 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 29 | -0.026 | -0.017 | 0.112 | 0.094 | 0.586 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 21 | 0.256 | 0.065 | 0.001 | 0.028 | 0.762 | 0.469 | False | 21 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 29 | -1.991 | -1.966 | 0.313 | 0.384 | 0.586 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 21 | -47.701 | -60.145 | 0.550 | 0.635 | 0.667 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 29 | -0.235 | -0.225 | 0.768 | 0.805 | 0.586 | 1.000 | False | 29 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 21 | 0.211 | 0.009 | 0.023 | 0.148 | 0.714 | 1.000 | False | 21 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 29 | 3 | 4.587 | [0.00, 7.31] | False | 0.172 | 0.151 | 0.131 | 0.089 | 0.007 |
| level_h100 | 5 | 21 | 15 | 6.111 | [2.53, 10.94] | True | 3.609 | 3.438 | 3.267 | 2.924 | 2.240 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 29 | 6 | 0.488 | [-6.29, 6.98] | False | 0.105 | 0.064 | 0.022 | -0.060 | -0.226 |
| level_b200 | 5 | 21 | 15 | 6.801 | [2.78, 14.98] | True | 3.972 | 3.801 | 3.630 | 3.288 | 2.603 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 29 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 21 | 15 | 4.323 | [-0.82, 12.86] | False | 3.156 | 2.989 | 2.822 | 2.488 | 1.821 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 29 | 3 | 3.597 | [-2.95, 5.76] | False | 0.094 | 0.073 | 0.053 | 0.012 | -0.069 |
| disp_b200 | 5 | 21 | 14 | 6.416 | [2.48, 14.69] | True | 3.816 | 3.656 | 3.496 | 3.177 | 2.538 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 29 | 7 | -2.933 | [-5.63, 1.07] | False | -0.125 | -0.173 | -0.220 | -0.316 | -0.506 |
| avail_h100 | 5 | 21 | 15 | 2.851 | [1.14, 5.51] | True | 2.356 | 2.189 | 2.022 | 1.689 | 1.021 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 29 | 6 | -3.591 | [-6.23, -0.11] | False | -0.181 | -0.222 | -0.263 | -0.344 | -0.507 |
| avail_b200 | 5 | 21 | 15 | 5.006 | [1.61, 11.13] | True | 3.401 | 3.232 | 3.063 | 2.724 | 2.048 |
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
| disp_b200|h1 | True | False | False | False | False |
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
| neocloud | level_h100 | 1 | 49 | 18 | -1.601 | -0.310 | [-0.50, 0.04] | 0.002 | 0.018 | 0.082 | False |  |
| neocloud | level_h100 | 5 | 45 | 15 | -2.551 | -0.199 | [-0.35, -0.01] | 0.000 | 0.001 | 0.216 | False |  |
| neocloud | level_h100 | 20 | 30 | 4 | n/a | -0.180 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 49 | 23 | -0.643 | -0.338 | [-0.51, -0.16] | 0.011 | 0.090 | 0.041 | True |  |
| neocloud | level_b200 | 5 | 45 | 23 | -1.123 | -0.239 | [-0.42, -0.06] | 0.013 | 0.090 | 0.216 | False |  |
| neocloud | level_b200 | 20 | 30 | 10 | n/a | -0.280 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 49 | 41 | -0.001 | -0.001 | [-0.18, 0.22] | 0.993 | 1.000 | 1.000 | False |  |
| neocloud | disp_h100 | 5 | 45 | 38 | -0.380 | -0.111 | [-0.42, 0.12] | 0.361 | 0.954 | 0.405 | False |  |
| neocloud | disp_h100 | 20 | 30 | 24 | n/a | -0.122 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 49 | 11 | 0.299 | 0.355 | [0.05, 0.52] | 0.000 | 0.000 | 0.020 | True |  |
| neocloud | disp_b200 | 5 | 45 | 7 | 0.440 | 0.211 | [0.05, 0.37] | 0.000 | 0.000 | 0.189 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 30 | 4 | n/a | 0.154 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 49 | 13 | -0.014 | -0.143 | [-0.41, 0.22] | 0.385 | 0.954 | 0.286 | False |  |
| neocloud | avail_h100 | 5 | 45 | 11 | -0.015 | -0.056 | [-0.31, 0.11] | 0.424 | 0.954 | 0.324 | False |  |
| neocloud | avail_h100 | 20 | 30 | 2 | n/a | -0.186 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 49 | 11 | -0.015 | -0.147 | [-0.41, 0.22] | 0.371 | 0.954 | 0.286 | False |  |
| neocloud | avail_b200 | 5 | 45 | 9 | -0.016 | -0.059 | [-0.25, 0.10] | 0.385 | 0.954 | 0.324 | False | insufficient variation (9 non-zero < 10) |
| neocloud | avail_b200 | 20 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 49 | 18 | -0.681 | -0.345 | [-0.62, 0.04] | 0.013 | 0.090 | 0.020 | True |  |
| gpu_semis | level_h100 | 5 | 45 | 15 | -0.540 | -0.100 | [-0.31, 0.23] | 0.368 | 0.954 | 0.595 | False |  |
| gpu_semis | level_h100 | 20 | 30 | 4 | n/a | -0.188 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 49 | 23 | -0.154 | -0.212 | [-0.64, 0.08] | 0.361 | 0.954 | 0.184 | False |  |
| gpu_semis | level_b200 | 5 | 45 | 23 | -0.342 | -0.173 | [-0.40, 0.04] | 0.052 | 0.256 | 0.351 | False |  |
| gpu_semis | level_b200 | 20 | 30 | 10 | n/a | -0.268 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 49 | 41 | -0.004 | -0.008 | [-0.24, 0.19] | 0.950 | 1.000 | 0.980 | False |  |
| gpu_semis | disp_h100 | 5 | 45 | 38 | -0.127 | -0.088 | [-0.31, 0.11] | 0.398 | 0.954 | 0.514 | False |  |
| gpu_semis | disp_h100 | 20 | 30 | 24 | n/a | -0.056 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 49 | 11 | 0.106 | 0.329 | [-0.08, 0.62] | 0.086 | 0.385 | 0.041 | False |  |
| gpu_semis | disp_b200 | 5 | 45 | 7 | 0.190 | 0.217 | [0.04, 0.37] | 0.000 | 0.001 | 0.243 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 30 | 4 | n/a | 0.140 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 49 | 13 | 0.000 | 0.004 | [-0.28, 0.39] | 0.983 | 1.000 | 0.980 | False |  |
| gpu_semis | avail_h100 | 5 | 45 | 11 | -0.006 | -0.056 | [-0.27, 0.12] | 0.419 | 0.954 | 0.297 | False |  |
| gpu_semis | avail_h100 | 20 | 30 | 2 | n/a | -0.056 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 49 | 11 | 0.000 | 0.010 | [-0.27, 0.39] | 0.952 | 1.000 | 0.918 | False |  |
| gpu_semis | avail_b200 | 5 | 45 | 9 | -0.006 | -0.057 | [-0.24, 0.12] | 0.409 | 0.954 | 0.405 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 49 | 18 | -0.708 | -0.205 | [-0.36, 0.09] | 0.022 | 0.132 | 0.224 | False |  |
| power_capacity | level_h100 | 5 | 45 | 15 | -0.176 | -0.022 | [-0.24, 0.38] | 0.852 | 1.000 | 0.838 | False |  |
| power_capacity | level_h100 | 20 | 30 | 4 | n/a | 0.125 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 49 | 23 | -0.251 | -0.198 | [-0.39, -0.05] | 0.111 | 0.462 | 0.224 | False |  |
| power_capacity | level_b200 | 5 | 45 | 23 | -0.195 | -0.067 | [-0.38, 0.16] | 0.556 | 1.000 | 0.649 | False |  |
| power_capacity | level_b200 | 20 | 30 | 10 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 49 | 41 | 0.060 | 0.066 | [-0.15, 0.32] | 0.645 | 1.000 | 0.612 | False |  |
| power_capacity | disp_h100 | 5 | 45 | 38 | -0.113 | -0.053 | [-0.36, 0.20] | 0.642 | 1.000 | 0.811 | False |  |
| power_capacity | disp_h100 | 20 | 30 | 24 | n/a | -0.178 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 49 | 11 | 0.108 | 0.192 | [-0.13, 0.34] | 0.025 | 0.133 | 0.184 | False |  |
| power_capacity | disp_b200 | 5 | 45 | 7 | 0.100 | 0.077 | [-0.13, 0.25] | 0.266 | 0.954 | 0.486 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 30 | 4 | n/a | -0.062 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 49 | 13 | -0.002 | -0.030 | [-0.22, 0.26] | 0.822 | 1.000 | 0.796 | False |  |
| power_capacity | avail_h100 | 5 | 45 | 11 | -0.007 | -0.040 | [-0.28, 0.21] | 0.630 | 1.000 | 0.324 | False |  |
| power_capacity | avail_h100 | 20 | 30 | 2 | n/a | -0.171 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 49 | 11 | -0.002 | -0.027 | [-0.21, 0.25] | 0.840 | 1.000 | 0.837 | False |  |
| power_capacity | avail_b200 | 5 | 45 | 9 | -0.004 | -0.025 | [-0.23, 0.23] | 0.771 | 1.000 | 0.568 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.22, 0.19] | 0.12 [-0.13, 0.25] |
| -4 | -0.02 [-0.20, 0.15] | -0.15 [-0.31, 0.08] |
| -3 | -0.18 [-0.31, 0.00] | -0.14 [-0.32, 0.03] |
| -2 | -0.15 [-0.36, 0.13] | -0.13 [-0.32, 0.23] |
| -1 | -0.08 [-0.33, 0.15] | -0.28 [-0.41, -0.01] |
| 0 | -0.30 [-0.54, -0.11] | -0.31 [-0.52, 0.03] |
| 1 | 0.04 [-0.24, 0.35] | -0.05 [-0.23, 0.34] |
| 2 | 0.02 [-0.40, 0.24] | 0.03 [-0.28, 0.28] |
| 3 | -0.10 [-0.34, 0.29] | 0.07 [-0.27, 0.24] |
| 4 | -0.07 [-0.28, 0.01] | -0.10 [-0.49, -0.00] |
| 5 | -0.13 [-0.31, 0.03] | -0.07 [-0.34, 0.25] |

