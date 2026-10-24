# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-24T01:57:18.255412+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `ea877f05932b5a21...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 26 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 0 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 46 | 2026-08-20 | 2026-10-23 | 0.40 | 0.53 |
| 5 | 42 | 2026-08-20 | 2026-10-19 | 0.42 | 0.55 |
| 20 | 27 | 2026-08-20 | 2026-09-28 | 0.52 | 0.65 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 46 | 16 | -0.970 | -0.319 | [-0.54, 0.10] | 0.012 | 0.186 | 0.065 | False |  |
| level_h100 | 5 | 42 | 13 | -1.091 | -0.134 | [-0.31, 0.19] | 0.123 | 1.000 | 0.382 | False |  |
| level_h100 | 20 | 27 | 3 | n/a | -0.064 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 46 | 23 | -0.333 | -0.298 | [-0.55, -0.09] | 0.090 | 1.000 | 0.065 | False |  |
| level_b200 | 5 | 42 | 20 | -0.562 | -0.188 | [-0.43, -0.03] | 0.080 | 1.000 | 0.324 | False |  |
| level_b200 | 20 | 27 | 10 | n/a | -0.255 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 46 | 39 | 0.002 | 0.002 | [-0.19, 0.20] | 0.987 | 1.000 | 1.000 | False |  |
| disp_h100 | 5 | 42 | 35 | -0.102 | -0.044 | [-0.29, 0.16] | 0.658 | 1.000 | 0.676 | False |  |
| disp_h100 | 20 | 27 | 22 | n/a | -0.109 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 46 | 8 | 0.167 | 0.337 | [-0.09, 0.53] | 0.003 | 0.043 | 0.043 | False | insufficient variation (8 non-zero < 10) |
| disp_b200 | 5 | 42 | 7 | 0.243 | 0.184 | [0.02, 0.34] | 0.000 | 0.002 | 0.206 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 27 | 2 | n/a | 0.103 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 46 | 13 | -0.005 | -0.079 | [-0.34, 0.29] | 0.648 | 1.000 | 0.587 | False |  |
| avail_h100 | 5 | 42 | 9 | -0.014 | -0.074 | [-0.35, 0.16] | 0.378 | 1.000 | 0.206 | False | insufficient variation (9 non-zero < 10) |
| avail_h100 | 20 | 27 | 2 | n/a | -0.170 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 46 | 11 | -0.005 | -0.081 | [-0.34, 0.28] | 0.639 | 1.000 | 0.609 | False |  |
| avail_b200 | 5 | 42 | 7 | -0.014 | -0.069 | [-0.26, 0.16] | 0.390 | 1.000 | 0.324 | False | insufficient variation (7 non-zero < 10) |
| avail_b200 | 20 | 27 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 26 | 0.009 | -0.021 | 0.023 | 0.042 | 0.615 | 0.624 | False | 26 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 18 | 0.206 | 0.012 | 0.002 | 0.038 | 0.889 | 0.604 | False | 18 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 26 | -0.409 | -0.451 | 0.088 | 0.111 | 0.654 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 18 | 0.270 | 0.092 | 0.001 | 0.007 | 0.889 | 0.127 | False | 18 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 26 | 0.001 | -0.029 | 0.364 | 0.930 | 0.577 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 18 | 0.170 | -0.033 | 0.027 | 1.000 | 0.722 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 26 | -0.001 | -0.031 | 0.067 | 0.110 | 0.654 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 18 | 0.253 | 0.069 | 0.003 | 0.017 | 0.778 | 0.287 | False | 18 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 26 | -2.271 | -2.370 | 0.274 | 0.405 | 0.577 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 18 | -51.218 | -64.016 | 0.557 | 0.635 | 0.667 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 26 | -0.242 | -0.279 | 0.724 | 0.832 | 0.577 | 1.000 | False | 26 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 18 | 0.208 | 0.014 | 0.035 | 0.135 | 0.722 | 1.000 | False | 18 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 26 | 3 | 4.859 | [0.00, 7.50] | False | 0.192 | 0.169 | 0.146 | 0.100 | 0.007 |
| level_h100 | 5 | 18 | 12 | 6.582 | [3.34, 11.45] | True | 3.844 | 3.684 | 3.524 | 3.205 | 2.566 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 26 | 6 | 0.515 | [-6.41, 7.36] | False | 0.117 | 0.071 | 0.025 | -0.067 | -0.252 |
| level_b200 | 5 | 18 | 12 | 7.453 | [3.51, 16.14] | True | 4.267 | 4.107 | 3.948 | 3.628 | 2.989 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 26 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 18 | 12 | 4.448 | [-0.87, 14.57] | False | 3.315 | 3.160 | 3.006 | 2.696 | 2.077 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 26 | 3 | 3.803 | [-3.11, 6.11] | False | 0.104 | 0.082 | 0.059 | 0.013 | -0.078 |
| disp_b200 | 5 | 18 | 11 | 6.961 | [3.02, 15.07] | True | 4.085 | 3.938 | 3.792 | 3.499 | 2.913 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 26 | 7 | -1.582 | [-4.79, 7.49] | False | -0.017 | -0.070 | -0.123 | -0.230 | -0.442 |
| avail_h100 | 5 | 18 | 12 | 2.789 | [0.89, 6.34] | True | 2.382 | 2.227 | 2.072 | 1.763 | 1.144 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 26 | 6 | -2.241 | [-5.44, 6.54] | False | -0.080 | -0.125 | -0.170 | -0.261 | -0.443 |
| avail_b200 | 5 | 18 | 12 | 5.240 | [1.26, 14.02] | True | 3.600 | 3.443 | 3.286 | 2.971 | 2.342 |
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
| neocloud | level_h100 | 1 | 46 | 16 | -1.539 | -0.324 | [-0.53, 0.16] | 0.007 | 0.079 | 0.065 | False |  |
| neocloud | level_h100 | 5 | 42 | 13 | -2.540 | -0.202 | [-0.36, 0.01] | 0.000 | 0.002 | 0.235 | False |  |
| neocloud | level_h100 | 20 | 27 | 3 | n/a | -0.114 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 46 | 23 | -0.610 | -0.349 | [-0.54, -0.10] | 0.020 | 0.136 | 0.022 | False |  |
| neocloud | level_b200 | 5 | 42 | 20 | -1.139 | -0.247 | [-0.45, -0.09] | 0.014 | 0.111 | 0.206 | False |  |
| neocloud | level_b200 | 20 | 27 | 10 | n/a | -0.302 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 46 | 39 | -0.047 | -0.037 | [-0.22, 0.16] | 0.737 | 1.000 | 0.761 | False |  |
| neocloud | disp_h100 | 5 | 42 | 35 | -0.172 | -0.048 | [-0.30, 0.15] | 0.621 | 1.000 | 0.618 | False |  |
| neocloud | disp_h100 | 20 | 27 | 22 | n/a | -0.109 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 46 | 8 | 0.292 | 0.377 | [-0.07, 0.55] | 0.000 | 0.000 | 0.043 | False | insufficient variation (8 non-zero < 10) |
| neocloud | disp_b200 | 5 | 42 | 7 | 0.440 | 0.215 | [0.04, 0.38] | 0.000 | 0.000 | 0.176 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 27 | 2 | n/a | 0.149 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 46 | 13 | -0.017 | -0.188 | [-0.42, 0.15] | 0.244 | 0.770 | 0.196 | False |  |
| neocloud | avail_h100 | 5 | 42 | 9 | -0.027 | -0.090 | [-0.38, 0.11] | 0.223 | 0.754 | 0.147 | False | insufficient variation (9 non-zero < 10) |
| neocloud | avail_h100 | 20 | 27 | 2 | n/a | -0.204 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 46 | 11 | -0.018 | -0.197 | [-0.43, 0.14] | 0.223 | 0.754 | 0.174 | False |  |
| neocloud | avail_b200 | 5 | 42 | 7 | -0.028 | -0.093 | [-0.28, 0.10] | 0.186 | 0.717 | 0.235 | False | insufficient variation (7 non-zero < 10) |
| neocloud | avail_b200 | 20 | 27 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 46 | 16 | -0.686 | -0.358 | [-0.65, 0.04] | 0.014 | 0.111 | 0.022 | False |  |
| gpu_semis | level_h100 | 5 | 42 | 13 | -0.535 | -0.100 | [-0.31, 0.27] | 0.384 | 1.000 | 0.529 | False |  |
| gpu_semis | level_h100 | 20 | 27 | 3 | n/a | -0.111 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 46 | 23 | -0.151 | -0.214 | [-0.65, 0.09] | 0.375 | 1.000 | 0.196 | False |  |
| gpu_semis | level_b200 | 5 | 42 | 20 | -0.347 | -0.177 | [-0.42, 0.02] | 0.056 | 0.274 | 0.382 | False |  |
| gpu_semis | level_b200 | 20 | 27 | 10 | n/a | -0.291 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 46 | 39 | -0.001 | -0.003 | [-0.25, 0.21] | 0.983 | 1.000 | 1.000 | False |  |
| gpu_semis | disp_h100 | 5 | 42 | 35 | -0.065 | -0.042 | [-0.26, 0.14] | 0.663 | 1.000 | 0.647 | False |  |
| gpu_semis | disp_h100 | 20 | 27 | 22 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 46 | 8 | 0.105 | 0.337 | [-0.09, 0.64] | 0.091 | 0.412 | 0.022 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 42 | 7 | 0.191 | 0.220 | [0.03, 0.38] | 0.000 | 0.001 | 0.206 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 27 | 2 | n/a | 0.133 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 46 | 13 | 0.001 | 0.040 | [-0.26, 0.44] | 0.820 | 1.000 | 0.761 | False |  |
| gpu_semis | avail_h100 | 5 | 42 | 9 | -0.008 | -0.063 | [-0.31, 0.13] | 0.436 | 1.000 | 0.324 | False | insufficient variation (9 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 27 | 2 | n/a | -0.061 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 46 | 11 | 0.002 | 0.048 | [-0.25, 0.44] | 0.788 | 1.000 | 0.739 | False |  |
| gpu_semis | avail_b200 | 5 | 42 | 7 | -0.008 | -0.063 | [-0.26, 0.14] | 0.429 | 1.000 | 0.382 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 27 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 46 | 16 | -0.685 | -0.202 | [-0.36, 0.13] | 0.041 | 0.248 | 0.174 | False |  |
| power_capacity | level_h100 | 5 | 42 | 13 | -0.198 | -0.025 | [-0.24, 0.37] | 0.830 | 1.000 | 0.794 | False |  |
| power_capacity | level_h100 | 20 | 27 | 3 | n/a | 0.141 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 46 | 23 | -0.240 | -0.192 | [-0.39, -0.03] | 0.137 | 0.568 | 0.261 | False |  |
| power_capacity | level_b200 | 5 | 42 | 20 | -0.202 | -0.070 | [-0.40, 0.18] | 0.539 | 1.000 | 0.559 | False |  |
| power_capacity | level_b200 | 20 | 27 | 10 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 46 | 39 | 0.053 | 0.059 | [-0.16, 0.29] | 0.680 | 1.000 | 0.565 | False |  |
| power_capacity | disp_h100 | 5 | 42 | 35 | -0.071 | -0.031 | [-0.31, 0.22] | 0.779 | 1.000 | 0.794 | False |  |
| power_capacity | disp_h100 | 20 | 27 | 22 | n/a | -0.178 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 46 | 8 | 0.104 | 0.188 | [-0.19, 0.35] | 0.047 | 0.256 | 0.283 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 42 | 7 | 0.100 | 0.078 | [-0.13, 0.25] | 0.257 | 0.770 | 0.529 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 27 | 2 | n/a | -0.076 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 46 | 13 | 0.002 | 0.030 | [-0.22, 0.31] | 0.847 | 1.000 | 0.870 | False |  |
| power_capacity | avail_h100 | 5 | 42 | 9 | -0.008 | -0.041 | [-0.31, 0.26] | 0.672 | 1.000 | 0.412 | False | insufficient variation (9 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 27 | 2 | n/a | -0.178 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 46 | 11 | 0.002 | 0.032 | [-0.19, 0.31] | 0.834 | 1.000 | 0.891 | False |  |
| power_capacity | avail_b200 | 5 | 42 | 7 | -0.005 | -0.025 | [-0.25, 0.28] | 0.809 | 1.000 | 0.588 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 27 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.04 [-0.22, 0.21] | 0.12 [-0.15, 0.27] |
| -4 | -0.01 [-0.19, 0.19] | -0.16 [-0.31, 0.08] |
| -3 | -0.17 [-0.31, 0.06] | -0.15 [-0.35, 0.00] |
| -2 | -0.14 [-0.38, 0.23] | -0.14 [-0.35, 0.24] |
| -1 | -0.07 [-0.34, 0.18] | -0.29 [-0.42, -0.01] |
| 0 | -0.30 [-0.55, -0.09] | -0.32 [-0.54, 0.10] |
| 1 | 0.06 [-0.25, 0.42] | -0.03 [-0.24, 0.42] |
| 2 | 0.03 [-0.37, 0.24] | 0.03 [-0.28, 0.28] |
| 3 | -0.10 [-0.34, 0.36] | 0.08 [-0.22, 0.27] |
| 4 | -0.07 [-0.30, 0.01] | -0.09 [-0.47, 0.02] |
| 5 | -0.13 [-0.33, 0.00] | -0.07 [-0.34, 0.27] |

