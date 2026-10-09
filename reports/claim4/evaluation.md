# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-09T03:04:39.330181+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 37.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `e55bc18375555c61...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 2 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 15 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 35 | 2026-08-20 | 2026-10-08 | 0.46 | 0.59 |
| 5 | 31 | 2026-08-20 | 2026-10-02 | 0.48 | 0.62 |
| 20 | 16 | 2026-08-20 | 2026-09-11 | 0.65 | 0.79 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 35 | 7 | -0.998 | -0.403 | [-0.59, 0.11] | 0.005 | 0.085 | 0.029 | False | insufficient variation (7 non-zero < 10) |
| level_h100 | 5 | 31 | 4 | -0.943 | -0.132 | [-0.34, 0.17] | 0.065 | 0.979 | 0.435 | False | insufficient variation (4 non-zero < 10) |
| level_h100 | 20 | 16 | 3 | n/a | 0.058 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 35 | 13 | -0.314 | -0.342 | [-0.59, -0.02] | 0.088 | 1.000 | 0.057 | False |  |
| level_b200 | 5 | 31 | 10 | -0.601 | -0.116 | [-0.37, 0.54] | 0.089 | 1.000 | 0.565 | False |  |
| level_b200 | 20 | 16 | 1 | n/a | 0.008 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 35 | 29 | -0.032 | -0.039 | [-0.27, 0.19] | 0.707 | 1.000 | 0.771 | False |  |
| disp_h100 | 5 | 31 | 25 | 0.180 | 0.077 | [-0.27, 0.33] | 0.518 | 1.000 | 0.739 | False |  |
| disp_h100 | 20 | 16 | 11 | n/a | -0.186 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 35 | 6 | 0.171 | 0.418 | [-0.16, 0.59] | 0.001 | 0.026 | 0.029 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 5 | 31 | 5 | 0.168 | 0.114 | [-0.21, 0.38] | 0.072 | 1.000 | 0.391 | False | insufficient variation (5 non-zero < 10) |
| disp_b200 | 20 | 16 | 1 | n/a | -0.008 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 35 | 5 | 0.015 | 0.136 | [-0.40, 0.33] | 0.145 | 1.000 | 0.486 | False | insufficient variation (5 non-zero < 10) |
| avail_h100 | 5 | 31 | 2 | -1.805 | -0.362 | [-0.55, -0.05] | 0.012 | 0.185 | 0.130 | False | insufficient variation (2 non-zero < 10) |
| avail_h100 | 20 | 16 | 2 | n/a | -0.376 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 35 | 3 | 0.013 | 0.121 | [-0.18, 0.32] | 0.261 | 1.000 | 0.514 | False | insufficient variation (3 non-zero < 10) |
| avail_b200 | 5 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| avail_b200 | 20 | 16 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 2 | -3.062 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| B200 | 5 | 1 | -3.443 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 15 | -0.031 | -0.036 | 0.028 | 0.017 | 0.600 | 0.502 | False | 15 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 7 | -0.126 | -0.108 | n/a | n/a | 0.857 | n/a | False | 7 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 15 | -1.299 | -1.311 | 0.127 | 0.125 | 0.600 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 7 | 0.055 | 0.069 | n/a | n/a | 0.857 | n/a | False | 7 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 15 | 0.005 | 0.000 | 0.370 | 0.445 | 0.533 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 7 | -0.098 | -0.081 | n/a | n/a | 0.429 | n/a | False | 7 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 15 | -0.078 | -0.083 | 0.122 | 0.119 | 0.600 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 7 | -0.034 | -0.018 | n/a | n/a | 0.571 | n/a | False | 7 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 15 | -6.122 | -6.158 | 0.115 | 0.167 | 0.467 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 7 | -0.016 | -0.000 | n/a | n/a | 0.571 | n/a | False | 7 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 15 | -0.394 | -0.401 | 0.786 | 0.820 | 0.467 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 7 | -0.016 | 0.000 | n/a | n/a | 0.571 | n/a | False | 7 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 15 | 2 | 5.358 | [0.00, 9.18] | False | 0.164 | 0.137 | 0.111 | 0.057 | -0.049 |
| level_h100 | 5 | 7 | 2 | 2.203 | n/a | False | 0.478 | 0.410 | 0.341 | 0.204 | -0.070 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 15 | 4 | -3.934 | [-10.30, 6.02] | False | -0.080 | -0.133 | -0.187 | -0.293 | -0.507 |
| level_b200 | 5 | 7 | 1 | 2.683 | n/a | False | 0.470 | 0.435 | 0.401 | 0.333 | 0.196 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 15 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 7 | 2 | -3.875 | n/a | False | -1.337 | -1.393 | -1.449 | -1.560 | -1.783 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 15 | 2 | 4.071 | [-4.10, 7.61] | False | 0.133 | 0.107 | 0.081 | 0.029 | -0.075 |
| disp_b200 | 5 | 7 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 15 | 3 | -2.546 | [-6.69, 6.02] | False | -0.065 | -0.104 | -0.144 | -0.222 | -0.380 |
| avail_h100 | 5 | 7 | 1 | 2.683 | n/a | False | 0.470 | 0.435 | 0.401 | 0.333 | 0.196 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 15 | 2 | -4.396 | [-8.11, 0.00] | False | -0.173 | -0.199 | -0.225 | -0.277 | -0.382 |
| avail_b200 | 5 | 7 | 1 | 2.683 | n/a | False | 0.470 | 0.435 | 0.401 | 0.333 | 0.196 |
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
| neocloud | level_h100 | 1 | 35 | 7 | -1.591 | -0.404 | [-0.57, 0.16] | 0.003 | 0.022 | 0.029 | False | insufficient variation (7 non-zero < 10) |
| neocloud | level_h100 | 5 | 31 | 4 | -2.143 | -0.197 | [-0.37, -0.03] | 0.000 | 0.000 | 0.217 | False | insufficient variation (4 non-zero < 10) |
| neocloud | level_h100 | 20 | 16 | 3 | n/a | -0.050 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 35 | 13 | -0.593 | -0.408 | [-0.58, -0.06] | 0.017 | 0.072 | 0.029 | True |  |
| neocloud | level_b200 | 5 | 31 | 10 | -0.945 | -0.120 | [-0.38, 0.59] | 0.082 | 0.262 | 0.652 | False |  |
| neocloud | level_b200 | 20 | 16 | 1 | n/a | -0.084 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 35 | 29 | -0.100 | -0.076 | [-0.33, 0.19] | 0.502 | 1.000 | 0.600 | False |  |
| neocloud | disp_h100 | 5 | 31 | 25 | 0.309 | 0.087 | [-0.24, 0.32] | 0.448 | 1.000 | 0.696 | False |  |
| neocloud | disp_h100 | 20 | 16 | 11 | n/a | -0.173 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 35 | 6 | 0.300 | 0.460 | [-0.09, 0.59] | 0.000 | 0.000 | 0.029 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 5 | 31 | 5 | 0.238 | 0.106 | [-0.32, 0.38] | 0.139 | 0.367 | 0.435 | False | insufficient variation (5 non-zero < 10) |
| neocloud | disp_b200 | 20 | 16 | 1 | n/a | 0.084 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 35 | 5 | 0.005 | 0.031 | [-0.37, 0.25] | 0.822 | 1.000 | 0.943 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_h100 | 5 | 31 | 2 | -2.806 | -0.370 | [-0.57, -0.02] | 0.020 | 0.077 | 0.130 | False | insufficient variation (2 non-zero < 10) |
| neocloud | avail_h100 | 20 | 16 | 2 | n/a | -0.438 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 35 | 3 | 0.000 | 0.001 | [-0.33, 0.27] | 0.995 | 1.000 | 1.000 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_b200 | 5 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| neocloud | avail_b200 | 20 | 16 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 35 | 7 | -0.738 | -0.467 | [-0.73, -0.06] | 0.002 | 0.018 | 0.057 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | level_h100 | 5 | 31 | 4 | -0.467 | -0.106 | [-0.35, 0.25] | 0.328 | 0.806 | 0.522 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 16 | 3 | n/a | -0.064 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 35 | 13 | -0.121 | -0.206 | [-0.70, 0.20] | 0.423 | 0.993 | 0.257 | False |  |
| gpu_semis | level_b200 | 5 | 31 | 10 | -0.199 | -0.063 | [-0.37, 0.62] | 0.651 | 1.000 | 0.739 | False |  |
| gpu_semis | level_b200 | 20 | 16 | 1 | n/a | -0.083 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 35 | 29 | 0.014 | 0.027 | [-0.33, 0.24] | 0.862 | 1.000 | 0.914 | False |  |
| gpu_semis | disp_h100 | 5 | 31 | 25 | 0.065 | 0.046 | [-0.31, 0.33] | 0.717 | 1.000 | 0.913 | False |  |
| gpu_semis | disp_h100 | 20 | 16 | 11 | n/a | -0.041 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 35 | 6 | 0.092 | 0.350 | [-0.26, 0.70] | 0.135 | 0.367 | 0.057 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 31 | 5 | 0.115 | 0.127 | [-0.26, 0.38] | 0.055 | 0.185 | 0.609 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 16 | 1 | n/a | 0.083 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 35 | 5 | 0.021 | 0.302 | [-0.31, 0.55] | 0.000 | 0.000 | 0.114 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 31 | 2 | -0.847 | -0.276 | [-0.46, -0.05] | 0.001 | 0.006 | 0.217 | False | insufficient variation (2 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 16 | 2 | n/a | -0.201 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 35 | 3 | 0.021 | 0.307 | [0.00, 0.55] | 0.000 | 0.000 | 0.086 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| gpu_semis | avail_b200 | 20 | 16 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 35 | 7 | -0.663 | -0.236 | [-0.39, 0.19] | 0.044 | 0.159 | 0.171 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | level_h100 | 5 | 31 | 4 | -0.219 | -0.029 | [-0.28, 0.42] | 0.769 | 1.000 | 0.696 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | level_h100 | 20 | 16 | 3 | n/a | 0.294 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 35 | 13 | -0.227 | -0.218 | [-0.42, -0.03] | 0.143 | 0.367 | 0.171 | False |  |
| power_capacity | level_b200 | 5 | 31 | 10 | -0.659 | -0.122 | [-0.39, 0.22] | 0.011 | 0.055 | 0.435 | False |  |
| power_capacity | level_b200 | 20 | 16 | 1 | n/a | 0.216 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 35 | 29 | -0.011 | -0.012 | [-0.22, 0.24] | 0.913 | 1.000 | 0.943 | False |  |
| power_capacity | disp_h100 | 5 | 31 | 25 | 0.166 | 0.068 | [-0.29, 0.33] | 0.602 | 1.000 | 0.696 | False |  |
| power_capacity | disp_h100 | 20 | 16 | 11 | n/a | -0.232 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 35 | 6 | 0.122 | 0.263 | [-0.13, 0.39] | 0.009 | 0.052 | 0.086 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 31 | 5 | 0.152 | 0.099 | [-0.11, 0.36] | 0.100 | 0.301 | 0.435 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 16 | 1 | n/a | -0.216 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 35 | 5 | 0.018 | 0.146 | [-0.45, 0.32] | 0.004 | 0.024 | 0.371 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 31 | 2 | -1.762 | -0.340 | [-0.53, -0.05] | 0.011 | 0.055 | 0.130 | False | insufficient variation (2 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 16 | 2 | n/a | -0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 35 | 3 | 0.017 | 0.147 | [-0.08, 0.31] | 0.012 | 0.055 | 0.371 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 31 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| power_capacity | avail_b200 | 20 | 16 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.25, 0.27] | 0.15 [-0.15, 0.34] |
| -4 | -0.04 [-0.36, 0.13] | -0.20 [-0.38, 0.02] |
| -3 | -0.19 [-0.38, 0.24] | -0.18 [-0.42, 0.03] |
| -2 | -0.18 [-0.41, 0.18] | -0.19 [-0.41, 0.22] |
| -1 | -0.09 [-0.37, 0.23] | -0.34 [-0.47, 0.07] |
| 0 | -0.34 [-0.59, -0.02] | -0.40 [-0.59, 0.11] |
| 1 | 0.04 [-0.32, 0.46] | -0.07 [-0.30, 0.48] |
| 2 | 0.09 [-0.28, 0.37] | 0.07 [-0.30, 0.39] |
| 3 | -0.18 [-0.43, 0.23] | 0.04 [-0.48, 0.26] |
| 4 | -0.02 [-0.30, 0.14] | -0.02 [-0.21, 0.09] |
| 5 | -0.01 [-0.39, 0.12] | -0.11 [-0.37, 0.13] |

