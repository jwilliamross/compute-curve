# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-08T02:53:21.180545+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 37.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `d12bc52012b79246...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 2 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 14 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 0 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 34 | 2026-08-20 | 2026-10-07 | 0.46 | 0.60 |
| 5 | 30 | 2026-08-20 | 2026-10-01 | 0.49 | 0.63 |
| 20 | 15 | 2026-08-20 | 2026-09-10 | 0.67 | 0.80 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 34 | 6 | -0.966 | -0.401 | [-0.60, 0.15] | 0.005 | 0.093 | 0.059 | False | insufficient variation (6 non-zero < 10) |
| level_h100 | 5 | 30 | 4 | -0.943 | -0.132 | [-0.31, 0.21] | 0.059 | 0.820 | 0.364 | False | insufficient variation (4 non-zero < 10) |
| level_h100 | 20 | 15 | 3 | n/a | 0.087 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 34 | 12 | -0.310 | -0.349 | [-0.60, 0.01] | 0.080 | 1.000 | 0.059 | False |  |
| level_b200 | 5 | 30 | 10 | -0.599 | -0.116 | [-0.36, 0.54] | 0.084 | 1.000 | 0.591 | False |  |
| level_b200 | 20 | 15 | 1 | n/a | 0.042 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 34 | 28 | -0.028 | -0.035 | [-0.27, 0.20] | 0.749 | 1.000 | 0.882 | False |  |
| disp_h100 | 5 | 30 | 24 | 0.187 | 0.080 | [-0.26, 0.33] | 0.507 | 1.000 | 0.909 | False |  |
| disp_h100 | 20 | 15 | 10 | n/a | -0.186 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 34 | 6 | 0.170 | 0.427 | [-0.18, 0.60] | 0.001 | 0.017 | 0.029 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 5 | 30 | 4 | 0.200 | 0.134 | [-0.18, 0.38] | 0.013 | 0.192 | 0.364 | False | insufficient variation (4 non-zero < 10) |
| disp_b200 | 20 | 15 | 1 | n/a | -0.042 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 34 | 4 | -0.008 | -0.054 | [-0.40, 0.05] | 0.433 | 1.000 | 0.765 | False | insufficient variation (4 non-zero < 10) |
| avail_h100 | 5 | 30 | 2 | -1.805 | -0.364 | [-0.55, -0.05] | 0.010 | 0.166 | 0.136 | False | insufficient variation (2 non-zero < 10) |
| avail_h100 | 20 | 15 | 2 | n/a | -0.419 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 34 | 2 | -0.009 | -0.066 | [-0.22, 0.05] | 0.417 | 1.000 | 0.706 | False | insufficient variation (2 non-zero < 10) |
| avail_b200 | 5 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| avail_b200 | 20 | 15 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 2 | -3.062 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| B200 | 5 | 1 | -3.443 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 14 | -0.107 | -0.088 | 0.056 | 0.033 | 0.571 | 1.000 | False | 14 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 6 | -0.198 | -0.130 | n/a | n/a | 0.833 | n/a | False | 6 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 14 | -1.686 | -1.638 | 0.136 | 0.127 | 0.571 | 1.000 | False | 14 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 6 | 0.019 | 0.075 | n/a | n/a | 0.833 | n/a | False | 6 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 14 | -0.019 | -0.001 | 0.682 | 0.585 | 0.500 | 1.000 | False | 14 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 6 | -0.146 | -0.081 | n/a | n/a | 0.333 | n/a | False | 6 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 14 | -0.134 | -0.114 | 0.140 | 0.123 | 0.571 | 1.000 | False | 14 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 6 | -0.011 | 0.047 | n/a | n/a | 0.667 | n/a | False | 6 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 14 | -7.678 | -7.523 | 0.089 | 0.116 | 0.500 | 1.000 | False | 14 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 6 | -0.061 | 0.000 | n/a | n/a | 0.500 | n/a | False | 6 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 14 | -0.385 | -0.360 | 0.214 | 0.113 | 0.500 | 1.000 | False | 14 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 6 | -0.061 | 0.000 | n/a | n/a | 0.500 | n/a | False | 6 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 14 | 2 | 5.556 | [0.00, 9.60] | False | 0.176 | 0.147 | 0.119 | 0.062 | -0.053 |
| level_h100 | 5 | 6 | 1 | -2.898 | n/a | False | 0.010 | -0.030 | -0.070 | -0.150 | -0.310 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 14 | 4 | -4.072 | [-10.79, 6.24] | False | -0.086 | -0.143 | -0.200 | -0.314 | -0.543 |
| level_b200 | 5 | 6 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 14 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 6 | 2 | -4.252 | n/a | False | -1.560 | -1.625 | -1.690 | -1.820 | -2.080 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 14 | 2 | 4.214 | [-4.24, 7.92] | False | 0.143 | 0.115 | 0.087 | 0.031 | -0.081 |
| disp_b200 | 5 | 6 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 14 | 2 | 3.380 | [-6.24, 6.74] | False | 0.129 | 0.100 | 0.072 | 0.015 | -0.100 |
| avail_h100 | 5 | 6 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 14 | 1 | -4.243 | [-7.99, 0.00] | False | 0.013 | -0.001 | -0.016 | -0.044 | -0.101 |
| avail_b200 | 5 | 6 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
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
| neocloud | level_h100 | 1 | 34 | 6 | -1.542 | -0.402 | [-0.58, 0.23] | 0.003 | 0.025 | 0.059 | False | insufficient variation (6 non-zero < 10) |
| neocloud | level_h100 | 5 | 30 | 4 | -2.143 | -0.200 | [-0.36, -0.03] | 0.000 | 0.000 | 0.182 | False | insufficient variation (4 non-zero < 10) |
| neocloud | level_h100 | 20 | 15 | 3 | n/a | -0.032 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 34 | 12 | -0.587 | -0.415 | [-0.58, -0.04] | 0.014 | 0.053 | 0.059 | False |  |
| neocloud | level_b200 | 5 | 30 | 10 | -0.938 | -0.121 | [-0.35, 0.59] | 0.069 | 0.197 | 0.682 | False |  |
| neocloud | level_b200 | 20 | 15 | 1 | n/a | -0.059 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 34 | 28 | -0.093 | -0.073 | [-0.33, 0.20] | 0.533 | 1.000 | 0.676 | False |  |
| neocloud | disp_h100 | 5 | 30 | 24 | 0.329 | 0.094 | [-0.23, 0.33] | 0.424 | 0.953 | 0.818 | False |  |
| neocloud | disp_h100 | 20 | 15 | 10 | n/a | -0.174 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 34 | 6 | 0.298 | 0.471 | [-0.11, 0.61] | 0.000 | 0.000 | 0.029 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 5 | 30 | 4 | 0.323 | 0.144 | [-0.16, 0.41] | 0.010 | 0.049 | 0.318 | False | insufficient variation (4 non-zero < 10) |
| neocloud | disp_b200 | 20 | 15 | 1 | n/a | 0.059 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 34 | 4 | -0.049 | -0.205 | [-0.40, -0.03] | 0.006 | 0.041 | 0.294 | False | insufficient variation (4 non-zero < 10) |
| neocloud | avail_h100 | 5 | 30 | 2 | -2.806 | -0.376 | [-0.56, -0.03] | 0.017 | 0.057 | 0.136 | False | insufficient variation (2 non-zero < 10) |
| neocloud | avail_h100 | 20 | 15 | 2 | n/a | -0.501 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 34 | 2 | -0.053 | -0.235 | [-0.44, -0.14] | 0.011 | 0.049 | 0.206 | False | insufficient variation (2 non-zero < 10) |
| neocloud | avail_b200 | 5 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| neocloud | avail_b200 | 20 | 15 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 34 | 6 | -0.719 | -0.467 | [-0.73, -0.04] | 0.002 | 0.019 | 0.029 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | level_h100 | 5 | 30 | 4 | -0.467 | -0.106 | [-0.33, 0.27] | 0.325 | 0.799 | 0.682 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 15 | 3 | n/a | -0.053 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 34 | 12 | -0.118 | -0.208 | [-0.70, 0.26] | 0.419 | 0.953 | 0.265 | False |  |
| gpu_semis | level_b200 | 5 | 30 | 10 | -0.199 | -0.062 | [-0.36, 0.62] | 0.650 | 1.000 | 0.773 | False |  |
| gpu_semis | level_b200 | 20 | 15 | 1 | n/a | -0.066 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 34 | 28 | 0.017 | 0.033 | [-0.33, 0.27] | 0.839 | 1.000 | 0.794 | False |  |
| gpu_semis | disp_h100 | 5 | 30 | 24 | 0.067 | 0.047 | [-0.28, 0.33] | 0.711 | 1.000 | 0.909 | False |  |
| gpu_semis | disp_h100 | 20 | 15 | 10 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 34 | 6 | 0.091 | 0.357 | [-0.30, 0.71] | 0.129 | 0.341 | 0.059 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 30 | 4 | 0.124 | 0.135 | [-0.30, 0.37] | 0.017 | 0.057 | 0.500 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 15 | 1 | n/a | 0.066 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 34 | 4 | 0.020 | 0.202 | [-0.32, 0.43] | 0.000 | 0.001 | 0.235 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 30 | 2 | -0.847 | -0.277 | [-0.47, -0.05] | 0.001 | 0.006 | 0.227 | False | insufficient variation (2 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 15 | 2 | n/a | -0.210 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 34 | 2 | 0.019 | 0.210 | [-0.01, 0.44] | 0.001 | 0.006 | 0.206 | False | insufficient variation (2 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| gpu_semis | avail_b200 | 20 | 15 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 34 | 6 | -0.637 | -0.230 | [-0.39, 0.23] | 0.049 | 0.155 | 0.235 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | level_h100 | 5 | 30 | 4 | -0.219 | -0.029 | [-0.25, 0.48] | 0.771 | 1.000 | 0.636 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | level_h100 | 20 | 15 | 3 | n/a | 0.324 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 34 | 12 | -0.223 | -0.219 | [-0.43, -0.02] | 0.133 | 0.341 | 0.265 | False |  |
| power_capacity | level_b200 | 5 | 30 | 10 | -0.659 | -0.123 | [-0.38, 0.25] | 0.010 | 0.049 | 0.545 | False |  |
| power_capacity | level_b200 | 20 | 15 | 1 | n/a | 0.248 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 34 | 28 | -0.008 | -0.008 | [-0.22, 0.26] | 0.941 | 1.000 | 0.971 | False |  |
| power_capacity | disp_h100 | 5 | 30 | 24 | 0.165 | 0.068 | [-0.29, 0.33] | 0.609 | 1.000 | 0.773 | False |  |
| power_capacity | disp_h100 | 20 | 15 | 10 | n/a | -0.230 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 34 | 6 | 0.121 | 0.265 | [-0.15, 0.40] | 0.007 | 0.041 | 0.147 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 30 | 4 | 0.152 | 0.098 | [-0.13, 0.35] | 0.065 | 0.195 | 0.409 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 15 | 1 | n/a | -0.248 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 34 | 4 | 0.005 | 0.031 | [-0.45, 0.16] | 0.615 | 1.000 | 0.912 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 30 | 2 | -1.762 | -0.340 | [-0.54, -0.04] | 0.012 | 0.049 | 0.136 | False | insufficient variation (2 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 15 | 2 | n/a | -0.266 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 34 | 2 | 0.006 | 0.037 | [-0.11, 0.15] | 0.566 | 1.000 | 0.853 | False | insufficient variation (2 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 30 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| power_capacity | avail_b200 | 20 | 15 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.26, 0.28] | 0.16 [-0.17, 0.34] |
| -4 | -0.05 [-0.37, 0.14] | -0.22 [-0.45, -0.03] |
| -3 | -0.21 [-0.41, 0.15] | -0.17 [-0.40, 0.05] |
| -2 | -0.19 [-0.41, 0.15] | -0.20 [-0.40, 0.24] |
| -1 | -0.08 [-0.36, 0.27] | -0.38 [-0.51, -0.09] |
| 0 | -0.35 [-0.60, 0.01] | -0.40 [-0.60, 0.15] |
| 1 | 0.04 [-0.31, 0.45] | -0.08 [-0.31, 0.46] |
| 2 | 0.09 [-0.31, 0.37] | 0.07 [-0.34, 0.40] |
| 3 | 0.10 [-0.28, 0.29] | 0.12 [-0.40, 0.34] |
| 4 | -0.01 [-0.32, 0.11] | -0.02 [-0.22, 0.09] |
| 5 | -0.01 [-0.43, 0.10] | 0.06 [-0.06, 0.25] |

