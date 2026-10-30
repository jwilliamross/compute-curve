# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-30T02:55:11.923077+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `9f73fc8960093fae...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 30 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 3 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 50 | 2026-08-20 | 2026-10-29 | 0.39 | 0.51 |
| 5 | 46 | 2026-08-20 | 2026-10-23 | 0.40 | 0.53 |
| 20 | 31 | 2026-08-20 | 2026-10-02 | 0.48 | 0.62 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 50 | 18 | -0.996 | -0.311 | [-0.51, 0.04] | 0.004 | 0.072 | 0.060 | False |  |
| level_h100 | 5 | 46 | 16 | -1.073 | -0.129 | [-0.30, 0.15] | 0.113 | 1.000 | 0.316 | False |  |
| level_h100 | 20 | 31 | 4 | n/a | -0.125 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 50 | 23 | -0.348 | -0.296 | [-0.53, -0.11] | 0.070 | 1.000 | 0.040 | False |  |
| level_b200 | 5 | 46 | 23 | -0.566 | -0.185 | [-0.41, -0.04] | 0.071 | 1.000 | 0.316 | False |  |
| level_b200 | 20 | 31 | 10 | n/a | -0.236 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 50 | 42 | 0.025 | 0.032 | [-0.15, 0.24] | 0.775 | 1.000 | 0.840 | False |  |
| disp_h100 | 5 | 46 | 39 | -0.212 | -0.095 | [-0.40, 0.15] | 0.412 | 1.000 | 0.447 | False |  |
| disp_h100 | 20 | 31 | 25 | n/a | -0.124 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 50 | 11 | 0.171 | 0.328 | [0.02, 0.51] | 0.001 | 0.012 | 0.020 | True |  |
| disp_b200 | 5 | 46 | 8 | 0.248 | 0.183 | [0.05, 0.33] | 0.000 | 0.001 | 0.237 | False | insufficient variation (8 non-zero < 10) |
| disp_b200 | 20 | 31 | 5 | n/a | 0.081 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 50 | 14 | -0.004 | -0.074 | [-0.33, 0.27] | 0.640 | 1.000 | 0.640 | False |  |
| avail_h100 | 5 | 46 | 11 | -0.010 | -0.055 | [-0.29, 0.13] | 0.450 | 1.000 | 0.263 | False |  |
| avail_h100 | 20 | 31 | 2 | n/a | -0.154 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 50 | 12 | -0.004 | -0.074 | [-0.33, 0.26] | 0.638 | 1.000 | 0.640 | False |  |
| avail_b200 | 5 | 46 | 9 | -0.009 | -0.052 | [-0.25, 0.13] | 0.459 | 1.000 | 0.316 | False | insufficient variation (9 non-zero < 10) |
| avail_b200 | 20 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 30 | -0.015 | -0.008 | 0.069 | 0.027 | 0.567 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 22 | 0.185 | 0.009 | 0.002 | 0.054 | 0.818 | 0.870 | False | 22 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 30 | -0.372 | -0.363 | 0.106 | 0.100 | 0.600 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 22 | 0.246 | 0.083 | 0.001 | 0.016 | 0.818 | 0.284 | False | 22 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 30 | -0.030 | -0.023 | 0.720 | 0.915 | 0.533 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 22 | 0.144 | -0.040 | 0.030 | 1.000 | 0.682 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 30 | -0.023 | -0.017 | 0.107 | 0.094 | 0.600 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 22 | 0.230 | 0.065 | 0.003 | 0.025 | 0.727 | 0.427 | False | 22 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 30 | -1.986 | -1.967 | 0.317 | 0.390 | 0.567 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 22 | -47.164 | -57.521 | 0.553 | 0.635 | 0.636 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 30 | -0.237 | -0.229 | 0.772 | 0.812 | 0.567 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 22 | 0.185 | 0.010 | 0.033 | 0.147 | 0.682 | 1.000 | False | 22 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 30 | 3 | 4.506 | [0.00, 7.08] | False | 0.166 | 0.146 | 0.126 | 0.086 | 0.006 |
| level_h100 | 5 | 22 | 16 | 5.306 | [1.17, 10.47] | True | 3.313 | 3.139 | 2.964 | 2.616 | 1.919 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 30 | 6 | 0.480 | [-6.14, 6.97] | False | 0.102 | 0.062 | 0.022 | -0.058 | -0.218 |
| level_b200 | 5 | 22 | 16 | 5.892 | [1.35, 13.74] | True | 3.659 | 3.485 | 3.311 | 2.962 | 2.265 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 30 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 22 | 16 | 3.826 | [-1.61, 12.09] | False | 2.880 | 2.710 | 2.540 | 2.200 | 1.519 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 30 | 3 | 3.535 | [-0.07, 6.03] | False | 0.090 | 0.071 | 0.051 | 0.012 | -0.067 |
| disp_b200 | 5 | 22 | 15 | 5.579 | [1.11, 13.25] | True | 3.510 | 3.347 | 3.183 | 2.856 | 2.203 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 30 | 7 | -2.883 | [-5.43, 1.06] | False | -0.121 | -0.167 | -0.213 | -0.305 | -0.489 |
| avail_h100 | 5 | 22 | 16 | 2.498 | [0.29, 5.28] | True | 2.117 | 1.947 | 1.776 | 1.436 | 0.755 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 30 | 6 | -3.529 | [-6.12, -0.28] | False | -0.175 | -0.214 | -0.254 | -0.333 | -0.490 |
| avail_b200 | 5 | 22 | 16 | 4.412 | [0.67, 10.46] | True | 3.114 | 2.942 | 2.769 | 2.425 | 1.736 |
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
| neocloud | level_h100 | 1 | 50 | 18 | -1.600 | -0.309 | [-0.49, 0.06] | 0.002 | 0.019 | 0.080 | False |  |
| neocloud | level_h100 | 5 | 46 | 16 | -2.527 | -0.196 | [-0.34, -0.01] | 0.000 | 0.001 | 0.211 | False |  |
| neocloud | level_h100 | 20 | 31 | 4 | n/a | -0.177 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 50 | 23 | -0.640 | -0.336 | [-0.51, -0.16] | 0.012 | 0.091 | 0.040 | True |  |
| neocloud | level_b200 | 5 | 46 | 23 | -1.142 | -0.241 | [-0.42, -0.06] | 0.011 | 0.091 | 0.211 | False |  |
| neocloud | level_b200 | 20 | 31 | 10 | n/a | -0.277 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 50 | 42 | 0.028 | 0.022 | [-0.17, 0.23] | 0.836 | 1.000 | 0.940 | False |  |
| neocloud | disp_h100 | 5 | 46 | 39 | -0.388 | -0.112 | [-0.43, 0.13] | 0.359 | 1.000 | 0.447 | False |  |
| neocloud | disp_h100 | 20 | 31 | 25 | n/a | -0.126 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 50 | 11 | 0.299 | 0.355 | [0.05, 0.52] | 0.000 | 0.000 | 0.020 | True |  |
| neocloud | disp_b200 | 5 | 46 | 8 | 0.446 | 0.212 | [0.07, 0.36] | 0.000 | 0.000 | 0.184 | False | insufficient variation (8 non-zero < 10) |
| neocloud | disp_b200 | 20 | 31 | 5 | n/a | 0.118 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 50 | 14 | -0.011 | -0.120 | [-0.40, 0.24] | 0.474 | 1.000 | 0.420 | False |  |
| neocloud | avail_h100 | 5 | 46 | 11 | -0.016 | -0.057 | [-0.29, 0.11] | 0.416 | 1.000 | 0.289 | False |  |
| neocloud | avail_h100 | 20 | 31 | 2 | n/a | -0.184 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 50 | 12 | -0.012 | -0.125 | [-0.41, 0.24] | 0.459 | 1.000 | 0.340 | False |  |
| neocloud | avail_b200 | 5 | 46 | 9 | -0.016 | -0.060 | [-0.25, 0.11] | 0.375 | 1.000 | 0.289 | False | insufficient variation (9 non-zero < 10) |
| neocloud | avail_b200 | 20 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 50 | 18 | -0.681 | -0.345 | [-0.62, 0.03] | 0.013 | 0.091 | 0.040 | True |  |
| gpu_semis | level_h100 | 5 | 46 | 16 | -0.535 | -0.099 | [-0.31, 0.23] | 0.367 | 1.000 | 0.579 | False |  |
| gpu_semis | level_h100 | 20 | 31 | 4 | n/a | -0.184 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 50 | 23 | -0.153 | -0.212 | [-0.63, 0.09] | 0.363 | 1.000 | 0.160 | False |  |
| gpu_semis | level_b200 | 5 | 46 | 23 | -0.346 | -0.175 | [-0.41, 0.05] | 0.048 | 0.237 | 0.342 | False |  |
| gpu_semis | level_b200 | 20 | 31 | 10 | n/a | -0.263 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 50 | 42 | 0.001 | 0.001 | [-0.21, 0.17] | 0.993 | 1.000 | 1.000 | False |  |
| gpu_semis | disp_h100 | 5 | 46 | 39 | -0.129 | -0.089 | [-0.32, 0.13] | 0.396 | 1.000 | 0.526 | False |  |
| gpu_semis | disp_h100 | 20 | 31 | 25 | n/a | -0.062 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 50 | 11 | 0.106 | 0.329 | [-0.07, 0.62] | 0.086 | 0.386 | 0.040 | False |  |
| gpu_semis | disp_b200 | 5 | 46 | 8 | 0.192 | 0.218 | [0.01, 0.37] | 0.000 | 0.001 | 0.211 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 31 | 5 | n/a | 0.095 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 50 | 14 | 0.000 | 0.009 | [-0.27, 0.38] | 0.954 | 1.000 | 0.960 | False |  |
| gpu_semis | avail_h100 | 5 | 46 | 11 | -0.007 | -0.057 | [-0.27, 0.12] | 0.415 | 1.000 | 0.316 | False |  |
| gpu_semis | avail_h100 | 20 | 31 | 2 | n/a | -0.055 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 50 | 12 | 0.001 | 0.016 | [-0.27, 0.38] | 0.923 | 1.000 | 0.880 | False |  |
| gpu_semis | avail_b200 | 5 | 46 | 9 | -0.006 | -0.057 | [-0.23, 0.12] | 0.403 | 1.000 | 0.395 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 50 | 18 | -0.708 | -0.205 | [-0.36, 0.09] | 0.022 | 0.130 | 0.200 | False |  |
| power_capacity | level_h100 | 5 | 46 | 16 | -0.158 | -0.020 | [-0.23, 0.36] | 0.863 | 1.000 | 0.921 | False |  |
| power_capacity | level_h100 | 20 | 31 | 4 | n/a | 0.125 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 50 | 23 | -0.251 | -0.198 | [-0.38, -0.06] | 0.110 | 0.457 | 0.180 | False |  |
| power_capacity | level_b200 | 5 | 46 | 23 | -0.211 | -0.071 | [-0.38, 0.15] | 0.520 | 1.000 | 0.658 | False |  |
| power_capacity | level_b200 | 20 | 31 | 10 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 50 | 42 | 0.046 | 0.055 | [-0.13, 0.29] | 0.663 | 1.000 | 0.740 | False |  |
| power_capacity | disp_h100 | 5 | 46 | 39 | -0.119 | -0.055 | [-0.35, 0.19] | 0.629 | 1.000 | 0.605 | False |  |
| power_capacity | disp_h100 | 20 | 31 | 25 | n/a | -0.177 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 50 | 11 | 0.108 | 0.192 | [-0.13, 0.34] | 0.024 | 0.131 | 0.200 | False |  |
| power_capacity | disp_b200 | 5 | 46 | 8 | 0.105 | 0.080 | [-0.10, 0.25] | 0.224 | 0.864 | 0.579 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 31 | 5 | n/a | -0.060 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 50 | 14 | -0.002 | -0.032 | [-0.22, 0.24] | 0.802 | 1.000 | 0.880 | False |  |
| power_capacity | avail_h100 | 5 | 46 | 11 | -0.007 | -0.041 | [-0.27, 0.20] | 0.617 | 1.000 | 0.368 | False |  |
| power_capacity | avail_h100 | 20 | 31 | 2 | n/a | -0.171 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 50 | 12 | -0.002 | -0.028 | [-0.20, 0.24] | 0.821 | 1.000 | 0.880 | False |  |
| power_capacity | avail_b200 | 5 | 46 | 9 | -0.005 | -0.027 | [-0.23, 0.22] | 0.754 | 1.000 | 0.553 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.21, 0.19] | 0.09 [-0.16, 0.23] |
| -4 | -0.02 [-0.19, 0.15] | -0.13 [-0.27, 0.11] |
| -3 | -0.18 [-0.31, -0.00] | -0.05 [-0.29, 0.29] |
| -2 | -0.15 [-0.37, 0.16] | -0.08 [-0.31, 0.29] |
| -1 | -0.08 [-0.32, 0.14] | -0.28 [-0.41, -0.03] |
| 0 | -0.30 [-0.53, -0.11] | -0.31 [-0.51, 0.04] |
| 1 | 0.04 [-0.24, 0.34] | -0.04 [-0.23, 0.34] |
| 2 | 0.02 [-0.40, 0.23] | 0.03 [-0.28, 0.29] |
| 3 | -0.10 [-0.33, 0.32] | 0.07 [-0.25, 0.25] |
| 4 | -0.07 [-0.28, 0.02] | -0.10 [-0.49, -0.00] |
| 5 | -0.13 [-0.31, 0.03] | -0.07 [-0.34, 0.25] |

