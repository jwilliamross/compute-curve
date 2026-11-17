# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-17T05:15:04.141795+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `b4d6ed227f1185fb...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 5 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 42 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 62 | 2026-08-20 | 2026-11-16 | 0.35 | 0.46 |
| 5 | 58 | 2026-08-20 | 2026-11-10 | 0.36 | 0.48 |
| 20 | 43 | 2026-08-20 | 2026-10-20 | 0.42 | 0.54 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 62 | 27 | 0.063 | 0.048 | [-0.36, 0.25] | 0.658 | 1.000 | 0.790 | False |  |
| level_h100 | 5 | 58 | 24 | 0.067 | 0.010 | [-0.26, 0.27] | 0.938 | 1.000 | 0.960 | False |  |
| level_h100 | 20 | 43 | 13 | n/a | -0.135 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 62 | 25 | -0.403 | -0.342 | [-0.51, -0.15] | 0.011 | 0.194 | 0.016 | False |  |
| level_b200 | 5 | 58 | 24 | -0.392 | -0.131 | [-0.32, 0.02] | 0.086 | 1.000 | 0.400 | False |  |
| level_b200 | 20 | 43 | 21 | n/a | -0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 62 | 49 | 0.069 | 0.093 | [-0.12, 0.32] | 0.461 | 1.000 | 0.597 | False |  |
| disp_h100 | 5 | 58 | 47 | -0.210 | -0.109 | [-0.40, 0.14] | 0.329 | 1.000 | 0.280 | False |  |
| disp_h100 | 20 | 43 | 36 | n/a | -0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 62 | 14 | 0.143 | 0.266 | [-0.11, 0.46] | 0.015 | 0.250 | 0.048 | False |  |
| disp_b200 | 5 | 58 | 13 | 0.163 | 0.116 | [-0.08, 0.25] | 0.055 | 0.881 | 0.320 | False |  |
| disp_b200 | 20 | 43 | 7 | n/a | 0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 62 | 18 | -0.004 | -0.056 | [-0.28, 0.23] | 0.712 | 1.000 | 0.694 | False |  |
| avail_h100 | 5 | 58 | 17 | -0.008 | -0.047 | [-0.21, 0.10] | 0.422 | 1.000 | 0.320 | False |  |
| avail_h100 | 20 | 43 | 10 | n/a | -0.027 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 62 | 15 | -0.003 | -0.047 | [-0.27, 0.24] | 0.760 | 1.000 | 0.774 | False |  |
| avail_b200 | 5 | 58 | 14 | -0.009 | -0.057 | [-0.21, 0.09] | 0.312 | 1.000 | 0.360 | False |  |
| avail_b200 | 20 | 43 | 8 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 5 | -0.081 | n/a | 1.000 | 1.000 | False | insufficient events (5 < 10); descriptive only |
| H100 | 5 | 3 | 0.974 | n/a | 1.000 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.733 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 42 | -0.221 | -0.203 | 0.691 | 0.744 | 0.476 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 34 | -0.026 | -0.118 | 0.212 | 0.726 | 0.765 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 4 | 0.851 | 0.033 | n/a | n/a | 1.000 | n/a | False | 4 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 42 | -0.166 | -0.148 | 0.051 | 0.037 | 0.524 | 0.920 | False | 42 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 34 | 0.105 | 0.024 | 0.024 | 0.061 | 0.765 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 4 | 0.908 | 0.404 | n/a | n/a | 1.000 | n/a | False | 4 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 42 | -0.033 | -0.017 | 0.800 | 0.811 | 0.476 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 34 | 0.049 | -0.037 | 0.118 | 0.982 | 0.676 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 4 | 0.887 | 0.267 | n/a | n/a | 1.000 | n/a | False | 4 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 42 | -0.044 | -0.029 | 0.197 | 0.175 | 0.500 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 34 | 0.087 | 0.005 | 0.052 | 0.242 | 0.706 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 4 | 0.856 | 0.065 | n/a | n/a | 1.000 | n/a | False | 4 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 42 | -1.253 | -1.220 | 0.373 | 0.426 | 0.476 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 34 | -30.126 | -32.919 | 0.544 | 0.631 | 0.647 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 4 | -188.628 | -1,228.753 | n/a | n/a | 0.250 | n/a | False | 4 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 42 | -0.173 | -0.156 | 0.832 | 0.841 | 0.476 | 1.000 | False | 42 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 34 | 0.094 | 0.013 | 0.061 | 0.119 | 0.676 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 4 | 0.846 | 0.000 | n/a | n/a | 1.000 | n/a | False | 4 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 42 | 9 | -1.341 | [-5.79, 4.55] | False | -0.006 | -0.049 | -0.091 | -0.176 | -0.346 |
| level_h100 | 5 | 34 | 27 | 2.610 | [-0.94, 7.33] | False | 2.189 | 1.999 | 1.808 | 1.428 | 0.667 |
| level_h100 | 20 | 4 | 4 | 6.718 | n/a | False | 5.750 | 5.362 | 4.973 | 4.196 | 2.643 |
| level_b200 | 1 | 42 | 7 | 1.920 | [-3.59, 6.19] | False | 0.163 | 0.129 | 0.096 | 0.029 | -0.104 |
| level_b200 | 5 | 34 | 28 | 3.072 | [-0.66, 8.59] | False | 2.554 | 2.356 | 2.159 | 1.764 | 0.975 |
| level_b200 | 20 | 4 | 4 | 6.718 | n/a | False | 5.750 | 5.362 | 4.973 | 4.196 | 2.643 |
| disp_h100 | 1 | 42 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 34 | 28 | 2.233 | [-1.56, 7.10] | False | 2.050 | 1.855 | 1.660 | 1.271 | 0.492 |
| disp_h100 | 20 | 4 | 4 | 6.718 | n/a | False | 5.750 | 5.362 | 4.973 | 4.196 | 2.643 |
| disp_b200 | 1 | 42 | 6 | -0.003 | [-4.32, 4.53] | False | 0.056 | 0.028 | -0.000 | -0.056 | -0.169 |
| disp_b200 | 5 | 34 | 27 | 2.947 | [-0.78, 8.27] | False | 2.457 | 2.267 | 2.076 | 1.696 | 0.935 |
| disp_b200 | 20 | 4 | 4 | 6.718 | n/a | False | 5.750 | 5.362 | 4.973 | 4.196 | 2.643 |
| avail_h100 | 1 | 42 | 9 | -2.084 | [-4.54, 1.24] | False | -0.086 | -0.128 | -0.170 | -0.255 | -0.423 |
| avail_h100 | 5 | 34 | 28 | 1.533 | [-1.16, 4.40] | False | 1.556 | 1.361 | 1.166 | 0.777 | -0.002 |
| avail_h100 | 20 | 4 | 4 | -1.803 | n/a | False | -2.678 | -2.933 | -3.187 | -3.696 | -4.714 |
| avail_b200 | 1 | 42 | 8 | -2.477 | [-4.97, 0.56] | False | -0.124 | -0.162 | -0.199 | -0.274 | -0.424 |
| avail_b200 | 5 | 34 | 28 | 2.488 | [-0.83, 7.06] | False | 2.201 | 2.005 | 1.809 | 1.417 | 0.633 |
| avail_b200 | 20 | 4 | 4 | 6.718 | n/a | False | 5.750 | 5.362 | 4.973 | 4.196 | 2.643 |

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
| neocloud | level_h100 | 1 | 62 | 27 | 0.219 | 0.104 | [-0.35, 0.34] | 0.352 | 1.000 | 0.548 | False |  |
| neocloud | level_h100 | 5 | 58 | 24 | -0.693 | -0.071 | [-0.30, 0.17] | 0.572 | 1.000 | 0.660 | False |  |
| neocloud | level_h100 | 20 | 43 | 13 | n/a | -0.192 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 62 | 25 | -0.668 | -0.353 | [-0.49, -0.20] | 0.001 | 0.016 | 0.016 | True |  |
| neocloud | level_b200 | 5 | 58 | 24 | -0.863 | -0.193 | [-0.33, -0.04] | 0.011 | 0.151 | 0.220 | False |  |
| neocloud | level_b200 | 20 | 43 | 21 | n/a | -0.288 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 62 | 49 | 0.060 | 0.050 | [-0.16, 0.25] | 0.667 | 1.000 | 0.806 | False |  |
| neocloud | disp_h100 | 5 | 58 | 47 | -0.385 | -0.133 | [-0.42, 0.12] | 0.242 | 1.000 | 0.060 | False |  |
| neocloud | disp_h100 | 20 | 43 | 36 | n/a | -0.140 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 62 | 14 | 0.238 | 0.275 | [-0.08, 0.46] | 0.003 | 0.046 | 0.032 | True |  |
| neocloud | disp_b200 | 5 | 58 | 13 | 0.382 | 0.181 | [0.03, 0.30] | 0.000 | 0.000 | 0.140 | False |  |
| neocloud | disp_b200 | 20 | 43 | 7 | n/a | 0.231 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 62 | 18 | -0.010 | -0.100 | [-0.34, 0.18] | 0.514 | 1.000 | 0.387 | False |  |
| neocloud | avail_h100 | 5 | 58 | 17 | -0.009 | -0.038 | [-0.20, 0.12] | 0.540 | 1.000 | 0.600 | False |  |
| neocloud | avail_h100 | 20 | 43 | 10 | n/a | -0.042 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 62 | 15 | -0.010 | -0.094 | [-0.34, 0.19] | 0.547 | 1.000 | 0.435 | False |  |
| neocloud | avail_b200 | 5 | 58 | 14 | -0.012 | -0.049 | [-0.21, 0.10] | 0.397 | 1.000 | 0.500 | False |  |
| neocloud | avail_b200 | 20 | 43 | 8 | n/a | -0.052 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 62 | 27 | -0.010 | -0.012 | [-0.41, 0.19] | 0.919 | 1.000 | 0.968 | False |  |
| gpu_semis | level_h100 | 5 | 58 | 24 | 0.156 | 0.034 | [-0.26, 0.30] | 0.798 | 1.000 | 0.740 | False |  |
| gpu_semis | level_h100 | 20 | 43 | 13 | n/a | -0.169 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 62 | 25 | -0.188 | -0.259 | [-0.58, 0.02] | 0.174 | 0.937 | 0.065 | False |  |
| gpu_semis | level_b200 | 5 | 58 | 24 | -0.230 | -0.107 | [-0.30, 0.07] | 0.129 | 0.868 | 0.480 | False |  |
| gpu_semis | level_b200 | 20 | 43 | 21 | n/a | -0.305 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 62 | 49 | 0.044 | 0.095 | [-0.18, 0.36] | 0.506 | 1.000 | 0.484 | False |  |
| gpu_semis | disp_h100 | 5 | 58 | 47 | -0.121 | -0.088 | [-0.35, 0.15] | 0.392 | 1.000 | 0.280 | False |  |
| gpu_semis | disp_h100 | 20 | 43 | 36 | n/a | -0.100 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 62 | 14 | 0.091 | 0.273 | [-0.11, 0.56] | 0.097 | 0.746 | 0.048 | False |  |
| gpu_semis | disp_b200 | 5 | 58 | 13 | 0.109 | 0.109 | [-0.14, 0.28] | 0.150 | 0.900 | 0.320 | False |  |
| gpu_semis | disp_b200 | 20 | 43 | 7 | n/a | 0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 62 | 18 | -0.001 | -0.018 | [-0.27, 0.31] | 0.911 | 1.000 | 0.935 | False |  |
| gpu_semis | avail_h100 | 5 | 58 | 17 | -0.006 | -0.055 | [-0.18, 0.08] | 0.295 | 1.000 | 0.340 | False |  |
| gpu_semis | avail_h100 | 20 | 43 | 10 | n/a | -0.015 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 62 | 15 | -0.000 | -0.003 | [-0.27, 0.32] | 0.984 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 58 | 14 | -0.008 | -0.068 | [-0.20, 0.06] | 0.194 | 0.952 | 0.260 | False |  |
| gpu_semis | avail_b200 | 20 | 43 | 8 | n/a | -0.028 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 62 | 27 | -0.019 | -0.013 | [-0.25, 0.10] | 0.860 | 1.000 | 0.952 | False |  |
| power_capacity | level_h100 | 5 | 58 | 24 | 0.738 | 0.113 | [-0.19, 0.36] | 0.353 | 1.000 | 0.340 | False |  |
| power_capacity | level_h100 | 20 | 43 | 13 | n/a | 0.093 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 62 | 25 | -0.352 | -0.277 | [-0.44, -0.09] | 0.022 | 0.234 | 0.048 | False |  |
| power_capacity | level_b200 | 5 | 58 | 24 | -0.081 | -0.027 | [-0.31, 0.12] | 0.701 | 1.000 | 0.860 | False |  |
| power_capacity | level_b200 | 20 | 43 | 21 | n/a | -0.015 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 62 | 49 | 0.103 | 0.128 | [-0.09, 0.34] | 0.286 | 1.000 | 0.323 | False |  |
| power_capacity | disp_h100 | 5 | 58 | 47 | -0.124 | -0.064 | [-0.34, 0.20] | 0.575 | 1.000 | 0.600 | False |  |
| power_capacity | disp_h100 | 20 | 43 | 36 | n/a | -0.013 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 62 | 14 | 0.100 | 0.172 | [-0.14, 0.32] | 0.074 | 0.665 | 0.323 | False |  |
| power_capacity | disp_b200 | 5 | 58 | 13 | -0.003 | -0.002 | [-0.19, 0.17] | 0.981 | 1.000 | 0.960 | False |  |
| power_capacity | disp_b200 | 20 | 43 | 7 | n/a | 0.000 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 62 | 18 | 0.000 | 0.004 | [-0.17, 0.24] | 0.970 | 1.000 | 0.984 | False |  |
| power_capacity | avail_h100 | 5 | 58 | 17 | -0.007 | -0.045 | [-0.23, 0.13] | 0.500 | 1.000 | 0.400 | False |  |
| power_capacity | avail_h100 | 20 | 43 | 10 | n/a | 0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 62 | 15 | 0.001 | 0.012 | [-0.17, 0.24] | 0.925 | 1.000 | 0.919 | False |  |
| power_capacity | avail_b200 | 5 | 58 | 14 | -0.008 | -0.048 | [-0.23, 0.14] | 0.491 | 1.000 | 0.440 | False |  |
| power_capacity | avail_b200 | 20 | 43 | 8 | n/a | 0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.15, 0.21] | -0.10 [-0.26, 0.18] |
| -4 | -0.02 [-0.14, 0.10] | -0.33 [-0.49, -0.13] |
| -3 | -0.11 [-0.26, 0.04] | 0.08 [-0.15, 0.38] |
| -2 | -0.22 [-0.42, 0.01] | -0.12 [-0.32, 0.11] |
| -1 | 0.08 [-0.26, 0.42] | -0.23 [-0.36, -0.07] |
| 0 | -0.34 [-0.51, -0.15] | 0.05 [-0.36, 0.25] |
| 1 | -0.06 [-0.29, 0.24] | 0.02 [-0.32, 0.26] |
| 2 | 0.06 [-0.24, 0.22] | 0.06 [-0.20, 0.36] |
| 3 | 0.01 [-0.25, 0.29] | 0.09 [-0.05, 0.25] |
| 4 | -0.03 [-0.15, 0.05] | 0.01 [-0.32, 0.25] |
| 5 | -0.03 [-0.19, 0.15] | -0.08 [-0.25, 0.11] |

