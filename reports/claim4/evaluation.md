# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-10T02:41:21.095335+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 48.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `fca86e0095f73388...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 2 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 16 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 36 | 2026-08-20 | 2026-10-09 | 0.45 | 0.58 |
| 5 | 32 | 2026-08-20 | 2026-10-05 | 0.48 | 0.61 |
| 20 | 17 | 2026-08-20 | 2026-09-14 | 0.63 | 0.77 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 36 | 8 | -0.976 | -0.396 | [-0.59, 0.11] | 0.007 | 0.107 | 0.028 | False | insufficient variation (8 non-zero < 10) |
| level_h100 | 5 | 32 | 5 | -1.104 | -0.159 | [-0.34, 0.12] | 0.012 | 0.174 | 0.333 | False | insufficient variation (5 non-zero < 10) |
| level_h100 | 20 | 17 | 3 | n/a | 0.048 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 36 | 14 | -0.314 | -0.343 | [-0.60, -0.01] | 0.089 | 1.000 | 0.028 | False |  |
| level_b200 | 5 | 32 | 11 | -0.417 | -0.163 | [-0.30, 0.31] | 0.008 | 0.117 | 0.375 | False |  |
| level_b200 | 20 | 17 | 1 | n/a | -0.005 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 36 | 30 | -0.032 | -0.038 | [-0.27, 0.18] | 0.712 | 1.000 | 0.833 | False |  |
| disp_h100 | 5 | 32 | 26 | 0.115 | 0.050 | [-0.29, 0.27] | 0.662 | 1.000 | 0.792 | False |  |
| disp_h100 | 20 | 17 | 12 | n/a | -0.252 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 36 | 7 | 0.167 | 0.417 | [-0.04, 0.59] | 0.001 | 0.021 | 0.028 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 32 | 6 | 0.189 | 0.165 | [-0.14, 0.37] | 0.000 | 0.000 | 0.250 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 20 | 17 | 1 | n/a | 0.005 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 36 | 5 | 0.015 | 0.136 | [-0.38, 0.34] | 0.140 | 1.000 | 0.444 | False | insufficient variation (5 non-zero < 10) |
| avail_h100 | 5 | 32 | 3 | -0.633 | -0.274 | [-0.49, -0.07] | 0.115 | 1.000 | 0.125 | False | insufficient variation (3 non-zero < 10) |
| avail_h100 | 20 | 17 | 2 | n/a | -0.368 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 36 | 3 | 0.013 | 0.121 | [-0.17, 0.34] | 0.256 | 1.000 | 0.472 | False | insufficient variation (3 non-zero < 10) |
| avail_b200 | 5 | 32 | 1 | -0.117 | -0.122 | [-0.26, -0.06] | 0.013 | 0.174 | 0.542 | False | insufficient variation (1 non-zero < 10) |
| avail_b200 | 20 | 17 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 2 | -3.062 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| B200 | 5 | 2 | -3.966 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| B200 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 16 | -0.041 | -0.054 | 0.031 | 0.023 | 0.562 | 0.565 | False | 16 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 8 | 0.062 | 0.027 | n/a | n/a | 0.875 | n/a | False | 8 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 16 | -1.273 | -1.300 | 0.125 | 0.125 | 0.625 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 8 | 0.188 | 0.157 | n/a | n/a | 0.875 | n/a | False | 8 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 16 | 0.012 | 0.000 | 0.299 | 0.472 | 0.562 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 8 | -0.073 | -0.114 | n/a | n/a | 0.500 | n/a | False | 8 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 16 | -0.070 | -0.083 | 0.096 | 0.101 | 0.625 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 8 | 0.168 | 0.136 | n/a | n/a | 0.625 | n/a | False | 8 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 16 | -6.030 | -6.113 | 0.114 | 0.169 | 0.500 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 8 | -2.774 | -2.917 | n/a | n/a | 0.625 | n/a | False | 8 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 16 | -0.382 | -0.398 | 0.769 | 0.827 | 0.500 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 8 | 0.036 | 0.000 | n/a | n/a | 0.625 | n/a | False | 8 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 16 | 2 | 5.180 | [0.00, 8.81] | False | 0.154 | 0.129 | 0.104 | 0.054 | -0.046 |
| level_h100 | 5 | 8 | 3 | 3.444 | n/a | False | 0.979 | 0.890 | 0.800 | 0.620 | 0.261 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 16 | 4 | -3.810 | [-10.41, 7.38] | False | -0.075 | -0.125 | -0.175 | -0.275 | -0.475 |
| level_b200 | 5 | 8 | 2 | 3.757 | n/a | False | 0.972 | 0.912 | 0.852 | 0.732 | 0.493 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 16 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 8 | 2 | -3.585 | n/a | False | -1.170 | -1.219 | -1.268 | -1.365 | -1.560 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 16 | 3 | 4.878 | [-3.97, 8.03] | False | 0.169 | 0.133 | 0.096 | 0.022 | -0.126 |
| disp_b200 | 5 | 8 | 1 | 2.510 | n/a | False | 0.561 | 0.531 | 0.501 | 0.441 | 0.322 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 16 | 3 | -2.469 | [-6.45, 5.81] | False | -0.061 | -0.098 | -0.135 | -0.208 | -0.356 |
| avail_h100 | 5 | 8 | 2 | 3.757 | n/a | False | 0.972 | 0.912 | 0.852 | 0.732 | 0.493 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 16 | 2 | -4.255 | [-7.80, 0.00] | False | -0.162 | -0.187 | -0.211 | -0.260 | -0.358 |
| avail_b200 | 5 | 8 | 2 | 3.757 | n/a | False | 0.972 | 0.912 | 0.852 | 0.732 | 0.493 |
| avail_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |

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
| neocloud | level_h100 | 1 | 36 | 8 | -1.556 | -0.397 | [-0.57, 0.17] | 0.004 | 0.021 | 0.028 | False | insufficient variation (8 non-zero < 10) |
| neocloud | level_h100 | 5 | 32 | 5 | -2.574 | -0.241 | [-0.42, -0.07] | 0.000 | 0.000 | 0.167 | False | insufficient variation (5 non-zero < 10) |
| neocloud | level_h100 | 20 | 17 | 3 | n/a | -0.060 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 36 | 14 | -0.594 | -0.408 | [-0.58, -0.06] | 0.018 | 0.064 | 0.028 | True |  |
| neocloud | level_b200 | 5 | 32 | 11 | -0.921 | -0.233 | [-0.41, 0.33] | 0.000 | 0.000 | 0.250 | False |  |
| neocloud | level_b200 | 20 | 17 | 1 | n/a | -0.098 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 36 | 30 | -0.099 | -0.075 | [-0.33, 0.19] | 0.506 | 1.000 | 0.722 | False |  |
| neocloud | disp_h100 | 5 | 32 | 26 | 0.149 | 0.042 | [-0.30, 0.25] | 0.718 | 1.000 | 0.875 | False |  |
| neocloud | disp_h100 | 20 | 17 | 12 | n/a | -0.267 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 36 | 7 | 0.292 | 0.459 | [-0.01, 0.60] | 0.000 | 0.000 | 0.028 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 32 | 6 | 0.368 | 0.208 | [-0.14, 0.44] | 0.000 | 0.000 | 0.083 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 20 | 17 | 1 | n/a | 0.098 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 36 | 5 | 0.005 | 0.032 | [-0.37, 0.26] | 0.820 | 1.000 | 0.944 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_h100 | 5 | 32 | 3 | -1.233 | -0.346 | [-0.52, -0.09] | 0.041 | 0.115 | 0.083 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_h100 | 20 | 17 | 2 | n/a | -0.420 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 36 | 3 | 0.000 | 0.001 | [-0.33, 0.27] | 0.993 | 1.000 | 1.000 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_b200 | 5 | 32 | 1 | -0.299 | -0.201 | [-0.39, -0.16] | 0.000 | 0.001 | 0.250 | False | insufficient variation (1 non-zero < 10) |
| neocloud | avail_b200 | 20 | 17 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 36 | 8 | -0.680 | -0.413 | [-0.70, 0.04] | 0.011 | 0.045 | 0.028 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | level_h100 | 5 | 32 | 5 | -0.609 | -0.142 | [-0.37, 0.19] | 0.126 | 0.323 | 0.500 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 17 | 3 | n/a | -0.069 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 36 | 14 | -0.124 | -0.202 | [-0.69, 0.19] | 0.428 | 0.925 | 0.361 | False |  |
| gpu_semis | level_b200 | 5 | 32 | 11 | -0.255 | -0.161 | [-0.34, 0.48] | 0.005 | 0.022 | 0.500 | False |  |
| gpu_semis | level_b200 | 20 | 17 | 1 | n/a | -0.089 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 36 | 30 | 0.017 | 0.032 | [-0.30, 0.23] | 0.820 | 1.000 | 0.806 | False |  |
| gpu_semis | disp_h100 | 5 | 32 | 26 | 0.019 | 0.013 | [-0.32, 0.27] | 0.919 | 1.000 | 0.917 | False |  |
| gpu_semis | disp_h100 | 20 | 17 | 12 | n/a | -0.083 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 36 | 7 | 0.105 | 0.391 | [-0.11, 0.71] | 0.081 | 0.219 | 0.028 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 32 | 6 | 0.136 | 0.192 | [-0.22, 0.38] | 0.000 | 0.000 | 0.167 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 17 | 1 | n/a | 0.089 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 36 | 5 | 0.021 | 0.290 | [-0.30, 0.52] | 0.000 | 0.000 | 0.111 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 32 | 3 | -0.370 | -0.259 | [-0.43, -0.08] | 0.026 | 0.087 | 0.125 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 17 | 2 | n/a | -0.199 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 36 | 3 | 0.021 | 0.295 | [0.01, 0.53] | 0.000 | 0.000 | 0.056 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 32 | 1 | -0.089 | -0.150 | [-0.31, -0.08] | 0.003 | 0.021 | 0.625 | False | insufficient variation (1 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 17 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 36 | 8 | -0.690 | -0.246 | [-0.40, 0.14] | 0.027 | 0.087 | 0.111 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | level_h100 | 5 | 32 | 5 | -0.130 | -0.018 | [-0.25, 0.45] | 0.862 | 1.000 | 0.917 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | level_h100 | 20 | 17 | 3 | n/a | 0.291 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 36 | 14 | -0.224 | -0.215 | [-0.41, -0.01] | 0.136 | 0.333 | 0.194 | False |  |
| power_capacity | level_b200 | 5 | 32 | 11 | -0.075 | -0.028 | [-0.30, 0.25] | 0.715 | 1.000 | 0.875 | False |  |
| power_capacity | level_b200 | 20 | 17 | 1 | n/a | 0.211 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 36 | 30 | -0.014 | -0.015 | [-0.22, 0.23] | 0.896 | 1.000 | 0.944 | False |  |
| power_capacity | disp_h100 | 5 | 32 | 26 | 0.177 | 0.074 | [-0.26, 0.32] | 0.542 | 1.000 | 0.500 | False |  |
| power_capacity | disp_h100 | 20 | 17 | 12 | n/a | -0.238 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 36 | 7 | 0.105 | 0.229 | [-0.23, 0.39] | 0.032 | 0.096 | 0.167 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 32 | 6 | 0.063 | 0.054 | [-0.18, 0.29] | 0.381 | 0.895 | 0.625 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 17 | 1 | n/a | -0.211 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 36 | 5 | 0.018 | 0.145 | [-0.43, 0.32] | 0.005 | 0.022 | 0.389 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 32 | 3 | -0.297 | -0.124 | [-0.47, 0.22] | 0.513 | 1.000 | 0.500 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 17 | 2 | n/a | -0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 36 | 3 | 0.017 | 0.145 | [-0.09, 0.31] | 0.016 | 0.060 | 0.361 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 32 | 1 | 0.036 | 0.037 | [-0.06, 0.27] | 0.424 | 0.925 | 1.000 | False | insufficient variation (1 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 17 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.25, 0.26] | -0.03 [-0.20, 0.30] |
| -4 | -0.04 [-0.32, 0.16] | 0.04 [-0.35, 0.32] |
| -3 | -0.19 [-0.37, 0.26] | -0.07 [-0.34, 0.06] |
| -2 | -0.18 [-0.42, 0.09] | -0.28 [-0.44, 0.14] |
| -1 | -0.09 [-0.37, 0.24] | -0.20 [-0.45, -0.01] |
| 0 | -0.34 [-0.60, -0.01] | -0.40 [-0.59, 0.11] |
| 1 | 0.04 [-0.32, 0.46] | -0.07 [-0.30, 0.47] |
| 2 | 0.09 [-0.27, 0.36] | 0.07 [-0.30, 0.37] |
| 3 | -0.17 [-0.45, 0.22] | 0.04 [-0.46, 0.26] |
| 4 | -0.05 [-0.26, 0.08] | -0.03 [-0.22, 0.09] |
| 5 | -0.01 [-0.38, 0.12] | -0.11 [-0.40, 0.15] |

