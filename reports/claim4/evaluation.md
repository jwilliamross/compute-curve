# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-28T02:36:30.704060+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `8a190c0dc4d5c798...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 28 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 48 | 2026-08-20 | 2026-10-27 | 0.39 | 0.52 |
| 5 | 44 | 2026-08-20 | 2026-10-21 | 0.41 | 0.54 |
| 20 | 29 | 2026-08-20 | 2026-09-30 | 0.50 | 0.64 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 48 | 17 | -0.983 | -0.310 | [-0.52, 0.05] | 0.006 | 0.100 | 0.021 | False |  |
| level_h100 | 5 | 44 | 14 | -1.071 | -0.131 | [-0.31, 0.19] | 0.140 | 1.000 | 0.417 | False |  |
| level_h100 | 20 | 29 | 3 | n/a | -0.072 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 48 | 23 | -0.345 | -0.296 | [-0.54, -0.11] | 0.074 | 1.000 | 0.042 | False |  |
| level_b200 | 5 | 44 | 22 | -0.559 | -0.186 | [-0.44, -0.03] | 0.086 | 1.000 | 0.333 | False |  |
| level_b200 | 20 | 29 | 10 | n/a | -0.239 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 48 | 40 | 0.002 | 0.002 | [-0.18, 0.22] | 0.985 | 1.000 | 1.000 | False |  |
| disp_h100 | 5 | 44 | 37 | -0.113 | -0.048 | [-0.31, 0.17] | 0.623 | 1.000 | 0.750 | False |  |
| disp_h100 | 20 | 29 | 23 | n/a | -0.115 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 48 | 10 | 0.171 | 0.330 | [0.01, 0.51] | 0.001 | 0.015 | 0.021 | True |  |
| disp_b200 | 5 | 44 | 7 | 0.244 | 0.184 | [0.03, 0.34] | 0.000 | 0.002 | 0.278 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 29 | 3 | n/a | 0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 48 | 12 | -0.008 | -0.130 | [-0.36, 0.25] | 0.411 | 1.000 | 0.396 | False |  |
| avail_h100 | 5 | 44 | 11 | -0.009 | -0.054 | [-0.31, 0.14] | 0.468 | 1.000 | 0.333 | False |  |
| avail_h100 | 20 | 29 | 2 | n/a | -0.157 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 48 | 10 | -0.008 | -0.132 | [-0.36, 0.24] | 0.401 | 1.000 | 0.375 | False |  |
| avail_b200 | 5 | 44 | 9 | -0.009 | -0.050 | [-0.24, 0.14] | 0.484 | 1.000 | 0.361 | False | insufficient variation (9 non-zero < 10) |
| avail_b200 | 20 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 28 | -0.014 | -0.013 | 0.064 | 0.033 | 0.571 | 0.962 | False | 28 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 20 | 0.234 | 0.010 | 0.001 | 0.050 | 0.900 | 0.796 | False | 20 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 28 | -0.378 | -0.377 | 0.103 | 0.102 | 0.607 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 20 | 0.295 | 0.088 | 0.000 | 0.012 | 0.900 | 0.221 | False | 20 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 28 | -0.026 | -0.025 | 0.704 | 0.929 | 0.536 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 20 | 0.201 | -0.033 | 0.014 | 1.000 | 0.750 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 28 | -0.019 | -0.018 | 0.097 | 0.094 | 0.607 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 20 | 0.279 | 0.068 | 0.001 | 0.023 | 0.800 | 0.391 | False | 20 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 28 | -2.007 | -2.003 | 0.275 | 0.351 | 0.607 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 20 | -48.112 | -62.481 | 0.547 | 0.635 | 0.700 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 28 | -0.212 | -0.211 | 0.714 | 0.761 | 0.607 | 1.000 | False | 28 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 20 | 0.233 | 0.009 | 0.019 | 0.146 | 0.750 | 1.000 | False | 20 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 28 | 3 | 4.672 | [0.00, 7.46] | False | 0.178 | 0.157 | 0.135 | 0.093 | 0.007 |
| level_h100 | 5 | 20 | 14 | 7.054 | [3.81, 11.57] | True | 3.916 | 3.748 | 3.580 | 3.245 | 2.574 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 28 | 6 | 0.496 | [-6.47, 7.06] | False | 0.109 | 0.066 | 0.023 | -0.063 | -0.234 |
| level_b200 | 5 | 20 | 14 | 7.898 | [4.03, 16.37] | True | 4.297 | 4.129 | 3.962 | 3.626 | 2.955 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 28 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 20 | 14 | 4.855 | [-0.42, 13.78] | False | 3.440 | 3.277 | 3.114 | 2.787 | 2.134 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 28 | 3 | 3.662 | [-3.00, 5.89] | False | 0.097 | 0.076 | 0.055 | 0.012 | -0.072 |
| disp_b200 | 5 | 20 | 13 | 7.406 | [3.59, 15.19] | True | 4.133 | 3.977 | 3.821 | 3.510 | 2.887 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 28 | 6 | -2.144 | [-4.77, 5.33] | False | -0.073 | -0.115 | -0.157 | -0.242 | -0.410 |
| avail_h100 | 5 | 20 | 14 | 3.209 | [1.82, 5.96] | True | 2.600 | 2.437 | 2.274 | 1.947 | 1.294 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 28 | 5 | -2.817 | [-5.59, 4.13] | False | -0.131 | -0.166 | -0.201 | -0.271 | -0.411 |
| avail_b200 | 5 | 20 | 14 | 5.661 | [2.36, 12.52] | True | 3.697 | 3.531 | 3.366 | 3.035 | 2.373 |
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
| neocloud | level_h100 | 1 | 48 | 17 | -1.564 | -0.310 | [-0.50, 0.08] | 0.003 | 0.035 | 0.062 | False |  |
| neocloud | level_h100 | 5 | 44 | 14 | -2.516 | -0.200 | [-0.36, 0.01] | 0.000 | 0.003 | 0.250 | False |  |
| neocloud | level_h100 | 20 | 29 | 3 | n/a | -0.119 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 48 | 23 | -0.632 | -0.340 | [-0.52, -0.14] | 0.014 | 0.106 | 0.021 | False |  |
| neocloud | level_b200 | 5 | 44 | 22 | -1.134 | -0.245 | [-0.45, -0.08] | 0.016 | 0.107 | 0.250 | False |  |
| neocloud | level_b200 | 20 | 29 | 10 | n/a | -0.282 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 48 | 40 | -0.047 | -0.034 | [-0.21, 0.17] | 0.746 | 1.000 | 0.812 | False |  |
| neocloud | disp_h100 | 5 | 44 | 37 | -0.188 | -0.052 | [-0.31, 0.16] | 0.586 | 1.000 | 0.750 | False |  |
| neocloud | disp_h100 | 20 | 29 | 23 | n/a | -0.114 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 48 | 10 | 0.299 | 0.363 | [0.04, 0.52] | 0.000 | 0.000 | 0.021 | True |  |
| neocloud | disp_b200 | 5 | 44 | 7 | 0.441 | 0.215 | [0.04, 0.38] | 0.000 | 0.000 | 0.194 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 29 | 3 | n/a | 0.153 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 48 | 12 | -0.022 | -0.218 | [-0.44, 0.14] | 0.138 | 0.496 | 0.146 | False |  |
| neocloud | avail_h100 | 5 | 44 | 11 | -0.015 | -0.056 | [-0.32, 0.11] | 0.435 | 1.000 | 0.306 | False |  |
| neocloud | avail_h100 | 20 | 29 | 2 | n/a | -0.188 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 48 | 10 | -0.023 | -0.227 | [-0.44, 0.13] | 0.123 | 0.473 | 0.125 | False |  |
| neocloud | avail_b200 | 5 | 44 | 9 | -0.015 | -0.058 | [-0.25, 0.11] | 0.399 | 1.000 | 0.361 | False | insufficient variation (9 non-zero < 10) |
| neocloud | avail_b200 | 20 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 48 | 17 | -0.684 | -0.347 | [-0.62, 0.03] | 0.012 | 0.106 | 0.042 | False |  |
| gpu_semis | level_h100 | 5 | 44 | 14 | -0.529 | -0.099 | [-0.32, 0.26] | 0.391 | 1.000 | 0.583 | False |  |
| gpu_semis | level_h100 | 20 | 29 | 3 | n/a | -0.116 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 48 | 23 | -0.155 | -0.213 | [-0.64, 0.08] | 0.359 | 1.000 | 0.167 | False |  |
| gpu_semis | level_b200 | 5 | 44 | 22 | -0.346 | -0.176 | [-0.42, 0.03] | 0.058 | 0.283 | 0.389 | False |  |
| gpu_semis | level_b200 | 20 | 29 | 10 | n/a | -0.271 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 48 | 40 | -0.002 | -0.004 | [-0.24, 0.19] | 0.976 | 1.000 | 0.979 | False |  |
| gpu_semis | disp_h100 | 5 | 44 | 37 | -0.067 | -0.044 | [-0.27, 0.17] | 0.653 | 1.000 | 0.833 | False |  |
| gpu_semis | disp_h100 | 20 | 29 | 23 | n/a | -0.047 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 48 | 10 | 0.106 | 0.329 | [-0.08, 0.63] | 0.085 | 0.382 | 0.021 | False |  |
| gpu_semis | disp_b200 | 5 | 44 | 7 | 0.191 | 0.220 | [0.05, 0.39] | 0.000 | 0.001 | 0.250 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 29 | 3 | n/a | 0.138 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 48 | 12 | 0.000 | 0.012 | [-0.29, 0.41] | 0.946 | 1.000 | 0.917 | False |  |
| gpu_semis | avail_h100 | 5 | 44 | 11 | -0.006 | -0.056 | [-0.28, 0.11] | 0.427 | 1.000 | 0.333 | False |  |
| gpu_semis | avail_h100 | 20 | 29 | 2 | n/a | -0.057 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 48 | 10 | 0.001 | 0.019 | [-0.28, 0.42] | 0.913 | 1.000 | 0.917 | False |  |
| gpu_semis | avail_b200 | 5 | 44 | 9 | -0.006 | -0.056 | [-0.24, 0.11] | 0.420 | 1.000 | 0.389 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 48 | 17 | -0.703 | -0.204 | [-0.36, 0.10] | 0.025 | 0.142 | 0.188 | False |  |
| power_capacity | level_h100 | 5 | 44 | 14 | -0.169 | -0.021 | [-0.24, 0.38] | 0.859 | 1.000 | 0.889 | False |  |
| power_capacity | level_h100 | 20 | 29 | 3 | n/a | 0.126 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 48 | 23 | -0.249 | -0.196 | [-0.39, -0.05] | 0.115 | 0.473 | 0.146 | False |  |
| power_capacity | level_b200 | 5 | 44 | 22 | -0.197 | -0.068 | [-0.39, 0.17] | 0.556 | 1.000 | 0.611 | False |  |
| power_capacity | level_b200 | 20 | 29 | 10 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 48 | 40 | 0.054 | 0.059 | [-0.15, 0.31] | 0.680 | 1.000 | 0.708 | False |  |
| power_capacity | disp_h100 | 5 | 44 | 37 | -0.084 | -0.037 | [-0.33, 0.22] | 0.738 | 1.000 | 0.806 | False |  |
| power_capacity | disp_h100 | 20 | 29 | 23 | n/a | -0.181 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 48 | 10 | 0.108 | 0.192 | [-0.14, 0.34] | 0.026 | 0.142 | 0.167 | False |  |
| power_capacity | disp_b200 | 5 | 44 | 7 | 0.101 | 0.078 | [-0.13, 0.24] | 0.271 | 0.915 | 0.528 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 29 | 3 | n/a | -0.061 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 48 | 12 | -0.003 | -0.046 | [-0.25, 0.26] | 0.732 | 1.000 | 0.729 | False |  |
| power_capacity | avail_h100 | 5 | 44 | 11 | -0.007 | -0.040 | [-0.28, 0.22] | 0.634 | 1.000 | 0.444 | False |  |
| power_capacity | avail_h100 | 20 | 29 | 2 | n/a | -0.171 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 48 | 10 | -0.003 | -0.044 | [-0.23, 0.25] | 0.745 | 1.000 | 0.729 | False |  |
| power_capacity | avail_b200 | 5 | 44 | 9 | -0.004 | -0.025 | [-0.23, 0.24] | 0.776 | 1.000 | 0.611 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 29 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.21, 0.19] | 0.12 [-0.13, 0.26] |
| -4 | -0.02 [-0.19, 0.16] | -0.15 [-0.31, 0.08] |
| -3 | -0.17 [-0.32, 0.00] | -0.14 [-0.33, 0.02] |
| -2 | -0.15 [-0.38, 0.13] | -0.13 [-0.33, 0.21] |
| -1 | -0.08 [-0.33, 0.15] | -0.29 [-0.41, -0.02] |
| 0 | -0.30 [-0.54, -0.11] | -0.31 [-0.52, 0.05] |
| 1 | 0.05 [-0.24, 0.36] | -0.05 [-0.23, 0.34] |
| 2 | 0.02 [-0.37, 0.24] | 0.03 [-0.26, 0.29] |
| 3 | -0.10 [-0.34, 0.35] | 0.07 [-0.25, 0.25] |
| 4 | -0.07 [-0.29, 0.00] | -0.10 [-0.49, 0.00] |
| 5 | -0.13 [-0.30, 0.02] | -0.07 [-0.33, 0.27] |

