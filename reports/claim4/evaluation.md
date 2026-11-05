# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-05T03:44:08.851978+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `27776bdc0eec44ff...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 4 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 34 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 54 | 2026-08-20 | 2026-11-04 | 0.37 | 0.49 |
| 5 | 50 | 2026-08-20 | 2026-10-29 | 0.39 | 0.51 |
| 20 | 35 | 2026-08-20 | 2026-10-08 | 0.46 | 0.59 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 54 | 21 | -0.733 | -0.236 | [-0.48, 0.11] | 0.132 | 1.000 | 0.056 | False |  |
| level_h100 | 5 | 50 | 18 | -1.126 | -0.132 | [-0.29, 0.13] | 0.094 | 1.000 | 0.429 | False |  |
| level_h100 | 20 | 35 | 7 | n/a | -0.166 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 54 | 24 | -0.387 | -0.348 | [-0.53, -0.13] | 0.015 | 0.241 | 0.019 | False |  |
| level_b200 | 5 | 50 | 23 | -0.563 | -0.180 | [-0.40, -0.02] | 0.069 | 1.000 | 0.286 | False |  |
| level_b200 | 20 | 35 | 13 | n/a | -0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 54 | 45 | 0.015 | 0.018 | [-0.14, 0.20] | 0.878 | 1.000 | 0.852 | False |  |
| disp_h100 | 5 | 50 | 42 | -0.012 | -0.006 | [-0.34, 0.26] | 0.966 | 1.000 | 1.000 | False |  |
| disp_h100 | 20 | 35 | 29 | n/a | -0.155 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 54 | 12 | 0.192 | 0.360 | [0.08, 0.52] | 0.000 | 0.001 | 0.019 | True |  |
| disp_b200 | 5 | 50 | 11 | 0.259 | 0.186 | [0.06, 0.33] | 0.000 | 0.001 | 0.167 | False |  |
| disp_b200 | 20 | 35 | 6 | n/a | 0.172 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 54 | 16 | -0.003 | -0.055 | [-0.30, 0.26] | 0.730 | 1.000 | 0.704 | False |  |
| avail_h100 | 5 | 50 | 14 | -0.006 | -0.037 | [-0.24, 0.18] | 0.624 | 1.000 | 0.476 | False |  |
| avail_h100 | 20 | 35 | 5 | n/a | 0.056 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 54 | 14 | -0.003 | -0.053 | [-0.30, 0.25] | 0.741 | 1.000 | 0.722 | False |  |
| avail_b200 | 5 | 50 | 12 | -0.005 | -0.035 | [-0.23, 0.18] | 0.644 | 1.000 | 0.571 | False |  |
| avail_b200 | 20 | 35 | 3 | n/a | 0.033 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 34 | -0.061 | -0.060 | 0.279 | 0.315 | 0.529 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 26 | 0.191 | 0.012 | 0.001 | 0.039 | 0.808 | 0.625 | False | 26 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 34 | -0.194 | -0.192 | 0.050 | 0.048 | 0.588 | 0.746 | False | 34 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 26 | 0.242 | 0.074 | 0.001 | 0.024 | 0.808 | 0.407 | False | 26 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 34 | -0.028 | -0.027 | 0.777 | 0.976 | 0.529 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 26 | 0.124 | -0.071 | 0.024 | 0.990 | 0.692 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 34 | 0.046 | 0.047 | 0.050 | 0.046 | 0.588 | 0.746 | False | 34 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 26 | 0.234 | 0.064 | 0.001 | 0.019 | 0.731 | 0.345 | False | 26 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 34 | -1.455 | -1.452 | 0.342 | 0.427 | 0.529 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 26 | -41.502 | -50.927 | 0.541 | 0.633 | 0.654 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 34 | -0.186 | -0.185 | 0.792 | 0.839 | 0.529 | 1.000 | False | 34 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 26 | 0.190 | 0.010 | 0.018 | 0.144 | 0.692 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 34 | 6 | 1.027 | [-3.15, 6.41] | False | 0.137 | 0.102 | 0.067 | -0.003 | -0.143 |
| level_h100 | 5 | 26 | 20 | 4.882 | [1.44, 9.22] | True | 3.157 | 2.973 | 2.789 | 2.420 | 1.683 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 34 | 7 | 2.131 | [-2.69, 6.30] | False | 0.201 | 0.160 | 0.119 | 0.036 | -0.128 |
| level_b200 | 5 | 26 | 20 | 5.350 | [1.55, 11.43] | True | 3.451 | 3.266 | 3.082 | 2.713 | 1.976 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 34 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 26 | 20 | 3.696 | [-0.38, 8.96] | False | 2.791 | 2.611 | 2.430 | 2.068 | 1.344 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 34 | 4 | 3.752 | [2.58, 5.73] | True | 0.191 | 0.168 | 0.144 | 0.098 | 0.005 |
| disp_b200 | 5 | 26 | 19 | 5.107 | [1.37, 10.74] | True | 3.324 | 3.149 | 2.974 | 2.624 | 1.923 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 34 | 9 | -2.314 | [-5.06, 1.00] | False | -0.106 | -0.158 | -0.210 | -0.315 | -0.523 |
| avail_h100 | 5 | 26 | 20 | 2.560 | [0.58, 4.72] | True | 2.145 | 1.964 | 1.784 | 1.422 | 0.698 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 34 | 8 | -2.753 | [-5.50, 0.53] | False | -0.154 | -0.200 | -0.246 | -0.339 | -0.524 |
| avail_b200 | 5 | 26 | 20 | 4.180 | [1.07, 8.97] | True | 2.989 | 2.806 | 2.624 | 2.259 | 1.528 |
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
| disp_b200|h1 | True | False | True | False | False |
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
| neocloud | level_h100 | 1 | 54 | 21 | -1.177 | -0.237 | [-0.47, 0.10] | 0.098 | 0.479 | 0.056 | False |  |
| neocloud | level_h100 | 5 | 50 | 18 | -2.615 | -0.198 | [-0.33, -0.03] | 0.000 | 0.000 | 0.238 | False |  |
| neocloud | level_h100 | 20 | 35 | 7 | n/a | -0.215 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 54 | 24 | -0.646 | -0.363 | [-0.51, -0.19] | 0.001 | 0.010 | 0.019 | True |  |
| neocloud | level_b200 | 5 | 50 | 23 | -1.142 | -0.235 | [-0.41, -0.03] | 0.009 | 0.071 | 0.167 | False |  |
| neocloud | level_b200 | 20 | 35 | 13 | n/a | -0.284 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 54 | 45 | -0.001 | -0.000 | [-0.16, 0.18] | 0.997 | 1.000 | 1.000 | False |  |
| neocloud | disp_h100 | 5 | 50 | 42 | -0.088 | -0.028 | [-0.36, 0.24] | 0.836 | 1.000 | 0.714 | False |  |
| neocloud | disp_h100 | 20 | 35 | 29 | n/a | -0.158 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 54 | 12 | 0.318 | 0.373 | [0.12, 0.52] | 0.000 | 0.000 | 0.019 | True |  |
| neocloud | disp_b200 | 5 | 50 | 11 | 0.465 | 0.215 | [0.08, 0.36] | 0.000 | 0.000 | 0.095 | False |  |
| neocloud | disp_b200 | 20 | 35 | 6 | n/a | 0.207 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 54 | 16 | -0.010 | -0.104 | [-0.36, 0.20] | 0.525 | 1.000 | 0.389 | False |  |
| neocloud | avail_h100 | 5 | 50 | 14 | -0.012 | -0.047 | [-0.23, 0.15] | 0.493 | 1.000 | 0.429 | False |  |
| neocloud | avail_h100 | 20 | 35 | 5 | n/a | 0.006 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 54 | 14 | -0.010 | -0.106 | [-0.37, 0.19] | 0.521 | 1.000 | 0.407 | False |  |
| neocloud | avail_b200 | 5 | 50 | 12 | -0.012 | -0.049 | [-0.23, 0.15] | 0.465 | 1.000 | 0.476 | False |  |
| neocloud | avail_b200 | 20 | 35 | 3 | n/a | -0.016 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 54 | 21 | -0.437 | -0.231 | [-0.58, 0.23] | 0.270 | 0.971 | 0.037 | False |  |
| gpu_semis | level_h100 | 5 | 50 | 18 | -0.483 | -0.084 | [-0.29, 0.26] | 0.467 | 1.000 | 0.738 | False |  |
| gpu_semis | level_h100 | 20 | 35 | 7 | n/a | -0.220 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 54 | 24 | -0.182 | -0.269 | [-0.60, 0.04] | 0.192 | 0.742 | 0.037 | False |  |
| gpu_semis | level_b200 | 5 | 50 | 23 | -0.308 | -0.146 | [-0.36, 0.18] | 0.097 | 0.479 | 0.452 | False |  |
| gpu_semis | level_b200 | 20 | 35 | 13 | n/a | -0.295 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 54 | 45 | -0.015 | -0.031 | [-0.24, 0.19] | 0.809 | 1.000 | 0.815 | False |  |
| gpu_semis | disp_h100 | 5 | 50 | 42 | 0.011 | 0.008 | [-0.29, 0.26] | 0.949 | 1.000 | 1.000 | False |  |
| gpu_semis | disp_h100 | 20 | 35 | 29 | n/a | -0.104 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 54 | 12 | 0.118 | 0.362 | [-0.03, 0.62] | 0.033 | 0.200 | 0.019 | False |  |
| gpu_semis | disp_b200 | 5 | 50 | 11 | 0.190 | 0.203 | [-0.05, 0.35] | 0.000 | 0.001 | 0.238 | False |  |
| gpu_semis | disp_b200 | 20 | 35 | 6 | n/a | 0.208 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 54 | 16 | -0.000 | -0.011 | [-0.29, 0.33] | 0.949 | 1.000 | 0.963 | False |  |
| gpu_semis | avail_h100 | 5 | 50 | 14 | -0.002 | -0.021 | [-0.20, 0.16] | 0.767 | 1.000 | 0.786 | False |  |
| gpu_semis | avail_h100 | 20 | 35 | 5 | n/a | 0.037 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 54 | 14 | -0.000 | -0.005 | [-0.28, 0.34] | 0.978 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 50 | 12 | -0.002 | -0.024 | [-0.19, 0.15] | 0.736 | 1.000 | 0.738 | False |  |
| gpu_semis | avail_b200 | 20 | 35 | 3 | n/a | 0.002 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 54 | 21 | -0.586 | -0.171 | [-0.33, 0.08] | 0.128 | 0.578 | 0.185 | False |  |
| power_capacity | level_h100 | 5 | 50 | 18 | -0.279 | -0.033 | [-0.24, 0.30] | 0.740 | 1.000 | 0.786 | False |  |
| power_capacity | level_h100 | 20 | 35 | 7 | n/a | 0.096 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 54 | 24 | -0.335 | -0.272 | [-0.42, -0.08] | 0.031 | 0.200 | 0.056 | False |  |
| power_capacity | level_b200 | 5 | 50 | 23 | -0.240 | -0.078 | [-0.43, 0.11] | 0.459 | 1.000 | 0.500 | False |  |
| power_capacity | level_b200 | 20 | 35 | 13 | n/a | -0.037 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 54 | 45 | 0.059 | 0.067 | [-0.10, 0.27] | 0.573 | 1.000 | 0.593 | False |  |
| power_capacity | disp_h100 | 5 | 50 | 42 | 0.042 | 0.021 | [-0.27, 0.27] | 0.870 | 1.000 | 0.786 | False |  |
| power_capacity | disp_h100 | 20 | 35 | 29 | n/a | -0.181 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 54 | 12 | 0.141 | 0.239 | [-0.04, 0.37] | 0.003 | 0.031 | 0.093 | False |  |
| power_capacity | disp_b200 | 5 | 50 | 11 | 0.122 | 0.089 | [-0.08, 0.30] | 0.146 | 0.606 | 0.452 | False |  |
| power_capacity | disp_b200 | 20 | 35 | 6 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 54 | 16 | 0.000 | 0.007 | [-0.19, 0.25] | 0.957 | 1.000 | 0.944 | False |  |
| power_capacity | avail_h100 | 5 | 50 | 14 | -0.004 | -0.025 | [-0.25, 0.23] | 0.780 | 1.000 | 0.548 | False |  |
| power_capacity | avail_h100 | 20 | 35 | 5 | n/a | 0.212 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 54 | 14 | 0.001 | 0.011 | [-0.18, 0.25] | 0.928 | 1.000 | 0.963 | False |  |
| power_capacity | avail_b200 | 5 | 50 | 12 | -0.002 | -0.011 | [-0.23, 0.24] | 0.902 | 1.000 | 0.810 | False |  |
| power_capacity | avail_b200 | 20 | 35 | 3 | n/a | 0.210 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.03 [-0.17, 0.22] | 0.09 [-0.11, 0.23] |
| -4 | -0.02 [-0.15, 0.12] | -0.18 [-0.30, -0.02] |
| -3 | -0.11 [-0.27, 0.06] | -0.07 [-0.25, 0.13] |
| -2 | -0.23 [-0.44, 0.02] | -0.12 [-0.31, 0.19] |
| -1 | 0.09 [-0.28, 0.44] | -0.17 [-0.36, 0.18] |
| 0 | -0.35 [-0.53, -0.13] | -0.24 [-0.48, 0.11] |
| 1 | 0.04 [-0.22, 0.31] | -0.18 [-0.46, 0.24] |
| 2 | 0.02 [-0.33, 0.20] | 0.17 [-0.20, 0.44] |
| 3 | -0.08 [-0.30, 0.27] | -0.00 [-0.33, 0.21] |
| 4 | -0.05 [-0.23, 0.02] | -0.10 [-0.46, -0.01] |
| 5 | -0.11 [-0.25, 0.03] | -0.04 [-0.28, 0.30] |

