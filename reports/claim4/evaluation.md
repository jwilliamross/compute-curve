# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-08T02:42:17.768765+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `8d03df1ebd360a2a...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 4 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 36 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 56 | 2026-08-20 | 2026-11-06 | 0.37 | 0.48 |
| 5 | 52 | 2026-08-20 | 2026-11-02 | 0.38 | 0.50 |
| 20 | 37 | 2026-08-20 | 2026-10-12 | 0.45 | 0.58 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 56 | 23 | -0.285 | -0.114 | [-0.44, 0.19] | 0.551 | 1.000 | 0.411 | False |  |
| level_h100 | 5 | 52 | 20 | -1.224 | -0.154 | [-0.32, 0.08] | 0.052 | 0.779 | 0.250 | False |  |
| level_h100 | 20 | 37 | 9 | n/a | -0.141 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 56 | 24 | -0.385 | -0.340 | [-0.52, -0.14] | 0.015 | 0.244 | 0.018 | False |  |
| level_b200 | 5 | 52 | 23 | -0.539 | -0.168 | [-0.38, 0.00] | 0.084 | 1.000 | 0.295 | False |  |
| level_b200 | 20 | 37 | 15 | n/a | -0.264 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 56 | 46 | 0.051 | 0.066 | [-0.12, 0.27] | 0.602 | 1.000 | 0.607 | False |  |
| disp_h100 | 5 | 52 | 44 | -0.098 | -0.049 | [-0.32, 0.15] | 0.641 | 1.000 | 0.591 | False |  |
| disp_h100 | 20 | 37 | 31 | n/a | -0.156 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 56 | 12 | 0.192 | 0.353 | [0.08, 0.52] | 0.000 | 0.001 | 0.018 | True |  |
| disp_b200 | 5 | 52 | 11 | 0.261 | 0.184 | [0.05, 0.35] | 0.000 | 0.002 | 0.205 | False |  |
| disp_b200 | 20 | 37 | 7 | n/a | 0.209 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 56 | 17 | -0.004 | -0.059 | [-0.29, 0.23] | 0.704 | 1.000 | 0.679 | False |  |
| avail_h100 | 5 | 52 | 15 | -0.008 | -0.052 | [-0.23, 0.12] | 0.443 | 1.000 | 0.341 | False |  |
| avail_h100 | 20 | 37 | 5 | n/a | 0.055 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 56 | 14 | -0.003 | -0.052 | [-0.30, 0.23] | 0.741 | 1.000 | 0.750 | False |  |
| avail_b200 | 5 | 52 | 13 | -0.008 | -0.049 | [-0.22, 0.12] | 0.454 | 1.000 | 0.386 | False |  |
| avail_b200 | 20 | 37 | 3 | n/a | 0.035 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 3 | -1.287 | n/a | 0.750 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 3 | -6.126 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 36 | -0.163 | -0.164 | 0.487 | 0.596 | 0.528 | 1.000 | False | 36 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 28 | 0.233 | 0.023 | 0.001 | 0.017 | 0.821 | 0.299 | False | 28 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 36 | -0.182 | -0.183 | 0.049 | 0.046 | 0.583 | 0.734 | False | 36 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 28 | 0.264 | 0.061 | 0.000 | 0.040 | 0.821 | 0.633 | False | 28 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 36 | -0.021 | -0.023 | 0.669 | 0.958 | 0.528 | 1.000 | False | 36 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 28 | 0.178 | -0.048 | 0.010 | 0.991 | 0.714 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 36 | 0.046 | 0.045 | 0.049 | 0.044 | 0.583 | 0.734 | False | 36 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 28 | 0.262 | 0.059 | 0.001 | 0.020 | 0.750 | 0.343 | False | 28 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 36 | -1.366 | -1.369 | 0.331 | 0.425 | 0.528 | 1.000 | False | 36 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 28 | -36.257 | -46.498 | 0.521 | 0.632 | 0.679 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 36 | -0.173 | -0.174 | 0.782 | 0.840 | 0.528 | 1.000 | False | 36 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 28 | 0.228 | 0.015 | 0.007 | 0.127 | 0.714 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 36 | 7 | 0.170 | [-3.40, 5.72] | False | 0.089 | 0.050 | 0.011 | -0.066 | -0.220 |
| level_h100 | 5 | 28 | 21 | 5.021 | [1.82, 9.03] | True | 3.278 | 3.098 | 2.918 | 2.559 | 1.840 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 36 | 7 | 2.072 | [-3.48, 6.29] | False | 0.190 | 0.151 | 0.112 | 0.034 | -0.121 |
| level_b200 | 5 | 28 | 22 | 5.782 | [2.18, 11.20] | True | 3.721 | 3.532 | 3.344 | 2.968 | 2.215 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 36 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 28 | 22 | 4.154 | [0.33, 9.42] | True | 3.109 | 2.924 | 2.738 | 2.368 | 1.628 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 36 | 4 | 3.644 | [0.00, 5.68] | False | 0.180 | 0.158 | 0.136 | 0.093 | 0.005 |
| disp_b200 | 5 | 28 | 21 | 5.544 | [1.93, 10.68] | True | 3.603 | 3.424 | 3.244 | 2.884 | 2.166 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 36 | 9 | -2.250 | [-4.88, 0.86] | False | -0.100 | -0.149 | -0.199 | -0.297 | -0.494 |
| avail_h100 | 5 | 28 | 22 | 3.049 | [0.93, 5.60] | True | 2.509 | 2.324 | 2.139 | 1.768 | 1.028 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 36 | 8 | -2.675 | [-5.42, 0.25] | False | -0.145 | -0.189 | -0.233 | -0.320 | -0.495 |
| avail_b200 | 5 | 28 | 22 | 4.632 | [1.33, 9.13] | True | 3.292 | 3.105 | 2.919 | 2.545 | 1.799 |
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
| neocloud | level_h100 | 1 | 56 | 23 | -0.447 | -0.112 | [-0.43, 0.19] | 0.544 | 1.000 | 0.446 | False |  |
| neocloud | level_h100 | 5 | 52 | 20 | -2.635 | -0.215 | [-0.36, -0.06] | 0.000 | 0.000 | 0.159 | False |  |
| neocloud | level_h100 | 20 | 37 | 9 | n/a | -0.196 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 56 | 24 | -0.642 | -0.355 | [-0.50, -0.19] | 0.001 | 0.010 | 0.018 | True |  |
| neocloud | level_b200 | 5 | 52 | 23 | -1.115 | -0.226 | [-0.40, -0.02] | 0.011 | 0.085 | 0.205 | False |  |
| neocloud | level_b200 | 20 | 37 | 15 | n/a | -0.292 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 56 | 46 | 0.057 | 0.046 | [-0.14, 0.25] | 0.705 | 1.000 | 0.732 | False |  |
| neocloud | disp_h100 | 5 | 52 | 44 | -0.167 | -0.054 | [-0.34, 0.15] | 0.626 | 1.000 | 0.591 | False |  |
| neocloud | disp_h100 | 20 | 37 | 31 | n/a | -0.159 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 56 | 12 | 0.318 | 0.366 | [0.14, 0.52] | 0.000 | 0.000 | 0.018 | True |  |
| neocloud | disp_b200 | 5 | 52 | 11 | 0.467 | 0.214 | [0.07, 0.36] | 0.000 | 0.000 | 0.114 | False |  |
| neocloud | disp_b200 | 20 | 37 | 7 | n/a | 0.234 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 56 | 17 | -0.011 | -0.107 | [-0.37, 0.18] | 0.503 | 1.000 | 0.411 | False |  |
| neocloud | avail_h100 | 5 | 52 | 15 | -0.012 | -0.051 | [-0.23, 0.12] | 0.433 | 1.000 | 0.318 | False |  |
| neocloud | avail_h100 | 20 | 37 | 5 | n/a | 0.006 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 56 | 14 | -0.010 | -0.104 | [-0.37, 0.18] | 0.521 | 1.000 | 0.446 | False |  |
| neocloud | avail_b200 | 5 | 52 | 13 | -0.013 | -0.053 | [-0.23, 0.12] | 0.405 | 1.000 | 0.364 | False |  |
| neocloud | avail_b200 | 20 | 37 | 3 | n/a | -0.014 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 56 | 23 | -0.233 | -0.151 | [-0.51, 0.22] | 0.460 | 1.000 | 0.196 | False |  |
| gpu_semis | level_h100 | 5 | 52 | 20 | -0.571 | -0.102 | [-0.31, 0.22] | 0.370 | 1.000 | 0.523 | False |  |
| gpu_semis | level_h100 | 20 | 37 | 9 | n/a | -0.176 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 56 | 24 | -0.177 | -0.252 | [-0.58, 0.04] | 0.205 | 0.924 | 0.107 | False |  |
| gpu_semis | level_b200 | 5 | 52 | 23 | -0.276 | -0.122 | [-0.35, 0.21] | 0.167 | 0.821 | 0.568 | False |  |
| gpu_semis | level_b200 | 20 | 37 | 15 | n/a | -0.306 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 56 | 46 | 0.024 | 0.050 | [-0.20, 0.30] | 0.735 | 1.000 | 0.679 | False |  |
| gpu_semis | disp_h100 | 5 | 52 | 44 | -0.123 | -0.086 | [-0.29, 0.11] | 0.341 | 1.000 | 0.409 | False |  |
| gpu_semis | disp_h100 | 20 | 37 | 31 | n/a | -0.108 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 56 | 12 | 0.118 | 0.349 | [-0.01, 0.60] | 0.036 | 0.217 | 0.018 | False |  |
| gpu_semis | disp_b200 | 5 | 52 | 11 | 0.193 | 0.192 | [-0.03, 0.35] | 0.000 | 0.002 | 0.205 | False |  |
| gpu_semis | disp_b200 | 20 | 37 | 7 | n/a | 0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 56 | 17 | -0.001 | -0.019 | [-0.28, 0.31] | 0.908 | 1.000 | 0.946 | False |  |
| gpu_semis | avail_h100 | 5 | 52 | 15 | -0.008 | -0.069 | [-0.23, 0.08] | 0.253 | 0.977 | 0.227 | False |  |
| gpu_semis | avail_h100 | 20 | 37 | 5 | n/a | 0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 56 | 14 | -0.000 | -0.004 | [-0.27, 0.32] | 0.979 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 52 | 13 | -0.008 | -0.073 | [-0.23, 0.08] | 0.231 | 0.959 | 0.205 | False |  |
| gpu_semis | avail_b200 | 20 | 37 | 3 | n/a | 0.006 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 56 | 23 | -0.175 | -0.064 | [-0.31, 0.18] | 0.663 | 1.000 | 0.750 | False |  |
| power_capacity | level_h100 | 5 | 52 | 20 | -0.465 | -0.060 | [-0.25, 0.24] | 0.536 | 1.000 | 0.523 | False |  |
| power_capacity | level_h100 | 20 | 37 | 9 | n/a | 0.110 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 56 | 24 | -0.336 | -0.271 | [-0.43, -0.08] | 0.029 | 0.198 | 0.054 | False |  |
| power_capacity | level_b200 | 5 | 52 | 23 | -0.227 | -0.073 | [-0.40, 0.11] | 0.482 | 1.000 | 0.568 | False |  |
| power_capacity | level_b200 | 20 | 37 | 15 | n/a | -0.048 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 56 | 46 | 0.073 | 0.086 | [-0.09, 0.29] | 0.462 | 1.000 | 0.500 | False |  |
| power_capacity | disp_h100 | 5 | 52 | 44 | -0.003 | -0.002 | [-0.26, 0.20] | 0.987 | 1.000 | 1.000 | False |  |
| power_capacity | disp_h100 | 20 | 37 | 31 | n/a | -0.179 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 56 | 12 | 0.141 | 0.236 | [-0.02, 0.37] | 0.003 | 0.029 | 0.143 | False |  |
| power_capacity | disp_b200 | 5 | 52 | 11 | 0.123 | 0.090 | [-0.08, 0.31] | 0.154 | 0.821 | 0.455 | False |  |
| power_capacity | disp_b200 | 20 | 37 | 7 | n/a | 0.009 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 56 | 17 | 0.000 | 0.004 | [-0.18, 0.24] | 0.972 | 1.000 | 0.982 | False |  |
| power_capacity | avail_h100 | 5 | 52 | 15 | -0.004 | -0.028 | [-0.24, 0.20] | 0.741 | 1.000 | 0.568 | False |  |
| power_capacity | avail_h100 | 20 | 37 | 5 | n/a | 0.209 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 56 | 14 | 0.001 | 0.011 | [-0.17, 0.25] | 0.928 | 1.000 | 0.964 | False |  |
| power_capacity | avail_b200 | 5 | 52 | 13 | -0.002 | -0.015 | [-0.22, 0.21] | 0.863 | 1.000 | 0.795 | False |  |
| power_capacity | avail_b200 | 20 | 37 | 3 | n/a | 0.209 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.03 [-0.16, 0.22] | 0.13 [-0.07, 0.24] |
| -4 | -0.02 [-0.14, 0.12] | -0.31 [-0.48, -0.07] |
| -3 | -0.11 [-0.27, 0.06] | 0.15 [-0.22, 0.46] |
| -2 | -0.22 [-0.43, 0.03] | -0.20 [-0.38, 0.18] |
| -1 | 0.09 [-0.27, 0.44] | -0.25 [-0.42, -0.01] |
| 0 | -0.34 [-0.52, -0.14] | -0.11 [-0.44, 0.19] |
| 1 | -0.05 [-0.29, 0.26] | -0.21 [-0.50, 0.21] |
| 2 | 0.08 [-0.16, 0.24] | 0.19 [-0.17, 0.48] |
| 3 | -0.08 [-0.28, 0.29] | 0.05 [-0.14, 0.20] |
| 4 | -0.05 [-0.23, 0.02] | -0.17 [-0.44, -0.03] |
| 5 | -0.11 [-0.24, 0.03] | -0.01 [-0.26, 0.29] |

