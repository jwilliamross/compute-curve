# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-06T03:39:10.952044+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `3acabfbc9a3b23a1...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 4 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 35 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 55 | 2026-08-20 | 2026-11-05 | 0.37 | 0.49 |
| 5 | 51 | 2026-08-20 | 2026-10-30 | 0.38 | 0.50 |
| 20 | 36 | 2026-08-20 | 2026-10-09 | 0.45 | 0.58 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 55 | 22 | -0.736 | -0.234 | [-0.48, 0.10] | 0.133 | 1.000 | 0.055 | False |  |
| level_h100 | 5 | 51 | 19 | -1.503 | -0.181 | [-0.39, 0.08] | 0.051 | 0.761 | 0.209 | False |  |
| level_h100 | 20 | 36 | 8 | n/a | -0.139 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 55 | 24 | -0.381 | -0.338 | [-0.52, -0.14] | 0.017 | 0.268 | 0.018 | False |  |
| level_b200 | 5 | 51 | 23 | -0.545 | -0.171 | [-0.39, -0.01] | 0.080 | 1.000 | 0.279 | False |  |
| level_b200 | 20 | 36 | 14 | n/a | -0.251 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 55 | 46 | 0.051 | 0.066 | [-0.13, 0.25] | 0.601 | 1.000 | 0.618 | False |  |
| disp_h100 | 5 | 51 | 43 | -0.070 | -0.034 | [-0.34, 0.19] | 0.768 | 1.000 | 0.791 | False |  |
| disp_h100 | 20 | 36 | 30 | n/a | -0.147 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 55 | 12 | 0.192 | 0.355 | [0.08, 0.52] | 0.000 | 0.001 | 0.018 | True |  |
| disp_b200 | 5 | 51 | 11 | 0.261 | 0.184 | [0.05, 0.34] | 0.000 | 0.002 | 0.209 | False |  |
| disp_b200 | 20 | 36 | 7 | n/a | 0.210 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 55 | 17 | -0.004 | -0.059 | [-0.30, 0.23] | 0.703 | 1.000 | 0.691 | False |  |
| avail_h100 | 5 | 51 | 14 | -0.006 | -0.036 | [-0.24, 0.18] | 0.621 | 1.000 | 0.558 | False |  |
| avail_h100 | 20 | 36 | 5 | n/a | 0.055 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 55 | 14 | -0.003 | -0.052 | [-0.29, 0.24] | 0.741 | 1.000 | 0.745 | False |  |
| avail_b200 | 5 | 51 | 12 | -0.005 | -0.033 | [-0.23, 0.18] | 0.646 | 1.000 | 0.698 | False |  |
| avail_b200 | 20 | 36 | 3 | n/a | 0.034 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 3 | -6.126 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 35 | -0.049 | -0.057 | 0.248 | 0.312 | 0.543 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 27 | 0.235 | 0.038 | 0.002 | 0.021 | 0.815 | 0.353 | False | 27 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 35 | -0.182 | -0.190 | 0.047 | 0.048 | 0.600 | 0.668 | False | 35 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 27 | 0.255 | 0.064 | 0.000 | 0.034 | 0.815 | 0.537 | False | 27 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 35 | -0.016 | -0.023 | 0.596 | 0.960 | 0.543 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 27 | 0.161 | -0.054 | 0.010 | 0.997 | 0.704 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 35 | 0.052 | 0.045 | 0.044 | 0.044 | 0.600 | 0.661 | False | 35 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 27 | 0.251 | 0.060 | 0.001 | 0.019 | 0.741 | 0.348 | False | 27 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 35 | -1.377 | -1.394 | 0.317 | 0.425 | 0.543 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 27 | -37.186 | -46.976 | 0.529 | 0.633 | 0.667 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 35 | -0.169 | -0.177 | 0.763 | 0.841 | 0.543 | 1.000 | False | 35 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 27 | 0.211 | 0.009 | 0.010 | 0.147 | 0.704 | 1.000 | False | 27 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 35 | 6 | 1.013 | [-2.96, 6.26] | False | 0.133 | 0.099 | 0.065 | -0.003 | -0.139 |
| level_h100 | 5 | 27 | 21 | 5.160 | [1.78, 9.35] | True | 3.399 | 3.213 | 3.026 | 2.654 | 1.908 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 35 | 7 | 2.101 | [-3.17, 6.36] | False | 0.195 | 0.155 | 0.115 | 0.035 | -0.125 |
| level_b200 | 5 | 27 | 21 | 5.620 | [1.94, 10.81] | True | 3.682 | 3.495 | 3.309 | 2.936 | 2.191 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 35 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 27 | 21 | 3.999 | [0.15, 8.93] | True | 3.047 | 2.864 | 2.681 | 2.315 | 1.582 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 35 | 4 | 3.697 | [0.00, 5.76] | False | 0.186 | 0.163 | 0.140 | 0.095 | 0.005 |
| disp_b200 | 5 | 27 | 20 | 5.382 | [1.82, 10.37] | True | 3.560 | 3.382 | 3.205 | 2.850 | 2.140 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 35 | 9 | -2.281 | [-4.86, 0.78] | False | -0.103 | -0.154 | -0.204 | -0.306 | -0.508 |
| avail_h100 | 5 | 27 | 21 | 2.890 | [0.83, 5.28] | True | 2.425 | 2.242 | 2.059 | 1.693 | 0.960 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 35 | 8 | -2.713 | [-5.37, 0.22] | False | -0.149 | -0.194 | -0.239 | -0.329 | -0.509 |
| avail_b200 | 5 | 27 | 21 | 4.475 | [1.33, 8.99] | True | 3.237 | 3.052 | 2.868 | 2.498 | 1.759 |
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
| disp_h100|h5 | False | False | True | False | False |
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
| neocloud | level_h100 | 1 | 55 | 22 | -1.181 | -0.235 | [-0.47, 0.08] | 0.099 | 0.534 | 0.073 | False |  |
| neocloud | level_h100 | 5 | 51 | 19 | -2.981 | -0.233 | [-0.38, -0.06] | 0.000 | 0.002 | 0.116 | False |  |
| neocloud | level_h100 | 20 | 36 | 8 | n/a | -0.195 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 55 | 24 | -0.636 | -0.354 | [-0.50, -0.18] | 0.001 | 0.012 | 0.018 | True |  |
| neocloud | level_b200 | 5 | 51 | 23 | -1.120 | -0.227 | [-0.40, -0.05] | 0.011 | 0.085 | 0.186 | False |  |
| neocloud | level_b200 | 20 | 36 | 14 | n/a | -0.283 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 55 | 46 | 0.057 | 0.046 | [-0.14, 0.22] | 0.705 | 1.000 | 0.727 | False |  |
| neocloud | disp_h100 | 5 | 51 | 43 | -0.159 | -0.050 | [-0.36, 0.18] | 0.674 | 1.000 | 0.651 | False |  |
| neocloud | disp_h100 | 20 | 36 | 30 | n/a | -0.153 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 55 | 12 | 0.318 | 0.368 | [0.13, 0.52] | 0.000 | 0.000 | 0.018 | True |  |
| neocloud | disp_b200 | 5 | 51 | 11 | 0.467 | 0.214 | [0.07, 0.36] | 0.000 | 0.000 | 0.070 | False |  |
| neocloud | disp_b200 | 20 | 36 | 7 | n/a | 0.234 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 55 | 17 | -0.011 | -0.108 | [-0.36, 0.18] | 0.502 | 1.000 | 0.400 | False |  |
| neocloud | avail_h100 | 5 | 51 | 14 | -0.012 | -0.046 | [-0.24, 0.15] | 0.489 | 1.000 | 0.465 | False |  |
| neocloud | avail_h100 | 20 | 36 | 5 | n/a | 0.006 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 55 | 14 | -0.010 | -0.105 | [-0.36, 0.19] | 0.520 | 1.000 | 0.418 | False |  |
| neocloud | avail_b200 | 5 | 51 | 12 | -0.012 | -0.048 | [-0.24, 0.14] | 0.464 | 1.000 | 0.535 | False |  |
| neocloud | avail_b200 | 20 | 36 | 3 | n/a | -0.015 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 55 | 22 | -0.439 | -0.225 | [-0.57, 0.22] | 0.272 | 0.917 | 0.091 | False |  |
| gpu_semis | level_h100 | 5 | 51 | 19 | -0.977 | -0.169 | [-0.44, 0.16] | 0.205 | 0.750 | 0.302 | False |  |
| gpu_semis | level_h100 | 20 | 36 | 8 | n/a | -0.175 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 55 | 24 | -0.176 | -0.251 | [-0.59, 0.04] | 0.208 | 0.750 | 0.055 | False |  |
| gpu_semis | level_b200 | 5 | 51 | 23 | -0.288 | -0.129 | [-0.34, 0.19] | 0.138 | 0.620 | 0.512 | False |  |
| gpu_semis | level_b200 | 20 | 36 | 14 | n/a | -0.285 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 55 | 46 | 0.024 | 0.050 | [-0.20, 0.30] | 0.735 | 1.000 | 0.673 | False |  |
| gpu_semis | disp_h100 | 5 | 51 | 43 | -0.056 | -0.038 | [-0.29, 0.16] | 0.682 | 1.000 | 0.651 | False |  |
| gpu_semis | disp_h100 | 20 | 36 | 30 | n/a | -0.092 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 55 | 12 | 0.118 | 0.349 | [-0.02, 0.62] | 0.037 | 0.221 | 0.018 | False |  |
| gpu_semis | disp_b200 | 5 | 51 | 11 | 0.192 | 0.194 | [-0.05, 0.34] | 0.000 | 0.002 | 0.233 | False |  |
| gpu_semis | disp_b200 | 20 | 36 | 7 | n/a | 0.261 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 55 | 17 | -0.001 | -0.019 | [-0.28, 0.33] | 0.908 | 1.000 | 0.945 | False |  |
| gpu_semis | avail_h100 | 5 | 51 | 14 | -0.002 | -0.020 | [-0.20, 0.15] | 0.763 | 1.000 | 0.791 | False |  |
| gpu_semis | avail_h100 | 20 | 36 | 5 | n/a | 0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 55 | 14 | -0.000 | -0.004 | [-0.27, 0.34] | 0.980 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 51 | 12 | -0.002 | -0.022 | [-0.19, 0.15] | 0.740 | 1.000 | 0.791 | False |  |
| gpu_semis | avail_b200 | 20 | 36 | 3 | n/a | 0.005 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 55 | 22 | -0.588 | -0.171 | [-0.33, 0.08] | 0.129 | 0.620 | 0.273 | False |  |
| power_capacity | level_h100 | 5 | 51 | 19 | -0.550 | -0.068 | [-0.28, 0.25] | 0.516 | 1.000 | 0.605 | False |  |
| power_capacity | level_h100 | 20 | 36 | 8 | n/a | 0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 55 | 24 | -0.332 | -0.269 | [-0.42, -0.08] | 0.032 | 0.215 | 0.055 | False |  |
| power_capacity | level_b200 | 5 | 51 | 23 | -0.229 | -0.074 | [-0.41, 0.12] | 0.480 | 1.000 | 0.581 | False |  |
| power_capacity | level_b200 | 20 | 36 | 14 | n/a | -0.039 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 55 | 46 | 0.073 | 0.086 | [-0.09, 0.27] | 0.460 | 1.000 | 0.655 | False |  |
| power_capacity | disp_h100 | 5 | 51 | 43 | 0.005 | 0.003 | [-0.27, 0.22] | 0.982 | 1.000 | 0.930 | False |  |
| power_capacity | disp_h100 | 20 | 36 | 30 | n/a | -0.175 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 55 | 12 | 0.141 | 0.238 | [-0.06, 0.37] | 0.004 | 0.032 | 0.091 | False |  |
| power_capacity | disp_b200 | 5 | 51 | 11 | 0.123 | 0.089 | [-0.08, 0.30] | 0.154 | 0.638 | 0.512 | False |  |
| power_capacity | disp_b200 | 20 | 36 | 7 | n/a | 0.009 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 55 | 17 | 0.000 | 0.004 | [-0.19, 0.25] | 0.971 | 1.000 | 0.982 | False |  |
| power_capacity | avail_h100 | 5 | 51 | 14 | -0.004 | -0.024 | [-0.25, 0.23] | 0.781 | 1.000 | 0.698 | False |  |
| power_capacity | avail_h100 | 20 | 36 | 5 | n/a | 0.209 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 55 | 14 | 0.001 | 0.012 | [-0.18, 0.25] | 0.927 | 1.000 | 0.945 | False |  |
| power_capacity | avail_b200 | 5 | 51 | 12 | -0.002 | -0.011 | [-0.23, 0.25] | 0.905 | 1.000 | 0.884 | False |  |
| power_capacity | avail_b200 | 20 | 36 | 3 | n/a | 0.209 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.03 [-0.16, 0.22] | 0.10 [-0.08, 0.22] |
| -4 | -0.02 [-0.14, 0.13] | -0.27 [-0.43, -0.05] |
| -3 | -0.11 [-0.26, 0.07] | 0.12 [-0.23, 0.42] |
| -2 | -0.22 [-0.43, 0.04] | -0.22 [-0.41, 0.16] |
| -1 | 0.09 [-0.27, 0.45] | -0.23 [-0.39, 0.02] |
| 0 | -0.34 [-0.52, -0.14] | -0.23 [-0.48, 0.10] |
| 1 | -0.05 [-0.29, 0.27] | -0.22 [-0.49, 0.22] |
| 2 | 0.02 [-0.30, 0.20] | 0.17 [-0.20, 0.45] |
| 3 | -0.08 [-0.28, 0.29] | 0.05 [-0.15, 0.21] |
| 4 | -0.05 [-0.23, 0.02] | -0.14 [-0.44, -0.02] |
| 5 | -0.10 [-0.24, 0.03] | -0.04 [-0.27, 0.30] |

