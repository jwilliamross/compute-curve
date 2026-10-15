# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-15T01:47:41.934084+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `3b3d43ce70857f16...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 19 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 39 | 2026-08-20 | 2026-10-14 | 0.44 | 0.56 |
| 5 | 35 | 2026-08-20 | 2026-10-08 | 0.46 | 0.59 |
| 20 | 20 | 2026-08-20 | 2026-09-17 | 0.59 | 0.73 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 39 | 10 | -0.959 | -0.359 | [-0.56, 0.13] | 0.011 | 0.166 | 0.026 | False |  |
| level_h100 | 5 | 35 | 7 | -1.183 | -0.159 | [-0.34, 0.15] | 0.034 | 0.407 | 0.333 | False | insufficient variation (7 non-zero < 10) |
| level_h100 | 20 | 20 | 3 | n/a | 0.000 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 39 | 17 | -0.327 | -0.333 | [-0.58, -0.07] | 0.087 | 0.958 | 0.051 | False |  |
| level_b200 | 5 | 35 | 13 | -0.419 | -0.152 | [-0.31, 0.29] | 0.031 | 0.403 | 0.556 | False |  |
| level_b200 | 20 | 20 | 4 | n/a | -0.151 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 39 | 33 | 0.006 | 0.007 | [-0.22, 0.23] | 0.944 | 1.000 | 1.000 | False |  |
| disp_h100 | 5 | 35 | 29 | 0.099 | 0.040 | [-0.27, 0.24] | 0.705 | 1.000 | 0.741 | False |  |
| disp_h100 | 20 | 20 | 15 | n/a | -0.068 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 39 | 7 | 0.168 | 0.387 | [-0.04, 0.57] | 0.002 | 0.030 | 0.026 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 35 | 6 | 0.199 | 0.161 | [-0.08, 0.34] | 0.000 | 0.000 | 0.481 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 20 | 20 | 1 | n/a | 0.057 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 39 | 6 | 0.021 | 0.217 | [-0.35, 0.47] | 0.009 | 0.147 | 0.179 | False | insufficient variation (6 non-zero < 10) |
| avail_h100 | 5 | 35 | 5 | 0.021 | 0.065 | [-0.46, 0.35] | 0.518 | 1.000 | 0.481 | False | insufficient variation (5 non-zero < 10) |
| avail_h100 | 20 | 20 | 2 | n/a | -0.288 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 39 | 4 | 0.020 | 0.205 | [-0.14, 0.46] | 0.026 | 0.360 | 0.205 | False | insufficient variation (4 non-zero < 10) |
| avail_b200 | 5 | 35 | 3 | 0.020 | 0.064 | [-0.27, 0.37] | 0.532 | 1.000 | 0.630 | False | insufficient variation (3 non-zero < 10) |
| avail_b200 | 20 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 3 | -2.614 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 5 | 2 | -3.966 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| B200 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 19 | -0.018 | -0.045 | 0.028 | 0.041 | 0.579 | 0.744 | False | 19 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 11 | 0.145 | 0.035 | n/a | n/a | 0.909 | n/a | False | 11 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 19 | -0.755 | -0.802 | 0.102 | 0.112 | 0.632 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 11 | 0.194 | 0.091 | n/a | n/a | 0.909 | n/a | False | 11 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 19 | 0.017 | -0.009 | 0.192 | 0.802 | 0.579 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 11 | 0.069 | -0.050 | n/a | n/a | 0.636 | n/a | False | 11 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 19 | -0.023 | -0.050 | 0.079 | 0.101 | 0.632 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 11 | 0.180 | 0.075 | n/a | n/a | 0.727 | n/a | False | 11 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 19 | -3.699 | -3.826 | 0.065 | 0.108 | 0.579 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 11 | -110.017 | -124.225 | n/a | n/a | 0.636 | n/a | False | 11 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 19 | -0.159 | -0.190 | 0.233 | 0.401 | 0.579 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 11 | 0.113 | 0.000 | n/a | n/a | 0.727 | n/a | False | 11 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 19 | 2 | 4.736 | [0.00, 8.27] | False | 0.130 | 0.108 | 0.087 | 0.045 | -0.039 |
| level_h100 | 5 | 11 | 6 | 5.122 | [1.43, 11.22] | True | 2.820 | 2.690 | 2.559 | 2.298 | 1.775 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 19 | 5 | -1.654 | [-8.39, 7.97] | False | 0.027 | -0.025 | -0.078 | -0.183 | -0.394 |
| level_b200 | 5 | 11 | 5 | 5.248 | [2.14, 11.75] | True | 2.815 | 2.706 | 2.597 | 2.379 | 1.944 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 19 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 11 | 5 | 1.603 | [-4.73, 6.70] | False | 1.257 | 1.156 | 1.056 | 0.854 | 0.451 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 19 | 3 | 4.465 | [-3.64, 7.25] | False | 0.143 | 0.112 | 0.081 | 0.018 | -0.106 |
| disp_b200 | 5 | 11 | 4 | 4.621 | [0.00, 9.14] | False | 2.516 | 2.429 | 2.342 | 2.168 | 1.819 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 19 | 4 | -0.508 | [-4.47, 6.63] | False | 0.054 | 0.013 | -0.028 | -0.111 | -0.275 |
| avail_h100 | 5 | 11 | 5 | 0.941 | [-2.14, 8.18] | False | 0.821 | 0.716 | 0.611 | 0.402 | -0.018 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 19 | 3 | -1.771 | [-5.70, 5.30] | False | -0.032 | -0.062 | -0.093 | -0.154 | -0.277 |
| avail_b200 | 5 | 11 | 5 | 5.248 | [2.14, 11.75] | True | 2.815 | 2.706 | 2.597 | 2.379 | 1.944 |
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
| disp_b200|h5 | False | False | False | False | False |
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
| neocloud | level_h100 | 1 | 39 | 10 | -1.527 | -0.367 | [-0.55, 0.19] | 0.007 | 0.038 | 0.051 | False |  |
| neocloud | level_h100 | 5 | 35 | 7 | -2.671 | -0.232 | [-0.38, -0.06] | 0.000 | 0.000 | 0.185 | False | insufficient variation (7 non-zero < 10) |
| neocloud | level_h100 | 20 | 20 | 3 | n/a | -0.085 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 39 | 17 | -0.604 | -0.395 | [-0.57, -0.10] | 0.019 | 0.084 | 0.026 | True |  |
| neocloud | level_b200 | 5 | 35 | 13 | -0.922 | -0.216 | [-0.36, 0.32] | 0.001 | 0.004 | 0.259 | False |  |
| neocloud | level_b200 | 20 | 20 | 4 | n/a | -0.229 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 39 | 33 | -0.039 | -0.028 | [-0.25, 0.24] | 0.808 | 1.000 | 0.821 | False |  |
| neocloud | disp_h100 | 5 | 35 | 29 | 0.126 | 0.033 | [-0.28, 0.23] | 0.754 | 1.000 | 0.667 | False |  |
| neocloud | disp_h100 | 20 | 20 | 15 | n/a | -0.072 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 39 | 7 | 0.293 | 0.434 | [-0.02, 0.58] | 0.000 | 0.000 | 0.026 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 35 | 6 | 0.383 | 0.201 | [-0.10, 0.40] | 0.000 | 0.000 | 0.222 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 20 | 20 | 1 | n/a | 0.133 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 39 | 6 | 0.016 | 0.105 | [-0.33, 0.35] | 0.358 | 0.913 | 0.590 | False | insufficient variation (6 non-zero < 10) |
| neocloud | avail_h100 | 5 | 35 | 5 | 0.014 | 0.028 | [-0.49, 0.33] | 0.796 | 1.000 | 0.815 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_h100 | 20 | 20 | 2 | n/a | -0.333 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 39 | 4 | 0.012 | 0.080 | [-0.26, 0.34] | 0.521 | 1.000 | 0.692 | False | insufficient variation (4 non-zero < 10) |
| neocloud | avail_b200 | 5 | 35 | 3 | 0.007 | 0.014 | [-0.33, 0.34] | 0.901 | 1.000 | 0.852 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_b200 | 20 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 39 | 10 | -0.683 | -0.385 | [-0.67, 0.03] | 0.012 | 0.058 | 0.026 | True |  |
| gpu_semis | level_h100 | 5 | 35 | 7 | -0.660 | -0.137 | [-0.35, 0.21] | 0.186 | 0.501 | 0.667 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 20 | 3 | n/a | -0.092 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 39 | 17 | -0.143 | -0.219 | [-0.66, 0.12] | 0.380 | 0.913 | 0.256 | False |  |
| gpu_semis | level_b200 | 5 | 35 | 13 | -0.253 | -0.142 | [-0.33, 0.42] | 0.023 | 0.090 | 0.667 | False |  |
| gpu_semis | level_b200 | 20 | 20 | 4 | n/a | -0.238 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 39 | 33 | 0.023 | 0.039 | [-0.26, 0.25] | 0.753 | 1.000 | 0.744 | False |  |
| gpu_semis | disp_h100 | 5 | 35 | 29 | 0.005 | 0.003 | [-0.30, 0.22] | 0.976 | 1.000 | 1.000 | False |  |
| gpu_semis | disp_h100 | 20 | 20 | 15 | n/a | 0.092 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 39 | 7 | 0.105 | 0.363 | [-0.10, 0.68] | 0.085 | 0.255 | 0.026 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 35 | 6 | 0.144 | 0.180 | [-0.16, 0.34] | 0.000 | 0.000 | 0.370 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 20 | 1 | n/a | 0.126 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 39 | 6 | 0.023 | 0.357 | [-0.27, 0.58] | 0.000 | 0.000 | 0.077 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 35 | 5 | 0.013 | 0.062 | [-0.39, 0.36] | 0.595 | 1.000 | 0.481 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 20 | 2 | n/a | -0.140 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 39 | 4 | 0.023 | 0.363 | [0.03, 0.58] | 0.000 | 0.000 | 0.077 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 35 | 3 | 0.011 | 0.053 | [-0.33, 0.38] | 0.662 | 1.000 | 0.704 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 39 | 10 | -0.667 | -0.220 | [-0.38, 0.17] | 0.045 | 0.153 | 0.179 | False |  |
| power_capacity | level_h100 | 5 | 35 | 7 | -0.217 | -0.029 | [-0.26, 0.43] | 0.788 | 1.000 | 0.741 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | level_h100 | 20 | 20 | 3 | n/a | 0.236 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 39 | 17 | -0.233 | -0.209 | [-0.40, -0.03] | 0.135 | 0.385 | 0.205 | False |  |
| power_capacity | level_b200 | 5 | 35 | 13 | -0.083 | -0.030 | [-0.31, 0.23] | 0.718 | 1.000 | 0.852 | False |  |
| power_capacity | level_b200 | 20 | 20 | 4 | n/a | 0.105 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 39 | 33 | 0.035 | 0.035 | [-0.17, 0.28] | 0.764 | 1.000 | 0.923 | False |  |
| power_capacity | disp_h100 | 5 | 35 | 29 | 0.164 | 0.067 | [-0.23, 0.29] | 0.573 | 1.000 | 0.667 | False |  |
| power_capacity | disp_h100 | 20 | 20 | 15 | n/a | -0.152 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 39 | 7 | 0.105 | 0.214 | [-0.21, 0.37] | 0.039 | 0.139 | 0.179 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 35 | 6 | 0.069 | 0.056 | [-0.17, 0.26] | 0.389 | 0.913 | 0.704 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 20 | 1 | n/a | -0.156 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 39 | 6 | 0.024 | 0.221 | [-0.38, 0.43] | 0.000 | 0.002 | 0.154 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 35 | 5 | 0.037 | 0.114 | [-0.43, 0.39] | 0.083 | 0.255 | 0.407 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 20 | 2 | n/a | -0.224 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 39 | 4 | 0.024 | 0.220 | [-0.06, 0.42] | 0.001 | 0.004 | 0.179 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 35 | 3 | 0.043 | 0.138 | [-0.07, 0.42] | 0.021 | 0.088 | 0.370 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.06 [-0.24, 0.22] | 0.14 [-0.16, 0.30] |
| -4 | -0.02 [-0.22, 0.19] | -0.18 [-0.33, 0.06] |
| -3 | -0.18 [-0.36, 0.10] | -0.16 [-0.39, 0.02] |
| -2 | -0.19 [-0.43, 0.05] | -0.18 [-0.39, 0.20] |
| -1 | -0.09 [-0.36, 0.21] | -0.32 [-0.45, 0.03] |
| 0 | -0.33 [-0.58, -0.07] | -0.36 [-0.56, 0.13] |
| 1 | 0.06 [-0.27, 0.46] | -0.04 [-0.28, 0.45] |
| 2 | 0.04 [-0.48, 0.29] | 0.03 [-0.36, 0.32] |
| 3 | -0.16 [-0.40, 0.18] | 0.08 [-0.23, 0.29] |
| 4 | -0.05 [-0.24, 0.05] | -0.06 [-0.28, 0.05] |
| 5 | -0.13 [-0.29, 0.06] | -0.12 [-0.42, 0.16] |

