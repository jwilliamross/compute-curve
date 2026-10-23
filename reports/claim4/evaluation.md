# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-23T01:53:18.799653+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `0ce813ffa89925a7...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 25 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 0 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 45 | 2026-08-20 | 2026-10-22 | 0.41 | 0.53 |
| 5 | 41 | 2026-08-20 | 2026-10-16 | 0.43 | 0.55 |
| 20 | 26 | 2026-08-20 | 2026-09-25 | 0.53 | 0.66 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 45 | 15 | -0.967 | -0.319 | [-0.54, 0.11] | 0.011 | 0.176 | 0.067 | False |  |
| level_h100 | 5 | 41 | 12 | -1.027 | -0.128 | [-0.30, 0.21] | 0.131 | 1.000 | 0.424 | False |  |
| level_h100 | 20 | 26 | 3 | n/a | -0.058 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 45 | 23 | -0.337 | -0.302 | [-0.55, -0.09] | 0.086 | 1.000 | 0.067 | False |  |
| level_b200 | 5 | 41 | 19 | -0.538 | -0.182 | [-0.41, -0.01] | 0.073 | 1.000 | 0.333 | False |  |
| level_b200 | 20 | 26 | 9 | n/a | -0.265 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 45 | 38 | 0.001 | 0.001 | [-0.20, 0.20] | 0.996 | 1.000 | 0.978 | False |  |
| disp_h100 | 5 | 41 | 34 | 0.093 | 0.035 | [-0.25, 0.24] | 0.720 | 1.000 | 0.697 | False |  |
| disp_h100 | 20 | 26 | 21 | n/a | -0.081 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 45 | 7 | 0.168 | 0.341 | [-0.04, 0.54] | 0.002 | 0.033 | 0.022 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 41 | 7 | 0.242 | 0.185 | [0.02, 0.34] | 0.000 | 0.001 | 0.152 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 26 | 1 | n/a | 0.120 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 45 | 12 | -0.003 | -0.053 | [-0.34, 0.33] | 0.772 | 1.000 | 0.733 | False |  |
| avail_h100 | 5 | 41 | 8 | -0.023 | -0.115 | [-0.38, 0.14] | 0.270 | 1.000 | 0.212 | False | insufficient variation (8 non-zero < 10) |
| avail_h100 | 20 | 26 | 2 | n/a | -0.180 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 45 | 10 | -0.003 | -0.056 | [-0.33, 0.32] | 0.761 | 1.000 | 0.689 | False |  |
| avail_b200 | 5 | 41 | 6 | -0.022 | -0.111 | [-0.33, 0.14] | 0.275 | 1.000 | 0.303 | False | insufficient variation (6 non-zero < 10) |
| avail_b200 | 20 | 26 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 25 | -0.001 | -0.023 | 0.033 | 0.043 | 0.600 | 0.692 | False | 25 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 17 | 0.180 | 0.007 | 0.002 | 0.064 | 0.882 | 0.963 | False | 17 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 25 | -0.425 | -0.455 | 0.092 | 0.108 | 0.640 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 17 | 0.248 | 0.089 | 0.002 | 0.010 | 0.882 | 0.171 | False | 17 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 25 | -0.009 | -0.030 | 0.521 | 0.925 | 0.560 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 17 | 0.152 | -0.027 | 0.039 | 0.991 | 0.706 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 25 | -0.007 | -0.029 | 0.075 | 0.105 | 0.640 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 17 | 0.235 | 0.073 | 0.006 | 0.014 | 0.765 | 0.242 | False | 17 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 25 | -2.343 | -2.413 | 0.299 | 0.415 | 0.560 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 17 | -56.399 | -68.505 | 0.570 | 0.639 | 0.647 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 25 | -0.263 | -0.289 | 0.767 | 0.842 | 0.560 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 17 | 0.170 | -0.005 | 0.061 | 0.172 | 0.706 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 25 | 3 | 4.961 | [0.00, 7.67] | False | 0.200 | 0.176 | 0.152 | 0.104 | 0.008 |
| level_h100 | 5 | 17 | 11 | 6.176 | [2.84, 11.07] | True | 3.613 | 3.458 | 3.303 | 2.993 | 2.373 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 25 | 6 | 0.524 | [-6.07, 7.51] | False | 0.122 | 0.074 | 0.026 | -0.070 | -0.262 |
| level_b200 | 5 | 17 | 11 | 7.046 | [3.06, 16.82] | True | 4.062 | 3.907 | 3.752 | 3.441 | 2.821 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 25 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 17 | 11 | 4.055 | [-1.58, 14.31] | False | 3.054 | 2.904 | 2.754 | 2.454 | 1.855 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 25 | 3 | 3.879 | [-3.17, 6.68] | False | 0.108 | 0.085 | 0.061 | 0.014 | -0.081 |
| disp_b200 | 5 | 17 | 10 | 6.556 | [2.49, 15.26] | True | 3.868 | 3.727 | 3.586 | 3.304 | 2.741 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 25 | 6 | -2.267 | [-4.83, 5.65] | False | -0.082 | -0.129 | -0.176 | -0.271 | -0.460 |
| avail_h100 | 5 | 17 | 11 | 2.379 | [-0.66, 6.22] | False | 2.065 | 1.916 | 1.766 | 1.466 | 0.867 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 25 | 5 | -2.980 | [-5.80, 4.59] | False | -0.147 | -0.186 | -0.225 | -0.304 | -0.461 |
| avail_b200 | 5 | 17 | 11 | 4.843 | [-0.21, 15.30] | False | 3.356 | 3.203 | 3.051 | 2.746 | 2.136 |
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
| avail_h100|h5 | False | False | False | False | False |
| avail_h100|h20 | False | False | False | False | False |
| avail_b200|h1 | False | False | False | False | False |
| avail_b200|h5 | False | False | False | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 45 | 15 | -1.533 | -0.324 | [-0.53, 0.16] | 0.007 | 0.074 | 0.067 | False |  |
| neocloud | level_h100 | 5 | 41 | 12 | -2.448 | -0.197 | [-0.35, 0.03] | 0.000 | 0.001 | 0.303 | False |  |
| neocloud | level_h100 | 20 | 26 | 3 | n/a | -0.112 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 45 | 23 | -0.616 | -0.354 | [-0.54, -0.10] | 0.019 | 0.125 | 0.022 | False |  |
| neocloud | level_b200 | 5 | 41 | 19 | -1.103 | -0.242 | [-0.43, -0.06] | 0.011 | 0.097 | 0.182 | False |  |
| neocloud | level_b200 | 20 | 26 | 9 | n/a | -0.312 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 45 | 38 | -0.049 | -0.039 | [-0.23, 0.17] | 0.727 | 1.000 | 0.756 | False |  |
| neocloud | disp_h100 | 5 | 41 | 34 | 0.113 | 0.028 | [-0.26, 0.23] | 0.775 | 1.000 | 0.818 | False |  |
| neocloud | disp_h100 | 20 | 26 | 21 | n/a | -0.082 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 45 | 7 | 0.294 | 0.381 | [-0.02, 0.55] | 0.000 | 0.000 | 0.022 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 41 | 7 | 0.439 | 0.217 | [0.04, 0.39] | 0.000 | 0.000 | 0.121 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 26 | 1 | n/a | 0.167 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 45 | 12 | -0.016 | -0.167 | [-0.42, 0.19] | 0.329 | 0.964 | 0.289 | False |  |
| neocloud | avail_h100 | 5 | 41 | 8 | -0.040 | -0.131 | [-0.40, 0.08] | 0.160 | 0.577 | 0.182 | False | insufficient variation (8 non-zero < 10) |
| neocloud | avail_h100 | 20 | 26 | 2 | n/a | -0.214 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 45 | 10 | -0.017 | -0.176 | [-0.43, 0.19] | 0.302 | 0.960 | 0.222 | False |  |
| neocloud | avail_b200 | 5 | 41 | 6 | -0.041 | -0.133 | [-0.34, 0.07] | 0.132 | 0.511 | 0.182 | False | insufficient variation (6 non-zero < 10) |
| neocloud | avail_b200 | 20 | 26 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 45 | 15 | -0.687 | -0.358 | [-0.65, 0.04] | 0.015 | 0.112 | 0.022 | False |  |
| gpu_semis | level_h100 | 5 | 41 | 12 | -0.510 | -0.096 | [-0.31, 0.29] | 0.399 | 0.979 | 0.606 | False |  |
| gpu_semis | level_h100 | 20 | 26 | 3 | n/a | -0.109 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 45 | 23 | -0.151 | -0.214 | [-0.65, 0.10] | 0.375 | 0.964 | 0.244 | False |  |
| gpu_semis | level_b200 | 5 | 41 | 19 | -0.337 | -0.173 | [-0.42, 0.04] | 0.053 | 0.261 | 0.394 | False |  |
| gpu_semis | level_b200 | 20 | 26 | 9 | n/a | -0.304 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 45 | 38 | -0.001 | -0.003 | [-0.27, 0.22] | 0.983 | 1.000 | 1.000 | False |  |
| gpu_semis | disp_h100 | 5 | 41 | 34 | 0.006 | 0.003 | [-0.26, 0.22] | 0.973 | 1.000 | 1.000 | False |  |
| gpu_semis | disp_h100 | 20 | 26 | 21 | n/a | -0.000 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 45 | 7 | 0.105 | 0.337 | [-0.10, 0.65] | 0.091 | 0.411 | 0.044 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 41 | 7 | 0.190 | 0.220 | [0.00, 0.38] | 0.000 | 0.001 | 0.242 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 26 | 1 | n/a | 0.154 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 45 | 12 | 0.002 | 0.042 | [-0.27, 0.46] | 0.820 | 1.000 | 0.667 | False |  |
| gpu_semis | avail_h100 | 5 | 41 | 8 | -0.012 | -0.088 | [-0.33, 0.13] | 0.370 | 0.964 | 0.333 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 26 | 2 | n/a | -0.066 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 45 | 10 | 0.002 | 0.050 | [-0.25, 0.46] | 0.788 | 1.000 | 0.622 | False |  |
| gpu_semis | avail_b200 | 5 | 41 | 6 | -0.012 | -0.088 | [-0.30, 0.13] | 0.364 | 0.964 | 0.364 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 26 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 45 | 15 | -0.680 | -0.202 | [-0.36, 0.15] | 0.039 | 0.211 | 0.156 | False |  |
| power_capacity | level_h100 | 5 | 41 | 12 | -0.124 | -0.016 | [-0.22, 0.41] | 0.889 | 1.000 | 0.879 | False |  |
| power_capacity | level_h100 | 20 | 26 | 3 | n/a | 0.155 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 45 | 23 | -0.244 | -0.197 | [-0.39, -0.04] | 0.127 | 0.511 | 0.222 | False |  |
| power_capacity | level_b200 | 5 | 41 | 19 | -0.173 | -0.060 | [-0.36, 0.19] | 0.568 | 1.000 | 0.667 | False |  |
| power_capacity | level_b200 | 20 | 26 | 9 | n/a | -0.032 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 45 | 38 | 0.052 | 0.057 | [-0.16, 0.27] | 0.690 | 1.000 | 0.778 | False |  |
| power_capacity | disp_h100 | 5 | 41 | 34 | 0.160 | 0.063 | [-0.23, 0.29] | 0.586 | 1.000 | 0.636 | False |  |
| power_capacity | disp_h100 | 20 | 26 | 21 | n/a | -0.157 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 45 | 7 | 0.105 | 0.192 | [-0.19, 0.35] | 0.038 | 0.211 | 0.200 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 41 | 7 | 0.098 | 0.078 | [-0.13, 0.25] | 0.240 | 0.808 | 0.576 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 26 | 1 | n/a | -0.070 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 45 | 12 | 0.004 | 0.066 | [-0.24, 0.38] | 0.693 | 1.000 | 0.644 | False |  |
| power_capacity | avail_h100 | 5 | 41 | 8 | -0.017 | -0.087 | [-0.37, 0.23] | 0.459 | 1.000 | 0.333 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 26 | 2 | n/a | -0.185 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 45 | 10 | 0.005 | 0.068 | [-0.19, 0.37] | 0.682 | 1.000 | 0.622 | False |  |
| power_capacity | avail_b200 | 5 | 41 | 6 | -0.013 | -0.070 | [-0.32, 0.25] | 0.567 | 1.000 | 0.455 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 26 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.04 [-0.21, 0.20] | 0.12 [-0.16, 0.27] |
| -4 | -0.01 [-0.19, 0.20] | -0.16 [-0.31, 0.09] |
| -3 | -0.18 [-0.32, 0.06] | -0.15 [-0.34, 0.00] |
| -2 | -0.15 [-0.39, 0.20] | -0.14 [-0.36, 0.23] |
| -1 | -0.08 [-0.33, 0.17] | -0.29 [-0.42, -0.02] |
| 0 | -0.30 [-0.55, -0.09] | -0.32 [-0.54, 0.11] |
| 1 | 0.06 [-0.25, 0.41] | -0.04 [-0.23, 0.41] |
| 2 | 0.03 [-0.38, 0.25] | 0.03 [-0.30, 0.29] |
| 3 | -0.11 [-0.36, 0.33] | 0.08 [-0.18, 0.27] |
| 4 | -0.06 [-0.28, 0.02] | -0.09 [-0.43, 0.02] |
| 5 | -0.13 [-0.32, 0.01] | -0.07 [-0.34, 0.27] |

