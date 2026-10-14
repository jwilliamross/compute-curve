# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-14T02:12:21.503313+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `bc825d6e2442e625...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 18 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 38 | 2026-08-20 | 2026-10-13 | 0.44 | 0.57 |
| 5 | 34 | 2026-08-20 | 2026-10-07 | 0.46 | 0.60 |
| 20 | 19 | 2026-08-20 | 2026-09-16 | 0.60 | 0.74 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 38 | 9 | -0.986 | -0.388 | [-0.58, 0.09] | 0.005 | 0.076 | 0.026 | False | insufficient variation (9 non-zero < 10) |
| level_h100 | 5 | 34 | 6 | -1.057 | -0.148 | [-0.32, 0.16] | 0.034 | 0.353 | 0.423 | False | insufficient variation (6 non-zero < 10) |
| level_h100 | 20 | 19 | 3 | n/a | 0.023 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 38 | 16 | -0.323 | -0.346 | [-0.60, -0.05] | 0.077 | 0.693 | 0.053 | False |  |
| level_b200 | 5 | 34 | 12 | -0.405 | -0.154 | [-0.29, 0.34] | 0.021 | 0.249 | 0.538 | False |  |
| level_b200 | 20 | 19 | 3 | n/a | -0.100 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 38 | 32 | -0.036 | -0.042 | [-0.27, 0.17] | 0.681 | 1.000 | 0.789 | False |  |
| disp_h100 | 5 | 34 | 28 | 0.115 | 0.049 | [-0.30, 0.27] | 0.659 | 1.000 | 0.808 | False |  |
| disp_h100 | 20 | 19 | 14 | n/a | -0.117 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 38 | 7 | 0.167 | 0.405 | [-0.04, 0.58] | 0.001 | 0.018 | 0.026 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 34 | 6 | 0.194 | 0.165 | [-0.11, 0.35] | 0.000 | 0.000 | 0.346 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 20 | 19 | 1 | n/a | 0.035 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 38 | 6 | 0.021 | 0.223 | [-0.35, 0.49] | 0.011 | 0.146 | 0.105 | False | insufficient variation (6 non-zero < 10) |
| avail_h100 | 5 | 34 | 4 | -0.099 | -0.220 | [-0.47, -0.10] | 0.008 | 0.117 | 0.231 | False | insufficient variation (4 non-zero < 10) |
| avail_h100 | 20 | 19 | 2 | n/a | -0.341 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 38 | 4 | 0.019 | 0.209 | [-0.15, 0.49] | 0.032 | 0.353 | 0.158 | False | insufficient variation (4 non-zero < 10) |
| avail_b200 | 5 | 34 | 2 | -0.086 | -0.205 | [-0.38, -0.09] | 0.001 | 0.019 | 0.308 | False | insufficient variation (2 non-zero < 10) |
| avail_b200 | 20 | 19 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 18 | -0.034 | -0.035 | 0.032 | 0.020 | 0.556 | 0.583 | False | 18 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 10 | 0.131 | 0.024 | n/a | n/a | 0.900 | n/a | False | 10 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 18 | -1.055 | -1.057 | 0.116 | 0.115 | 0.611 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 10 | 0.209 | 0.112 | n/a | n/a | 0.900 | n/a | False | 10 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 18 | 0.002 | 0.001 | 0.399 | 0.404 | 0.556 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 10 | 0.044 | -0.074 | n/a | n/a | 0.600 | n/a | False | 10 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 18 | -0.069 | -0.070 | 0.103 | 0.104 | 0.611 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 10 | 0.205 | 0.106 | n/a | n/a | 0.700 | n/a | False | 10 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 18 | -5.000 | -5.004 | 0.079 | 0.113 | 0.556 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 10 | -81.832 | -92.094 | n/a | n/a | 0.700 | n/a | False | 10 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 18 | -0.256 | -0.257 | 0.345 | 0.426 | 0.556 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 10 | 0.110 | 0.000 | n/a | n/a | 0.700 | n/a | False | 10 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 18 | 2 | 4.871 | [0.00, 8.56] | False | 0.137 | 0.115 | 0.092 | 0.048 | -0.041 |
| level_h100 | 5 | 10 | 5 | 4.997 | [-2.24, 11.01] | False | 2.006 | 1.886 | 1.766 | 1.527 | 1.047 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 18 | 5 | -1.697 | [-8.27, 6.90] | False | 0.029 | -0.027 | -0.082 | -0.193 | -0.416 |
| level_b200 | 5 | 10 | 4 | 5.194 | [0.00, 11.54] | False | 2.000 | 1.904 | 1.808 | 1.617 | 1.233 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 18 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 10 | 4 | 0.218 | [-5.06, 5.48] | False | 0.286 | 0.199 | 0.112 | -0.062 | -0.409 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 18 | 3 | 4.591 | [-3.74, 7.50] | False | 0.151 | 0.118 | 0.085 | 0.019 | -0.112 |
| disp_b200 | 5 | 10 | 3 | 4.329 | [0.00, 7.99] | False | 1.671 | 1.599 | 1.527 | 1.384 | 1.096 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 18 | 4 | -0.522 | [-4.75, 6.84] | False | 0.057 | 0.013 | -0.030 | -0.117 | -0.291 |
| avail_h100 | 5 | 10 | 4 | 5.194 | [0.00, 11.54] | False | 2.000 | 1.904 | 1.808 | 1.617 | 1.233 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 18 | 3 | -1.817 | [-5.87, 5.45] | False | -0.033 | -0.066 | -0.098 | -0.163 | -0.292 |
| avail_b200 | 5 | 10 | 4 | 5.194 | [0.00, 11.54] | False | 2.000 | 1.904 | 1.808 | 1.617 | 1.233 |
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
| neocloud | level_h100 | 1 | 38 | 9 | -1.568 | -0.394 | [-0.56, 0.17] | 0.003 | 0.013 | 0.026 | False | insufficient variation (9 non-zero < 10) |
| neocloud | level_h100 | 5 | 34 | 6 | -2.490 | -0.225 | [-0.38, -0.06] | 0.000 | 0.000 | 0.154 | False | insufficient variation (6 non-zero < 10) |
| neocloud | level_h100 | 20 | 19 | 3 | n/a | -0.078 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 38 | 16 | -0.598 | -0.409 | [-0.58, -0.07] | 0.014 | 0.049 | 0.026 | True |  |
| neocloud | level_b200 | 5 | 34 | 12 | -0.900 | -0.220 | [-0.38, 0.39] | 0.000 | 0.001 | 0.308 | False |  |
| neocloud | level_b200 | 20 | 19 | 3 | n/a | -0.193 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 38 | 32 | -0.102 | -0.077 | [-0.31, 0.18] | 0.491 | 0.975 | 0.605 | False |  |
| neocloud | disp_h100 | 5 | 34 | 28 | 0.151 | 0.041 | [-0.32, 0.27] | 0.709 | 1.000 | 0.769 | False |  |
| neocloud | disp_h100 | 20 | 19 | 14 | n/a | -0.114 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 38 | 7 | 0.292 | 0.452 | [-0.01, 0.59] | 0.000 | 0.000 | 0.026 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 34 | 6 | 0.376 | 0.206 | [-0.12, 0.42] | 0.000 | 0.000 | 0.192 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 20 | 19 | 1 | n/a | 0.123 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 38 | 6 | 0.015 | 0.104 | [-0.33, 0.38] | 0.389 | 0.807 | 0.605 | False | insufficient variation (6 non-zero < 10) |
| neocloud | avail_h100 | 5 | 34 | 4 | -0.181 | -0.259 | [-0.50, -0.12] | 0.004 | 0.017 | 0.192 | False | insufficient variation (4 non-zero < 10) |
| neocloud | avail_h100 | 20 | 19 | 2 | n/a | -0.381 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 38 | 4 | 0.011 | 0.077 | [-0.28, 0.38] | 0.561 | 1.000 | 0.737 | False | insufficient variation (4 non-zero < 10) |
| neocloud | avail_b200 | 5 | 34 | 2 | -0.170 | -0.262 | [-0.46, -0.18] | 0.000 | 0.001 | 0.192 | False | insufficient variation (2 non-zero < 10) |
| neocloud | avail_b200 | 20 | 19 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 38 | 9 | -0.693 | -0.395 | [-0.68, 0.03] | 0.008 | 0.030 | 0.026 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | level_h100 | 5 | 34 | 6 | -0.567 | -0.124 | [-0.34, 0.23] | 0.215 | 0.529 | 0.769 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 19 | 3 | n/a | -0.087 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 38 | 16 | -0.142 | -0.220 | [-0.66, 0.13] | 0.377 | 0.807 | 0.211 | False |  |
| gpu_semis | level_b200 | 5 | 34 | 12 | -0.242 | -0.144 | [-0.31, 0.51] | 0.018 | 0.057 | 0.654 | False |  |
| gpu_semis | level_b200 | 20 | 19 | 3 | n/a | -0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 38 | 32 | 0.009 | 0.015 | [-0.31, 0.22] | 0.909 | 1.000 | 0.895 | False |  |
| gpu_semis | disp_h100 | 5 | 34 | 28 | 0.017 | 0.012 | [-0.32, 0.25] | 0.923 | 1.000 | 0.962 | False |  |
| gpu_semis | disp_h100 | 20 | 19 | 14 | n/a | 0.072 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 38 | 7 | 0.105 | 0.367 | [-0.11, 0.68] | 0.081 | 0.219 | 0.026 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 34 | 6 | 0.141 | 0.187 | [-0.19, 0.36] | 0.000 | 0.000 | 0.308 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 19 | 1 | n/a | 0.118 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 38 | 6 | 0.023 | 0.359 | [-0.27, 0.58] | 0.000 | 0.000 | 0.053 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 34 | 4 | -0.077 | -0.270 | [-0.42, -0.12] | 0.000 | 0.001 | 0.154 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 19 | 2 | n/a | -0.172 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 38 | 4 | 0.023 | 0.364 | [0.02, 0.59] | 0.000 | 0.000 | 0.079 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 34 | 2 | -0.071 | -0.264 | [-0.43, -0.11] | 0.000 | 0.000 | 0.269 | False | insufficient variation (2 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 19 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 38 | 9 | -0.699 | -0.243 | [-0.40, 0.13] | 0.021 | 0.063 | 0.132 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | level_h100 | 5 | 34 | 6 | -0.114 | -0.016 | [-0.23, 0.47] | 0.883 | 1.000 | 0.808 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | level_h100 | 20 | 19 | 3 | n/a | 0.286 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 38 | 16 | -0.228 | -0.216 | [-0.41, -0.02] | 0.118 | 0.303 | 0.211 | False |  |
| power_capacity | level_b200 | 5 | 34 | 12 | -0.071 | -0.027 | [-0.27, 0.24] | 0.736 | 1.000 | 0.885 | False |  |
| power_capacity | level_b200 | 20 | 19 | 3 | n/a | 0.186 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 38 | 32 | -0.014 | -0.015 | [-0.22, 0.24] | 0.895 | 1.000 | 0.947 | False |  |
| power_capacity | disp_h100 | 5 | 34 | 28 | 0.177 | 0.074 | [-0.26, 0.31] | 0.543 | 1.000 | 0.577 | False |  |
| power_capacity | disp_h100 | 20 | 19 | 14 | n/a | -0.202 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 38 | 7 | 0.105 | 0.224 | [-0.22, 0.37] | 0.028 | 0.079 | 0.211 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 34 | 6 | 0.065 | 0.055 | [-0.16, 0.26] | 0.381 | 0.807 | 0.731 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 19 | 1 | n/a | -0.204 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 38 | 6 | 0.024 | 0.227 | [-0.38, 0.45] | 0.000 | 0.001 | 0.105 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 34 | 4 | -0.038 | -0.083 | [-0.44, 0.08] | 0.246 | 0.577 | 0.808 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 19 | 2 | n/a | -0.252 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 38 | 4 | 0.023 | 0.225 | [-0.06, 0.44] | 0.001 | 0.003 | 0.105 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 34 | 2 | -0.017 | -0.040 | [-0.18, 0.14] | 0.505 | 0.975 | 0.923 | False | insufficient variation (2 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 19 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.06 [-0.25, 0.25] | 0.15 [-0.16, 0.32] |
| -4 | -0.03 [-0.24, 0.18] | -0.18 [-0.35, 0.06] |
| -3 | -0.19 [-0.38, 0.10] | -0.17 [-0.43, 0.02] |
| -2 | -0.21 [-0.46, 0.00] | -0.19 [-0.39, 0.19] |
| -1 | -0.09 [-0.36, 0.21] | -0.34 [-0.48, 0.06] |
| 0 | -0.35 [-0.60, -0.05] | -0.39 [-0.58, 0.09] |
| 1 | 0.07 [-0.27, 0.50] | -0.05 [-0.27, 0.47] |
| 2 | 0.09 [-0.24, 0.36] | 0.04 [-0.39, 0.35] |
| 3 | -0.16 [-0.43, 0.23] | 0.05 [-0.34, 0.26] |
| 4 | -0.04 [-0.21, 0.07] | -0.04 [-0.24, 0.06] |
| 5 | -0.14 [-0.31, 0.08] | -0.14 [-0.46, 0.11] |

