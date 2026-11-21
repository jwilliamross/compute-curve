# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-21T04:15:48.770275+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `3ddcdc6d1f852496...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 7 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 46 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 66 | 2026-08-20 | 2026-11-20 | 0.34 | 0.45 |
| 5 | 62 | 2026-08-20 | 2026-11-16 | 0.35 | 0.46 |
| 20 | 47 | 2026-08-20 | 2026-10-26 | 0.40 | 0.52 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 66 | 29 | 0.056 | 0.042 | [-0.30, 0.23] | 0.703 | 1.000 | 0.758 | False |  |
| level_h100 | 5 | 62 | 27 | 0.252 | 0.073 | [-0.21, 0.24] | 0.310 | 1.000 | 0.537 | False |  |
| level_h100 | 20 | 47 | 17 | n/a | -0.134 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 66 | 25 | -0.381 | -0.304 | [-0.49, -0.11] | 0.017 | 0.309 | 0.015 | False |  |
| level_b200 | 5 | 62 | 25 | -0.371 | -0.121 | [-0.32, 0.03] | 0.118 | 1.000 | 0.352 | False |  |
| level_b200 | 20 | 47 | 23 | n/a | -0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 66 | 51 | 0.069 | 0.087 | [-0.11, 0.30] | 0.444 | 1.000 | 0.470 | False |  |
| disp_h100 | 5 | 62 | 49 | -0.209 | -0.108 | [-0.37, 0.12] | 0.302 | 1.000 | 0.407 | False |  |
| disp_h100 | 20 | 47 | 40 | n/a | -0.113 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 66 | 14 | 0.143 | 0.249 | [-0.08, 0.45] | 0.019 | 0.330 | 0.076 | False |  |
| disp_b200 | 5 | 62 | 14 | 0.107 | 0.076 | [-0.17, 0.24] | 0.362 | 1.000 | 0.667 | False |  |
| disp_b200 | 20 | 47 | 9 | n/a | 0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 66 | 20 | -0.004 | -0.052 | [-0.26, 0.20] | 0.709 | 1.000 | 0.667 | False |  |
| avail_h100 | 5 | 62 | 18 | -0.007 | -0.044 | [-0.18, 0.10] | 0.434 | 1.000 | 0.389 | False |  |
| avail_h100 | 20 | 47 | 12 | n/a | -0.028 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 66 | 15 | -0.003 | -0.044 | [-0.25, 0.21] | 0.759 | 1.000 | 0.788 | False |  |
| avail_b200 | 5 | 62 | 15 | -0.008 | -0.049 | [-0.18, 0.10] | 0.361 | 1.000 | 0.426 | False |  |
| avail_b200 | 20 | 47 | 10 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 7 | -0.089 | n/a | 0.969 | 1.000 | False | insufficient events (7 < 10); descriptive only |
| H100 | 5 | 4 | 2.753 | n/a | 0.500 | 1.000 | False | insufficient events (4 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.733 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 46 | -0.167 | -0.178 | 0.619 | 0.769 | 0.522 | 1.000 | False | 46 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 38 | 0.073 | -0.077 | 0.044 | 0.485 | 0.789 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 8 | 0.883 | 0.014 | n/a | n/a | 1.000 | n/a | False | 8 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 46 | -0.130 | -0.140 | 0.047 | 0.050 | 0.565 | 0.905 | False | 46 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 38 | 0.156 | 0.019 | 0.004 | 0.073 | 0.789 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 8 | 0.918 | 0.308 | n/a | n/a | 1.000 | n/a | False | 8 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 46 | -0.006 | -0.015 | 0.456 | 0.812 | 0.522 | 1.000 | False | 46 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 38 | 0.115 | -0.029 | 0.028 | 0.912 | 0.711 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 8 | 0.888 | 0.058 | n/a | n/a | 1.000 | n/a | False | 8 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 46 | -0.016 | -0.025 | 0.142 | 0.176 | 0.543 | 1.000 | False | 46 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 38 | 0.128 | -0.013 | 0.012 | 0.407 | 0.737 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 8 | 0.888 | 0.052 | n/a | n/a | 1.000 | n/a | False | 8 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 46 | -1.009 | -1.027 | 0.302 | 0.426 | 0.522 | 1.000 | False | 46 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 38 | -25.594 | -29.896 | 0.513 | 0.631 | 0.684 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 8 | -87.464 | -746.121 | n/a | n/a | 0.500 | n/a | False | 8 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 46 | -0.121 | -0.131 | 0.728 | 0.841 | 0.522 | 1.000 | False | 46 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 38 | 0.149 | 0.011 | 0.017 | 0.127 | 0.711 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 8 | 0.882 | 0.000 | n/a | n/a | 1.000 | n/a | False | 8 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 46 | 9 | -1.282 | [-5.39, 3.98] | False | -0.006 | -0.045 | -0.083 | -0.161 | -0.316 |
| level_h100 | 5 | 38 | 31 | 3.308 | [-0.01, 7.88] | False | 2.669 | 2.473 | 2.278 | 1.887 | 1.105 |
| level_h100 | 20 | 8 | 8 | 9.431 | n/a | False | 7.237 | 6.849 | 6.460 | 5.683 | 4.130 |
| level_b200 | 1 | 46 | 7 | 1.835 | [-3.82, 5.77] | False | 0.148 | 0.118 | 0.088 | 0.027 | -0.095 |
| level_b200 | 5 | 38 | 32 | 3.739 | [0.30, 8.96] | True | 2.995 | 2.793 | 2.591 | 2.188 | 1.381 |
| level_b200 | 20 | 8 | 8 | 9.431 | n/a | False | 7.237 | 6.849 | 6.460 | 5.683 | 4.130 |
| disp_h100 | 1 | 46 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 38 | 32 | 2.916 | [-0.35, 7.53] | False | 2.544 | 2.345 | 2.145 | 1.746 | 0.949 |
| disp_h100 | 20 | 8 | 8 | 9.431 | n/a | False | 7.237 | 6.849 | 6.460 | 5.683 | 4.130 |
| disp_b200 | 1 | 46 | 6 | -0.003 | [-4.12, 4.41] | False | 0.051 | 0.026 | -0.000 | -0.051 | -0.154 |
| disp_b200 | 5 | 38 | 31 | 3.619 | [0.24, 8.76] | True | 2.908 | 2.713 | 2.518 | 2.127 | 1.345 |
| disp_b200 | 20 | 8 | 8 | 9.431 | n/a | False | 7.237 | 6.849 | 6.460 | 5.683 | 4.130 |
| avail_h100 | 1 | 46 | 9 | -1.992 | [-4.23, 0.93] | False | -0.078 | -0.117 | -0.155 | -0.232 | -0.387 |
| avail_h100 | 5 | 38 | 32 | 2.248 | [-0.27, 5.23] | False | 2.102 | 1.903 | 1.703 | 1.304 | 0.507 |
| avail_h100 | 20 | 8 | 8 | 0.049 | n/a | False | 0.708 | 0.408 | 0.109 | -0.489 | -1.685 |
| avail_b200 | 1 | 46 | 8 | -2.366 | [-4.67, 0.44] | False | -0.114 | -0.148 | -0.182 | -0.250 | -0.387 |
| avail_b200 | 5 | 38 | 32 | 3.168 | [-0.01, 7.47] | False | 2.679 | 2.479 | 2.278 | 1.877 | 1.074 |
| avail_b200 | 20 | 8 | 8 | 9.431 | n/a | False | 7.237 | 6.849 | 6.460 | 5.683 | 4.130 |

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
| disp_b200|h5 | False | False | True | False | False |
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
| neocloud | level_h100 | 1 | 66 | 29 | 0.184 | 0.085 | [-0.30, 0.30] | 0.460 | 1.000 | 0.500 | False |  |
| neocloud | level_h100 | 5 | 62 | 27 | 0.198 | 0.038 | [-0.26, 0.22] | 0.684 | 1.000 | 0.741 | False |  |
| neocloud | level_h100 | 20 | 47 | 17 | n/a | -0.189 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 66 | 25 | -0.631 | -0.311 | [-0.46, -0.14] | 0.002 | 0.083 | 0.015 | True |  |
| neocloud | level_b200 | 5 | 62 | 25 | -0.823 | -0.176 | [-0.33, -0.01] | 0.023 | 0.380 | 0.185 | False |  |
| neocloud | level_b200 | 20 | 47 | 23 | n/a | -0.286 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 66 | 51 | 0.058 | 0.045 | [-0.14, 0.24] | 0.665 | 1.000 | 0.712 | False |  |
| neocloud | disp_h100 | 5 | 62 | 49 | -0.392 | -0.133 | [-0.40, 0.10] | 0.208 | 0.975 | 0.259 | False |  |
| neocloud | disp_h100 | 20 | 47 | 40 | n/a | -0.127 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 66 | 14 | 0.238 | 0.256 | [-0.08, 0.45] | 0.004 | 0.098 | 0.061 | False |  |
| neocloud | disp_b200 | 5 | 62 | 14 | 0.274 | 0.128 | [-0.13, 0.27] | 0.074 | 0.736 | 0.296 | False |  |
| neocloud | disp_b200 | 20 | 47 | 9 | n/a | 0.228 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 66 | 20 | -0.010 | -0.094 | [-0.31, 0.15] | 0.506 | 1.000 | 0.409 | False |  |
| neocloud | avail_h100 | 5 | 62 | 18 | -0.009 | -0.033 | [-0.17, 0.11] | 0.558 | 1.000 | 0.722 | False |  |
| neocloud | avail_h100 | 20 | 47 | 12 | n/a | -0.039 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 66 | 15 | -0.009 | -0.087 | [-0.30, 0.16] | 0.543 | 1.000 | 0.470 | False |  |
| neocloud | avail_b200 | 5 | 62 | 15 | -0.010 | -0.040 | [-0.18, 0.11] | 0.463 | 1.000 | 0.667 | False |  |
| neocloud | avail_b200 | 20 | 47 | 10 | n/a | -0.048 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 66 | 29 | -0.015 | -0.018 | [-0.35, 0.17] | 0.880 | 1.000 | 0.848 | False |  |
| gpu_semis | level_h100 | 5 | 62 | 27 | 0.276 | 0.113 | [-0.21, 0.29] | 0.102 | 0.742 | 0.519 | False |  |
| gpu_semis | level_h100 | 20 | 47 | 17 | n/a | -0.158 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 66 | 25 | -0.175 | -0.227 | [-0.53, 0.04] | 0.210 | 0.975 | 0.061 | False |  |
| gpu_semis | level_b200 | 5 | 62 | 25 | -0.220 | -0.100 | [-0.28, 0.07] | 0.160 | 0.961 | 0.500 | False |  |
| gpu_semis | level_b200 | 20 | 47 | 23 | n/a | -0.295 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 66 | 51 | 0.043 | 0.088 | [-0.15, 0.35] | 0.496 | 1.000 | 0.485 | False |  |
| gpu_semis | disp_h100 | 5 | 62 | 49 | -0.122 | -0.088 | [-0.35, 0.13] | 0.358 | 1.000 | 0.481 | False |  |
| gpu_semis | disp_h100 | 20 | 47 | 40 | n/a | -0.080 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 66 | 14 | 0.090 | 0.256 | [-0.08, 0.53] | 0.110 | 0.742 | 0.061 | False |  |
| gpu_semis | disp_b200 | 5 | 62 | 14 | 0.070 | 0.070 | [-0.22, 0.26] | 0.482 | 1.000 | 0.667 | False |  |
| gpu_semis | disp_b200 | 20 | 47 | 9 | n/a | 0.242 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 66 | 20 | -0.001 | -0.017 | [-0.24, 0.29] | 0.908 | 1.000 | 0.939 | False |  |
| gpu_semis | avail_h100 | 5 | 62 | 18 | -0.006 | -0.052 | [-0.17, 0.08] | 0.300 | 1.000 | 0.407 | False |  |
| gpu_semis | avail_h100 | 20 | 47 | 12 | n/a | 0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 66 | 15 | -0.000 | -0.003 | [-0.23, 0.31] | 0.986 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 62 | 15 | -0.007 | -0.060 | [-0.18, 0.08] | 0.227 | 0.975 | 0.352 | False |  |
| gpu_semis | avail_b200 | 20 | 47 | 10 | n/a | -0.009 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 66 | 29 | -0.002 | -0.001 | [-0.20, 0.12] | 0.988 | 1.000 | 1.000 | False |  |
| power_capacity | level_h100 | 5 | 62 | 27 | 0.281 | 0.083 | [-0.12, 0.27] | 0.235 | 0.975 | 0.519 | False |  |
| power_capacity | level_h100 | 20 | 47 | 17 | n/a | 0.072 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 66 | 25 | -0.336 | -0.257 | [-0.42, -0.07] | 0.028 | 0.380 | 0.045 | False |  |
| power_capacity | level_b200 | 5 | 62 | 25 | -0.071 | -0.023 | [-0.31, 0.13] | 0.743 | 1.000 | 0.796 | False |  |
| power_capacity | level_b200 | 20 | 47 | 23 | n/a | -0.028 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 66 | 51 | 0.106 | 0.128 | [-0.07, 0.34] | 0.264 | 1.000 | 0.273 | False |  |
| power_capacity | disp_h100 | 5 | 62 | 49 | -0.114 | -0.060 | [-0.33, 0.19] | 0.589 | 1.000 | 0.630 | False |  |
| power_capacity | disp_h100 | 20 | 47 | 40 | n/a | -0.071 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 66 | 14 | 0.100 | 0.167 | [-0.12, 0.32] | 0.082 | 0.736 | 0.197 | False |  |
| power_capacity | disp_b200 | 5 | 62 | 14 | -0.022 | -0.016 | [-0.21, 0.16] | 0.850 | 1.000 | 0.852 | False |  |
| power_capacity | disp_b200 | 20 | 47 | 9 | n/a | 0.015 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 66 | 20 | 0.000 | 0.005 | [-0.17, 0.23] | 0.964 | 1.000 | 0.955 | False |  |
| power_capacity | avail_h100 | 5 | 62 | 18 | -0.007 | -0.044 | [-0.21, 0.14] | 0.508 | 1.000 | 0.370 | False |  |
| power_capacity | avail_h100 | 20 | 47 | 12 | n/a | -0.027 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 66 | 15 | 0.001 | 0.012 | [-0.16, 0.23] | 0.922 | 1.000 | 0.939 | False |  |
| power_capacity | avail_b200 | 5 | 62 | 15 | -0.007 | -0.045 | [-0.20, 0.15] | 0.515 | 1.000 | 0.389 | False |  |
| power_capacity | avail_b200 | 20 | 47 | 10 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.03 [-0.13, 0.21] | -0.02 [-0.22, 0.22] |
| -4 | -0.01 [-0.12, 0.13] | -0.29 [-0.45, -0.10] |
| -3 | -0.09 [-0.23, 0.06] | 0.02 [-0.16, 0.31] |
| -2 | -0.19 [-0.39, 0.06] | -0.18 [-0.34, 0.02] |
| -1 | 0.09 [-0.23, 0.41] | -0.26 [-0.39, -0.10] |
| 0 | -0.30 [-0.49, -0.11] | 0.04 [-0.30, 0.23] |
| 1 | -0.04 [-0.28, 0.24] | -0.03 [-0.35, 0.20] |
| 2 | 0.08 [-0.10, 0.22] | 0.06 [-0.10, 0.33] |
| 3 | 0.02 [-0.21, 0.30] | 0.15 [-0.00, 0.26] |
| 4 | -0.02 [-0.13, 0.05] | 0.18 [-0.24, 0.36] |
| 5 | -0.03 [-0.17, 0.14] | 0.09 [-0.25, 0.28] |

