# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-27T02:25:16.040832+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `258ac19e36679ade...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 27 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 0 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 47 | 2026-08-20 | 2026-10-26 | 0.40 | 0.52 |
| 5 | 43 | 2026-08-20 | 2026-10-20 | 0.42 | 0.54 |
| 20 | 28 | 2026-08-20 | 2026-09-29 | 0.51 | 0.64 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 47 | 17 | -0.979 | -0.321 | [-0.53, 0.07] | 0.009 | 0.152 | 0.043 | False |  |
| level_h100 | 5 | 43 | 13 | -1.086 | -0.133 | [-0.31, 0.20] | 0.132 | 1.000 | 0.400 | False |  |
| level_h100 | 20 | 28 | 3 | n/a | -0.068 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 47 | 23 | -0.336 | -0.299 | [-0.55, -0.09] | 0.087 | 1.000 | 0.064 | False |  |
| level_b200 | 5 | 43 | 21 | -0.560 | -0.187 | [-0.43, -0.03] | 0.084 | 1.000 | 0.314 | False |  |
| level_b200 | 20 | 28 | 10 | n/a | -0.245 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 47 | 40 | 0.003 | 0.003 | [-0.18, 0.23] | 0.980 | 1.000 | 0.979 | False |  |
| disp_h100 | 5 | 43 | 36 | -0.109 | -0.046 | [-0.30, 0.16] | 0.637 | 1.000 | 0.686 | False |  |
| disp_h100 | 20 | 28 | 23 | n/a | -0.115 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 47 | 9 | 0.168 | 0.339 | [-0.02, 0.53] | 0.002 | 0.033 | 0.043 | False | insufficient variation (9 non-zero < 10) |
| disp_b200 | 5 | 43 | 7 | 0.244 | 0.184 | [0.03, 0.35] | 0.000 | 0.002 | 0.229 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 28 | 3 | n/a | 0.105 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 47 | 14 | -0.005 | -0.097 | [-0.35, 0.24] | 0.551 | 1.000 | 0.574 | False |  |
| avail_h100 | 5 | 43 | 10 | -0.007 | -0.041 | [-0.31, 0.18] | 0.602 | 1.000 | 0.600 | False |  |
| avail_h100 | 20 | 28 | 2 | n/a | -0.161 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 47 | 12 | -0.006 | -0.099 | [-0.35, 0.24] | 0.542 | 1.000 | 0.553 | False |  |
| avail_b200 | 5 | 43 | 8 | -0.007 | -0.037 | [-0.25, 0.18] | 0.628 | 1.000 | 0.686 | False | insufficient variation (8 non-zero < 10) |
| avail_b200 | 20 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 27 | 0.007 | -0.017 | 0.025 | 0.035 | 0.593 | 0.567 | False | 27 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 19 | 0.222 | 0.011 | 0.001 | 0.042 | 0.895 | 0.627 | False | 19 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 27 | -0.411 | -0.444 | 0.091 | 0.109 | 0.630 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 19 | 0.284 | 0.089 | 0.000 | 0.010 | 0.895 | 0.172 | False | 19 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 27 | -0.005 | -0.029 | 0.432 | 0.929 | 0.556 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 19 | 0.187 | -0.033 | 0.019 | 1.000 | 0.737 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 27 | -0.002 | -0.026 | 0.069 | 0.103 | 0.630 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 19 | 0.267 | 0.069 | 0.002 | 0.020 | 0.789 | 0.338 | False | 19 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 27 | -2.262 | -2.339 | 0.275 | 0.394 | 0.556 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 19 | -49.276 | -62.904 | 0.553 | 0.636 | 0.684 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 27 | -0.241 | -0.271 | 0.724 | 0.817 | 0.556 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 19 | 0.218 | 0.006 | 0.028 | 0.150 | 0.737 | 1.000 | False | 19 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 27 | 3 | 4.763 | [0.00, 7.54] | False | 0.185 | 0.163 | 0.140 | 0.096 | 0.007 |
| level_h100 | 5 | 19 | 13 | 6.867 | [3.60, 11.55] | True | 3.909 | 3.745 | 3.581 | 3.253 | 2.598 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 27 | 6 | 0.505 | [-6.39, 7.22] | False | 0.113 | 0.068 | 0.024 | -0.065 | -0.243 |
| level_b200 | 5 | 19 | 13 | 7.730 | [3.91, 16.26] | True | 4.310 | 4.146 | 3.982 | 3.655 | 2.999 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 27 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 19 | 13 | 4.690 | [-0.43, 13.35] | False | 3.408 | 3.249 | 3.090 | 2.771 | 2.134 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 27 | 3 | 3.730 | [-3.06, 6.00] | False | 0.100 | 0.079 | 0.057 | 0.013 | -0.075 |
| disp_b200 | 5 | 19 | 12 | 7.235 | [3.34, 15.13] | True | 4.137 | 3.986 | 3.835 | 3.532 | 2.927 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 27 | 7 | -1.553 | [-4.84, 6.99] | False | -0.016 | -0.068 | -0.119 | -0.221 | -0.426 |
| avail_h100 | 5 | 19 | 13 | 3.036 | [1.55, 6.08] | True | 2.524 | 2.365 | 2.206 | 1.887 | 1.250 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 27 | 6 | -2.200 | [-5.58, 6.32] | False | -0.077 | -0.120 | -0.164 | -0.252 | -0.427 |
| avail_b200 | 5 | 19 | 13 | 5.493 | [1.93, 13.09] | True | 3.679 | 3.517 | 3.355 | 3.032 | 2.386 |
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
| neocloud | level_h100 | 1 | 47 | 17 | -1.555 | -0.326 | [-0.52, 0.11] | 0.006 | 0.061 | 0.064 | False |  |
| neocloud | level_h100 | 5 | 43 | 13 | -2.531 | -0.201 | [-0.36, 0.02] | 0.000 | 0.003 | 0.286 | False |  |
| neocloud | level_h100 | 20 | 28 | 3 | n/a | -0.117 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 47 | 23 | -0.614 | -0.350 | [-0.54, -0.11] | 0.019 | 0.126 | 0.043 | False |  |
| neocloud | level_b200 | 5 | 43 | 21 | -1.135 | -0.245 | [-0.45, -0.09] | 0.016 | 0.124 | 0.286 | False |  |
| neocloud | level_b200 | 20 | 28 | 10 | n/a | -0.289 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 47 | 40 | -0.045 | -0.035 | [-0.22, 0.19] | 0.747 | 1.000 | 0.830 | False |  |
| neocloud | disp_h100 | 5 | 43 | 36 | -0.185 | -0.051 | [-0.30, 0.15] | 0.595 | 1.000 | 0.657 | False |  |
| neocloud | disp_h100 | 20 | 28 | 23 | n/a | -0.115 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 47 | 9 | 0.294 | 0.379 | [0.00, 0.55] | 0.000 | 0.000 | 0.021 | False | insufficient variation (9 non-zero < 10) |
| neocloud | disp_b200 | 5 | 43 | 7 | 0.441 | 0.215 | [0.05, 0.38] | 0.000 | 0.000 | 0.143 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 28 | 3 | n/a | 0.148 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 47 | 14 | -0.018 | -0.205 | [-0.45, 0.12] | 0.179 | 0.644 | 0.255 | False |  |
| neocloud | avail_h100 | 5 | 43 | 10 | -0.014 | -0.050 | [-0.34, 0.16] | 0.498 | 1.000 | 0.514 | False |  |
| neocloud | avail_h100 | 20 | 28 | 2 | n/a | -0.194 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 47 | 12 | -0.019 | -0.213 | [-0.45, 0.10] | 0.163 | 0.627 | 0.234 | False |  |
| neocloud | avail_b200 | 5 | 43 | 8 | -0.015 | -0.052 | [-0.27, 0.16] | 0.464 | 1.000 | 0.543 | False | insufficient variation (8 non-zero < 10) |
| neocloud | avail_b200 | 20 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 47 | 17 | -0.681 | -0.355 | [-0.64, 0.04] | 0.016 | 0.124 | 0.043 | False |  |
| gpu_semis | level_h100 | 5 | 43 | 13 | -0.534 | -0.100 | [-0.31, 0.28] | 0.387 | 1.000 | 0.571 | False |  |
| gpu_semis | level_h100 | 20 | 28 | 3 | n/a | -0.114 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 47 | 23 | -0.150 | -0.212 | [-0.65, 0.10] | 0.378 | 1.000 | 0.255 | False |  |
| gpu_semis | level_b200 | 5 | 43 | 21 | -0.346 | -0.177 | [-0.42, 0.02] | 0.057 | 0.278 | 0.400 | False |  |
| gpu_semis | level_b200 | 20 | 28 | 10 | n/a | -0.277 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 47 | 40 | -0.002 | -0.003 | [-0.24, 0.19] | 0.979 | 1.000 | 0.979 | False |  |
| gpu_semis | disp_h100 | 5 | 43 | 36 | -0.066 | -0.043 | [-0.26, 0.15] | 0.658 | 1.000 | 0.714 | False |  |
| gpu_semis | disp_h100 | 20 | 28 | 23 | n/a | -0.045 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 47 | 9 | 0.105 | 0.335 | [-0.10, 0.64] | 0.095 | 0.430 | 0.043 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 43 | 7 | 0.191 | 0.220 | [0.06, 0.38] | 0.000 | 0.001 | 0.229 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 28 | 3 | n/a | 0.133 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 47 | 14 | 0.002 | 0.050 | [-0.26, 0.42] | 0.768 | 1.000 | 0.702 | False |  |
| gpu_semis | avail_h100 | 5 | 43 | 10 | -0.006 | -0.051 | [-0.29, 0.12] | 0.464 | 1.000 | 0.600 | False |  |
| gpu_semis | avail_h100 | 20 | 28 | 2 | n/a | -0.058 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 47 | 12 | 0.002 | 0.057 | [-0.24, 0.43] | 0.736 | 1.000 | 0.660 | False |  |
| gpu_semis | avail_b200 | 5 | 43 | 8 | -0.006 | -0.051 | [-0.24, 0.13] | 0.456 | 1.000 | 0.629 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 47 | 17 | -0.700 | -0.206 | [-0.36, 0.10] | 0.031 | 0.187 | 0.170 | False |  |
| power_capacity | level_h100 | 5 | 43 | 13 | -0.194 | -0.024 | [-0.24, 0.39] | 0.836 | 1.000 | 0.771 | False |  |
| power_capacity | level_h100 | 20 | 28 | 3 | n/a | 0.132 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 47 | 23 | -0.243 | -0.194 | [-0.39, -0.04] | 0.127 | 0.529 | 0.170 | False |  |
| power_capacity | level_b200 | 5 | 43 | 21 | -0.200 | -0.069 | [-0.41, 0.17] | 0.547 | 1.000 | 0.571 | False |  |
| power_capacity | level_b200 | 20 | 28 | 10 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 47 | 40 | 0.055 | 0.060 | [-0.15, 0.33] | 0.675 | 1.000 | 0.702 | False |  |
| power_capacity | disp_h100 | 5 | 43 | 36 | -0.077 | -0.034 | [-0.33, 0.21] | 0.760 | 1.000 | 0.771 | False |  |
| power_capacity | disp_h100 | 20 | 28 | 23 | n/a | -0.181 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 47 | 9 | 0.107 | 0.192 | [-0.16, 0.35] | 0.035 | 0.189 | 0.170 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 43 | 7 | 0.100 | 0.078 | [-0.14, 0.25] | 0.263 | 0.889 | 0.457 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 28 | 3 | n/a | -0.069 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 47 | 14 | -0.000 | -0.003 | [-0.23, 0.27] | 0.986 | 1.000 | 0.979 | False |  |
| power_capacity | avail_h100 | 5 | 43 | 10 | -0.002 | -0.012 | [-0.28, 0.26] | 0.896 | 1.000 | 0.943 | False |  |
| power_capacity | avail_h100 | 20 | 28 | 2 | n/a | -0.173 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 47 | 12 | -0.000 | -0.000 | [-0.22, 0.27] | 0.999 | 1.000 | 1.000 | False |  |
| power_capacity | avail_b200 | 5 | 43 | 8 | 0.001 | 0.004 | [-0.22, 0.27] | 0.971 | 1.000 | 0.943 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.04 [-0.21, 0.20] | 0.13 [-0.13, 0.27] |
| -4 | -0.01 [-0.19, 0.17] | -0.16 [-0.32, 0.07] |
| -3 | -0.17 [-0.31, 0.04] | -0.15 [-0.33, 0.02] |
| -2 | -0.14 [-0.39, 0.19] | -0.13 [-0.35, 0.26] |
| -1 | -0.07 [-0.33, 0.17] | -0.29 [-0.42, -0.01] |
| 0 | -0.30 [-0.55, -0.09] | -0.32 [-0.53, 0.07] |
| 1 | 0.06 [-0.25, 0.39] | -0.03 [-0.25, 0.41] |
| 2 | 0.03 [-0.36, 0.25] | 0.03 [-0.29, 0.29] |
| 3 | -0.10 [-0.34, 0.37] | 0.08 [-0.26, 0.26] |
| 4 | -0.07 [-0.31, 0.01] | -0.10 [-0.47, 0.02] |
| 5 | -0.13 [-0.30, 0.02] | -0.07 [-0.33, 0.29] |

