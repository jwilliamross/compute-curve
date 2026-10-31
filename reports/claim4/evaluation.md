# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-31T02:43:23.536944+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `04f199da6d9499b7...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 31 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 3 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 51 | 2026-08-20 | 2026-10-30 | 0.38 | 0.50 |
| 5 | 47 | 2026-08-20 | 2026-10-26 | 0.40 | 0.52 |
| 20 | 32 | 2026-08-20 | 2026-10-05 | 0.48 | 0.61 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 51 | 19 | -0.875 | -0.286 | [-0.51, 0.07] | 0.017 | 0.264 | 0.078 | False |  |
| level_h100 | 5 | 47 | 17 | -1.132 | -0.135 | [-0.30, 0.13] | 0.080 | 1.000 | 0.333 | False |  |
| level_h100 | 20 | 32 | 5 | n/a | -0.167 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 51 | 23 | -0.349 | -0.296 | [-0.53, -0.11] | 0.069 | 0.960 | 0.020 | False |  |
| level_b200 | 5 | 47 | 23 | -0.580 | -0.188 | [-0.43, -0.03] | 0.062 | 0.929 | 0.256 | False |  |
| level_b200 | 20 | 32 | 11 | n/a | -0.269 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 51 | 43 | 0.028 | 0.037 | [-0.15, 0.24] | 0.740 | 1.000 | 0.706 | False |  |
| disp_h100 | 5 | 47 | 40 | -0.207 | -0.091 | [-0.38, 0.16] | 0.423 | 1.000 | 0.564 | False |  |
| disp_h100 | 20 | 32 | 26 | n/a | -0.156 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 51 | 11 | 0.171 | 0.327 | [0.03, 0.51] | 0.001 | 0.011 | 0.039 | True |  |
| disp_b200 | 5 | 47 | 9 | 0.257 | 0.188 | [0.06, 0.34] | 0.000 | 0.001 | 0.179 | False | insufficient variation (9 non-zero < 10) |
| disp_b200 | 20 | 32 | 6 | n/a | 0.174 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 51 | 14 | -0.004 | -0.074 | [-0.33, 0.27] | 0.639 | 1.000 | 0.627 | False |  |
| avail_h100 | 5 | 47 | 12 | -0.017 | -0.101 | [-0.33, 0.09] | 0.162 | 1.000 | 0.154 | False |  |
| avail_h100 | 20 | 32 | 3 | n/a | -0.228 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 51 | 12 | -0.004 | -0.074 | [-0.33, 0.27] | 0.637 | 1.000 | 0.647 | False |  |
| avail_b200 | 5 | 47 | 10 | -0.016 | -0.098 | [-0.31, 0.10] | 0.164 | 1.000 | 0.179 | False |  |
| avail_b200 | 20 | 32 | 1 | n/a | -0.178 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 3 | -2.614 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 5 | 3 | -6.126 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 31 | -0.044 | -0.036 | 0.090 | 0.057 | 0.548 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 23 | 0.155 | 0.013 | 0.013 | 0.034 | 0.783 | 0.552 | False | 23 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 31 | -0.372 | -0.361 | 0.107 | 0.100 | 0.581 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 23 | 0.215 | 0.083 | 0.006 | 0.014 | 0.783 | 0.256 | False | 23 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 31 | -0.031 | -0.023 | 0.728 | 0.908 | 0.516 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 23 | 0.112 | -0.038 | 0.071 | 1.000 | 0.652 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 31 | -0.025 | -0.017 | 0.110 | 0.095 | 0.581 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 23 | 0.202 | 0.067 | 0.012 | 0.017 | 0.696 | 0.284 | False | 23 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 31 | -1.986 | -1.962 | 0.319 | 0.390 | 0.548 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 23 | -46.362 | -54.346 | 0.556 | 0.631 | 0.609 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 31 | -0.238 | -0.228 | 0.775 | 0.811 | 0.548 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 23 | 0.166 | 0.026 | 0.045 | 0.112 | 0.652 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 31 | 4 | 3.416 | [-3.74, 6.71] | False | 0.151 | 0.125 | 0.100 | 0.048 | -0.055 |
| level_h100 | 5 | 23 | 17 | 4.560 | [0.00, 10.39] | True | 3.014 | 2.837 | 2.660 | 2.306 | 1.597 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 31 | 6 | 0.473 | [-5.91, 6.71] | False | 0.098 | 0.060 | 0.021 | -0.057 | -0.211 |
| level_b200 | 5 | 23 | 17 | 5.071 | [0.10, 12.91] | True | 3.345 | 3.168 | 2.991 | 2.637 | 1.929 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 31 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 23 | 17 | 3.331 | [-2.43, 11.07] | False | 2.600 | 2.427 | 2.254 | 1.908 | 1.215 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 31 | 3 | 3.477 | [-2.85, 5.93] | False | 0.087 | 0.068 | 0.049 | 0.011 | -0.065 |
| disp_b200 | 5 | 23 | 16 | 4.811 | [-0.22, 12.02] | False | 3.203 | 3.036 | 2.869 | 2.536 | 1.869 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 31 | 7 | -2.836 | [-5.18, 1.81] | False | -0.117 | -0.161 | -0.206 | -0.295 | -0.473 |
| avail_h100 | 5 | 23 | 17 | 2.130 | [-0.66, 4.84] | False | 1.870 | 1.697 | 1.524 | 1.177 | 0.484 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 31 | 6 | -3.471 | [-5.97, -0.02] | False | -0.169 | -0.207 | -0.246 | -0.322 | -0.474 |
| avail_b200 | 5 | 23 | 17 | 3.835 | [-0.29, 9.40] | False | 2.824 | 2.648 | 2.473 | 2.123 | 1.422 |
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
| neocloud | level_h100 | 1 | 51 | 19 | -1.456 | -0.294 | [-0.49, 0.05] | 0.005 | 0.049 | 0.039 | True |  |
| neocloud | level_h100 | 5 | 47 | 17 | -2.623 | -0.201 | [-0.34, -0.03] | 0.000 | 0.000 | 0.179 | False |  |
| neocloud | level_h100 | 20 | 32 | 5 | n/a | -0.219 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 51 | 23 | -0.639 | -0.336 | [-0.51, -0.15] | 0.012 | 0.090 | 0.020 | True |  |
| neocloud | level_b200 | 5 | 47 | 23 | -1.165 | -0.242 | [-0.44, -0.06] | 0.009 | 0.077 | 0.179 | False |  |
| neocloud | level_b200 | 20 | 32 | 11 | n/a | -0.299 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 51 | 43 | 0.028 | 0.022 | [-0.18, 0.23] | 0.833 | 1.000 | 0.843 | False |  |
| neocloud | disp_h100 | 5 | 47 | 40 | -0.379 | -0.108 | [-0.41, 0.14] | 0.369 | 0.933 | 0.436 | False |  |
| neocloud | disp_h100 | 20 | 32 | 26 | n/a | -0.160 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 51 | 11 | 0.299 | 0.355 | [0.05, 0.52] | 0.000 | 0.000 | 0.020 | True |  |
| neocloud | disp_b200 | 5 | 47 | 9 | 0.462 | 0.217 | [0.08, 0.37] | 0.000 | 0.000 | 0.128 | False | insufficient variation (9 non-zero < 10) |
| neocloud | disp_b200 | 20 | 32 | 6 | n/a | 0.210 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 51 | 14 | -0.011 | -0.120 | [-0.41, 0.24] | 0.474 | 0.960 | 0.431 | False |  |
| neocloud | avail_h100 | 5 | 47 | 12 | -0.028 | -0.106 | [-0.34, 0.07] | 0.139 | 0.500 | 0.077 | False |  |
| neocloud | avail_h100 | 20 | 32 | 3 | n/a | -0.252 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 51 | 12 | -0.012 | -0.125 | [-0.41, 0.24] | 0.459 | 0.960 | 0.412 | False |  |
| neocloud | avail_b200 | 5 | 47 | 10 | -0.029 | -0.109 | [-0.32, 0.06] | 0.123 | 0.476 | 0.128 | False |  |
| neocloud | avail_b200 | 20 | 32 | 1 | n/a | -0.190 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 51 | 19 | -0.592 | -0.314 | [-0.60, 0.07] | 0.038 | 0.230 | 0.020 | False |  |
| gpu_semis | level_h100 | 5 | 47 | 17 | -0.533 | -0.099 | [-0.30, 0.24] | 0.367 | 0.933 | 0.615 | False |  |
| gpu_semis | level_h100 | 20 | 32 | 5 | n/a | -0.237 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 51 | 23 | -0.154 | -0.213 | [-0.63, 0.07] | 0.358 | 0.933 | 0.118 | False |  |
| gpu_semis | level_b200 | 5 | 47 | 23 | -0.345 | -0.174 | [-0.40, 0.07] | 0.048 | 0.261 | 0.333 | False |  |
| gpu_semis | level_b200 | 20 | 32 | 11 | n/a | -0.333 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 51 | 43 | 0.004 | 0.009 | [-0.20, 0.20] | 0.942 | 1.000 | 0.961 | False |  |
| gpu_semis | disp_h100 | 5 | 47 | 40 | -0.129 | -0.089 | [-0.32, 0.14] | 0.396 | 0.933 | 0.538 | False |  |
| gpu_semis | disp_h100 | 20 | 32 | 26 | n/a | -0.108 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 51 | 11 | 0.106 | 0.328 | [-0.08, 0.62] | 0.084 | 0.380 | 0.020 | False |  |
| gpu_semis | disp_b200 | 5 | 47 | 9 | 0.191 | 0.218 | [-0.05, 0.37] | 0.000 | 0.001 | 0.179 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 32 | 6 | n/a | 0.222 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 51 | 14 | 0.000 | 0.009 | [-0.28, 0.38] | 0.954 | 1.000 | 0.961 | False |  |
| gpu_semis | avail_h100 | 5 | 47 | 12 | -0.006 | -0.052 | [-0.23, 0.10] | 0.415 | 0.933 | 0.513 | False |  |
| gpu_semis | avail_h100 | 20 | 32 | 3 | n/a | -0.236 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 51 | 12 | 0.001 | 0.015 | [-0.28, 0.38] | 0.924 | 1.000 | 0.902 | False |  |
| gpu_semis | avail_b200 | 5 | 47 | 10 | -0.006 | -0.052 | [-0.22, 0.10] | 0.403 | 0.933 | 0.564 | False |  |
| gpu_semis | avail_b200 | 20 | 32 | 1 | n/a | -0.238 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 51 | 19 | -0.578 | -0.175 | [-0.34, 0.14] | 0.084 | 0.380 | 0.275 | False |  |
| power_capacity | level_h100 | 5 | 47 | 17 | -0.240 | -0.029 | [-0.23, 0.32] | 0.781 | 1.000 | 0.795 | False |  |
| power_capacity | level_h100 | 20 | 32 | 5 | n/a | 0.114 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 51 | 23 | -0.253 | -0.199 | [-0.39, -0.05] | 0.105 | 0.436 | 0.196 | False |  |
| power_capacity | level_b200 | 5 | 47 | 23 | -0.230 | -0.076 | [-0.42, 0.13] | 0.480 | 0.960 | 0.538 | False |  |
| power_capacity | level_b200 | 20 | 32 | 11 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 51 | 43 | 0.054 | 0.065 | [-0.13, 0.30] | 0.609 | 1.000 | 0.569 | False |  |
| power_capacity | disp_h100 | 5 | 47 | 40 | -0.112 | -0.051 | [-0.32, 0.21] | 0.649 | 1.000 | 0.744 | False |  |
| power_capacity | disp_h100 | 20 | 32 | 26 | n/a | -0.178 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 51 | 11 | 0.108 | 0.191 | [-0.13, 0.34] | 0.023 | 0.153 | 0.157 | False |  |
| power_capacity | disp_b200 | 5 | 47 | 9 | 0.119 | 0.089 | [-0.08, 0.31] | 0.162 | 0.546 | 0.564 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 32 | 6 | n/a | -0.033 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 51 | 14 | -0.002 | -0.031 | [-0.22, 0.25] | 0.802 | 1.000 | 0.863 | False |  |
| power_capacity | avail_h100 | 5 | 47 | 12 | -0.018 | -0.106 | [-0.37, 0.15] | 0.243 | 0.770 | 0.154 | False |  |
| power_capacity | avail_h100 | 20 | 32 | 3 | n/a | -0.097 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 51 | 12 | -0.002 | -0.028 | [-0.21, 0.24] | 0.819 | 1.000 | 0.863 | False |  |
| power_capacity | avail_b200 | 5 | 47 | 10 | -0.015 | -0.093 | [-0.35, 0.17] | 0.317 | 0.933 | 0.205 | False |  |
| power_capacity | avail_b200 | 20 | 32 | 1 | n/a | -0.021 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.22, 0.19] | 0.07 [-0.18, 0.23] |
| -4 | -0.02 [-0.19, 0.14] | -0.19 [-0.36, -0.01] |
| -3 | -0.18 [-0.31, 0.00] | -0.09 [-0.29, 0.15] |
| -2 | -0.15 [-0.38, 0.15] | -0.07 [-0.30, 0.23] |
| -1 | -0.08 [-0.32, 0.14] | -0.28 [-0.40, -0.05] |
| 0 | -0.30 [-0.53, -0.11] | -0.29 [-0.51, 0.07] |
| 1 | 0.04 [-0.23, 0.32] | -0.04 [-0.22, 0.34] |
| 2 | 0.02 [-0.40, 0.23] | 0.03 [-0.28, 0.28] |
| 3 | -0.10 [-0.34, 0.31] | 0.07 [-0.23, 0.24] |
| 4 | -0.07 [-0.28, 0.01] | -0.10 [-0.49, -0.00] |
| 5 | -0.13 [-0.30, 0.02] | -0.07 [-0.33, 0.23] |

