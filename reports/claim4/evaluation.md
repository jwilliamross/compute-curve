# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-13T03:50:06.517694+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `7c1b4142b8831624...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 17 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 37 | 2026-08-20 | 2026-10-12 | 0.45 | 0.58 |
| 5 | 33 | 2026-08-20 | 2026-10-06 | 0.47 | 0.60 |
| 20 | 18 | 2026-08-20 | 2026-09-15 | 0.62 | 0.76 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 37 | 9 | -0.983 | -0.395 | [-0.59, 0.11] | 0.007 | 0.114 | 0.054 | False | insufficient variation (9 non-zero < 10) |
| level_h100 | 5 | 33 | 5 | -1.095 | -0.156 | [-0.33, 0.13] | 0.019 | 0.245 | 0.400 | False | insufficient variation (5 non-zero < 10) |
| level_h100 | 20 | 18 | 3 | n/a | 0.035 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 37 | 15 | -0.326 | -0.356 | [-0.61, -0.09] | 0.084 | 1.000 | 0.054 | False |  |
| level_b200 | 5 | 33 | 11 | -0.406 | -0.157 | [-0.30, 0.33] | 0.014 | 0.208 | 0.440 | False |  |
| level_b200 | 20 | 18 | 2 | n/a | -0.067 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 37 | 31 | -0.041 | -0.050 | [-0.28, 0.17] | 0.631 | 1.000 | 0.784 | False |  |
| disp_h100 | 5 | 33 | 27 | 0.107 | 0.046 | [-0.31, 0.26] | 0.684 | 1.000 | 0.800 | False |  |
| disp_h100 | 20 | 18 | 13 | n/a | -0.120 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 37 | 7 | 0.168 | 0.414 | [-0.06, 0.59] | 0.002 | 0.026 | 0.027 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 33 | 6 | 0.192 | 0.165 | [-0.12, 0.35] | 0.000 | 0.000 | 0.240 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 20 | 18 | 1 | n/a | 0.020 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 37 | 5 | 0.015 | 0.135 | [-0.38, 0.33] | 0.128 | 1.000 | 0.459 | False | insufficient variation (5 non-zero < 10) |
| avail_h100 | 5 | 33 | 3 | -0.622 | -0.266 | [-0.50, -0.06] | 0.130 | 1.000 | 0.120 | False | insufficient variation (3 non-zero < 10) |
| avail_h100 | 20 | 18 | 2 | n/a | -0.355 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 37 | 3 | 0.013 | 0.121 | [-0.18, 0.32] | 0.238 | 1.000 | 0.486 | False | insufficient variation (3 non-zero < 10) |
| avail_b200 | 5 | 33 | 1 | -0.112 | -0.115 | [-0.25, -0.06] | 0.015 | 0.208 | 0.560 | False | insufficient variation (1 non-zero < 10) |
| avail_b200 | 20 | 18 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 17 | -0.013 | -0.043 | 0.020 | 0.021 | 0.588 | 0.377 | False | 17 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 9 | 0.111 | 0.032 | n/a | n/a | 0.889 | n/a | False | 9 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 17 | -1.127 | -1.189 | 0.105 | 0.112 | 0.647 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 9 | 0.198 | 0.126 | n/a | n/a | 0.889 | n/a | False | 9 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 17 | 0.031 | 0.003 | 0.161 | 0.231 | 0.588 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 9 | -0.007 | -0.097 | n/a | n/a | 0.556 | n/a | False | 9 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 17 | -0.045 | -0.076 | 0.084 | 0.100 | 0.647 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 9 | 0.193 | 0.121 | n/a | n/a | 0.667 | n/a | False | 9 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 17 | -5.564 | -5.757 | 0.106 | 0.170 | 0.529 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 9 | -2.042 | -2.313 | n/a | n/a | 0.667 | n/a | False | 9 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 17 | -0.335 | -0.374 | 0.642 | 0.823 | 0.529 | 1.000 | False | 17 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 9 | 0.082 | 0.000 | n/a | n/a | 0.667 | n/a | False | 9 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 17 | 2 | 5.018 | [0.00, 8.87] | False | 0.145 | 0.121 | 0.098 | 0.051 | -0.043 |
| level_h100 | 5 | 9 | 4 | 4.293 | n/a | False | 1.509 | 1.402 | 1.296 | 1.083 | 0.657 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 17 | 5 | -1.744 | [-8.07, 7.13] | False | 0.030 | -0.028 | -0.087 | -0.205 | -0.440 |
| level_b200 | 5 | 9 | 3 | 4.527 | n/a | False | 1.502 | 1.422 | 1.342 | 1.183 | 0.863 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 17 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 9 | 3 | -1.202 | n/a | False | -0.402 | -0.472 | -0.542 | -0.682 | -0.962 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 17 | 3 | 4.728 | [-3.85, 7.74] | False | 0.160 | 0.125 | 0.090 | 0.020 | -0.119 |
| disp_b200 | 5 | 9 | 2 | 3.536 | n/a | False | 1.137 | 1.083 | 1.030 | 0.924 | 0.711 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 17 | 3 | -2.398 | [-6.24, 5.62] | False | -0.057 | -0.092 | -0.127 | -0.196 | -0.335 |
| avail_h100 | 5 | 9 | 3 | 4.527 | n/a | False | 1.502 | 1.422 | 1.342 | 1.183 | 0.863 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 17 | 2 | -4.127 | [-7.72, 0.00] | False | -0.153 | -0.176 | -0.199 | -0.245 | -0.337 |
| avail_b200 | 5 | 9 | 3 | 4.527 | n/a | False | 1.502 | 1.422 | 1.342 | 1.183 | 0.863 |
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
| neocloud | level_h100 | 1 | 37 | 9 | -1.564 | -0.397 | [-0.57, 0.17] | 0.004 | 0.022 | 0.027 | False | insufficient variation (9 non-zero < 10) |
| neocloud | level_h100 | 5 | 33 | 5 | -2.558 | -0.236 | [-0.40, -0.07] | 0.000 | 0.000 | 0.240 | False | insufficient variation (5 non-zero < 10) |
| neocloud | level_h100 | 20 | 18 | 3 | n/a | -0.069 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 37 | 15 | -0.601 | -0.415 | [-0.58, -0.10] | 0.017 | 0.059 | 0.027 | True |  |
| neocloud | level_b200 | 5 | 33 | 11 | -0.903 | -0.226 | [-0.39, 0.37] | 0.000 | 0.001 | 0.280 | False |  |
| neocloud | level_b200 | 20 | 18 | 2 | n/a | -0.162 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 37 | 31 | -0.109 | -0.083 | [-0.33, 0.20] | 0.466 | 0.967 | 0.649 | False |  |
| neocloud | disp_h100 | 5 | 33 | 27 | 0.135 | 0.038 | [-0.32, 0.26] | 0.742 | 1.000 | 0.880 | False |  |
| neocloud | disp_h100 | 20 | 18 | 13 | n/a | -0.118 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 37 | 7 | 0.293 | 0.457 | [-0.02, 0.60] | 0.000 | 0.000 | 0.027 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 33 | 6 | 0.372 | 0.207 | [-0.13, 0.43] | 0.000 | 0.000 | 0.160 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 20 | 18 | 1 | n/a | 0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 37 | 5 | 0.006 | 0.032 | [-0.38, 0.24] | 0.816 | 1.000 | 0.919 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_h100 | 5 | 33 | 3 | -1.215 | -0.336 | [-0.51, -0.08] | 0.048 | 0.137 | 0.080 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_h100 | 20 | 18 | 2 | n/a | -0.401 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 37 | 3 | 0.000 | 0.002 | [-0.33, 0.26] | 0.989 | 1.000 | 1.000 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_b200 | 5 | 33 | 1 | -0.291 | -0.193 | [-0.37, -0.16] | 0.000 | 0.002 | 0.240 | False | insufficient variation (1 non-zero < 10) |
| neocloud | avail_b200 | 20 | 18 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 37 | 9 | -0.690 | -0.405 | [-0.69, 0.04] | 0.012 | 0.048 | 0.027 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | level_h100 | 5 | 33 | 5 | -0.599 | -0.135 | [-0.35, 0.21] | 0.161 | 0.395 | 0.640 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 18 | 3 | n/a | -0.079 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 37 | 15 | -0.144 | -0.230 | [-0.70, 0.14] | 0.383 | 0.847 | 0.270 | False |  |
| gpu_semis | level_b200 | 5 | 33 | 11 | -0.244 | -0.149 | [-0.32, 0.50] | 0.012 | 0.048 | 0.520 | False |  |
| gpu_semis | level_b200 | 20 | 18 | 2 | n/a | -0.171 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 37 | 31 | 0.004 | 0.008 | [-0.32, 0.20] | 0.954 | 1.000 | 0.919 | False |  |
| gpu_semis | disp_h100 | 5 | 33 | 27 | 0.010 | 0.007 | [-0.34, 0.26] | 0.956 | 1.000 | 0.960 | False |  |
| gpu_semis | disp_h100 | 20 | 18 | 13 | n/a | 0.079 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 37 | 7 | 0.105 | 0.379 | [-0.11, 0.70] | 0.088 | 0.237 | 0.054 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 33 | 6 | 0.139 | 0.189 | [-0.19, 0.36] | 0.000 | 0.000 | 0.240 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 18 | 1 | n/a | 0.105 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 37 | 5 | 0.021 | 0.281 | [-0.29, 0.51] | 0.000 | 0.000 | 0.108 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 33 | 3 | -0.359 | -0.243 | [-0.42, -0.06] | 0.040 | 0.120 | 0.080 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 18 | 2 | n/a | -0.184 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 37 | 3 | 0.021 | 0.288 | [0.00, 0.52] | 0.000 | 0.000 | 0.081 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 33 | 1 | -0.084 | -0.136 | [-0.29, -0.07] | 0.005 | 0.024 | 0.680 | False | insufficient variation (1 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 18 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 37 | 9 | -0.695 | -0.246 | [-0.40, 0.14] | 0.028 | 0.096 | 0.216 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | level_h100 | 5 | 33 | 5 | -0.127 | -0.018 | [-0.26, 0.45] | 0.867 | 1.000 | 0.920 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | level_h100 | 20 | 18 | 3 | n/a | 0.288 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 37 | 15 | -0.231 | -0.223 | [-0.42, -0.03] | 0.129 | 0.331 | 0.189 | False |  |
| power_capacity | level_b200 | 5 | 33 | 11 | -0.072 | -0.027 | [-0.29, 0.23] | 0.728 | 1.000 | 0.920 | False |  |
| power_capacity | level_b200 | 20 | 18 | 2 | n/a | 0.194 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 37 | 31 | -0.020 | -0.021 | [-0.23, 0.22] | 0.847 | 1.000 | 0.919 | False |  |
| power_capacity | disp_h100 | 5 | 33 | 27 | 0.174 | 0.073 | [-0.27, 0.31] | 0.545 | 1.000 | 0.720 | False |  |
| power_capacity | disp_h100 | 20 | 18 | 13 | n/a | -0.202 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 37 | 7 | 0.105 | 0.229 | [-0.24, 0.38] | 0.034 | 0.109 | 0.189 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 33 | 6 | 0.064 | 0.054 | [-0.17, 0.29] | 0.380 | 0.847 | 0.640 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 18 | 1 | n/a | -0.208 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 37 | 5 | 0.018 | 0.144 | [-0.42, 0.33] | 0.004 | 0.022 | 0.378 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 33 | 3 | -0.294 | -0.123 | [-0.46, 0.22] | 0.519 | 1.000 | 0.640 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 18 | 2 | n/a | -0.252 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 37 | 3 | 0.017 | 0.145 | [-0.08, 0.32] | 0.013 | 0.049 | 0.405 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 33 | 1 | 0.038 | 0.038 | [-0.06, 0.25] | 0.392 | 0.847 | 0.960 | False | insufficient variation (1 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 18 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.25, 0.25] | 0.15 [-0.15, 0.33] |
| -4 | -0.01 [-0.23, 0.23] | -0.19 [-0.36, 0.04] |
| -3 | -0.19 [-0.37, 0.13] | -0.18 [-0.41, 0.02] |
| -2 | -0.21 [-0.45, 0.03] | -0.19 [-0.40, 0.22] |
| -1 | -0.09 [-0.37, 0.23] | -0.34 [-0.47, 0.10] |
| 0 | -0.36 [-0.61, -0.09] | -0.39 [-0.59, 0.11] |
| 1 | 0.04 [-0.32, 0.44] | -0.05 [-0.29, 0.48] |
| 2 | 0.09 [-0.29, 0.36] | 0.06 [-0.31, 0.36] |
| 3 | -0.17 [-0.43, 0.22] | 0.04 [-0.41, 0.27] |
| 4 | -0.04 [-0.23, 0.08] | -0.03 [-0.20, 0.08] |
| 5 | -0.13 [-0.33, 0.08] | -0.14 [-0.44, 0.10] |

