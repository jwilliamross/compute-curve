# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-10-06T02:47:50.537916+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 15.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `afdec263a4bedd11...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 2 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 12 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 32 | 2026-08-20 | 2026-10-05 | 0.48 | 0.61 |
| 5 | 28 | 2026-08-20 | 2026-09-29 | 0.51 | 0.64 |
| 20 | 13 | 2026-08-20 | 2026-09-08 | 0.71 | 0.84 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 32 | 5 | -0.964 | -0.405 | [-0.60, 0.17] | 0.007 | 0.119 | 0.031 | False | insufficient variation (5 non-zero < 10) |
| level_h100 | 5 | 28 | 3 | -1.555 | -0.177 | [-0.41, -0.04] | 0.012 | 0.172 | 0.150 | False | insufficient variation (3 non-zero < 10) |
| level_h100 | 20 | 13 | 3 | n/a | 0.164 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 32 | 11 | -0.306 | -0.349 | [-0.61, 0.03] | 0.091 | 0.947 | 0.062 | False |  |
| level_b200 | 5 | 28 | 10 | -0.599 | -0.116 | [-0.37, 0.58] | 0.086 | 0.947 | 0.750 | False |  |
| level_b200 | 20 | 13 | 1 | n/a | 0.133 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 32 | 26 | -0.031 | -0.039 | [-0.28, 0.21] | 0.721 | 1.000 | 0.812 | False |  |
| disp_h100 | 5 | 28 | 23 | 0.185 | 0.079 | [-0.27, 0.32] | 0.521 | 1.000 | 0.900 | False |  |
| disp_h100 | 20 | 13 | 9 | n/a | -0.105 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 32 | 6 | 0.171 | 0.435 | [-0.18, 0.61] | 0.001 | 0.022 | 0.031 | False | insufficient variation (6 non-zero < 10) |
| disp_b200 | 5 | 28 | 3 | 0.200 | 0.134 | [-0.18, 0.40] | 0.018 | 0.237 | 0.400 | False | insufficient variation (3 non-zero < 10) |
| disp_b200 | 20 | 13 | 1 | n/a | -0.133 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 32 | 3 | -0.204 | -0.257 | [-0.43, -0.08] | 0.031 | 0.377 | 0.125 | False | insufficient variation (3 non-zero < 10) |
| avail_h100 | 5 | 28 | 2 | -1.805 | -0.364 | [-0.57, -0.03] | 0.011 | 0.163 | 0.150 | False | insufficient variation (2 non-zero < 10) |
| avail_h100 | 20 | 13 | 1 | n/a | -0.265 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 32 | 1 | -0.047 | -0.142 | [-0.28, -0.11] | 0.000 | 0.006 | 0.469 | False | insufficient variation (1 non-zero < 10) |
| avail_b200 | 5 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| avail_b200 | 20 | 13 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 1 | -3.443 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 2 | -3.062 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| B200 | 5 | 1 | -3.443 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 12 | -0.100 | -0.101 | 0.051 | 0.036 | 0.583 | 0.927 | False | 12 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 4 | 0.006 | 0.067 | n/a | n/a | 0.750 | n/a | False | 4 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 12 | -1.831 | -1.835 | 0.143 | 0.136 | 0.583 | 1.000 | False | 12 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 4 | 0.015 | 0.075 | n/a | n/a | 0.750 | n/a | False | 4 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 12 | 0.002 | 0.000 | 0.425 | 0.480 | 0.500 | 1.000 | False | 12 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 4 | -0.151 | -0.081 | n/a | n/a | 0.000 | n/a | False | 4 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 12 | -0.117 | -0.119 | 0.141 | 0.129 | 0.583 | 1.000 | False | 12 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 4 | -0.017 | 0.045 | n/a | n/a | 0.500 | n/a | False | 4 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 12 | -0.615 | -0.617 | 0.151 | 0.147 | 0.500 | 1.000 | False | 12 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 4 | -0.065 | 0.000 | n/a | n/a | 0.250 | n/a | False | 4 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 12 | 0.001 | 0.000 | 0.425 | n/a | 0.500 | n/a | False | 12 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 4 | -0.065 | 0.000 | n/a | n/a | 0.250 | n/a | False | 4 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 12 | 2 | 6.029 | [0.00, 9.95] | False | 0.205 | 0.172 | 0.138 | 0.072 | -0.061 |
| level_h100 | 5 | 4 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 12 | 4 | -4.396 | [-10.17, 4.58] | False | -0.100 | -0.167 | -0.233 | -0.367 | -0.633 |
| level_b200 | 5 | 4 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 12 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 4 | 2 | -5.576 | n/a | False | -2.340 | -2.438 | -2.535 | -2.730 | -3.120 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 12 | 2 | 4.551 | [-4.58, 8.70] | False | 0.167 | 0.134 | 0.101 | 0.036 | -0.094 |
| disp_b200 | 5 | 4 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 12 | 1 | 4.583 | [0.00, 8.77] | False | 0.135 | 0.119 | 0.102 | 0.069 | 0.002 |
| avail_h100 | 5 | 4 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 12 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avail_b200 | 5 | 4 | 0 | 0.000 | n/a | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avail_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |

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
| neocloud | level_h100 | 1 | 32 | 5 | -1.556 | -0.415 | [-0.59, 0.20] | 0.003 | 0.031 | 0.031 | False | insufficient variation (5 non-zero < 10) |
| neocloud | level_h100 | 5 | 28 | 3 | -2.461 | -0.187 | [-0.43, -0.04] | 0.017 | 0.067 | 0.150 | False | insufficient variation (3 non-zero < 10) |
| neocloud | level_h100 | 20 | 13 | 3 | n/a | 0.020 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 32 | 11 | -0.584 | -0.421 | [-0.59, -0.02] | 0.015 | 0.067 | 0.031 | True |  |
| neocloud | level_b200 | 5 | 28 | 10 | -0.933 | -0.121 | [-0.36, 0.60] | 0.060 | 0.191 | 0.800 | False |  |
| neocloud | level_b200 | 20 | 13 | 1 | n/a | 0.012 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 32 | 26 | -0.101 | -0.081 | [-0.37, 0.23] | 0.501 | 0.967 | 0.719 | False |  |
| neocloud | disp_h100 | 5 | 28 | 23 | 0.351 | 0.101 | [-0.22, 0.34] | 0.405 | 0.910 | 0.800 | False |  |
| neocloud | disp_h100 | 20 | 13 | 9 | n/a | -0.074 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 32 | 6 | 0.298 | 0.481 | [-0.10, 0.63] | 0.000 | 0.000 | 0.031 | False | insufficient variation (6 non-zero < 10) |
| neocloud | disp_b200 | 5 | 28 | 3 | 0.314 | 0.140 | [-0.15, 0.41] | 0.017 | 0.067 | 0.450 | False | insufficient variation (3 non-zero < 10) |
| neocloud | disp_b200 | 20 | 13 | 1 | n/a | -0.012 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 32 | 3 | -0.386 | -0.309 | [-0.49, -0.00] | 0.000 | 0.007 | 0.094 | False | insufficient variation (3 non-zero < 10) |
| neocloud | avail_h100 | 5 | 28 | 2 | -2.806 | -0.378 | [-0.58, -0.03] | 0.014 | 0.067 | 0.150 | False | insufficient variation (2 non-zero < 10) |
| neocloud | avail_h100 | 20 | 13 | 1 | n/a | -0.356 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 32 | 1 | -0.122 | -0.234 | [-0.46, -0.21] | 0.000 | 0.000 | 0.250 | False | insufficient variation (1 non-zero < 10) |
| neocloud | avail_b200 | 5 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| neocloud | avail_b200 | 20 | 13 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 32 | 5 | -0.709 | -0.473 | [-0.75, -0.02] | 0.004 | 0.040 | 0.031 | False | insufficient variation (5 non-zero < 10) |
| gpu_semis | level_h100 | 5 | 28 | 3 | -1.062 | -0.197 | [-0.43, -0.06] | 0.019 | 0.067 | 0.400 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | level_h100 | 20 | 13 | 3 | n/a | -0.039 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 32 | 11 | -0.117 | -0.211 | [-0.73, 0.26] | 0.440 | 0.936 | 0.281 | False |  |
| gpu_semis | level_b200 | 5 | 28 | 10 | -0.200 | -0.063 | [-0.38, 0.65] | 0.654 | 1.000 | 0.800 | False |  |
| gpu_semis | level_b200 | 20 | 13 | 1 | n/a | -0.045 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 32 | 26 | 0.018 | 0.036 | [-0.35, 0.28] | 0.817 | 1.000 | 0.812 | False |  |
| gpu_semis | disp_h100 | 5 | 28 | 23 | 0.059 | 0.041 | [-0.29, 0.30] | 0.744 | 1.000 | 0.950 | False |  |
| gpu_semis | disp_h100 | 20 | 13 | 9 | n/a | 0.005 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 32 | 6 | 0.092 | 0.371 | [-0.28, 0.74] | 0.138 | 0.354 | 0.062 | False | insufficient variation (6 non-zero < 10) |
| gpu_semis | disp_b200 | 5 | 28 | 3 | 0.125 | 0.136 | [-0.33, 0.38] | 0.023 | 0.077 | 0.600 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | disp_b200 | 20 | 13 | 1 | n/a | 0.045 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 32 | 3 | -0.041 | -0.081 | [-0.33, 0.12] | 0.468 | 0.936 | 0.656 | False | insufficient variation (3 non-zero < 10) |
| gpu_semis | avail_h100 | 5 | 28 | 2 | -0.847 | -0.278 | [-0.49, -0.03] | 0.001 | 0.010 | 0.250 | False | insufficient variation (2 non-zero < 10) |
| gpu_semis | avail_h100 | 20 | 13 | 1 | n/a | -0.187 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 32 | 1 | 0.005 | 0.024 | [-0.04, 0.15] | 0.456 | 0.936 | 0.938 | False | insufficient variation (1 non-zero < 10) |
| gpu_semis | avail_b200 | 5 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| gpu_semis | avail_b200 | 20 | 13 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 32 | 5 | -0.627 | -0.231 | [-0.41, 0.25] | 0.071 | 0.203 | 0.188 | False | insufficient variation (5 non-zero < 10) |
| power_capacity | level_h100 | 5 | 28 | 3 | -1.142 | -0.126 | [-0.36, 0.02] | 0.009 | 0.059 | 0.250 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | level_h100 | 20 | 13 | 3 | n/a | 0.433 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 32 | 11 | -0.219 | -0.218 | [-0.44, -0.02] | 0.162 | 0.396 | 0.219 | False |  |
| power_capacity | level_b200 | 5 | 28 | 10 | -0.665 | -0.125 | [-0.39, 0.37] | 0.007 | 0.053 | 0.600 | False |  |
| power_capacity | level_b200 | 20 | 13 | 1 | n/a | 0.365 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 32 | 26 | -0.010 | -0.011 | [-0.23, 0.28] | 0.922 | 1.000 | 0.938 | False |  |
| power_capacity | disp_h100 | 5 | 28 | 23 | 0.144 | 0.060 | [-0.35, 0.33] | 0.663 | 1.000 | 0.850 | False |  |
| power_capacity | disp_h100 | 20 | 13 | 9 | n/a | -0.177 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 32 | 6 | 0.123 | 0.274 | [-0.14, 0.42] | 0.010 | 0.059 | 0.062 | False | insufficient variation (6 non-zero < 10) |
| power_capacity | disp_b200 | 5 | 28 | 3 | 0.160 | 0.104 | [-0.14, 0.38] | 0.066 | 0.197 | 0.350 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | disp_b200 | 20 | 13 | 1 | n/a | -0.365 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 32 | 3 | -0.185 | -0.205 | [-0.47, -0.03] | 0.169 | 0.396 | 0.281 | False | insufficient variation (3 non-zero < 10) |
| power_capacity | avail_h100 | 5 | 28 | 2 | -1.762 | -0.344 | [-0.58, -0.03] | 0.016 | 0.067 | 0.150 | False | insufficient variation (2 non-zero < 10) |
| power_capacity | avail_h100 | 20 | 13 | 1 | n/a | -0.078 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 32 | 1 | -0.024 | -0.062 | [-0.15, -0.02] | 0.076 | 0.204 | 0.812 | False | insufficient variation (1 non-zero < 10) |
| power_capacity | avail_b200 | 5 | 28 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | no variation in signal |
| power_capacity | avail_b200 | 20 | 13 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.04 [-0.25, 0.29] | 0.16 [-0.16, 0.35] |
| -4 | -0.04 [-0.34, 0.15] | -0.22 [-0.45, -0.05] |
| -3 | -0.20 [-0.40, 0.23] | -0.16 [-0.39, 0.07] |
| -2 | -0.19 [-0.43, 0.11] | -0.21 [-0.42, 0.23] |
| -1 | -0.08 [-0.37, 0.29] | -0.38 [-0.50, -0.08] |
| 0 | -0.35 [-0.61, 0.03] | -0.41 [-0.60, 0.17] |
| 1 | -0.20 [-0.37, 0.47] | -0.13 [-0.33, 0.38] |
| 2 | 0.19 [-0.39, 0.43] | 0.08 [-0.36, 0.44] |
| 3 | 0.10 [-0.27, 0.36] | 0.03 [-0.50, 0.20] |
| 4 | -0.02 [-0.32, 0.18] | -0.03 [-0.29, 0.10] |
| 5 | -0.01 [-0.42, 0.15] | 0.05 [-0.08, 0.28] |

