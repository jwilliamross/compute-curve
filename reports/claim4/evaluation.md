# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-20T04:16:27.250040+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `9184ac85fcaaf018...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 6 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 45 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 65 | 2026-08-20 | 2026-11-19 | 0.34 | 0.45 |
| 5 | 61 | 2026-08-20 | 2026-11-13 | 0.35 | 0.46 |
| 20 | 46 | 2026-08-20 | 2026-10-23 | 0.40 | 0.53 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 65 | 28 | -0.003 | -0.002 | [-0.41, 0.22] | 0.985 | 1.000 | 1.000 | False |  |
| level_h100 | 5 | 61 | 27 | 0.251 | 0.074 | [-0.20, 0.24] | 0.311 | 1.000 | 0.491 | False |  |
| level_h100 | 20 | 46 | 16 | n/a | -0.135 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 65 | 25 | -0.388 | -0.318 | [-0.50, -0.12] | 0.014 | 0.260 | 0.015 | False |  |
| level_b200 | 5 | 61 | 25 | -0.385 | -0.127 | [-0.31, 0.03] | 0.102 | 1.000 | 0.377 | False |  |
| level_b200 | 20 | 46 | 23 | n/a | -0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 65 | 50 | 0.058 | 0.076 | [-0.14, 0.31] | 0.523 | 1.000 | 0.446 | False |  |
| disp_h100 | 5 | 61 | 48 | -0.250 | -0.129 | [-0.40, 0.10] | 0.221 | 1.000 | 0.132 | False |  |
| disp_h100 | 20 | 46 | 39 | n/a | -0.113 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 65 | 14 | 0.143 | 0.256 | [-0.08, 0.46] | 0.018 | 0.298 | 0.031 | False |  |
| disp_b200 | 5 | 61 | 14 | 0.108 | 0.077 | [-0.19, 0.24] | 0.353 | 1.000 | 0.566 | False |  |
| disp_b200 | 20 | 46 | 8 | n/a | 0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 65 | 19 | -0.004 | -0.057 | [-0.27, 0.21] | 0.692 | 1.000 | 0.615 | False |  |
| avail_h100 | 5 | 61 | 18 | -0.007 | -0.044 | [-0.19, 0.11] | 0.437 | 1.000 | 0.434 | False |  |
| avail_h100 | 20 | 46 | 11 | n/a | -0.029 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 65 | 15 | -0.003 | -0.045 | [-0.27, 0.22] | 0.759 | 1.000 | 0.723 | False |  |
| avail_b200 | 5 | 61 | 15 | -0.008 | -0.050 | [-0.19, 0.10] | 0.363 | 1.000 | 0.415 | False |  |
| avail_b200 | 20 | 46 | 9 | n/a | -0.038 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 6 | -0.793 | n/a | 0.531 | 1.000 | False | insufficient events (6 < 10); descriptive only |
| H100 | 5 | 4 | 2.753 | n/a | 0.500 | 1.000 | False | insufficient events (4 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.733 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 45 | -0.190 | -0.189 | 0.663 | 0.768 | 0.511 | 1.000 | False | 45 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 37 | 0.054 | -0.081 | 0.050 | 0.485 | 0.784 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 7 | 0.872 | 0.022 | n/a | n/a | 1.000 | n/a | False | 7 out-of-sample forecasts < 120 required |
| level_b200 | 1 | 45 | -0.144 | -0.144 | 0.050 | 0.045 | 0.556 | 0.901 | False | 45 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 37 | 0.144 | 0.022 | 0.005 | 0.065 | 0.784 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 7 | 0.913 | 0.338 | n/a | n/a | 1.000 | n/a | False | 7 out-of-sample forecasts < 120 required |
| disp_h100 | 1 | 45 | -0.019 | -0.019 | 0.657 | 0.859 | 0.511 | 1.000 | False | 45 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 37 | 0.105 | -0.022 | 0.033 | 0.778 | 0.703 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 7 | 0.876 | 0.050 | n/a | n/a | 1.000 | n/a | False | 7 out-of-sample forecasts < 120 required |
| disp_b200 | 1 | 45 | -0.027 | -0.026 | 0.164 | 0.176 | 0.533 | 1.000 | False | 45 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 37 | 0.113 | -0.013 | 0.018 | 0.404 | 0.730 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 7 | 0.878 | 0.072 | n/a | n/a | 1.000 | n/a | False | 7 out-of-sample forecasts < 120 required |
| avail_h100 | 1 | 45 | -1.098 | -1.097 | 0.331 | 0.424 | 0.511 | 1.000 | False | 45 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 37 | -27.161 | -31.178 | 0.522 | 0.631 | 0.676 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 7 | -90.715 | -699.540 | n/a | n/a | 0.571 | n/a | False | 7 out-of-sample forecasts < 120 required |
| avail_b200 | 1 | 45 | -0.141 | -0.140 | 0.778 | 0.841 | 0.511 | 1.000 | False | 45 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 37 | 0.135 | 0.011 | 0.023 | 0.126 | 0.703 | 1.000 | False | 37 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 7 | 0.869 | 0.000 | n/a | n/a | 1.000 | n/a | False | 7 out-of-sample forecasts < 120 required |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 45 | 9 | -1.296 | [-5.56, 4.23] | False | -0.006 | -0.046 | -0.085 | -0.164 | -0.323 |
| level_h100 | 5 | 37 | 30 | 3.098 | [-0.23, 7.54] | False | 2.506 | 2.312 | 2.118 | 1.729 | 0.952 |
| level_h100 | 20 | 7 | 7 | 8.856 | n/a | False | 6.948 | 6.559 | 6.171 | 5.394 | 3.841 |
| level_b200 | 1 | 45 | 7 | 1.855 | [-3.34, 5.95] | False | 0.152 | 0.121 | 0.090 | 0.027 | -0.097 |
| level_b200 | 5 | 37 | 31 | 3.536 | [0.05, 8.64] | True | 2.841 | 2.641 | 2.440 | 2.038 | 1.235 |
| level_b200 | 20 | 7 | 7 | 8.856 | n/a | False | 6.948 | 6.559 | 6.171 | 5.394 | 3.841 |
| disp_h100 | 1 | 45 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 37 | 31 | 2.708 | [-0.70, 7.21] | False | 2.378 | 2.180 | 1.981 | 1.585 | 0.791 |
| disp_h100 | 20 | 7 | 7 | 8.856 | n/a | False | 6.948 | 6.559 | 6.171 | 5.394 | 3.841 |
| disp_b200 | 1 | 45 | 6 | -0.003 | [-4.18, 4.39] | False | 0.052 | 0.026 | -0.000 | -0.053 | -0.158 |
| disp_b200 | 5 | 37 | 30 | 3.415 | [-0.06, 8.27] | False | 2.752 | 2.558 | 2.364 | 1.975 | 1.198 |
| disp_b200 | 20 | 7 | 7 | 8.856 | n/a | False | 6.948 | 6.559 | 6.171 | 5.394 | 3.841 |
| avail_h100 | 1 | 45 | 9 | -2.014 | [-4.25, 0.60] | False | -0.080 | -0.119 | -0.159 | -0.238 | -0.395 |
| avail_h100 | 5 | 37 | 31 | 2.030 | [-0.46, 4.72] | False | 1.924 | 1.726 | 1.527 | 1.131 | 0.337 |
| avail_h100 | 20 | 7 | 7 | 0.726 | n/a | False | 2.132 | 1.820 | 1.508 | 0.884 | -0.363 |
| avail_b200 | 1 | 45 | 8 | -2.393 | [-4.68, 0.19] | False | -0.116 | -0.151 | -0.186 | -0.256 | -0.396 |
| avail_b200 | 5 | 37 | 31 | 2.961 | [-0.23, 6.95] | False | 2.517 | 2.317 | 2.118 | 1.719 | 0.921 |
| avail_b200 | 20 | 7 | 7 | 8.856 | n/a | False | 6.948 | 6.559 | 6.171 | 5.394 | 3.841 |

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
| avail_b200|h5 | False | False | False | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 65 | 28 | 0.093 | 0.043 | [-0.41, 0.30] | 0.750 | 1.000 | 0.738 | False |  |
| neocloud | level_h100 | 5 | 61 | 27 | 0.197 | 0.038 | [-0.25, 0.22] | 0.689 | 1.000 | 0.755 | False |  |
| neocloud | level_h100 | 20 | 46 | 16 | n/a | -0.191 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 65 | 25 | -0.643 | -0.325 | [-0.47, -0.16] | 0.001 | 0.059 | 0.015 | True |  |
| neocloud | level_b200 | 5 | 61 | 25 | -0.846 | -0.183 | [-0.33, -0.02] | 0.018 | 0.318 | 0.208 | False |  |
| neocloud | level_b200 | 20 | 46 | 23 | n/a | -0.287 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 65 | 50 | 0.041 | 0.033 | [-0.17, 0.25] | 0.762 | 1.000 | 0.754 | False |  |
| neocloud | disp_h100 | 5 | 61 | 48 | -0.459 | -0.157 | [-0.43, 0.07] | 0.150 | 0.808 | 0.113 | False |  |
| neocloud | disp_h100 | 20 | 46 | 39 | n/a | -0.127 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 65 | 14 | 0.238 | 0.262 | [-0.07, 0.45] | 0.003 | 0.086 | 0.031 | True |  |
| neocloud | disp_b200 | 5 | 61 | 14 | 0.274 | 0.130 | [-0.14, 0.28] | 0.070 | 0.704 | 0.302 | False |  |
| neocloud | disp_b200 | 20 | 46 | 8 | n/a | 0.230 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 65 | 19 | -0.011 | -0.099 | [-0.34, 0.16] | 0.493 | 1.000 | 0.369 | False |  |
| neocloud | avail_h100 | 5 | 61 | 18 | -0.009 | -0.034 | [-0.18, 0.12] | 0.562 | 1.000 | 0.660 | False |  |
| neocloud | avail_h100 | 20 | 46 | 11 | n/a | -0.051 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 65 | 15 | -0.009 | -0.089 | [-0.34, 0.18] | 0.545 | 1.000 | 0.431 | False |  |
| neocloud | avail_b200 | 5 | 61 | 15 | -0.010 | -0.040 | [-0.18, 0.11] | 0.466 | 1.000 | 0.623 | False |  |
| neocloud | avail_b200 | 20 | 46 | 9 | n/a | -0.060 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 65 | 28 | -0.049 | -0.059 | [-0.45, 0.16] | 0.659 | 1.000 | 0.708 | False |  |
| gpu_semis | level_h100 | 5 | 61 | 27 | 0.275 | 0.114 | [-0.19, 0.28] | 0.100 | 0.712 | 0.491 | False |  |
| gpu_semis | level_h100 | 20 | 46 | 16 | n/a | -0.165 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 65 | 25 | -0.179 | -0.236 | [-0.55, 0.04] | 0.197 | 0.963 | 0.046 | False |  |
| gpu_semis | level_b200 | 5 | 61 | 25 | -0.231 | -0.106 | [-0.28, 0.07] | 0.137 | 0.808 | 0.491 | False |  |
| gpu_semis | level_b200 | 20 | 46 | 23 | n/a | -0.301 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 65 | 50 | 0.037 | 0.078 | [-0.16, 0.35] | 0.561 | 1.000 | 0.508 | False |  |
| gpu_semis | disp_h100 | 5 | 61 | 48 | -0.152 | -0.110 | [-0.36, 0.11] | 0.255 | 0.985 | 0.226 | False |  |
| gpu_semis | disp_h100 | 20 | 46 | 39 | n/a | -0.079 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 65 | 14 | 0.090 | 0.261 | [-0.09, 0.54] | 0.105 | 0.712 | 0.015 | False |  |
| gpu_semis | disp_b200 | 5 | 61 | 14 | 0.070 | 0.071 | [-0.22, 0.26] | 0.476 | 1.000 | 0.698 | False |  |
| gpu_semis | disp_b200 | 20 | 46 | 8 | n/a | 0.250 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 65 | 19 | -0.001 | -0.020 | [-0.26, 0.29] | 0.892 | 1.000 | 0.908 | False |  |
| gpu_semis | avail_h100 | 5 | 61 | 18 | -0.006 | -0.052 | [-0.17, 0.08] | 0.306 | 1.000 | 0.340 | False |  |
| gpu_semis | avail_h100 | 20 | 46 | 11 | n/a | -0.039 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 65 | 15 | -0.000 | -0.003 | [-0.25, 0.31] | 0.986 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 61 | 15 | -0.007 | -0.061 | [-0.18, 0.07] | 0.232 | 0.963 | 0.264 | False |  |
| gpu_semis | avail_b200 | 20 | 46 | 9 | n/a | -0.051 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 65 | 28 | -0.055 | -0.039 | [-0.27, 0.08] | 0.642 | 1.000 | 0.831 | False |  |
| power_capacity | level_h100 | 5 | 61 | 27 | 0.281 | 0.083 | [-0.12, 0.28] | 0.230 | 0.963 | 0.491 | False |  |
| power_capacity | level_h100 | 20 | 46 | 16 | n/a | 0.084 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 65 | 25 | -0.343 | -0.266 | [-0.43, -0.09] | 0.025 | 0.338 | 0.046 | False |  |
| power_capacity | level_b200 | 5 | 61 | 25 | -0.079 | -0.026 | [-0.29, 0.12] | 0.712 | 1.000 | 0.849 | False |  |
| power_capacity | level_b200 | 20 | 46 | 23 | n/a | -0.022 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 65 | 50 | 0.097 | 0.120 | [-0.10, 0.34] | 0.309 | 1.000 | 0.308 | False |  |
| power_capacity | disp_h100 | 5 | 61 | 48 | -0.139 | -0.073 | [-0.33, 0.17] | 0.508 | 1.000 | 0.566 | False |  |
| power_capacity | disp_h100 | 20 | 46 | 39 | n/a | -0.075 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 65 | 14 | 0.100 | 0.170 | [-0.13, 0.33] | 0.078 | 0.704 | 0.231 | False |  |
| power_capacity | disp_b200 | 5 | 61 | 14 | -0.022 | -0.016 | [-0.21, 0.15] | 0.849 | 1.000 | 0.906 | False |  |
| power_capacity | disp_b200 | 20 | 46 | 8 | n/a | 0.005 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 65 | 19 | 0.000 | 0.003 | [-0.17, 0.23] | 0.983 | 1.000 | 1.000 | False |  |
| power_capacity | avail_h100 | 5 | 61 | 18 | -0.007 | -0.044 | [-0.21, 0.15] | 0.509 | 1.000 | 0.340 | False |  |
| power_capacity | avail_h100 | 20 | 46 | 11 | n/a | 0.042 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 65 | 15 | 0.001 | 0.012 | [-0.17, 0.23] | 0.923 | 1.000 | 0.954 | False |  |
| power_capacity | avail_b200 | 5 | 61 | 15 | -0.007 | -0.045 | [-0.21, 0.15] | 0.514 | 1.000 | 0.358 | False |  |
| power_capacity | avail_b200 | 20 | 46 | 9 | n/a | 0.041 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.03 [-0.14, 0.21] | -0.04 [-0.24, 0.28] |
| -4 | -0.01 [-0.12, 0.11] | -0.32 [-0.47, -0.15] |
| -3 | -0.10 [-0.24, 0.06] | 0.08 [-0.11, 0.36] |
| -2 | -0.20 [-0.39, 0.04] | -0.10 [-0.27, 0.14] |
| -1 | 0.09 [-0.23, 0.40] | -0.19 [-0.34, 0.04] |
| 0 | -0.32 [-0.50, -0.12] | -0.00 [-0.41, 0.22] |
| 1 | -0.05 [-0.29, 0.23] | 0.02 [-0.30, 0.26] |
| 2 | 0.07 [-0.13, 0.22] | 0.06 [-0.10, 0.33] |
| 3 | 0.01 [-0.22, 0.29] | 0.15 [-0.02, 0.27] |
| 4 | -0.03 [-0.14, 0.05] | 0.18 [-0.23, 0.39] |
| 5 | -0.02 [-0.17, 0.16] | -0.13 [-0.28, 0.09] |

