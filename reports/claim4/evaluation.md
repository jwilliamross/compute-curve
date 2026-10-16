# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-16T01:38:57.345174+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `dfaa4a3c98688e0e...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 20 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 40 | 2026-08-20 | 2026-10-15 | 0.43 | 0.56 |
| 5 | 36 | 2026-08-20 | 2026-10-09 | 0.45 | 0.58 |
| 20 | 21 | 2026-08-20 | 2026-09-18 | 0.58 | 0.72 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 40 | 11 | -0.958 | -0.334 | [-0.55, 0.13] | 0.007 | 0.108 | 0.075 | False |  |
| level_h100 | 5 | 36 | 8 | -1.028 | -0.136 | [-0.31, 0.17] | 0.070 | 0.976 | 0.464 | False | insufficient variation (8 non-zero < 10) |
| level_h100 | 20 | 21 | 3 | n/a | -0.013 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 40 | 18 | -0.322 | -0.305 | [-0.55, -0.03] | 0.074 | 0.976 | 0.075 | False |  |
| level_b200 | 5 | 36 | 14 | -0.428 | -0.153 | [-0.30, 0.20] | 0.040 | 0.598 | 0.429 | False |  |
| level_b200 | 20 | 21 | 5 | n/a | -0.184 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 40 | 34 | 0.008 | 0.009 | [-0.20, 0.21] | 0.929 | 1.000 | 0.975 | False |  |
| disp_h100 | 5 | 36 | 30 | 0.108 | 0.043 | [-0.27, 0.25] | 0.677 | 1.000 | 0.786 | False |  |
| disp_h100 | 20 | 21 | 16 | n/a | -0.094 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 40 | 7 | 0.167 | 0.358 | [-0.02, 0.55] | 0.001 | 0.015 | 0.075 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 36 | 7 | 0.238 | 0.194 | [0.01, 0.36] | 0.000 | 0.000 | 0.286 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 21 | 1 | n/a | 0.072 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 40 | 7 | -0.001 | -0.010 | [-0.45, 0.36] | 0.966 | 1.000 | 0.975 | False | insufficient variation (7 non-zero < 10) |
| avail_h100 | 5 | 36 | 5 | 0.022 | 0.065 | [-0.46, 0.35] | 0.506 | 1.000 | 0.500 | False | insufficient variation (5 non-zero < 10) |
| avail_h100 | 20 | 21 | 2 | n/a | -0.266 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 40 | 5 | -0.001 | -0.016 | [-0.43, 0.36] | 0.944 | 1.000 | 0.900 | False | insufficient variation (5 non-zero < 10) |
| avail_b200 | 5 | 36 | 3 | 0.021 | 0.065 | [-0.25, 0.36] | 0.514 | 1.000 | 0.607 | False | insufficient variation (3 non-zero < 10) |
| avail_b200 | 20 | 21 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 20 | -0.048 | -0.033 | 0.092 | 0.045 | 0.550 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 12 | 0.136 | 0.012 | n/a | n/a | 0.917 | n/a | False | 12 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 20 | -0.612 | -0.590 | 0.127 | 0.118 | 0.600 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 12 | 0.205 | 0.091 | n/a | n/a | 0.917 | n/a | False | 12 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 20 | -0.021 | -0.006 | 0.670 | 0.805 | 0.550 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 12 | 0.090 | -0.041 | n/a | n/a | 0.667 | n/a | False | 12 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 20 | -0.054 | -0.039 | 0.126 | 0.106 | 0.600 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 12 | 0.220 | 0.108 | n/a | n/a | 0.750 | n/a | False | 12 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 20 | -3.047 | -2.990 | 0.316 | 0.380 | 0.550 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 12 | -91.749 | -105.066 | n/a | n/a | 0.667 | n/a | False | 12 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 20 | -0.348 | -0.329 | 0.783 | 0.803 | 0.550 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 12 | 0.126 | 0.000 | n/a | n/a | 0.750 | n/a | False | 12 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 20 | 2 | 4.612 | [0.00, 8.02] | False | 0.123 | 0.103 | 0.083 | 0.043 | -0.037 |
| level_h100 | 5 | 12 | 6 | 4.811 | [0.00, 10.87] | False | 2.585 | 2.466 | 2.346 | 2.106 | 1.627 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 20 | 5 | -1.613 | [-8.53, 7.73] | False | 0.026 | -0.024 | -0.074 | -0.174 | -0.374 |
| level_b200 | 5 | 12 | 6 | 5.872 | [2.05, 13.68] | True | 3.221 | 3.101 | 2.981 | 2.742 | 2.262 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 20 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 12 | 6 | 2.321 | [-4.46, 8.79] | False | 1.793 | 1.680 | 1.568 | 1.343 | 0.894 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 20 | 3 | 4.349 | [-3.55, 7.04] | False | 0.136 | 0.106 | 0.076 | 0.017 | -0.101 |
| disp_b200 | 5 | 12 | 5 | 5.262 | [0.00, 11.99] | False | 2.947 | 2.847 | 2.747 | 2.547 | 2.148 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 20 | 5 | -3.077 | [-5.78, 3.55] | False | -0.165 | -0.214 | -0.264 | -0.362 | -0.558 |
| avail_h100 | 5 | 12 | 6 | 1.720 | [-0.61, 7.43] | False | 1.393 | 1.277 | 1.161 | 0.929 | 0.464 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 20 | 4 | -3.918 | [-6.64, 0.00] | False | -0.247 | -0.286 | -0.325 | -0.403 | -0.559 |
| avail_b200 | 5 | 12 | 6 | 5.872 | [2.05, 13.68] | True | 3.221 | 3.101 | 2.981 | 2.742 | 2.262 |
| avail_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |

## Gate

| pair | G1 | G2 | G3 | G4 | validated |
|---|---|---|---|---|---|
| level_h100|h1 | False | False | False | False | False |
| level_h100|h5 | False | False | False | False | False |
| level_h100|h20 | False | False | False | False | False |
| level_b200|h1 | False | False | False | False | False |
| level_b200|h5 | False | False | True | False | False |
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
| avail_b200|h5 | False | False | True | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 40 | 11 | -1.525 | -0.339 | [-0.54, 0.18] | 0.004 | 0.036 | 0.100 | False |  |
| neocloud | level_h100 | 5 | 36 | 8 | -2.452 | -0.211 | [-0.37, -0.02] | 0.000 | 0.000 | 0.250 | False | insufficient variation (8 non-zero < 10) |
| neocloud | level_h100 | 20 | 21 | 3 | n/a | -0.092 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 40 | 18 | -0.596 | -0.360 | [-0.54, -0.03] | 0.013 | 0.086 | 0.050 | False |  |
| neocloud | level_b200 | 5 | 36 | 14 | -0.934 | -0.216 | [-0.36, 0.24] | 0.001 | 0.011 | 0.286 | False |  |
| neocloud | level_b200 | 20 | 21 | 5 | n/a | -0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 40 | 34 | -0.035 | -0.024 | [-0.24, 0.22] | 0.825 | 1.000 | 0.875 | False |  |
| neocloud | disp_h100 | 5 | 36 | 30 | 0.139 | 0.036 | [-0.28, 0.25] | 0.727 | 1.000 | 0.750 | False |  |
| neocloud | disp_h100 | 20 | 21 | 16 | n/a | -0.093 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 40 | 7 | 0.292 | 0.399 | [0.00, 0.57] | 0.000 | 0.000 | 0.075 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 36 | 7 | 0.431 | 0.228 | [0.01, 0.41] | 0.000 | 0.000 | 0.107 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 21 | 1 | n/a | 0.142 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 40 | 7 | -0.015 | -0.109 | [-0.48, 0.24] | 0.618 | 1.000 | 0.500 | False | insufficient variation (7 non-zero < 10) |
| neocloud | avail_h100 | 5 | 36 | 5 | 0.014 | 0.028 | [-0.48, 0.32] | 0.788 | 1.000 | 0.786 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_h100 | 20 | 21 | 2 | n/a | -0.314 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 40 | 5 | -0.017 | -0.126 | [-0.49, 0.23] | 0.567 | 1.000 | 0.425 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_b200 | 5 | 36 | 3 | 0.008 | 0.015 | [-0.32, 0.34] | 0.890 | 1.000 | 0.821 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_b200 | 20 | 21 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 40 | 11 | -0.683 | -0.376 | [-0.67, 0.03] | 0.009 | 0.071 | 0.025 | True |  |
| gpu_semis | level_h100 | 5 | 36 | 8 | -0.507 | -0.101 | [-0.30, 0.26] | 0.336 | 0.955 | 0.714 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 21 | 3 | n/a | -0.096 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 40 | 18 | -0.141 | -0.212 | [-0.65, 0.13] | 0.375 | 1.000 | 0.200 | False |  |
| gpu_semis | level_b200 | 5 | 36 | 14 | -0.262 | -0.141 | [-0.32, 0.32] | 0.032 | 0.143 | 0.607 | False |  |
| gpu_semis | level_b200 | 20 | 21 | 5 | n/a | -0.264 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 40 | 34 | 0.024 | 0.040 | [-0.25, 0.26] | 0.752 | 1.000 | 0.850 | False |  |
| gpu_semis | disp_h100 | 5 | 36 | 30 | 0.015 | 0.009 | [-0.29, 0.23] | 0.930 | 1.000 | 1.000 | False |  |
| gpu_semis | disp_h100 | 20 | 21 | 16 | n/a | 0.035 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 40 | 7 | 0.105 | 0.354 | [-0.09, 0.66] | 0.079 | 0.306 | 0.025 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 36 | 7 | 0.188 | 0.230 | [0.02, 0.41] | 0.000 | 0.002 | 0.250 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 21 | 1 | n/a | 0.133 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 40 | 7 | 0.011 | 0.195 | [-0.28, 0.53] | 0.299 | 0.897 | 0.225 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 36 | 5 | 0.013 | 0.060 | [-0.38, 0.33] | 0.578 | 1.000 | 0.464 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 21 | 2 | n/a | -0.119 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 40 | 5 | 0.011 | 0.202 | [-0.23, 0.54] | 0.275 | 0.873 | 0.175 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 36 | 3 | 0.011 | 0.053 | [-0.32, 0.34] | 0.638 | 1.000 | 0.643 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 21 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 40 | 11 | -0.666 | -0.208 | [-0.38, 0.15] | 0.031 | 0.143 | 0.200 | False |  |
| power_capacity | level_h100 | 5 | 36 | 8 | -0.125 | -0.017 | [-0.23, 0.44] | 0.880 | 1.000 | 0.821 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | level_h100 | 20 | 21 | 3 | n/a | 0.215 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 40 | 18 | -0.228 | -0.193 | [-0.39, -0.01] | 0.117 | 0.421 | 0.350 | False |  |
| power_capacity | level_b200 | 5 | 36 | 14 | -0.089 | -0.032 | [-0.31, 0.23] | 0.712 | 1.000 | 0.821 | False |  |
| power_capacity | level_b200 | 20 | 21 | 5 | n/a | 0.063 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 40 | 34 | 0.037 | 0.035 | [-0.17, 0.27] | 0.754 | 1.000 | 0.875 | False |  |
| power_capacity | disp_h100 | 5 | 36 | 30 | 0.170 | 0.069 | [-0.24, 0.30] | 0.565 | 1.000 | 0.679 | False |  |
| power_capacity | disp_h100 | 20 | 21 | 16 | n/a | -0.169 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 40 | 7 | 0.104 | 0.201 | [-0.18, 0.36] | 0.027 | 0.143 | 0.250 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 36 | 7 | 0.096 | 0.080 | [-0.14, 0.27] | 0.203 | 0.686 | 0.536 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 21 | 1 | n/a | -0.134 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 40 | 7 | 0.002 | 0.017 | [-0.42, 0.36] | 0.934 | 1.000 | 0.925 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 36 | 5 | 0.037 | 0.114 | [-0.43, 0.40] | 0.076 | 0.306 | 0.393 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 21 | 2 | n/a | -0.213 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 40 | 5 | 0.002 | 0.020 | [-0.37, 0.36] | 0.922 | 1.000 | 0.850 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 36 | 3 | 0.043 | 0.138 | [-0.08, 0.43] | 0.018 | 0.106 | 0.357 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 21 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.06 [-0.25, 0.22] | 0.13 [-0.15, 0.29] |
| -4 | -0.03 [-0.25, 0.16] | -0.17 [-0.34, 0.08] |
| -3 | -0.17 [-0.34, 0.10] | -0.15 [-0.38, 0.02] |
| -2 | -0.20 [-0.43, -0.01] | -0.17 [-0.37, 0.15] |
| -1 | -0.08 [-0.33, 0.19] | -0.30 [-0.44, 0.04] |
| 0 | -0.31 [-0.55, -0.03] | -0.33 [-0.55, 0.13] |
| 1 | 0.06 [-0.25, 0.42] | -0.05 [-0.26, 0.38] |
| 2 | 0.04 [-0.39, 0.30] | 0.03 [-0.36, 0.32] |
| 3 | -0.10 [-0.38, 0.44] | 0.09 [-0.22, 0.28] |
| 4 | -0.04 [-0.16, 0.08] | -0.09 [-0.46, 0.03] |
| 5 | -0.11 [-0.25, 0.09] | -0.09 [-0.40, 0.22] |

