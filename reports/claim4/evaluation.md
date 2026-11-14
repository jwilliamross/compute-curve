# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-14T03:32:28.249563+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `e4fb79451b16cc3d...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 5 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 41 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 61 | 2026-08-20 | 2026-11-13 | 0.35 | 0.46 |
| 5 | 57 | 2026-08-20 | 2026-11-09 | 0.36 | 0.48 |
| 20 | 42 | 2026-08-20 | 2026-10-19 | 0.42 | 0.55 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 61 | 27 | 0.063 | 0.048 | [-0.35, 0.24] | 0.658 | 1.000 | 0.787 | False |  |
| level_h100 | 5 | 57 | 24 | 0.066 | 0.010 | [-0.26, 0.26] | 0.938 | 1.000 | 0.918 | False |  |
| level_h100 | 20 | 42 | 13 | n/a | -0.135 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 61 | 25 | -0.402 | -0.342 | [-0.51, -0.15] | 0.011 | 0.197 | 0.016 | False |  |
| level_b200 | 5 | 57 | 24 | -0.393 | -0.131 | [-0.33, 0.02] | 0.086 | 1.000 | 0.429 | False |  |
| level_b200 | 20 | 42 | 20 | n/a | -0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 61 | 48 | 0.071 | 0.095 | [-0.12, 0.32] | 0.450 | 1.000 | 0.426 | False |  |
| disp_h100 | 5 | 57 | 47 | -0.210 | -0.109 | [-0.41, 0.15] | 0.329 | 1.000 | 0.265 | False |  |
| disp_h100 | 20 | 42 | 35 | n/a | -0.113 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 61 | 14 | 0.143 | 0.266 | [-0.08, 0.46] | 0.015 | 0.253 | 0.049 | False |  |
| disp_b200 | 5 | 57 | 13 | 0.163 | 0.116 | [-0.07, 0.26] | 0.055 | 0.873 | 0.327 | False |  |
| disp_b200 | 20 | 42 | 7 | n/a | 0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 61 | 18 | -0.004 | -0.056 | [-0.29, 0.22] | 0.712 | 1.000 | 0.689 | False |  |
| avail_h100 | 5 | 57 | 17 | -0.008 | -0.047 | [-0.21, 0.10] | 0.422 | 1.000 | 0.429 | False |  |
| avail_h100 | 20 | 42 | 9 | n/a | -0.011 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 61 | 15 | -0.003 | -0.047 | [-0.28, 0.23] | 0.760 | 1.000 | 0.770 | False |  |
| avail_b200 | 5 | 57 | 14 | -0.009 | -0.057 | [-0.21, 0.09] | 0.313 | 1.000 | 0.429 | False |  |
| avail_b200 | 20 | 42 | 7 | n/a | -0.021 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 5 | -0.081 | n/a | 1.000 | 1.000 | False | insufficient events (5 < 10); descriptive only |
| H100 | 5 | 3 | 0.974 | n/a | 1.000 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.734 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 41 | -0.221 | -0.203 | 0.690 | 0.744 | 0.488 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 33 | -0.030 | -0.118 | 0.230 | 0.723 | 0.758 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 3 | 0.820 | 0.033 | n/a | n/a | 1.000 | n/a | False | 3 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 41 | -0.166 | -0.149 | 0.051 | 0.037 | 0.537 | 0.917 | False | 41 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 33 | 0.101 | 0.024 | 0.028 | 0.060 | 0.758 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 3 | 0.891 | 0.414 | n/a | n/a | 1.000 | n/a | False | 3 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 41 | -0.031 | -0.017 | 0.797 | 0.803 | 0.488 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 33 | 0.045 | -0.037 | 0.138 | 0.982 | 0.667 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 3 | 0.867 | 0.288 | n/a | n/a | 1.000 | n/a | False | 3 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 41 | -0.044 | -0.029 | 0.196 | 0.174 | 0.512 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 33 | 0.083 | 0.005 | 0.062 | 0.239 | 0.697 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 3 | 0.823 | 0.051 | n/a | n/a | 1.000 | n/a | False | 3 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 41 | -1.252 | -1.220 | 0.373 | 0.426 | 0.488 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 33 | -30.248 | -32.920 | 0.546 | 0.631 | 0.636 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 3 | -218.601 | -1,177.727 | n/a | n/a | 0.333 | n/a | False | 3 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 41 | -0.173 | -0.156 | 0.832 | 0.841 | 0.488 | 1.000 | False | 41 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 33 | 0.091 | 0.013 | 0.069 | 0.118 | 0.667 | 1.000 | False | 33 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 3 | 0.814 | 0.000 | n/a | n/a | 1.000 | n/a | False | 3 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 41 | 9 | -1.357 | [-5.68, 4.63] | False | -0.007 | -0.050 | -0.093 | -0.180 | -0.354 |
| level_h100 | 5 | 33 | 26 | 2.578 | [-1.08, 7.75] | False | 2.192 | 2.003 | 1.814 | 1.437 | 0.681 |
| level_h100 | 20 | 3 | 3 | 5.304 | n/a | False | 5.317 | 4.928 | 4.540 | 3.763 | 2.209 |
| level_b200 | 1 | 41 | 7 | 1.943 | [-3.67, 6.29] | False | 0.167 | 0.132 | 0.098 | 0.030 | -0.107 |
| level_b200 | 5 | 33 | 27 | 3.049 | [-0.77, 9.07] | False | 2.567 | 2.371 | 2.175 | 1.783 | 0.999 |
| level_b200 | 20 | 3 | 3 | 5.304 | n/a | False | 5.317 | 4.928 | 4.540 | 3.763 | 2.209 |
| disp_h100 | 1 | 41 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 33 | 27 | 2.201 | [-1.62, 7.37] | False | 2.048 | 1.855 | 1.661 | 1.275 | 0.501 |
| disp_h100 | 20 | 3 | 3 | 5.304 | n/a | False | 5.317 | 4.928 | 4.540 | 3.763 | 2.209 |
| disp_b200 | 1 | 41 | 6 | -0.003 | [-4.38, 4.69] | False | 0.058 | 0.029 | -0.000 | -0.058 | -0.173 |
| disp_b200 | 5 | 33 | 26 | 2.922 | [-0.90, 8.65] | False | 2.468 | 2.279 | 2.090 | 1.713 | 0.958 |
| disp_b200 | 20 | 3 | 3 | 5.304 | n/a | False | 5.317 | 4.928 | 4.540 | 3.763 | 2.209 |
| avail_h100 | 1 | 41 | 9 | -2.109 | [-4.55, 0.87] | False | -0.088 | -0.131 | -0.174 | -0.261 | -0.434 |
| avail_h100 | 5 | 33 | 27 | 1.491 | [-1.26, 4.49] | False | 1.539 | 1.346 | 1.152 | 0.766 | -0.008 |
| avail_h100 | 20 | 3 | 3 | -0.913 | n/a | False | -1.221 | -1.490 | -1.760 | -2.298 | -3.376 |
| avail_b200 | 1 | 41 | 8 | -2.507 | [-5.14, 0.34] | False | -0.128 | -0.166 | -0.204 | -0.281 | -0.434 |
| avail_b200 | 5 | 33 | 27 | 2.457 | [-1.06, 7.17] | False | 2.204 | 2.009 | 1.814 | 1.425 | 0.646 |
| avail_b200 | 20 | 3 | 3 | 5.304 | n/a | False | 5.317 | 4.928 | 4.540 | 3.763 | 2.209 |

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
| neocloud | level_h100 | 1 | 61 | 27 | 0.219 | 0.104 | [-0.35, 0.34] | 0.352 | 1.000 | 0.492 | False |  |
| neocloud | level_h100 | 5 | 57 | 24 | -0.704 | -0.073 | [-0.29, 0.16] | 0.562 | 1.000 | 0.551 | False |  |
| neocloud | level_h100 | 20 | 42 | 13 | n/a | -0.192 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 61 | 25 | -0.668 | -0.353 | [-0.49, -0.20] | 0.001 | 0.016 | 0.016 | True |  |
| neocloud | level_b200 | 5 | 57 | 24 | -0.875 | -0.196 | [-0.35, -0.04] | 0.010 | 0.130 | 0.163 | False |  |
| neocloud | level_b200 | 20 | 42 | 20 | n/a | -0.288 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 61 | 48 | 0.061 | 0.051 | [-0.16, 0.25] | 0.664 | 1.000 | 0.738 | False |  |
| neocloud | disp_h100 | 5 | 57 | 47 | -0.385 | -0.134 | [-0.43, 0.10] | 0.243 | 1.000 | 0.102 | False |  |
| neocloud | disp_h100 | 20 | 42 | 35 | n/a | -0.140 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 61 | 14 | 0.238 | 0.275 | [-0.09, 0.47] | 0.003 | 0.046 | 0.016 | True |  |
| neocloud | disp_b200 | 5 | 57 | 13 | 0.383 | 0.182 | [0.03, 0.30] | 0.000 | 0.000 | 0.122 | False |  |
| neocloud | disp_b200 | 20 | 42 | 7 | n/a | 0.231 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 61 | 18 | -0.010 | -0.100 | [-0.34, 0.17] | 0.514 | 1.000 | 0.361 | False |  |
| neocloud | avail_h100 | 5 | 57 | 17 | -0.009 | -0.038 | [-0.20, 0.11] | 0.541 | 1.000 | 0.612 | False |  |
| neocloud | avail_h100 | 20 | 42 | 9 | n/a | -0.046 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 61 | 15 | -0.010 | -0.094 | [-0.34, 0.18] | 0.547 | 1.000 | 0.443 | False |  |
| neocloud | avail_b200 | 5 | 57 | 14 | -0.012 | -0.050 | [-0.21, 0.10] | 0.399 | 1.000 | 0.531 | False |  |
| neocloud | avail_b200 | 20 | 42 | 7 | n/a | -0.056 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 61 | 27 | -0.010 | -0.012 | [-0.42, 0.19] | 0.919 | 1.000 | 0.951 | False |  |
| gpu_semis | level_h100 | 5 | 57 | 24 | 0.159 | 0.034 | [-0.25, 0.30] | 0.795 | 1.000 | 0.776 | False |  |
| gpu_semis | level_h100 | 20 | 42 | 13 | n/a | -0.170 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 61 | 25 | -0.188 | -0.259 | [-0.57, 0.03] | 0.173 | 0.937 | 0.033 | False |  |
| gpu_semis | level_b200 | 5 | 57 | 24 | -0.227 | -0.106 | [-0.29, 0.07] | 0.137 | 0.926 | 0.510 | False |  |
| gpu_semis | level_b200 | 20 | 42 | 20 | n/a | -0.306 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 61 | 48 | 0.044 | 0.096 | [-0.16, 0.36] | 0.506 | 1.000 | 0.410 | False |  |
| gpu_semis | disp_h100 | 5 | 57 | 47 | -0.121 | -0.088 | [-0.39, 0.16] | 0.392 | 1.000 | 0.367 | False |  |
| gpu_semis | disp_h100 | 20 | 42 | 35 | n/a | -0.098 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 61 | 14 | 0.091 | 0.273 | [-0.09, 0.55] | 0.097 | 0.746 | 0.033 | False |  |
| gpu_semis | disp_b200 | 5 | 57 | 13 | 0.109 | 0.109 | [-0.13, 0.28] | 0.155 | 0.930 | 0.245 | False |  |
| gpu_semis | disp_b200 | 20 | 42 | 7 | n/a | 0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 61 | 18 | -0.001 | -0.018 | [-0.27, 0.30] | 0.911 | 1.000 | 0.951 | False |  |
| gpu_semis | avail_h100 | 5 | 57 | 17 | -0.006 | -0.055 | [-0.19, 0.08] | 0.293 | 1.000 | 0.408 | False |  |
| gpu_semis | avail_h100 | 20 | 42 | 9 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 61 | 15 | -0.000 | -0.003 | [-0.26, 0.32] | 0.984 | 1.000 | 0.984 | False |  |
| gpu_semis | avail_b200 | 5 | 57 | 14 | -0.008 | -0.068 | [-0.20, 0.07] | 0.193 | 0.946 | 0.347 | False |  |
| gpu_semis | avail_b200 | 20 | 42 | 7 | n/a | -0.050 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 61 | 27 | -0.019 | -0.013 | [-0.25, 0.10] | 0.860 | 1.000 | 0.951 | False |  |
| power_capacity | level_h100 | 5 | 57 | 24 | 0.744 | 0.114 | [-0.19, 0.36] | 0.354 | 1.000 | 0.245 | False |  |
| power_capacity | level_h100 | 20 | 42 | 13 | n/a | 0.099 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 61 | 25 | -0.351 | -0.276 | [-0.44, -0.09] | 0.022 | 0.241 | 0.033 | False |  |
| power_capacity | level_b200 | 5 | 57 | 24 | -0.076 | -0.025 | [-0.30, 0.11] | 0.723 | 1.000 | 0.878 | False |  |
| power_capacity | level_b200 | 20 | 42 | 20 | n/a | -0.013 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 61 | 48 | 0.108 | 0.134 | [-0.08, 0.35] | 0.267 | 1.000 | 0.279 | False |  |
| power_capacity | disp_h100 | 5 | 57 | 47 | -0.124 | -0.064 | [-0.36, 0.19] | 0.576 | 1.000 | 0.531 | False |  |
| power_capacity | disp_h100 | 20 | 42 | 35 | n/a | -0.025 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 61 | 14 | 0.100 | 0.172 | [-0.11, 0.32] | 0.075 | 0.672 | 0.230 | False |  |
| power_capacity | disp_b200 | 5 | 57 | 13 | -0.003 | -0.002 | [-0.20, 0.18] | 0.978 | 1.000 | 0.959 | False |  |
| power_capacity | disp_b200 | 20 | 42 | 7 | n/a | 0.002 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 61 | 18 | 0.000 | 0.005 | [-0.18, 0.23] | 0.970 | 1.000 | 0.951 | False |  |
| power_capacity | avail_h100 | 5 | 57 | 17 | -0.007 | -0.045 | [-0.22, 0.14] | 0.500 | 1.000 | 0.449 | False |  |
| power_capacity | avail_h100 | 20 | 42 | 9 | n/a | 0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 61 | 15 | 0.001 | 0.012 | [-0.17, 0.23] | 0.925 | 1.000 | 0.934 | False |  |
| power_capacity | avail_b200 | 5 | 57 | 14 | -0.008 | -0.048 | [-0.22, 0.14] | 0.492 | 1.000 | 0.469 | False |  |
| power_capacity | avail_b200 | 20 | 42 | 7 | n/a | 0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.15, 0.21] | -0.10 [-0.27, 0.18] |
| -4 | -0.02 [-0.14, 0.10] | -0.33 [-0.49, -0.13] |
| -3 | -0.11 [-0.25, 0.04] | 0.08 [-0.15, 0.39] |
| -2 | -0.22 [-0.42, 0.01] | -0.12 [-0.31, 0.11] |
| -1 | 0.08 [-0.26, 0.41] | -0.23 [-0.36, -0.06] |
| 0 | -0.34 [-0.51, -0.15] | 0.05 [-0.35, 0.24] |
| 1 | -0.06 [-0.30, 0.23] | 0.04 [-0.35, 0.35] |
| 2 | 0.06 [-0.20, 0.22] | 0.06 [-0.19, 0.37] |
| 3 | 0.01 [-0.25, 0.30] | 0.11 [-0.11, 0.26] |
| 4 | -0.03 [-0.14, 0.05] | 0.01 [-0.30, 0.25] |
| 5 | -0.03 [-0.19, 0.15] | -0.08 [-0.26, 0.11] |

