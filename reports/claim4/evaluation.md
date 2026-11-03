# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-03T04:06:13.878187+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `2ccd02dc7e553ada...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 1 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 3 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 32 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 1 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 52 | 2026-08-20 | 2026-11-02 | 0.38 | 0.50 |
| 5 | 48 | 2026-08-20 | 2026-10-27 | 0.39 | 0.52 |
| 20 | 33 | 2026-08-20 | 2026-10-06 | 0.47 | 0.60 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 52 | 20 | -0.581 | -0.193 | [-0.49, 0.29] | 0.276 | 1.000 | 0.212 | False |  |
| level_h100 | 5 | 48 | 17 | -1.132 | -0.135 | [-0.30, 0.13] | 0.080 | 1.000 | 0.350 | False |  |
| level_h100 | 20 | 33 | 5 | n/a | -0.162 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 52 | 23 | -0.340 | -0.280 | [-0.51, -0.09] | 0.079 | 1.000 | 0.058 | False |  |
| level_b200 | 5 | 48 | 23 | -0.580 | -0.188 | [-0.44, -0.04] | 0.061 | 0.981 | 0.225 | False |  |
| level_b200 | 20 | 33 | 11 | n/a | -0.259 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 52 | 44 | -0.022 | -0.029 | [-0.21, 0.19] | 0.808 | 1.000 | 0.827 | False |  |
| disp_h100 | 5 | 48 | 40 | -0.206 | -0.091 | [-0.38, 0.16] | 0.423 | 1.000 | 0.625 | False |  |
| disp_h100 | 20 | 33 | 27 | n/a | -0.158 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 52 | 11 | 0.172 | 0.319 | [0.00, 0.51] | 0.001 | 0.016 | 0.019 | True |  |
| disp_b200 | 5 | 48 | 10 | 0.257 | 0.188 | [0.06, 0.35] | 0.000 | 0.001 | 0.175 | False |  |
| disp_b200 | 20 | 33 | 6 | n/a | 0.173 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 52 | 15 | -0.008 | -0.133 | [-0.38, 0.19] | 0.392 | 1.000 | 0.327 | False |  |
| avail_h100 | 5 | 48 | 12 | -0.017 | -0.101 | [-0.33, 0.10] | 0.162 | 1.000 | 0.150 | False |  |
| avail_h100 | 20 | 33 | 3 | n/a | -0.217 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 52 | 13 | -0.008 | -0.136 | [-0.38, 0.18] | 0.383 | 1.000 | 0.327 | False |  |
| avail_b200 | 5 | 48 | 10 | -0.016 | -0.098 | [-0.32, 0.10] | 0.164 | 1.000 | 0.150 | False |  |
| avail_b200 | 20 | 33 | 1 | n/a | -0.168 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 2 | -2.668 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 3 | -2.614 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 5 | 3 | -6.126 | n/a | 0.250 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 32 | -0.107 | -0.113 | 0.402 | 0.486 | 0.531 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 24 | 0.161 | 0.013 | 0.008 | 0.035 | 0.792 | 0.566 | False | 24 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 32 | -0.326 | -0.333 | 0.102 | 0.107 | 0.594 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 24 | 0.220 | 0.083 | 0.005 | 0.016 | 0.792 | 0.286 | False | 24 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 32 | -0.024 | -0.028 | 0.678 | 0.956 | 0.531 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 24 | 0.117 | -0.038 | 0.051 | 1.000 | 0.667 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 32 | -0.009 | -0.014 | 0.086 | 0.092 | 0.594 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 24 | 0.207 | 0.067 | 0.008 | 0.018 | 0.708 | 0.300 | False | 24 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 32 | -1.745 | -1.758 | 0.268 | 0.356 | 0.562 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 24 | -46.064 | -54.342 | 0.553 | 0.631 | 0.625 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 32 | -0.185 | -0.191 | 0.680 | 0.762 | 0.562 | 1.000 | False | 32 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 24 | 0.172 | 0.026 | 0.038 | 0.112 | 0.667 | 1.000 | False | 24 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 32 | 5 | -0.618 | [-5.19, 6.51] | False | 0.028 | -0.003 | -0.034 | -0.096 | -0.220 |
| level_h100 | 5 | 24 | 18 | 4.585 | [0.34, 10.29] | True | 2.978 | 2.798 | 2.619 | 2.259 | 1.541 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 32 | 6 | 0.465 | [-5.74, 6.51] | False | 0.095 | 0.058 | 0.020 | -0.055 | -0.205 |
| level_b200 | 5 | 24 | 18 | 5.079 | [0.41, 12.08] | True | 3.296 | 3.116 | 2.936 | 2.577 | 1.858 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 32 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 24 | 18 | 3.368 | [-1.93, 10.42] | False | 2.582 | 2.406 | 2.230 | 1.878 | 1.174 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 32 | 3 | 3.421 | [-2.81, 5.83] | False | 0.085 | 0.066 | 0.048 | 0.011 | -0.063 |
| disp_b200 | 5 | 24 | 17 | 4.825 | [0.19, 11.70] | True | 3.159 | 2.989 | 2.819 | 2.480 | 1.801 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 32 | 8 | -1.138 | [-4.68, 4.06] | False | 0.006 | -0.044 | -0.093 | -0.192 | -0.390 |
| avail_h100 | 5 | 24 | 18 | 2.186 | [-0.31, 4.64] | False | 1.882 | 1.706 | 1.530 | 1.178 | 0.474 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 32 | 7 | -1.632 | [-5.27, 3.44] | False | -0.045 | -0.088 | -0.132 | -0.218 | -0.391 |
| avail_b200 | 5 | 24 | 18 | 3.865 | [-0.17, 9.62] | False | 2.796 | 2.618 | 2.440 | 2.084 | 1.373 |
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
| avail_h100|h5 | False | False | False | False | False |
| avail_h100|h20 | False | False | False | False | False |
| avail_b200|h1 | False | False | False | False | False |
| avail_b200|h5 | False | False | False | False | False |
| avail_b200|h20 | False | False | False | False | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 54 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_h100 | 1 | 52 | 20 | -0.987 | -0.203 | [-0.48, 0.26] | 0.206 | 0.793 | 0.192 | False |  |
| neocloud | level_h100 | 5 | 48 | 17 | -2.624 | -0.201 | [-0.33, -0.03] | 0.000 | 0.000 | 0.175 | False |  |
| neocloud | level_h100 | 20 | 33 | 5 | n/a | -0.214 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 52 | 23 | -0.626 | -0.320 | [-0.50, -0.12] | 0.015 | 0.132 | 0.019 | False |  |
| neocloud | level_b200 | 5 | 48 | 23 | -1.165 | -0.242 | [-0.45, -0.09] | 0.008 | 0.089 | 0.175 | False |  |
| neocloud | level_b200 | 20 | 33 | 11 | n/a | -0.289 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 52 | 44 | -0.050 | -0.041 | [-0.25, 0.17] | 0.720 | 1.000 | 0.827 | False |  |
| neocloud | disp_h100 | 5 | 48 | 40 | -0.379 | -0.108 | [-0.41, 0.15] | 0.370 | 0.857 | 0.400 | False |  |
| neocloud | disp_h100 | 20 | 33 | 27 | n/a | -0.161 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 52 | 11 | 0.300 | 0.346 | [0.03, 0.52] | 0.000 | 0.000 | 0.019 | True |  |
| neocloud | disp_b200 | 5 | 48 | 10 | 0.463 | 0.217 | [0.07, 0.37] | 0.000 | 0.000 | 0.125 | False |  |
| neocloud | disp_b200 | 20 | 33 | 6 | n/a | 0.209 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 52 | 15 | -0.017 | -0.175 | [-0.44, 0.13] | 0.282 | 0.857 | 0.135 | False |  |
| neocloud | avail_h100 | 5 | 48 | 12 | -0.028 | -0.106 | [-0.34, 0.07] | 0.139 | 0.624 | 0.075 | False |  |
| neocloud | avail_h100 | 20 | 33 | 3 | n/a | -0.242 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 52 | 13 | -0.017 | -0.181 | [-0.45, 0.13] | 0.268 | 0.857 | 0.135 | False |  |
| neocloud | avail_b200 | 5 | 48 | 10 | -0.029 | -0.109 | [-0.33, 0.07] | 0.123 | 0.605 | 0.100 | False |  |
| neocloud | avail_b200 | 20 | 33 | 1 | n/a | -0.181 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 52 | 20 | -0.353 | -0.185 | [-0.58, 0.37] | 0.412 | 0.857 | 0.173 | False |  |
| gpu_semis | level_h100 | 5 | 48 | 17 | -0.529 | -0.097 | [-0.30, 0.24] | 0.384 | 0.857 | 0.625 | False |  |
| gpu_semis | level_h100 | 20 | 33 | 5 | n/a | -0.226 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 52 | 23 | -0.147 | -0.191 | [-0.60, 0.09] | 0.386 | 0.857 | 0.308 | False |  |
| gpu_semis | level_b200 | 5 | 48 | 23 | -0.336 | -0.168 | [-0.39, 0.09] | 0.057 | 0.385 | 0.400 | False |  |
| gpu_semis | level_b200 | 20 | 33 | 11 | n/a | -0.314 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 52 | 44 | -0.038 | -0.078 | [-0.24, 0.11] | 0.562 | 1.000 | 0.615 | False |  |
| gpu_semis | disp_h100 | 5 | 48 | 40 | -0.128 | -0.088 | [-0.33, 0.13] | 0.394 | 0.857 | 0.550 | False |  |
| gpu_semis | disp_h100 | 20 | 33 | 27 | n/a | -0.110 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 52 | 11 | 0.106 | 0.311 | [-0.07, 0.59] | 0.091 | 0.546 | 0.038 | False |  |
| gpu_semis | disp_b200 | 5 | 48 | 10 | 0.189 | 0.213 | [-0.07, 0.37] | 0.000 | 0.001 | 0.175 | False |  |
| gpu_semis | disp_b200 | 20 | 33 | 6 | n/a | 0.217 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 52 | 15 | -0.003 | -0.078 | [-0.37, 0.33] | 0.634 | 1.000 | 0.635 | False |  |
| gpu_semis | avail_h100 | 5 | 48 | 12 | -0.006 | -0.051 | [-0.23, 0.10] | 0.410 | 0.857 | 0.450 | False |  |
| gpu_semis | avail_h100 | 20 | 33 | 3 | n/a | -0.219 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 52 | 13 | -0.003 | -0.076 | [-0.37, 0.33] | 0.643 | 1.000 | 0.635 | False |  |
| gpu_semis | avail_b200 | 5 | 48 | 10 | -0.006 | -0.051 | [-0.22, 0.11] | 0.401 | 0.857 | 0.500 | False |  |
| gpu_semis | avail_b200 | 20 | 33 | 1 | n/a | -0.221 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 52 | 20 | -0.403 | -0.127 | [-0.34, 0.23] | 0.330 | 0.857 | 0.404 | False |  |
| power_capacity | level_h100 | 5 | 48 | 17 | -0.243 | -0.029 | [-0.22, 0.31] | 0.775 | 1.000 | 0.850 | False |  |
| power_capacity | level_h100 | 20 | 33 | 5 | n/a | 0.115 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 52 | 23 | -0.248 | -0.194 | [-0.38, -0.05] | 0.114 | 0.605 | 0.154 | False |  |
| power_capacity | level_b200 | 5 | 48 | 23 | -0.237 | -0.078 | [-0.43, 0.12] | 0.465 | 0.931 | 0.475 | False |  |
| power_capacity | level_b200 | 20 | 33 | 11 | n/a | -0.033 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 52 | 44 | 0.022 | 0.028 | [-0.16, 0.26] | 0.821 | 1.000 | 0.769 | False |  |
| power_capacity | disp_h100 | 5 | 48 | 40 | -0.112 | -0.051 | [-0.33, 0.20] | 0.648 | 1.000 | 0.800 | False |  |
| power_capacity | disp_h100 | 20 | 33 | 27 | n/a | -0.179 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 52 | 11 | 0.108 | 0.190 | [-0.14, 0.34] | 0.025 | 0.196 | 0.173 | False |  |
| power_capacity | disp_b200 | 5 | 48 | 10 | 0.121 | 0.090 | [-0.08, 0.32] | 0.152 | 0.630 | 0.500 | False |  |
| power_capacity | disp_b200 | 20 | 33 | 6 | n/a | -0.031 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 52 | 15 | -0.004 | -0.065 | [-0.24, 0.19] | 0.601 | 1.000 | 0.731 | False |  |
| power_capacity | avail_h100 | 5 | 48 | 12 | -0.018 | -0.106 | [-0.37, 0.15] | 0.241 | 0.857 | 0.125 | False |  |
| power_capacity | avail_h100 | 20 | 33 | 3 | n/a | -0.094 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 52 | 13 | -0.004 | -0.063 | [-0.24, 0.19] | 0.608 | 1.000 | 0.731 | False |  |
| power_capacity | avail_b200 | 5 | 48 | 10 | -0.015 | -0.093 | [-0.35, 0.17] | 0.315 | 0.857 | 0.150 | False |  |
| power_capacity | avail_b200 | 20 | 33 | 1 | n/a | -0.018 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | -0.05 [-0.20, 0.19] | 0.07 [-0.17, 0.23] |
| -4 | -0.01 [-0.17, 0.14] | -0.19 [-0.33, -0.01] |
| -3 | -0.17 [-0.30, 0.01] | -0.08 [-0.29, 0.14] |
| -2 | -0.14 [-0.37, 0.16] | -0.07 [-0.30, 0.23] |
| -1 | -0.07 [-0.32, 0.15] | -0.27 [-0.39, -0.04] |
| 0 | -0.28 [-0.51, -0.09] | -0.19 [-0.49, 0.29] |
| 1 | 0.05 [-0.23, 0.34] | -0.11 [-0.32, 0.26] |
| 2 | 0.02 [-0.35, 0.22] | 0.03 [-0.26, 0.26] |
| 3 | -0.09 [-0.32, 0.33] | 0.08 [-0.18, 0.25] |
| 4 | -0.06 [-0.26, 0.02] | -0.10 [-0.47, -0.01] |
| 5 | -0.12 [-0.27, 0.02] | -0.05 [-0.30, 0.28] |

