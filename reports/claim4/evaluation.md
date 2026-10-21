# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-21T02:00:04.123991+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `3bcb01d6fb55f59c...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 23 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 2 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 43 | 2026-08-20 | 2026-10-20 | 0.42 | 0.54 |
| 5 | 39 | 2026-08-20 | 2026-10-14 | 0.44 | 0.56 |
| 20 | 24 | 2026-08-20 | 2026-09-23 | 0.55 | 0.68 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 43 | 13 | -0.985 | -0.332 | [-0.55, 0.08] | 0.006 | 0.101 | 0.047 | False |  |
| level_h100 | 5 | 39 | 10 | -1.027 | -0.129 | [-0.31, 0.20] | 0.127 | 1.000 | 0.452 | False |  |
| level_h100 | 20 | 24 | 3 | n/a | -0.045 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 43 | 21 | -0.335 | -0.307 | [-0.55, -0.10] | 0.077 | 1.000 | 0.047 | False |  |
| level_b200 | 5 | 39 | 17 | -0.536 | -0.183 | [-0.43, -0.01] | 0.071 | 1.000 | 0.323 | False |  |
| level_b200 | 20 | 24 | 7 | n/a | -0.228 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 43 | 36 | -0.061 | -0.072 | [-0.26, 0.14] | 0.522 | 1.000 | 0.767 | False |  |
| disp_h100 | 5 | 39 | 33 | 0.092 | 0.035 | [-0.25, 0.25] | 0.722 | 1.000 | 0.677 | False |  |
| disp_h100 | 20 | 24 | 19 | n/a | -0.064 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 43 | 7 | 0.168 | 0.346 | [-0.03, 0.55] | 0.001 | 0.022 | 0.047 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 5 | 39 | 7 | 0.242 | 0.187 | [0.01, 0.35] | 0.000 | 0.001 | 0.290 | False | insufficient variation (7 non-zero < 10) |
| disp_b200 | 20 | 24 | 1 | n/a | 0.106 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 43 | 10 | -0.007 | -0.103 | [-0.38, 0.32] | 0.587 | 1.000 | 0.488 | False |  |
| avail_h100 | 5 | 39 | 6 | -0.009 | -0.030 | [-0.42, 0.18] | 0.777 | 1.000 | 0.613 | False | insufficient variation (6 non-zero < 10) |
| avail_h100 | 20 | 24 | 2 | n/a | -0.201 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 43 | 8 | -0.007 | -0.106 | [-0.38, 0.30] | 0.575 | 1.000 | 0.512 | False | insufficient variation (8 non-zero < 10) |
| avail_b200 | 5 | 39 | 4 | -0.007 | -0.025 | [-0.27, 0.17] | 0.798 | 1.000 | 0.774 | False | insufficient variation (4 non-zero < 10) |
| avail_b200 | 20 | 24 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

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
| level_h100 | 1 | 23 | -0.016 | -0.017 | 0.049 | 0.029 | 0.565 | 0.772 | False | 23 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 15 | 0.167 | 0.007 | 0.007 | 0.048 | 0.933 | 0.772 | False | 15 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 23 | -0.493 | -0.494 | 0.108 | 0.108 | 0.609 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 15 | 0.238 | 0.092 | 0.006 | 0.006 | 0.933 | 0.109 | False | 15 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 23 | -0.010 | -0.010 | 0.536 | 0.917 | 0.565 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 15 | 0.137 | -0.028 | 0.068 | 0.999 | 0.733 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 23 | -0.032 | -0.032 | 0.104 | 0.106 | 0.609 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 15 | 0.225 | 0.077 | 0.014 | 0.010 | 0.800 | 0.239 | False | 15 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 23 | -2.582 | -2.584 | 0.303 | 0.383 | 0.565 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 15 | -59.958 | -71.615 | 0.567 | 0.632 | 0.733 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 23 | -0.286 | -0.286 | 0.775 | 0.810 | 0.565 | 1.000 | False | 23 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 15 | 0.212 | 0.062 | 0.071 | 0.130 | 0.800 | 1.000 | False | 15 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 23 | 3 | 5.185 | [0.00, 8.07] | False | 0.217 | 0.191 | 0.165 | 0.113 | 0.008 |
| level_h100 | 5 | 15 | 9 | 6.291 | [2.78, 11.68] | True | 3.712 | 3.569 | 3.425 | 3.137 | 2.562 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 23 | 6 | 0.546 | [-5.82, 7.90] | False | 0.132 | 0.080 | 0.028 | -0.076 | -0.285 |
| level_b200 | 5 | 15 | 9 | 7.302 | [3.07, 20.45] | True | 4.221 | 4.077 | 3.933 | 3.646 | 3.071 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 23 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 15 | 9 | 3.968 | [-2.47, 14.96] | False | 3.078 | 2.941 | 2.803 | 2.527 | 1.976 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 23 | 3 | 4.048 | [-3.31, 7.02] | False | 0.118 | 0.092 | 0.067 | 0.015 | -0.088 |
| disp_b200 | 5 | 15 | 8 | 6.733 | [2.58, 19.06] | True | 4.002 | 3.874 | 3.746 | 3.490 | 2.979 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 23 | 5 | -2.871 | [-5.54, 4.29] | False | -0.144 | -0.186 | -0.229 | -0.315 | -0.485 |
| avail_h100 | 5 | 15 | 9 | 3.450 | [1.54, 7.71] | True | 2.759 | 2.618 | 2.477 | 2.195 | 1.632 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 23 | 4 | -3.650 | [-6.23, 0.00] | False | -0.214 | -0.248 | -0.282 | -0.350 | -0.486 |
| avail_b200 | 5 | 15 | 9 | 7.302 | [3.07, 20.45] | True | 4.221 | 4.077 | 3.933 | 3.646 | 3.071 |
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
| neocloud | level_h100 | 1 | 43 | 13 | -1.562 | -0.334 | [-0.53, 0.13] | 0.004 | 0.043 | 0.047 | True |  |
| neocloud | level_h100 | 5 | 39 | 10 | -2.446 | -0.199 | [-0.37, 0.02] | 0.000 | 0.001 | 0.323 | False |  |
| neocloud | level_h100 | 20 | 24 | 3 | n/a | -0.106 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 43 | 21 | -0.615 | -0.358 | [-0.54, -0.11] | 0.015 | 0.103 | 0.047 | False |  |
| neocloud | level_b200 | 5 | 39 | 17 | -1.097 | -0.242 | [-0.43, -0.04] | 0.009 | 0.069 | 0.258 | False |  |
| neocloud | level_b200 | 20 | 24 | 7 | n/a | -0.281 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 43 | 36 | -0.117 | -0.087 | [-0.28, 0.15] | 0.413 | 1.000 | 0.674 | False |  |
| neocloud | disp_h100 | 5 | 39 | 33 | 0.113 | 0.028 | [-0.27, 0.24] | 0.775 | 1.000 | 0.774 | False |  |
| neocloud | disp_h100 | 20 | 24 | 19 | n/a | -0.066 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 43 | 7 | 0.293 | 0.385 | [-0.00, 0.56] | 0.000 | 0.000 | 0.047 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 5 | 39 | 7 | 0.437 | 0.218 | [-0.00, 0.39] | 0.000 | 0.000 | 0.129 | False | insufficient variation (7 non-zero < 10) |
| neocloud | disp_b200 | 20 | 24 | 1 | n/a | 0.159 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 43 | 10 | -0.021 | -0.198 | [-0.45, 0.19] | 0.266 | 0.899 | 0.186 | False |  |
| neocloud | avail_h100 | 5 | 39 | 6 | -0.033 | -0.073 | [-0.45, 0.11] | 0.513 | 1.000 | 0.419 | False | insufficient variation (6 non-zero < 10) |
| neocloud | avail_h100 | 20 | 24 | 2 | n/a | -0.244 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 43 | 8 | -0.022 | -0.208 | [-0.46, 0.18] | 0.240 | 0.899 | 0.186 | False | insufficient variation (8 non-zero < 10) |
| neocloud | avail_b200 | 5 | 39 | 4 | -0.034 | -0.077 | [-0.33, 0.09] | 0.460 | 1.000 | 0.484 | False | insufficient variation (4 non-zero < 10) |
| neocloud | avail_b200 | 20 | 24 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 43 | 13 | -0.701 | -0.372 | [-0.66, 0.03] | 0.009 | 0.069 | 0.047 | True |  |
| gpu_semis | level_h100 | 5 | 39 | 10 | -0.509 | -0.096 | [-0.31, 0.27] | 0.392 | 1.000 | 0.710 | False |  |
| gpu_semis | level_h100 | 20 | 24 | 3 | n/a | -0.103 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 43 | 21 | -0.151 | -0.217 | [-0.65, 0.09] | 0.365 | 1.000 | 0.140 | False |  |
| gpu_semis | level_b200 | 5 | 39 | 17 | -0.336 | -0.173 | [-0.43, 0.09] | 0.050 | 0.247 | 0.323 | False |  |
| gpu_semis | level_b200 | 20 | 24 | 7 | n/a | -0.274 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 43 | 36 | -0.028 | -0.052 | [-0.32, 0.15] | 0.722 | 1.000 | 0.767 | False |  |
| gpu_semis | disp_h100 | 5 | 39 | 33 | 0.006 | 0.003 | [-0.25, 0.23] | 0.973 | 1.000 | 0.968 | False |  |
| gpu_semis | disp_h100 | 20 | 24 | 19 | n/a | 0.031 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 43 | 7 | 0.105 | 0.342 | [-0.08, 0.65] | 0.085 | 0.383 | 0.070 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 39 | 7 | 0.190 | 0.221 | [-0.01, 0.39] | 0.000 | 0.001 | 0.290 | False | insufficient variation (7 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 24 | 1 | n/a | 0.146 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 43 | 10 | 0.002 | 0.046 | [-0.29, 0.47] | 0.819 | 1.000 | 0.721 | False |  |
| gpu_semis | avail_h100 | 5 | 39 | 6 | -0.004 | -0.020 | [-0.35, 0.15] | 0.845 | 1.000 | 0.774 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 24 | 2 | n/a | -0.076 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 43 | 8 | 0.002 | 0.054 | [-0.26, 0.47] | 0.788 | 1.000 | 0.698 | False | insufficient variation (8 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 39 | 4 | -0.004 | -0.022 | [-0.29, 0.15] | 0.833 | 1.000 | 0.871 | False | insufficient variation (4 non-zero < 10) |
| gpu_semis | avail_b200 | 20 | 24 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 43 | 13 | -0.693 | -0.213 | [-0.37, 0.12] | 0.026 | 0.155 | 0.163 | False |  |
| power_capacity | level_h100 | 5 | 39 | 10 | -0.125 | -0.016 | [-0.24, 0.44] | 0.891 | 1.000 | 0.903 | False |  |
| power_capacity | level_h100 | 20 | 24 | 3 | n/a | 0.169 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 43 | 21 | -0.240 | -0.200 | [-0.39, -0.04] | 0.116 | 0.481 | 0.256 | False |  |
| power_capacity | level_b200 | 5 | 39 | 17 | -0.176 | -0.063 | [-0.42, 0.19] | 0.569 | 1.000 | 0.645 | False |  |
| power_capacity | level_b200 | 20 | 24 | 7 | n/a | -0.003 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 43 | 36 | -0.038 | -0.041 | [-0.23, 0.20] | 0.726 | 1.000 | 0.860 | False |  |
| power_capacity | disp_h100 | 5 | 39 | 33 | 0.158 | 0.063 | [-0.24, 0.29] | 0.593 | 1.000 | 0.677 | False |  |
| power_capacity | disp_h100 | 20 | 24 | 19 | n/a | -0.147 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 43 | 7 | 0.105 | 0.197 | [-0.19, 0.35] | 0.031 | 0.166 | 0.233 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 39 | 7 | 0.099 | 0.080 | [-0.15, 0.27] | 0.250 | 0.899 | 0.677 | False | insufficient variation (7 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 24 | 1 | n/a | -0.085 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 43 | 10 | -0.002 | -0.025 | [-0.30, 0.32] | 0.877 | 1.000 | 0.837 | False |  |
| power_capacity | avail_h100 | 5 | 39 | 6 | 0.010 | 0.036 | [-0.39, 0.29] | 0.682 | 1.000 | 0.613 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 24 | 2 | n/a | -0.191 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 43 | 8 | -0.002 | -0.022 | [-0.24, 0.31] | 0.890 | 1.000 | 0.721 | False | insufficient variation (8 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 39 | 4 | 0.016 | 0.060 | [-0.15, 0.32] | 0.456 | 1.000 | 0.419 | False | insufficient variation (4 non-zero < 10) |
| power_capacity | avail_b200 | 20 | 24 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.07 [-0.24, 0.19] | 0.13 [-0.14, 0.27] |
| -4 | -0.01 [-0.19, 0.19] | -0.16 [-0.32, 0.05] |
| -3 | -0.18 [-0.33, 0.03] | -0.16 [-0.37, 0.00] |
| -2 | -0.16 [-0.41, 0.11] | -0.14 [-0.35, 0.24] |
| -1 | -0.08 [-0.34, 0.17] | -0.30 [-0.44, 0.01] |
| 0 | -0.31 [-0.55, -0.10] | -0.33 [-0.55, 0.08] |
| 1 | 0.06 [-0.24, 0.41] | -0.04 [-0.24, 0.39] |
| 2 | 0.03 [-0.38, 0.28] | 0.03 [-0.30, 0.31] |
| 3 | -0.10 [-0.37, 0.38] | 0.09 [-0.19, 0.30] |
| 4 | -0.06 [-0.27, 0.03] | -0.09 [-0.45, 0.03] |
| 5 | -0.13 [-0.29, 0.02] | -0.08 [-0.37, 0.28] |

