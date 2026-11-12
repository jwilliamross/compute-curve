# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-12T04:08:04.097532+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `852d15af383b40d5...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 4 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 39 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 59 | 2026-08-20 | 2026-11-11 | 0.36 | 0.47 |
| 5 | 55 | 2026-08-20 | 2026-11-05 | 0.37 | 0.49 |
| 20 | 40 | 2026-08-20 | 2026-10-15 | 0.43 | 0.56 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 59 | 25 | -0.083 | -0.042 | [-0.40, 0.23] | 0.804 | 1.000 | 0.712 | False |  |
| level_h100 | 5 | 55 | 22 | -1.023 | -0.125 | [-0.27, 0.07] | 0.076 | 1.000 | 0.234 | False |  |
| level_h100 | 20 | 40 | 11 | n/a | -0.137 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 59 | 24 | -0.395 | -0.342 | [-0.52, -0.14] | 0.012 | 0.189 | 0.017 | False |  |
| level_b200 | 5 | 55 | 24 | -0.366 | -0.125 | [-0.32, 0.04] | 0.131 | 1.000 | 0.319 | False |  |
| level_b200 | 20 | 40 | 18 | n/a | -0.260 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 59 | 47 | 0.086 | 0.116 | [-0.11, 0.35] | 0.365 | 1.000 | 0.322 | False |  |
| disp_h100 | 5 | 55 | 46 | -0.312 | -0.155 | [-0.47, 0.11] | 0.258 | 1.000 | 0.255 | False |  |
| disp_h100 | 20 | 40 | 34 | n/a | -0.146 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 59 | 13 | 0.163 | 0.301 | [-0.04, 0.49] | 0.003 | 0.046 | 0.034 | True |  |
| disp_b200 | 5 | 55 | 12 | 0.202 | 0.144 | [-0.02, 0.28] | 0.004 | 0.073 | 0.255 | False |  |
| disp_b200 | 20 | 40 | 7 | n/a | 0.206 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 59 | 17 | -0.004 | -0.058 | [-0.29, 0.23] | 0.704 | 1.000 | 0.644 | False |  |
| avail_h100 | 5 | 55 | 17 | -0.008 | -0.048 | [-0.20, 0.10] | 0.415 | 1.000 | 0.511 | False |  |
| avail_h100 | 20 | 40 | 7 | n/a | -0.057 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 59 | 14 | -0.003 | -0.052 | [-0.28, 0.23] | 0.740 | 1.000 | 0.695 | False |  |
| avail_b200 | 5 | 55 | 14 | -0.009 | -0.058 | [-0.21, 0.09] | 0.309 | 1.000 | 0.511 | False |  |
| avail_b200 | 20 | 40 | 5 | n/a | -0.069 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 4 | -0.550 | n/a | 0.875 | 1.000 | False | insufficient events (4 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.734 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 39 | -0.211 | -0.196 | 0.625 | 0.692 | 0.513 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 31 | 0.137 | 0.008 | 0.008 | 0.044 | 0.806 | 0.793 | False | 31 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 1 | n/a | n/a | n/a | n/a | n/a | n/a | False | 1 out-of-sample forecasts |
| level_b200 | 1 | 39 | -0.178 | -0.164 | 0.053 | 0.041 | 0.538 | 0.900 | False | 39 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 31 | 0.149 | 0.022 | 0.003 | 0.071 | 0.806 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 1 | n/a | n/a | n/a | n/a | n/a | n/a | False | 1 out-of-sample forecasts |
| disp_h100 | 1 | 39 | -0.024 | -0.011 | 0.703 | 0.706 | 0.513 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 31 | 0.101 | -0.033 | 0.034 | 0.946 | 0.710 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 1 | n/a | n/a | n/a | n/a | n/a | n/a | False | 1 out-of-sample forecasts |
| disp_b200 | 1 | 39 | -0.016 | -0.003 | 0.137 | 0.121 | 0.538 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 31 | 0.153 | 0.027 | 0.006 | 0.076 | 0.742 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 1 | n/a | n/a | n/a | n/a | n/a | n/a | False | 1 out-of-sample forecasts |
| avail_h100 | 1 | 39 | -1.316 | -1.287 | 0.365 | 0.425 | 0.487 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 31 | -31.477 | -36.310 | 0.535 | 0.631 | 0.677 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 1 | n/a | n/a | n/a | n/a | n/a | n/a | False | 1 out-of-sample forecasts |
| avail_b200 | 1 | 39 | -0.178 | -0.164 | 0.822 | 0.839 | 0.487 | 1.000 | False | 39 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 31 | 0.142 | 0.014 | 0.022 | 0.118 | 0.710 | 1.000 | False | 31 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 1 | n/a | n/a | n/a | n/a | n/a | n/a | False | 1 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 39 | 8 | -0.630 | [-4.50, 5.07] | False | 0.039 | -0.002 | -0.042 | -0.124 | -0.287 |
| level_h100 | 5 | 31 | 24 | 3.290 | [-0.07, 8.14] | False | 2.607 | 2.421 | 2.236 | 1.865 | 1.123 |
| level_h100 | 20 | 1 | 1 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 39 | 7 | 1.992 | [-3.55, 6.26] | False | 0.175 | 0.139 | 0.103 | 0.032 | -0.112 |
| level_b200 | 5 | 31 | 25 | 3.822 | [0.21, 9.81] | True | 3.007 | 2.813 | 2.620 | 2.234 | 1.461 |
| level_b200 | 20 | 1 | 1 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 39 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 31 | 25 | 2.810 | [-1.25, 8.38] | False | 2.454 | 2.263 | 2.073 | 1.692 | 0.931 |
| disp_h100 | 20 | 1 | 1 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 39 | 5 | 1.206 | [-2.88, 4.91] | False | 0.106 | 0.081 | 0.056 | 0.005 | -0.097 |
| disp_b200 | 5 | 31 | 24 | 3.673 | [0.05, 9.36] | True | 2.901 | 2.715 | 2.530 | 2.159 | 1.417 |
| disp_b200 | 20 | 1 | 1 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 39 | 9 | -2.162 | [-4.68, 0.90] | False | -0.092 | -0.138 | -0.183 | -0.274 | -0.456 |
| avail_h100 | 5 | 31 | 25 | 2.007 | [-0.36, 4.64] | False | 1.912 | 1.722 | 1.531 | 1.150 | 0.389 |
| avail_h100 | 20 | 1 | 1 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 39 | 8 | -2.570 | [-5.15, 0.30] | False | -0.134 | -0.174 | -0.215 | -0.295 | -0.457 |
| avail_b200 | 5 | 31 | 25 | 3.116 | [-0.14, 7.41] | False | 2.619 | 2.428 | 2.236 | 1.852 | 1.085 |
| avail_b200 | 20 | 1 | 1 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |

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
| disp_b200|h1 | True | False | False | False | False |
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
| neocloud | level_h100 | 1 | 59 | 25 | -0.042 | -0.013 | [-0.39, 0.28] | 0.938 | 1.000 | 0.949 | False |  |
| neocloud | level_h100 | 5 | 55 | 22 | -2.411 | -0.194 | [-0.32, -0.05] | 0.000 | 0.000 | 0.064 | False |  |
| neocloud | level_h100 | 20 | 40 | 11 | n/a | -0.191 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 59 | 24 | -0.653 | -0.355 | [-0.50, -0.19] | 0.001 | 0.009 | 0.017 | True |  |
| neocloud | level_b200 | 5 | 55 | 24 | -0.860 | -0.194 | [-0.34, -0.04] | 0.014 | 0.122 | 0.149 | False |  |
| neocloud | level_b200 | 20 | 40 | 18 | n/a | -0.288 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 59 | 47 | 0.094 | 0.080 | [-0.13, 0.29] | 0.501 | 1.000 | 0.475 | False |  |
| neocloud | disp_h100 | 5 | 55 | 46 | -0.432 | -0.142 | [-0.45, 0.11] | 0.276 | 0.932 | 0.404 | False |  |
| neocloud | disp_h100 | 20 | 40 | 34 | n/a | -0.149 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 59 | 13 | 0.282 | 0.327 | [0.02, 0.49] | 0.000 | 0.000 | 0.034 | True |  |
| neocloud | disp_b200 | 5 | 55 | 12 | 0.399 | 0.187 | [0.04, 0.31] | 0.000 | 0.000 | 0.170 | False |  |
| neocloud | disp_b200 | 20 | 40 | 7 | n/a | 0.231 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 59 | 17 | -0.011 | -0.105 | [-0.36, 0.18] | 0.504 | 1.000 | 0.373 | False |  |
| neocloud | avail_h100 | 5 | 55 | 17 | -0.009 | -0.038 | [-0.19, 0.11] | 0.539 | 1.000 | 0.702 | False |  |
| neocloud | avail_h100 | 20 | 40 | 7 | n/a | -0.083 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 59 | 14 | -0.010 | -0.103 | [-0.36, 0.18] | 0.521 | 1.000 | 0.424 | False |  |
| neocloud | avail_b200 | 5 | 55 | 14 | -0.012 | -0.050 | [-0.20, 0.09] | 0.396 | 1.000 | 0.596 | False |  |
| neocloud | avail_b200 | 20 | 40 | 5 | n/a | -0.096 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 59 | 25 | -0.085 | -0.068 | [-0.47, 0.24] | 0.717 | 1.000 | 0.593 | False |  |
| gpu_semis | level_h100 | 5 | 55 | 22 | -0.491 | -0.086 | [-0.27, 0.18] | 0.406 | 1.000 | 0.511 | False |  |
| gpu_semis | level_h100 | 20 | 40 | 11 | n/a | -0.168 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 59 | 24 | -0.185 | -0.257 | [-0.57, 0.03] | 0.179 | 0.818 | 0.051 | False |  |
| gpu_semis | level_b200 | 5 | 55 | 24 | -0.200 | -0.097 | [-0.29, 0.08] | 0.224 | 0.929 | 0.532 | False |  |
| gpu_semis | level_b200 | 20 | 40 | 18 | n/a | -0.304 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 59 | 47 | 0.049 | 0.105 | [-0.17, 0.37] | 0.470 | 1.000 | 0.322 | False |  |
| gpu_semis | disp_h100 | 5 | 55 | 46 | -0.244 | -0.174 | [-0.44, 0.06] | 0.164 | 0.818 | 0.255 | False |  |
| gpu_semis | disp_h100 | 20 | 40 | 34 | n/a | -0.090 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 59 | 13 | 0.099 | 0.292 | [-0.09, 0.56] | 0.075 | 0.452 | 0.017 | False |  |
| gpu_semis | disp_b200 | 5 | 55 | 12 | 0.161 | 0.163 | [-0.02, 0.31] | 0.001 | 0.012 | 0.213 | False |  |
| gpu_semis | disp_b200 | 20 | 40 | 7 | n/a | 0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 59 | 17 | -0.001 | -0.018 | [-0.28, 0.32] | 0.908 | 1.000 | 0.949 | False |  |
| gpu_semis | avail_h100 | 5 | 55 | 17 | -0.006 | -0.058 | [-0.19, 0.08] | 0.276 | 0.932 | 0.426 | False |  |
| gpu_semis | avail_h100 | 20 | 40 | 7 | n/a | -0.030 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 59 | 14 | -0.000 | -0.005 | [-0.28, 0.33] | 0.977 | 1.000 | 0.983 | False |  |
| gpu_semis | avail_b200 | 5 | 55 | 14 | -0.008 | -0.071 | [-0.20, 0.06] | 0.182 | 0.818 | 0.362 | False |  |
| gpu_semis | avail_b200 | 20 | 40 | 5 | n/a | -0.049 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 59 | 25 | -0.122 | -0.056 | [-0.28, 0.12] | 0.625 | 1.000 | 0.576 | False |  |
| power_capacity | level_h100 | 5 | 55 | 22 | -0.168 | -0.021 | [-0.19, 0.21] | 0.801 | 1.000 | 0.851 | False |  |
| power_capacity | level_h100 | 20 | 40 | 11 | n/a | 0.093 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 59 | 24 | -0.347 | -0.274 | [-0.43, -0.09] | 0.024 | 0.184 | 0.051 | False |  |
| power_capacity | level_b200 | 5 | 55 | 24 | -0.037 | -0.013 | [-0.30, 0.16] | 0.873 | 1.000 | 0.851 | False |  |
| power_capacity | level_b200 | 20 | 40 | 18 | n/a | -0.033 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 59 | 47 | 0.116 | 0.143 | [-0.08, 0.37] | 0.246 | 0.932 | 0.288 | False |  |
| power_capacity | disp_h100 | 5 | 55 | 46 | -0.258 | -0.131 | [-0.44, 0.16] | 0.370 | 1.000 | 0.298 | False |  |
| power_capacity | disp_h100 | 20 | 40 | 34 | n/a | -0.169 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 59 | 13 | 0.110 | 0.185 | [-0.13, 0.33] | 0.053 | 0.358 | 0.203 | False |  |
| power_capacity | disp_b200 | 5 | 55 | 12 | 0.047 | 0.034 | [-0.14, 0.21] | 0.614 | 1.000 | 0.723 | False |  |
| power_capacity | disp_b200 | 20 | 40 | 7 | n/a | 0.005 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 59 | 17 | 0.000 | 0.004 | [-0.18, 0.24] | 0.973 | 1.000 | 0.966 | False |  |
| power_capacity | avail_h100 | 5 | 55 | 17 | -0.007 | -0.047 | [-0.22, 0.16] | 0.501 | 1.000 | 0.447 | False |  |
| power_capacity | avail_h100 | 20 | 40 | 7 | n/a | -0.007 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 59 | 14 | 0.001 | 0.011 | [-0.18, 0.24] | 0.932 | 1.000 | 0.966 | False |  |
| power_capacity | avail_b200 | 5 | 55 | 14 | -0.008 | -0.049 | [-0.23, 0.17] | 0.498 | 1.000 | 0.447 | False |  |
| power_capacity | avail_b200 | 20 | 40 | 5 | n/a | -0.004 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.16, 0.22] | -0.04 [-0.26, 0.21] |
| -4 | -0.03 [-0.15, 0.10] | -0.34 [-0.51, -0.11] |
| -3 | -0.12 [-0.26, 0.04] | 0.18 [-0.17, 0.43] |
| -2 | -0.23 [-0.42, 0.01] | -0.06 [-0.34, 0.25] |
| -1 | 0.08 [-0.27, 0.42] | -0.17 [-0.34, 0.03] |
| 0 | -0.34 [-0.52, -0.14] | -0.04 [-0.40, 0.23] |
| 1 | -0.06 [-0.30, 0.24] | -0.07 [-0.39, 0.24] |
| 2 | 0.07 [-0.23, 0.23] | 0.15 [-0.14, 0.40] |
| 3 | 0.01 [-0.25, 0.31] | 0.14 [-0.05, 0.31] |
| 4 | -0.03 [-0.14, 0.06] | -0.15 [-0.37, -0.03] |
| 5 | -0.03 [-0.19, 0.16] | -0.02 [-0.24, 0.20] |

