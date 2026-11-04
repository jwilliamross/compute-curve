# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-04T03:12:41.735060+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `9305799e4851d21a...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 33 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 53 | 2026-08-20 | 2026-11-03 | 0.38 | 0.49 |
| 5 | 49 | 2026-08-20 | 2026-10-28 | 0.39 | 0.51 |
| 20 | 34 | 2026-08-20 | 2026-10-07 | 0.46 | 0.60 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 53 | 20 | -0.584 | -0.186 | [-0.48, 0.25] | 0.263 | 1.000 | 0.226 | False |  |
| level_h100 | 5 | 49 | 18 | -1.132 | -0.135 | [-0.30, 0.13] | 0.079 | 1.000 | 0.366 | False |  |
| level_h100 | 20 | 34 | 6 | n/a | -0.157 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 53 | 23 | -0.350 | -0.277 | [-0.50, -0.11] | 0.067 | 1.000 | 0.038 | False |  |
| level_b200 | 5 | 49 | 23 | -0.580 | -0.188 | [-0.43, -0.04] | 0.060 | 0.965 | 0.220 | False |  |
| level_b200 | 20 | 34 | 12 | n/a | -0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 53 | 44 | -0.023 | -0.029 | [-0.20, 0.19] | 0.805 | 1.000 | 0.811 | False |  |
| disp_h100 | 5 | 49 | 41 | -0.200 | -0.090 | [-0.38, 0.14] | 0.419 | 1.000 | 0.463 | False |  |
| disp_h100 | 20 | 34 | 28 | n/a | -0.154 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 53 | 11 | 0.171 | 0.304 | [0.01, 0.49] | 0.001 | 0.009 | 0.019 | True |  |
| disp_b200 | 5 | 49 | 11 | 0.257 | 0.188 | [0.05, 0.34] | 0.000 | 0.001 | 0.195 | False |  |
| disp_b200 | 20 | 34 | 6 | n/a | 0.173 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 53 | 15 | -0.008 | -0.130 | [-0.36, 0.18] | 0.388 | 1.000 | 0.340 | False |  |
| avail_h100 | 5 | 49 | 13 | -0.015 | -0.095 | [-0.29, 0.09] | 0.170 | 1.000 | 0.195 | False |  |
| avail_h100 | 20 | 34 | 4 | n/a | -0.161 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 53 | 13 | -0.008 | -0.132 | [-0.36, 0.17] | 0.377 | 1.000 | 0.340 | False |  |
| avail_b200 | 5 | 49 | 11 | -0.015 | -0.092 | [-0.28, 0.09] | 0.170 | 1.000 | 0.195 | False |  |
| avail_b200 | 20 | 34 | 2 | n/a | -0.181 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 33 | -0.111 | -0.098 | 0.475 | 0.482 | 0.515 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 25 | 0.164 | 0.013 | 0.006 | 0.035 | 0.800 | 0.564 | False | 25 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 33 | -0.301 | -0.286 | 0.113 | 0.100 | 0.576 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 25 | 0.223 | 0.083 | 0.004 | 0.017 | 0.800 | 0.312 | False | 25 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 33 | -0.037 | -0.025 | 0.824 | 0.957 | 0.515 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 25 | 0.120 | -0.038 | 0.037 | 1.000 | 0.680 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 33 | -0.025 | -0.014 | 0.124 | 0.096 | 0.576 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 25 | 0.210 | 0.067 | 0.006 | 0.019 | 0.720 | 0.319 | False | 25 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 33 | -1.573 | -1.544 | 0.297 | 0.355 | 0.545 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 25 | -45.850 | -54.315 | 0.550 | 0.631 | 0.640 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 33 | -0.180 | -0.167 | 0.731 | 0.758 | 0.545 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 25 | 0.174 | 0.024 | 0.032 | 0.115 | 0.680 | 1.000 | False | 25 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 33 | 5 | -0.609 | [-4.98, 6.48] | False | 0.027 | -0.003 | -0.033 | -0.093 | -0.213 |
| level_h100 | 5 | 25 | 19 | 4.585 | [0.54, 9.71] | True | 2.933 | 2.751 | 2.569 | 2.204 | 1.476 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 33 | 6 | 0.459 | [-5.71, 6.40] | False | 0.092 | 0.056 | 0.020 | -0.053 | -0.198 |
| level_b200 | 5 | 25 | 19 | 5.061 | [0.62, 11.73] | True | 3.238 | 3.056 | 2.873 | 2.509 | 1.781 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 33 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 25 | 19 | 3.385 | [-1.74, 9.61] | False | 2.552 | 2.374 | 2.195 | 1.838 | 1.124 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 33 | 3 | 3.368 | [0.00, 5.73] | False | 0.082 | 0.064 | 0.046 | 0.011 | -0.061 |
| disp_b200 | 5 | 25 | 18 | 4.815 | [0.38, 10.78] | True | 3.106 | 2.934 | 2.761 | 2.416 | 1.726 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 33 | 8 | -1.121 | [-4.52, 3.99] | False | 0.005 | -0.043 | -0.090 | -0.186 | -0.378 |
| avail_h100 | 5 | 25 | 19 | 2.224 | [-0.03, 4.44] | False | 1.880 | 1.702 | 1.523 | 1.166 | 0.452 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 33 | 7 | -1.608 | [-5.11, 3.41] | False | -0.044 | -0.086 | -0.128 | -0.211 | -0.379 |
| avail_b200 | 5 | 25 | 19 | 3.874 | [0.07, 9.04] | True | 2.758 | 2.577 | 2.397 | 2.036 | 1.315 |
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
| avail_h100|h5 | False | False | False | False | False |
| avail_h100|h20 | False | False | False | False | False |
| avail_b200|h1 | False | False | False | False | False |
| avail_b200|h5 | False | False | True | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 53 | 20 | -0.992 | -0.196 | [-0.46, 0.22] | 0.194 | 0.654 | 0.226 | False |  |
| neocloud | level_h100 | 5 | 49 | 18 | -2.624 | -0.201 | [-0.34, -0.03] | 0.000 | 0.000 | 0.220 | False |  |
| neocloud | level_h100 | 20 | 34 | 6 | n/a | -0.208 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 53 | 23 | -0.640 | -0.315 | [-0.49, -0.15] | 0.011 | 0.102 | 0.019 | False |  |
| neocloud | level_b200 | 5 | 49 | 23 | -1.166 | -0.242 | [-0.43, -0.08] | 0.008 | 0.086 | 0.122 | False |  |
| neocloud | level_b200 | 20 | 34 | 12 | n/a | -0.286 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 53 | 44 | -0.052 | -0.040 | [-0.23, 0.18] | 0.719 | 1.000 | 0.679 | False |  |
| neocloud | disp_h100 | 5 | 49 | 41 | -0.367 | -0.106 | [-0.40, 0.13] | 0.366 | 0.916 | 0.317 | False |  |
| neocloud | disp_h100 | 20 | 34 | 28 | n/a | -0.157 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 53 | 11 | 0.299 | 0.331 | [0.04, 0.50] | 0.000 | 0.000 | 0.019 | True |  |
| neocloud | disp_b200 | 5 | 49 | 11 | 0.463 | 0.217 | [0.06, 0.36] | 0.000 | 0.000 | 0.122 | False |  |
| neocloud | disp_b200 | 20 | 34 | 6 | n/a | 0.208 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 53 | 15 | -0.017 | -0.170 | [-0.41, 0.12] | 0.280 | 0.811 | 0.189 | False |  |
| neocloud | avail_h100 | 5 | 49 | 13 | -0.025 | -0.100 | [-0.29, 0.07] | 0.140 | 0.581 | 0.171 | False |  |
| neocloud | avail_h100 | 20 | 34 | 4 | n/a | -0.177 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 53 | 13 | -0.017 | -0.176 | [-0.43, 0.11] | 0.265 | 0.811 | 0.189 | False |  |
| neocloud | avail_b200 | 5 | 49 | 11 | -0.026 | -0.102 | [-0.29, 0.06] | 0.119 | 0.581 | 0.146 | False |  |
| neocloud | avail_b200 | 20 | 34 | 2 | n/a | -0.197 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 53 | 20 | -0.353 | -0.184 | [-0.57, 0.35] | 0.415 | 0.916 | 0.208 | False |  |
| gpu_semis | level_h100 | 5 | 49 | 18 | -0.489 | -0.088 | [-0.29, 0.26] | 0.440 | 0.916 | 0.707 | False |  |
| gpu_semis | level_h100 | 20 | 34 | 6 | n/a | -0.212 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 53 | 23 | -0.146 | -0.189 | [-0.61, 0.09] | 0.393 | 0.916 | 0.226 | False |  |
| gpu_semis | level_b200 | 5 | 49 | 23 | -0.324 | -0.159 | [-0.38, 0.10] | 0.072 | 0.485 | 0.415 | False |  |
| gpu_semis | level_b200 | 20 | 34 | 12 | n/a | -0.304 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 53 | 44 | -0.038 | -0.078 | [-0.26, 0.13] | 0.560 | 1.000 | 0.528 | False |  |
| gpu_semis | disp_h100 | 5 | 49 | 41 | -0.170 | -0.115 | [-0.34, 0.09] | 0.286 | 0.811 | 0.341 | False |  |
| gpu_semis | disp_h100 | 20 | 34 | 28 | n/a | -0.102 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 53 | 11 | 0.106 | 0.311 | [-0.07, 0.60] | 0.092 | 0.498 | 0.057 | False |  |
| gpu_semis | disp_b200 | 5 | 49 | 11 | 0.188 | 0.208 | [-0.07, 0.36] | 0.000 | 0.001 | 0.220 | False |  |
| gpu_semis | disp_b200 | 20 | 34 | 6 | n/a | 0.214 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 53 | 15 | -0.003 | -0.078 | [-0.37, 0.32] | 0.635 | 1.000 | 0.623 | False |  |
| gpu_semis | avail_h100 | 5 | 49 | 13 | -0.011 | -0.105 | [-0.31, 0.07] | 0.177 | 0.637 | 0.098 | False |  |
| gpu_semis | avail_h100 | 20 | 34 | 4 | n/a | -0.273 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 53 | 13 | -0.003 | -0.075 | [-0.37, 0.32] | 0.645 | 1.000 | 0.604 | False |  |
| gpu_semis | avail_b200 | 5 | 49 | 11 | -0.011 | -0.108 | [-0.30, 0.07] | 0.170 | 0.637 | 0.146 | False |  |
| gpu_semis | avail_b200 | 20 | 34 | 2 | n/a | -0.305 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 53 | 20 | -0.408 | -0.117 | [-0.33, 0.17] | 0.301 | 0.811 | 0.415 | False |  |
| power_capacity | level_h100 | 5 | 49 | 18 | -0.283 | -0.034 | [-0.24, 0.29] | 0.731 | 1.000 | 0.756 | False |  |
| power_capacity | level_h100 | 20 | 34 | 6 | n/a | 0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 53 | 23 | -0.263 | -0.188 | [-0.37, -0.07] | 0.087 | 0.498 | 0.226 | False |  |
| power_capacity | level_b200 | 5 | 49 | 23 | -0.250 | -0.081 | [-0.45, 0.11] | 0.441 | 0.916 | 0.439 | False |  |
| power_capacity | level_b200 | 20 | 34 | 12 | n/a | -0.034 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 53 | 44 | 0.021 | 0.024 | [-0.15, 0.26] | 0.840 | 1.000 | 0.849 | False |  |
| power_capacity | disp_h100 | 5 | 49 | 41 | -0.064 | -0.029 | [-0.30, 0.21] | 0.796 | 1.000 | 0.854 | False |  |
| power_capacity | disp_h100 | 20 | 34 | 28 | n/a | -0.180 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 53 | 11 | 0.107 | 0.172 | [-0.12, 0.32] | 0.017 | 0.128 | 0.302 | False |  |
| power_capacity | disp_b200 | 5 | 49 | 11 | 0.121 | 0.089 | [-0.08, 0.30] | 0.139 | 0.581 | 0.488 | False |  |
| power_capacity | disp_b200 | 20 | 34 | 6 | n/a | -0.033 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 53 | 15 | -0.004 | -0.062 | [-0.22, 0.18] | 0.585 | 1.000 | 0.736 | False |  |
| power_capacity | avail_h100 | 5 | 49 | 13 | -0.010 | -0.061 | [-0.27, 0.18] | 0.441 | 0.916 | 0.341 | False |  |
| power_capacity | avail_h100 | 20 | 34 | 4 | n/a | 0.090 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 53 | 13 | -0.004 | -0.061 | [-0.22, 0.17] | 0.587 | 1.000 | 0.717 | False |  |
| power_capacity | avail_b200 | 5 | 49 | 11 | -0.007 | -0.046 | [-0.25, 0.20] | 0.569 | 1.000 | 0.463 | False |  |
| power_capacity | avail_b200 | 20 | 34 | 2 | n/a | 0.091 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.17, 0.23] | 0.09 [-0.11, 0.24] |
| -4 | -0.03 [-0.15, 0.11] | -0.18 [-0.31, -0.02] |
| -3 | -0.12 [-0.28, 0.05] | -0.07 [-0.26, 0.15] |
| -2 | -0.24 [-0.45, 0.02] | -0.13 [-0.32, 0.18] |
| -1 | 0.08 [-0.29, 0.45] | -0.17 [-0.36, 0.17] |
| 0 | -0.28 [-0.50, -0.11] | -0.19 [-0.48, 0.25] |
| 1 | 0.04 [-0.22, 0.31] | -0.19 [-0.46, 0.23] |
| 2 | 0.01 [-0.36, 0.21] | 0.11 [-0.21, 0.34] |
| 3 | -0.09 [-0.31, 0.29] | 0.07 [-0.18, 0.25] |
| 4 | -0.06 [-0.26, 0.01] | -0.11 [-0.50, -0.01] |
| 5 | -0.12 [-0.28, 0.02] | -0.05 [-0.30, 0.26] |

