# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-22T01:47:57.061253+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `2fd07b6265333b39...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 24 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 44 | 2026-08-20 | 2026-10-21 | 0.41 | 0.54 |
| 5 | 40 | 2026-08-20 | 2026-10-15 | 0.43 | 0.56 |
| 20 | 25 | 2026-08-20 | 2026-09-24 | 0.54 | 0.67 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 44 | 14 | -0.976 | -0.328 | [-0.55, 0.10] | 0.008 | 0.125 | 0.045 | False |  |
| level_h100 | 5 | 40 | 11 | -1.026 | -0.128 | [-0.31, 0.19] | 0.119 | 1.000 | 0.438 | False |  |
| level_h100 | 20 | 25 | 3 | n/a | -0.052 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 44 | 22 | -0.334 | -0.305 | [-0.54, -0.09] | 0.080 | 1.000 | 0.068 | False |  |
| level_b200 | 5 | 40 | 18 | -0.533 | -0.181 | [-0.41, -0.00] | 0.067 | 1.000 | 0.312 | False |  |
| level_b200 | 20 | 25 | 8 | n/a | -0.247 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 44 | 37 | -0.064 | -0.074 | [-0.27, 0.14] | 0.503 | 1.000 | 0.636 | False |  |
| disp_h100 | 5 | 40 | 34 | 0.093 | 0.036 | [-0.24, 0.25] | 0.719 | 1.000 | 0.750 | False |  |
| disp_h100 | 20 | 25 | 20 | n/a | -0.064 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 44 | 7 | 0.168 | 0.346 | [-0.04, 0.54] | 0.001 | 0.025 | 0.023 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 40 | 7 | 0.242 | 0.186 | [0.03, 0.35] | 0.000 | 0.001 | 0.250 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 25 | 1 | n/a | 0.113 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 44 | 11 | -0.008 | -0.122 | [-0.39, 0.31] | 0.498 | 1.000 | 0.477 | False |  |
| avail_h100 | 5 | 40 | 7 | -0.015 | -0.060 | [-0.40, 0.14] | 0.525 | 1.000 | 0.406 | False | insufficient variation (7 non-zero < 10) |
| avail_h100 | 20 | 25 | 2 | n/a | -0.193 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 44 | 9 | -0.008 | -0.125 | [-0.38, 0.31] | 0.488 | 1.000 | 0.432 | False | insufficient variation (9 non-zero < 10) |
| avail_b200 | 5 | 40 | 5 | -0.014 | -0.056 | [-0.31, 0.13] | 0.536 | 1.000 | 0.438 | False | insufficient variation (5 non-zero < 10) |
| avail_b200 | 20 | 25 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 24 | -0.013 | -0.020 | 0.046 | 0.035 | 0.583 | 0.736 | False | 24 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 16 | 0.161 | 0.007 | 0.006 | 0.057 | 0.875 | 0.853 | False | 16 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 24 | -0.480 | -0.489 | 0.104 | 0.109 | 0.625 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 16 | 0.232 | 0.091 | 0.005 | 0.008 | 0.875 | 0.144 | False | 16 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 24 | -0.002 | -0.009 | 0.425 | 0.898 | 0.583 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 16 | 0.132 | -0.028 | 0.061 | 0.995 | 0.688 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 24 | -0.025 | -0.032 | 0.094 | 0.106 | 0.625 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 16 | 0.219 | 0.076 | 0.012 | 0.012 | 0.750 | 0.204 | False | 16 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 24 | -2.523 | -2.547 | 0.277 | 0.367 | 0.583 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 16 | -59.968 | -71.185 | 0.567 | 0.633 | 0.688 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 24 | -0.267 | -0.275 | 0.728 | 0.787 | 0.583 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 16 | 0.195 | 0.047 | 0.061 | 0.125 | 0.750 | 1.000 | False | 16 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 24 | 3 | 5.069 | [0.00, 7.87] | False | 0.208 | 0.183 | 0.158 | 0.108 | 0.008 |
| level_h100 | 5 | 16 | 10 | 5.795 | [2.16, 11.04] | True | 3.464 | 3.314 | 3.164 | 2.865 | 2.266 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 24 | 6 | 0.535 | [-5.96, 7.70] | False | 0.127 | 0.077 | 0.027 | -0.073 | -0.273 |
| level_b200 | 5 | 16 | 10 | 6.670 | [2.41, 17.51] | True | 3.940 | 3.791 | 3.641 | 3.341 | 2.742 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 24 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 16 | 10 | 3.721 | [-2.61, 14.33] | False | 2.869 | 2.725 | 2.581 | 2.293 | 1.716 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 24 | 3 | 3.961 | [-3.24, 6.40] | False | 0.113 | 0.088 | 0.064 | 0.015 | -0.084 |
| disp_b200 | 5 | 16 | 9 | 6.185 | [1.77, 16.19] | True | 3.735 | 3.600 | 3.465 | 3.196 | 2.657 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 24 | 6 | -2.313 | [-5.23, 5.80] | False | -0.085 | -0.134 | -0.183 | -0.282 | -0.479 |
| avail_h100 | 5 | 16 | 10 | 3.238 | [1.02, 7.27] | True | 2.570 | 2.423 | 2.276 | 1.982 | 1.394 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 24 | 5 | -3.041 | [-6.06, 4.69] | False | -0.153 | -0.194 | -0.234 | -0.316 | -0.480 |
| avail_b200 | 5 | 16 | 10 | 6.670 | [2.41, 17.51] | True | 3.940 | 3.791 | 3.641 | 3.341 | 2.742 |
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
| neocloud | level_h100 | 1 | 44 | 14 | -1.543 | -0.329 | [-0.54, 0.16] | 0.005 | 0.058 | 0.068 | False |  |
| neocloud | level_h100 | 5 | 40 | 11 | -2.446 | -0.198 | [-0.36, 0.02] | 0.000 | 0.001 | 0.281 | False |  |
| neocloud | level_h100 | 20 | 25 | 3 | n/a | -0.109 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 44 | 22 | -0.613 | -0.355 | [-0.54, -0.10] | 0.017 | 0.113 | 0.023 | False |  |
| neocloud | level_b200 | 5 | 40 | 18 | -1.096 | -0.242 | [-0.43, -0.03] | 0.009 | 0.079 | 0.281 | False |  |
| neocloud | level_b200 | 20 | 25 | 8 | n/a | -0.298 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 44 | 37 | -0.122 | -0.090 | [-0.29, 0.15] | 0.389 | 1.000 | 0.636 | False |  |
| neocloud | disp_h100 | 5 | 40 | 34 | 0.114 | 0.028 | [-0.26, 0.23] | 0.774 | 1.000 | 0.781 | False |  |
| neocloud | disp_h100 | 20 | 25 | 20 | n/a | -0.065 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 44 | 7 | 0.293 | 0.383 | [-0.02, 0.56] | 0.000 | 0.000 | 0.023 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 40 | 7 | 0.437 | 0.218 | [0.03, 0.38] | 0.000 | 0.000 | 0.094 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 25 | 1 | n/a | 0.164 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 44 | 11 | -0.022 | -0.220 | [-0.47, 0.19] | 0.194 | 0.700 | 0.114 | False |  |
| neocloud | avail_h100 | 5 | 40 | 7 | -0.027 | -0.070 | [-0.42, 0.08] | 0.382 | 1.000 | 0.375 | False | insufficient variation (7 non-zero < 10) |
| neocloud | avail_h100 | 20 | 25 | 2 | n/a | -0.230 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 44 | 9 | -0.023 | -0.229 | [-0.47, 0.17] | 0.175 | 0.675 | 0.114 | False | insufficient variation (9 non-zero < 10) |
| neocloud | avail_b200 | 5 | 40 | 5 | -0.028 | -0.074 | [-0.31, 0.07] | 0.332 | 1.000 | 0.438 | False | insufficient variation (5 non-zero < 10) |
| neocloud | avail_b200 | 20 | 25 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 44 | 14 | -0.691 | -0.364 | [-0.65, 0.02] | 0.012 | 0.092 | 0.023 | True |  |
| gpu_semis | level_h100 | 5 | 40 | 11 | -0.509 | -0.096 | [-0.32, 0.27] | 0.389 | 1.000 | 0.719 | False |  |
| gpu_semis | level_h100 | 20 | 25 | 3 | n/a | -0.107 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 44 | 22 | -0.150 | -0.214 | [-0.64, 0.10] | 0.372 | 1.000 | 0.205 | False |  |
| gpu_semis | level_b200 | 5 | 40 | 18 | -0.335 | -0.172 | [-0.42, 0.09] | 0.049 | 0.238 | 0.281 | False |  |
| gpu_semis | level_b200 | 20 | 25 | 8 | n/a | -0.291 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 44 | 37 | -0.031 | -0.057 | [-0.33, 0.16] | 0.693 | 1.000 | 0.705 | False |  |
| gpu_semis | disp_h100 | 5 | 40 | 34 | 0.006 | 0.003 | [-0.25, 0.23] | 0.972 | 1.000 | 0.969 | False |  |
| gpu_semis | disp_h100 | 20 | 25 | 20 | n/a | 0.026 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 44 | 7 | 0.105 | 0.340 | [-0.10, 0.64] | 0.088 | 0.397 | 0.045 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 40 | 7 | 0.190 | 0.221 | [0.05, 0.39] | 0.000 | 0.001 | 0.281 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 25 | 1 | n/a | 0.151 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 44 | 11 | -0.000 | -0.001 | [-0.33, 0.47] | 0.995 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_h100 | 5 | 40 | 7 | -0.005 | -0.033 | [-0.34, 0.12] | 0.693 | 1.000 | 0.625 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 25 | 2 | n/a | -0.072 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 44 | 9 | 0.000 | 0.007 | [-0.32, 0.48] | 0.971 | 1.000 | 0.955 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 40 | 5 | -0.005 | -0.034 | [-0.27, 0.13] | 0.679 | 1.000 | 0.625 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 25 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 44 | 14 | -0.694 | -0.213 | [-0.38, 0.12] | 0.025 | 0.148 | 0.250 | False |  |
| power_capacity | level_h100 | 5 | 40 | 11 | -0.124 | -0.016 | [-0.22, 0.41] | 0.888 | 1.000 | 0.812 | False |  |
| power_capacity | level_h100 | 20 | 25 | 3 | n/a | 0.167 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 44 | 22 | -0.240 | -0.200 | [-0.39, -0.03] | 0.115 | 0.476 | 0.182 | False |  |
| power_capacity | level_b200 | 5 | 40 | 18 | -0.170 | -0.060 | [-0.37, 0.19] | 0.566 | 1.000 | 0.688 | False |  |
| power_capacity | level_b200 | 20 | 25 | 8 | n/a | -0.008 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 44 | 37 | -0.038 | -0.040 | [-0.24, 0.19] | 0.731 | 1.000 | 0.841 | False |  |
| power_capacity | disp_h100 | 5 | 40 | 34 | 0.161 | 0.063 | [-0.21, 0.29] | 0.584 | 1.000 | 0.750 | False |  |
| power_capacity | disp_h100 | 20 | 25 | 20 | n/a | -0.147 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 44 | 7 | 0.105 | 0.197 | [-0.18, 0.36] | 0.030 | 0.162 | 0.205 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 40 | 7 | 0.098 | 0.078 | [-0.13, 0.25] | 0.232 | 0.784 | 0.656 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 25 | 1 | n/a | -0.083 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 44 | 11 | -0.001 | -0.018 | [-0.28, 0.32] | 0.906 | 1.000 | 0.955 | False |  |
| power_capacity | avail_h100 | 5 | 40 | 7 | -0.013 | -0.053 | [-0.41, 0.23] | 0.678 | 1.000 | 0.469 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 25 | 2 | n/a | -0.191 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 44 | 9 | -0.001 | -0.015 | [-0.22, 0.32] | 0.919 | 1.000 | 0.977 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 40 | 5 | -0.008 | -0.032 | [-0.36, 0.26] | 0.804 | 1.000 | 0.625 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 25 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.22, 0.21] | 0.13 [-0.15, 0.28] |
| -4 | -0.01 [-0.20, 0.17] | -0.16 [-0.31, 0.07] |
| -3 | -0.18 [-0.33, 0.03] | -0.16 [-0.36, 0.00] |
| -2 | -0.15 [-0.39, 0.16] | -0.14 [-0.35, 0.23] |
| -1 | -0.08 [-0.34, 0.17] | -0.30 [-0.43, 0.01] |
| 0 | -0.31 [-0.54, -0.09] | -0.33 [-0.55, 0.10] |
| 1 | 0.06 [-0.24, 0.41] | -0.04 [-0.25, 0.40] |
| 2 | 0.03 [-0.39, 0.26] | 0.03 [-0.33, 0.30] |
| 3 | -0.10 [-0.35, 0.35] | 0.09 [-0.18, 0.28] |
| 4 | -0.06 [-0.27, 0.02] | -0.09 [-0.44, 0.02] |
| 5 | -0.13 [-0.31, 0.02] | -0.07 [-0.36, 0.29] |

