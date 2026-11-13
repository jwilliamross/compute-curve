# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-13T03:35:02.463850+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `f52b1af1ea847260...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 4 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 40 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 60 | 2026-08-20 | 2026-11-12 | 0.35 | 0.47 |
| 5 | 56 | 2026-08-20 | 2026-11-06 | 0.37 | 0.48 |
| 20 | 41 | 2026-08-20 | 2026-10-16 | 0.43 | 0.55 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 60 | 26 | -0.087 | -0.043 | [-0.39, 0.20] | 0.794 | 1.000 | 0.683 | False |  |
| level_h100 | 5 | 56 | 23 | 0.179 | 0.027 | [-0.26, 0.31] | 0.851 | 1.000 | 0.833 | False |  |
| level_h100 | 20 | 41 | 12 | n/a | -0.137 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 60 | 24 | -0.400 | -0.342 | [-0.52, -0.15] | 0.010 | 0.167 | 0.017 | False |  |
| level_b200 | 5 | 56 | 24 | -0.384 | -0.129 | [-0.32, 0.02] | 0.098 | 1.000 | 0.375 | False |  |
| level_b200 | 20 | 41 | 19 | n/a | -0.258 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 60 | 47 | 0.086 | 0.114 | [-0.10, 0.35] | 0.371 | 1.000 | 0.333 | False |  |
| disp_h100 | 5 | 56 | 46 | -0.310 | -0.151 | [-0.46, 0.11] | 0.259 | 1.000 | 0.208 | False |  |
| disp_h100 | 20 | 41 | 34 | n/a | -0.146 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 60 | 13 | 0.164 | 0.298 | [-0.02, 0.47] | 0.002 | 0.037 | 0.017 | True |  |
| disp_b200 | 5 | 56 | 12 | 0.203 | 0.141 | [-0.02, 0.27] | 0.003 | 0.046 | 0.333 | False |  |
| disp_b200 | 20 | 41 | 7 | n/a | 0.205 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 60 | 17 | -0.004 | -0.057 | [-0.28, 0.23] | 0.705 | 1.000 | 0.700 | False |  |
| avail_h100 | 5 | 56 | 17 | -0.008 | -0.047 | [-0.21, 0.10] | 0.420 | 1.000 | 0.417 | False |  |
| avail_h100 | 20 | 41 | 8 | n/a | -0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 60 | 14 | -0.003 | -0.051 | [-0.28, 0.24] | 0.740 | 1.000 | 0.750 | False |  |
| avail_b200 | 5 | 56 | 14 | -0.009 | -0.057 | [-0.22, 0.08] | 0.311 | 1.000 | 0.396 | False |  |
| avail_b200 | 20 | 41 | 6 | n/a | -0.014 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 4 | -0.550 | n/a | 0.875 | 1.000 | False | insufficient events (4 < 10); descriptive only |
| H100 | 5 | 3 | 0.974 | n/a | 1.000 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.734 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 40 | -0.209 | -0.188 | 0.643 | 0.692 | 0.500 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 32 | -0.025 | -0.130 | 0.215 | 0.738 | 0.781 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 2 | n/a | n/a | n/a | n/a | n/a | n/a | False | 2 out-of-sample forecasts |
| level_b200 | 1 | 40 | -0.173 | -0.153 | 0.054 | 0.038 | 0.525 | 0.968 | False | 40 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 32 | 0.114 | 0.023 | 0.017 | 0.063 | 0.781 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 2 | n/a | n/a | n/a | n/a | n/a | n/a | False | 2 out-of-sample forecasts |
| disp_h100 | 1 | 40 | -0.028 | -0.011 | 0.763 | 0.708 | 0.500 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 32 | 0.065 | -0.031 | 0.098 | 0.941 | 0.688 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 2 | n/a | n/a | n/a | n/a | n/a | n/a | False | 2 out-of-sample forecasts |
| disp_b200 | 1 | 40 | -0.020 | -0.002 | 0.147 | 0.120 | 0.525 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 32 | 0.115 | 0.024 | 0.032 | 0.085 | 0.719 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 2 | n/a | n/a | n/a | n/a | n/a | n/a | False | 2 out-of-sample forecasts |
| avail_h100 | 1 | 40 | -1.276 | -1.237 | 0.380 | 0.425 | 0.475 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 32 | -30.348 | -33.561 | 0.544 | 0.631 | 0.656 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 2 | n/a | n/a | n/a | n/a | n/a | n/a | False | 2 out-of-sample forecasts |
| avail_b200 | 1 | 40 | -0.177 | -0.157 | 0.838 | 0.839 | 0.475 | 1.000 | False | 40 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 32 | 0.105 | 0.013 | 0.052 | 0.118 | 0.688 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 2 | n/a | n/a | n/a | n/a | n/a | n/a | False | 2 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 40 | 8 | -0.623 | [-4.26, 4.97] | False | 0.038 | -0.002 | -0.041 | -0.121 | -0.280 |
| level_h100 | 5 | 32 | 25 | 2.761 | [-0.92, 7.80] | False | 2.324 | 2.137 | 1.950 | 1.576 | 0.827 |
| level_h100 | 20 | 2 | 2 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 40 | 7 | 1.967 | [-3.51, 6.17] | False | 0.171 | 0.136 | 0.101 | 0.031 | -0.109 |
| level_b200 | 5 | 32 | 26 | 3.249 | [-0.56, 9.35] | False | 2.712 | 2.517 | 2.323 | 1.933 | 1.154 |
| level_b200 | 20 | 2 | 2 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 40 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 32 | 26 | 2.360 | [-1.62, 7.87] | False | 2.176 | 1.984 | 1.793 | 1.409 | 0.641 |
| disp_h100 | 20 | 2 | 2 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 40 | 5 | 1.191 | [-2.64, 5.07] | False | 0.104 | 0.079 | 0.054 | 0.005 | -0.094 |
| disp_b200 | 5 | 32 | 25 | 3.117 | [-0.74, 8.82] | False | 2.609 | 2.422 | 2.235 | 1.860 | 1.112 |
| disp_b200 | 20 | 2 | 2 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 40 | 9 | -2.135 | [-4.58, 0.81] | False | -0.090 | -0.134 | -0.179 | -0.267 | -0.445 |
| avail_h100 | 5 | 32 | 26 | 1.627 | [-1.20, 4.56] | False | 1.651 | 1.460 | 1.268 | 0.884 | 0.116 |
| avail_h100 | 20 | 2 | 2 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 40 | 8 | -2.538 | [-5.14, 0.30] | False | -0.131 | -0.170 | -0.209 | -0.288 | -0.445 |
| avail_b200 | 5 | 32 | 26 | 2.629 | [-0.89, 7.22] | False | 2.337 | 2.144 | 1.950 | 1.564 | 0.791 |
| avail_b200 | 20 | 2 | 2 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |

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
| disp_b200|h1 | True | False | False | False | False |
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
| neocloud | level_h100 | 1 | 60 | 26 | -0.049 | -0.015 | [-0.38, 0.26] | 0.927 | 1.000 | 0.900 | False |  |
| neocloud | level_h100 | 5 | 56 | 23 | -0.738 | -0.075 | [-0.30, 0.17] | 0.550 | 1.000 | 0.583 | False |  |
| neocloud | level_h100 | 20 | 41 | 12 | n/a | -0.191 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 60 | 24 | -0.664 | -0.354 | [-0.49, -0.20] | 0.000 | 0.008 | 0.017 | True |  |
| neocloud | level_b200 | 5 | 56 | 24 | -0.877 | -0.196 | [-0.35, -0.05] | 0.010 | 0.104 | 0.125 | False |  |
| neocloud | level_b200 | 20 | 41 | 19 | n/a | -0.288 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 60 | 47 | 0.094 | 0.078 | [-0.12, 0.29] | 0.508 | 1.000 | 0.500 | False |  |
| neocloud | disp_h100 | 5 | 56 | 46 | -0.431 | -0.140 | [-0.45, 0.11] | 0.277 | 1.000 | 0.333 | False |  |
| neocloud | disp_h100 | 20 | 41 | 34 | n/a | -0.149 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 60 | 13 | 0.283 | 0.321 | [0.03, 0.48] | 0.000 | 0.000 | 0.017 | True |  |
| neocloud | disp_b200 | 5 | 56 | 12 | 0.400 | 0.186 | [0.04, 0.31] | 0.000 | 0.000 | 0.104 | False |  |
| neocloud | disp_b200 | 20 | 41 | 7 | n/a | 0.231 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 60 | 17 | -0.011 | -0.103 | [-0.35, 0.18] | 0.506 | 1.000 | 0.400 | False |  |
| neocloud | avail_h100 | 5 | 56 | 17 | -0.009 | -0.038 | [-0.20, 0.11] | 0.542 | 1.000 | 0.667 | False |  |
| neocloud | avail_h100 | 20 | 41 | 8 | n/a | -0.052 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 60 | 14 | -0.010 | -0.101 | [-0.35, 0.18] | 0.522 | 1.000 | 0.433 | False |  |
| neocloud | avail_b200 | 5 | 56 | 14 | -0.012 | -0.050 | [-0.21, 0.09] | 0.399 | 1.000 | 0.500 | False |  |
| neocloud | avail_b200 | 20 | 41 | 6 | n/a | -0.063 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 60 | 26 | -0.086 | -0.069 | [-0.46, 0.22] | 0.711 | 1.000 | 0.600 | False |  |
| gpu_semis | level_h100 | 5 | 56 | 23 | 0.327 | 0.071 | [-0.25, 0.37] | 0.652 | 1.000 | 0.458 | False |  |
| gpu_semis | level_h100 | 20 | 41 | 12 | n/a | -0.168 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 60 | 24 | -0.187 | -0.258 | [-0.57, 0.02] | 0.173 | 0.844 | 0.033 | False |  |
| gpu_semis | level_b200 | 5 | 56 | 24 | -0.215 | -0.102 | [-0.29, 0.07] | 0.172 | 0.844 | 0.479 | False |  |
| gpu_semis | level_b200 | 20 | 41 | 19 | n/a | -0.305 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 60 | 47 | 0.049 | 0.105 | [-0.16, 0.37] | 0.474 | 1.000 | 0.350 | False |  |
| gpu_semis | disp_h100 | 5 | 56 | 46 | -0.242 | -0.168 | [-0.44, 0.07] | 0.164 | 0.844 | 0.188 | False |  |
| gpu_semis | disp_h100 | 20 | 41 | 34 | n/a | -0.090 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 60 | 13 | 0.099 | 0.291 | [-0.08, 0.56] | 0.073 | 0.490 | 0.033 | False |  |
| gpu_semis | disp_b200 | 5 | 56 | 12 | 0.161 | 0.159 | [-0.02, 0.30] | 0.001 | 0.008 | 0.208 | False |  |
| gpu_semis | disp_b200 | 20 | 41 | 7 | n/a | 0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 60 | 17 | -0.001 | -0.018 | [-0.27, 0.32] | 0.908 | 1.000 | 0.933 | False |  |
| gpu_semis | avail_h100 | 5 | 56 | 17 | -0.006 | -0.056 | [-0.19, 0.08] | 0.285 | 1.000 | 0.333 | False |  |
| gpu_semis | avail_h100 | 20 | 41 | 8 | n/a | -0.047 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 60 | 14 | -0.000 | -0.005 | [-0.27, 0.34] | 0.976 | 1.000 | 0.983 | False |  |
| gpu_semis | avail_b200 | 5 | 56 | 14 | -0.008 | -0.069 | [-0.20, 0.07] | 0.188 | 0.844 | 0.354 | False |  |
| gpu_semis | avail_b200 | 20 | 41 | 6 | n/a | -0.062 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 60 | 26 | -0.125 | -0.057 | [-0.27, 0.10] | 0.614 | 1.000 | 0.650 | False |  |
| power_capacity | level_h100 | 5 | 56 | 23 | 0.947 | 0.144 | [-0.17, 0.44] | 0.315 | 1.000 | 0.188 | False |  |
| power_capacity | level_h100 | 20 | 41 | 12 | n/a | 0.089 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 60 | 24 | -0.350 | -0.275 | [-0.43, -0.09] | 0.022 | 0.200 | 0.017 | False |  |
| power_capacity | level_b200 | 5 | 56 | 24 | -0.061 | -0.021 | [-0.29, 0.13] | 0.778 | 1.000 | 0.896 | False |  |
| power_capacity | level_b200 | 20 | 41 | 19 | n/a | -0.028 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 60 | 47 | 0.116 | 0.142 | [-0.07, 0.37] | 0.249 | 1.000 | 0.267 | False |  |
| power_capacity | disp_h100 | 5 | 56 | 46 | -0.256 | -0.125 | [-0.41, 0.16] | 0.370 | 1.000 | 0.292 | False |  |
| power_capacity | disp_h100 | 20 | 41 | 34 | n/a | -0.161 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 60 | 13 | 0.110 | 0.184 | [-0.11, 0.33] | 0.050 | 0.389 | 0.117 | False |  |
| power_capacity | disp_b200 | 5 | 56 | 12 | 0.047 | 0.033 | [-0.13, 0.21] | 0.587 | 1.000 | 0.771 | False |  |
| power_capacity | disp_b200 | 20 | 41 | 7 | n/a | 0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 60 | 17 | 0.000 | 0.004 | [-0.18, 0.24] | 0.973 | 1.000 | 0.983 | False |  |
| power_capacity | avail_h100 | 5 | 56 | 17 | -0.007 | -0.046 | [-0.23, 0.14] | 0.500 | 1.000 | 0.458 | False |  |
| power_capacity | avail_h100 | 20 | 41 | 8 | n/a | 0.177 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 60 | 14 | 0.001 | 0.010 | [-0.17, 0.24] | 0.933 | 1.000 | 0.950 | False |  |
| power_capacity | avail_b200 | 5 | 56 | 14 | -0.008 | -0.048 | [-0.23, 0.15] | 0.494 | 1.000 | 0.438 | False |  |
| power_capacity | avail_b200 | 20 | 41 | 6 | n/a | 0.176 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.16, 0.22] | -0.10 [-0.26, 0.19] |
| -4 | -0.03 [-0.14, 0.09] | -0.33 [-0.49, -0.14] |
| -3 | -0.12 [-0.26, 0.04] | 0.08 [-0.15, 0.37] |
| -2 | -0.23 [-0.41, 0.01] | -0.12 [-0.32, 0.10] |
| -1 | 0.08 [-0.26, 0.40] | -0.23 [-0.36, -0.06] |
| 0 | -0.34 [-0.52, -0.15] | -0.04 [-0.39, 0.20] |
| 1 | -0.06 [-0.30, 0.23] | 0.04 [-0.35, 0.35] |
| 2 | 0.06 [-0.26, 0.22] | 0.15 [-0.16, 0.39] |
| 3 | 0.01 [-0.25, 0.29] | 0.11 [-0.08, 0.27] |
| 4 | -0.03 [-0.15, 0.05] | -0.01 [-0.31, 0.22] |
| 5 | -0.04 [-0.20, 0.15] | -0.02 [-0.25, 0.20] |

