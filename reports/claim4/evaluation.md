# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-07T02:41:30.686786+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 37.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `416377db4fb73d41...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 2 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 13 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 33 | 2026-08-20 | 2026-10-06 | 0.47 | 0.60 |
| 5 | 29 | 2026-08-20 | 2026-09-30 | 0.50 | 0.64 |
| 20 | 14 | 2026-08-20 | 2026-09-09 | 0.69 | 0.82 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 33 | 5 | -0.967 | -0.402 | [-0.60, 0.17] | 0.005 | 0.087 | 0.030 | False | insufficient variation (5 non-zero < 10) |
| level_h100 | 5 | 29 | 3 | -1.557 | -0.177 | [-0.41, -0.04] | 0.011 | 0.162 | 0.143 | False | insufficient variation (3 non-zero < 10) |
| level_h100 | 20 | 14 | 3 | n/a | 0.110 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 33 | 11 | -0.310 | -0.349 | [-0.60, 0.01] | 0.080 | 0.879 | 0.030 | False |  |
| level_b200 | 5 | 29 | 10 | -0.600 | -0.116 | [-0.36, 0.56] | 0.086 | 0.879 | 0.667 | False |  |
| level_b200 | 20 | 14 | 1 | n/a | 0.071 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 33 | 27 | -0.028 | -0.035 | [-0.27, 0.20] | 0.749 | 1.000 | 0.909 | False |  |
| disp_h100 | 5 | 29 | 23 | 0.185 | 0.079 | [-0.27, 0.34] | 0.520 | 1.000 | 0.905 | False |  |
| disp_h100 | 20 | 14 | 9 | n/a | -0.114 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 33 | 6 | 0.170 | 0.427 | [-0.17, 0.60] | 0.001 | 0.017 | 0.030 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 5 | 29 | 3 | 0.200 | 0.134 | [-0.18, 0.40] | 0.014 | 0.185 | 0.381 | False | insufficient variation (3 non-zero < 10) |
| disp_b200 | 20 | 14 | 1 | n/a | -0.071 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 33 | 3 | -0.207 | -0.258 | [-0.43, -0.08] | 0.024 | 0.284 | 0.121 | False | insufficient variation (3 non-zero < 10) |
| avail_h100 | 5 | 29 | 2 | -1.805 | -0.364 | [-0.55, -0.04] | 0.011 | 0.162 | 0.143 | False | insufficient variation (2 non-zero < 10) |
| avail_h100 | 20 | 14 | 1 | n/a | -0.264 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 33 | 1 | -0.048 | -0.145 | [-0.30, -0.11] | 0.000 | 0.003 | 0.485 | False | insufficient variation (1 non-zero < 10) |
| avail_b200 | 5 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| avail_b200 | 20 | 14 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 1 | -3.443 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 2 | -3.062 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| B200 | 5 | 1 | -3.443 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 13 | -0.107 | -0.087 | 0.053 | 0.030 | 0.538 | 0.953 | False | 13 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 5 | 0.013 | 0.069 | n/a | n/a | 0.800 | n/a | False | 5 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 13 | -1.689 | -1.638 | 0.134 | 0.125 | 0.538 | 1.000 | False | 13 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 5 | 0.019 | 0.075 | n/a | n/a | 0.800 | n/a | False | 5 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 13 | -0.020 | -0.001 | 0.695 | 0.583 | 0.462 | 1.000 | False | 13 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 5 | -0.147 | -0.081 | n/a | n/a | 0.200 | n/a | False | 5 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 13 | -0.135 | -0.114 | 0.139 | 0.121 | 0.538 | 1.000 | False | 13 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 5 | -0.010 | 0.048 | n/a | n/a | 0.600 | n/a | False | 5 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 13 | -0.576 | -0.546 | 0.144 | 0.136 | 0.462 | 1.000 | False | 13 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 5 | -0.060 | 0.000 | n/a | n/a | 0.400 | n/a | False | 5 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 13 | -0.014 | 0.005 | 0.651 | 0.148 | 0.462 | 1.000 | False | 13 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 5 | -0.060 | 0.000 | n/a | n/a | 0.400 | n/a | False | 5 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 13 | 2 | 5.778 | [0.00, 10.08] | False | 0.189 | 0.159 | 0.128 | 0.066 | -0.057 |
| level_h100 | 5 | 5 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 13 | 4 | -4.224 | [-10.70, 4.40] | False | -0.092 | -0.154 | -0.215 | -0.339 | -0.585 |
| level_b200 | 5 | 5 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 13 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 5 | 2 | -4.773 | n/a | False | -1.872 | -1.950 | -2.028 | -2.184 | -2.496 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 13 | 2 | 4.373 | [-4.40, 8.29] | False | 0.154 | 0.124 | 0.094 | 0.034 | -0.087 |
| disp_b200 | 5 | 5 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 13 | 1 | 4.403 | [0.00, 8.35] | False | 0.125 | 0.110 | 0.094 | 0.063 | 0.002 |
| avail_h100 | 5 | 5 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 13 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avail_b200 | 5 | 5 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
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
| neocloud | level_h100 | 1 | 33 | 5 | -1.560 | -0.412 | [-0.59, 0.21] | 0.002 | 0.023 | 0.061 | False | insufficient variation (5 non-zero < 10) |
| neocloud | level_h100 | 5 | 29 | 3 | -2.480 | -0.188 | [-0.43, -0.05] | 0.014 | 0.058 | 0.095 | False | insufficient variation (3 non-zero < 10) |
| neocloud | level_h100 | 20 | 14 | 3 | n/a | -0.013 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 33 | 11 | -0.588 | -0.421 | [-0.59, -0.03] | 0.012 | 0.058 | 0.030 | True |  |
| neocloud | level_b200 | 5 | 29 | 10 | -0.935 | -0.121 | [-0.38, 0.60] | 0.064 | 0.173 | 0.714 | False |  |
| neocloud | level_b200 | 20 | 14 | 1 | n/a | -0.034 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 33 | 27 | -0.097 | -0.077 | [-0.34, 0.21] | 0.518 | 1.000 | 0.697 | False |  |
| neocloud | disp_h100 | 5 | 29 | 23 | 0.349 | 0.100 | [-0.23, 0.35] | 0.406 | 0.913 | 0.857 | False |  |
| neocloud | disp_h100 | 20 | 14 | 9 | n/a | -0.088 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 33 | 6 | 0.297 | 0.474 | [-0.11, 0.62] | 0.000 | 0.000 | 0.030 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 5 | 29 | 3 | 0.319 | 0.142 | [-0.14, 0.41] | 0.013 | 0.058 | 0.333 | False | insufficient variation (3 non-zero < 10) |
| neocloud | disp_b200 | 20 | 14 | 1 | n/a | 0.034 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 33 | 3 | -0.390 | -0.309 | [-0.49, -0.01] | 0.000 | 0.003 | 0.091 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_h100 | 5 | 29 | 2 | -2.806 | -0.377 | [-0.57, -0.03] | 0.015 | 0.058 | 0.143 | False | insufficient variation (2 non-zero < 10) |
| neocloud | avail_h100 | 20 | 14 | 1 | n/a | -0.335 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 33 | 1 | -0.124 | -0.236 | [-0.47, -0.21] | 0.000 | 0.000 | 0.242 | False | insufficient variation (1 non-zero < 10) |
| neocloud | avail_b200 | 5 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| neocloud | avail_b200 | 20 | 14 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 33 | 5 | -0.710 | -0.472 | [-0.75, -0.02] | 0.004 | 0.034 | 0.061 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | level_h100 | 5 | 29 | 3 | -1.065 | -0.197 | [-0.42, -0.06] | 0.017 | 0.060 | 0.333 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 14 | 3 | n/a | -0.048 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 33 | 11 | -0.118 | -0.212 | [-0.72, 0.24] | 0.431 | 0.931 | 0.212 | False |  |
| gpu_semis | level_b200 | 5 | 29 | 10 | -0.200 | -0.063 | [-0.37, 0.64] | 0.654 | 1.000 | 0.762 | False |  |
| gpu_semis | level_b200 | 20 | 14 | 1 | n/a | -0.059 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 33 | 27 | 0.019 | 0.038 | [-0.34, 0.28] | 0.810 | 1.000 | 0.939 | False |  |
| gpu_semis | disp_h100 | 5 | 29 | 23 | 0.059 | 0.041 | [-0.32, 0.32] | 0.745 | 1.000 | 0.952 | False |  |
| gpu_semis | disp_h100 | 20 | 14 | 9 | n/a | -0.005 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 33 | 6 | 0.092 | 0.369 | [-0.27, 0.72] | 0.136 | 0.340 | 0.030 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 29 | 3 | 0.126 | 0.137 | [-0.33, 0.39] | 0.018 | 0.061 | 0.524 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 14 | 1 | n/a | 0.059 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 33 | 3 | -0.042 | -0.083 | [-0.32, 0.10] | 0.448 | 0.931 | 0.485 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 29 | 2 | -0.847 | -0.278 | [-0.49, -0.05] | 0.001 | 0.011 | 0.238 | False | insufficient variation (2 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 14 | 1 | n/a | -0.198 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 33 | 1 | 0.004 | 0.021 | [-0.05, 0.13] | 0.493 | 0.986 | 0.970 | False | insufficient variation (1 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| gpu_semis | avail_b200 | 20 | 14 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 33 | 5 | -0.631 | -0.229 | [-0.40, 0.25] | 0.056 | 0.169 | 0.121 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | level_h100 | 5 | 29 | 3 | -1.125 | -0.124 | [-0.34, 0.01] | 0.009 | 0.053 | 0.286 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | level_h100 | 20 | 14 | 3 | n/a | 0.350 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 33 | 11 | -0.223 | -0.219 | [-0.43, -0.02] | 0.138 | 0.340 | 0.212 | False |  |
| power_capacity | level_b200 | 5 | 29 | 10 | -0.663 | -0.124 | [-0.38, 0.31] | 0.008 | 0.053 | 0.571 | False |  |
| power_capacity | level_b200 | 20 | 14 | 1 | n/a | 0.278 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 33 | 27 | -0.006 | -0.007 | [-0.22, 0.27] | 0.951 | 1.000 | 1.000 | False |  |
| power_capacity | disp_h100 | 5 | 29 | 23 | 0.146 | 0.061 | [-0.33, 0.32] | 0.657 | 1.000 | 0.857 | False |  |
| power_capacity | disp_h100 | 20 | 14 | 9 | n/a | -0.177 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 33 | 6 | 0.122 | 0.267 | [-0.14, 0.41] | 0.008 | 0.053 | 0.121 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 29 | 3 | 0.156 | 0.101 | [-0.14, 0.35] | 0.062 | 0.173 | 0.381 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 14 | 1 | n/a | -0.278 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 33 | 3 | -0.190 | -0.207 | [-0.46, -0.04] | 0.146 | 0.342 | 0.242 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 29 | 2 | -1.762 | -0.343 | [-0.56, -0.03] | 0.014 | 0.058 | 0.143 | False | insufficient variation (2 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 14 | 1 | n/a | -0.106 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 33 | 1 | -0.026 | -0.067 | [-0.18, -0.02] | 0.049 | 0.157 | 0.818 | False | insufficient variation (1 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| power_capacity | avail_b200 | 20 | 14 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.26, 0.28] | 0.17 [-0.14, 0.35] |
| -4 | -0.05 [-0.37, 0.15] | -0.22 [-0.45, -0.04] |
| -3 | -0.20 [-0.39, 0.19] | -0.16 [-0.39, 0.06] |
| -2 | -0.19 [-0.42, 0.07] | -0.21 [-0.41, 0.21] |
| -1 | -0.08 [-0.36, 0.26] | -0.38 [-0.51, -0.10] |
| 0 | -0.35 [-0.60, 0.01] | -0.40 [-0.60, 0.17] |
| 1 | 0.04 [-0.31, 0.45] | -0.08 [-0.31, 0.48] |
| 2 | 0.19 [-0.40, 0.44] | 0.08 [-0.37, 0.42] |
| 3 | 0.10 [-0.27, 0.29] | 0.12 [-0.38, 0.33] |
| 4 | -0.01 [-0.33, 0.12] | -0.03 [-0.30, 0.10] |
| 5 | -0.01 [-0.43, 0.12] | 0.06 [-0.07, 0.25] |

