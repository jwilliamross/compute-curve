# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?

Generated 2026-11-11T02:59:14.342348+00:00. Pre-registration: `docs/claim4_plan.md`. Tests and evaluations declared for claim 4: 114; variant entries project-wide: 66.

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 `1845f7439bfb1f05...`. Index: fixed-panel history series built from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").

This report shows aggregate statistics only. Outcome: category-balanced basket of 21 compute-linked stocks minus XLK, from the open after the signal to the close h sessions later.

## Verdict

- **No signal passed the validation gate. The paper strategy stays in shadow mode.**
- Family P (primary lead-lag): 0 of 18 tests pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon range from 1 to 4 (minimum for inference: 10).
- Family W (walk-forward): 0 of 18 pass; at most 38 out-of-sample forecasts (minimum: 120).
- Family S (bucket baskets, secondary): 3 of 54 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 58 | 2026-08-20 | 2026-11-10 | 0.36 | 0.48 |
| 5 | 54 | 2026-08-20 | 2026-11-04 | 0.37 | 0.49 |
| 20 | 39 | 2026-08-20 | 2026-10-14 | 0.44 | 0.56 |

MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, so the effective sample is smaller still. Realistic predictive correlations for daily returns are 0.1 or less; detecting 0.1 after Holm needs about 1,463 sessions.

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 58 | 24 | -0.348 | -0.140 | [-0.43, 0.14] | 0.432 | 1.000 | 0.431 | False |  |
| level_h100 | 5 | 54 | 21 | -1.038 | -0.135 | [-0.29, 0.10] | 0.090 | 1.000 | 0.217 | False |  |
| level_h100 | 20 | 39 | 10 | n/a | -0.139 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| level_b200 | 1 | 58 | 24 | -0.391 | -0.341 | [-0.52, -0.14] | 0.013 | 0.207 | 0.034 | False |  |
| level_b200 | 5 | 54 | 24 | -0.333 | -0.121 | [-0.32, 0.09] | 0.210 | 1.000 | 0.326 | False |  |
| level_b200 | 20 | 39 | 17 | n/a | -0.265 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_h100 | 1 | 58 | 47 | 0.087 | 0.117 | [-0.10, 0.36] | 0.361 | 1.000 | 0.328 | False |  |
| disp_h100 | 5 | 54 | 45 | -0.113 | -0.057 | [-0.34, 0.14] | 0.584 | 1.000 | 0.761 | False |  |
| disp_h100 | 20 | 39 | 33 | n/a | -0.149 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| disp_b200 | 1 | 58 | 13 | 0.163 | 0.303 | [-0.06, 0.48] | 0.003 | 0.053 | 0.034 | False |  |
| disp_b200 | 5 | 54 | 12 | 0.202 | 0.153 | [-0.05, 0.29] | 0.009 | 0.151 | 0.196 | False |  |
| disp_b200 | 20 | 39 | 7 | n/a | 0.210 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_h100 | 1 | 58 | 17 | -0.004 | -0.058 | [-0.30, 0.23] | 0.704 | 1.000 | 0.690 | False |  |
| avail_h100 | 5 | 54 | 16 | -0.009 | -0.063 | [-0.25, 0.10] | 0.306 | 1.000 | 0.283 | False |  |
| avail_h100 | 20 | 39 | 6 | n/a | 0.026 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| avail_b200 | 1 | 58 | 14 | -0.003 | -0.052 | [-0.30, 0.23] | 0.740 | 1.000 | 0.759 | False |  |
| avail_b200 | 5 | 54 | 14 | -0.009 | -0.061 | [-0.25, 0.10] | 0.305 | 1.000 | 0.370 | False |  |
| avail_b200 | 20 | 39 | 4 | n/a | 0.011 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Family E: event study on index moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| H100 | 1 | 3 | -1.287 | n/a | 0.750 | 1.000 | False | insufficient events (3 < 10); descriptive only |
| H100 | 5 | 2 | -1.751 | n/a | 0.500 | 1.000 | False | insufficient events (2 < 10); descriptive only |
| H100 | 20 | 1 | 2.018 | n/a | 1.000 | 1.000 | False | insufficient events (1 < 10); descriptive only |
| B200 | 1 | 4 | -2.906 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 5 | 4 | -4.734 | n/a | 0.125 | 0.750 | False | insufficient events (4 < 10); descriptive only |
| B200 | 20 | 2 | -7.052 | n/a | 1.000 | 1.000 | False | insufficient events (2 < 10); descriptive only |

## Family W: walk-forward forecasts against naive baselines

Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the 18 models uses the larger of the two.

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 38 | -0.158 | -0.148 | 0.487 | 0.556 | 0.526 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| level_h100 | 5 | 30 | 0.221 | 0.013 | 0.000 | 0.031 | 0.833 | 0.560 | False | 30 out-of-sample forecasts < 120 required |
| level_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| level_b200 | 1 | 38 | -0.180 | -0.170 | 0.052 | 0.043 | 0.553 | 0.882 | False | 38 out-of-sample forecasts < 120 required |
| level_b200 | 5 | 30 | 0.227 | 0.021 | 0.000 | 0.090 | 0.833 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| level_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_h100 | 1 | 38 | -0.020 | -0.011 | 0.650 | 0.705 | 0.526 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| disp_h100 | 5 | 30 | 0.175 | -0.045 | 0.006 | 0.973 | 0.733 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| disp_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| disp_b200 | 1 | 38 | -0.012 | -0.004 | 0.130 | 0.122 | 0.553 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| disp_b200 | 5 | 30 | 0.239 | 0.036 | 0.000 | 0.064 | 0.767 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| disp_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_h100 | 1 | 38 | -1.332 | -1.313 | 0.354 | 0.425 | 0.500 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| avail_h100 | 5 | 30 | -36.240 | -46.185 | 0.520 | 0.631 | 0.700 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| avail_h100 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |
| avail_b200 | 1 | 38 | -0.177 | -0.167 | 0.810 | 0.840 | 0.500 | 1.000 | False | 38 out-of-sample forecasts < 120 required |
| avail_b200 | 5 | 30 | 0.225 | 0.018 | 0.005 | 0.117 | 0.733 | 1.000 | False | 30 out-of-sample forecasts < 120 required |
| avail_b200 | 20 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | False | 0 out-of-sample forecasts |

## Gate G3: long-short strategy on the walk-forward forecasts, net of costs

Trades only when the forecast exceeds the round-trip cost. Mean net return per window in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): 15 bps per side for stocks, 3 bps for XLK, 1 bp fees on sells, borrow 5.0% a year on short stocks and 0.5% on the short benchmark.

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_h100 | 1 | 38 | 7 | 0.166 | [-3.34, 5.55] | False | 0.084 | 0.047 | 0.011 | -0.062 | -0.209 |
| level_h100 | 5 | 30 | 23 | 4.778 | [1.69, 8.55] | True | 3.092 | 2.909 | 2.725 | 2.358 | 1.623 |
| level_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| level_b200 | 1 | 38 | 7 | 2.017 | [-3.68, 6.32] | False | 0.180 | 0.143 | 0.106 | 0.032 | -0.115 |
| level_b200 | 5 | 30 | 24 | 5.472 | [2.02, 10.24] | True | 3.506 | 3.314 | 3.122 | 2.739 | 1.972 |
| level_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_h100 | 1 | 38 | 0 | 0.000 | [0.00, 0.00] | False | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| disp_h100 | 5 | 30 | 24 | 3.974 | [-0.03, 8.87] | False | 2.935 | 2.746 | 2.557 | 2.180 | 1.425 |
| disp_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| disp_b200 | 1 | 38 | 5 | 1.221 | [-3.36, 5.07] | False | 0.109 | 0.083 | 0.057 | 0.005 | -0.099 |
| disp_b200 | 5 | 30 | 23 | 5.257 | [1.77, 9.89] | True | 3.396 | 3.213 | 3.029 | 2.661 | 1.927 |
| disp_b200 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_h100 | 1 | 38 | 9 | -2.190 | [-4.77, 0.93] | False | -0.095 | -0.141 | -0.188 | -0.281 | -0.468 |
| avail_h100 | 5 | 30 | 24 | 2.932 | [0.96, 5.21] | True | 2.375 | 2.186 | 1.997 | 1.620 | 0.865 |
| avail_h100 | 20 | 0 | 0 | n/a | n/a | False | n/a | n/a | n/a | n/a | n/a |
| avail_b200 | 1 | 38 | 8 | -2.604 | [-5.26, 0.36] | False | -0.138 | -0.179 | -0.220 | -0.303 | -0.469 |
| avail_b200 | 5 | 30 | 24 | 4.419 | [1.44, 8.85] | True | 3.106 | 2.915 | 2.725 | 2.345 | 1.584 |
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
| neocloud | level_h100 | 1 | 58 | 24 | -0.506 | -0.129 | [-0.42, 0.16] | 0.466 | 1.000 | 0.483 | False |  |
| neocloud | level_h100 | 5 | 54 | 21 | -2.431 | -0.206 | [-0.33, -0.05] | 0.000 | 0.001 | 0.022 | True |  |
| neocloud | level_h100 | 20 | 39 | 10 | n/a | -0.193 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | level_b200 | 1 | 58 | 24 | -0.645 | -0.355 | [-0.50, -0.18] | 0.001 | 0.011 | 0.034 | True |  |
| neocloud | level_b200 | 5 | 54 | 24 | -0.817 | -0.193 | [-0.34, -0.00] | 0.031 | 0.243 | 0.174 | False |  |
| neocloud | level_b200 | 20 | 39 | 17 | n/a | -0.293 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_h100 | 1 | 58 | 47 | 0.095 | 0.081 | [-0.13, 0.30] | 0.495 | 1.000 | 0.466 | False |  |
| neocloud | disp_h100 | 5 | 54 | 45 | -0.164 | -0.054 | [-0.34, 0.15] | 0.626 | 1.000 | 0.804 | False |  |
| neocloud | disp_h100 | 20 | 39 | 33 | n/a | -0.151 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | disp_b200 | 1 | 58 | 13 | 0.281 | 0.330 | [-0.00, 0.49] | 0.000 | 0.000 | 0.017 | True |  |
| neocloud | disp_b200 | 5 | 54 | 12 | 0.399 | 0.196 | [0.02, 0.33] | 0.000 | 0.000 | 0.130 | False |  |
| neocloud | disp_b200 | 20 | 39 | 7 | n/a | 0.234 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_h100 | 1 | 58 | 17 | -0.011 | -0.106 | [-0.37, 0.18] | 0.503 | 1.000 | 0.362 | False |  |
| neocloud | avail_h100 | 5 | 54 | 16 | -0.012 | -0.050 | [-0.23, 0.11] | 0.416 | 1.000 | 0.500 | False |  |
| neocloud | avail_h100 | 20 | 39 | 6 | n/a | -0.020 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| neocloud | avail_b200 | 1 | 58 | 14 | -0.010 | -0.104 | [-0.37, 0.19] | 0.521 | 1.000 | 0.379 | False |  |
| neocloud | avail_b200 | 5 | 54 | 14 | -0.012 | -0.052 | [-0.23, 0.10] | 0.390 | 1.000 | 0.522 | False |  |
| neocloud | avail_b200 | 20 | 39 | 4 | n/a | -0.036 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_h100 | 1 | 58 | 24 | -0.276 | -0.178 | [-0.51, 0.18] | 0.345 | 1.000 | 0.241 | False |  |
| gpu_semis | level_h100 | 5 | 54 | 21 | -0.500 | -0.092 | [-0.29, 0.22] | 0.417 | 1.000 | 0.457 | False |  |
| gpu_semis | level_h100 | 20 | 39 | 10 | n/a | -0.168 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | level_b200 | 1 | 58 | 24 | -0.183 | -0.255 | [-0.57, 0.03] | 0.186 | 0.890 | 0.086 | False |  |
| gpu_semis | level_b200 | 5 | 54 | 24 | -0.179 | -0.092 | [-0.29, 0.12] | 0.315 | 1.000 | 0.522 | False |  |
| gpu_semis | level_b200 | 20 | 39 | 17 | n/a | -0.304 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_h100 | 1 | 58 | 47 | 0.049 | 0.106 | [-0.17, 0.37] | 0.466 | 1.000 | 0.328 | False |  |
| gpu_semis | disp_h100 | 5 | 54 | 45 | -0.122 | -0.087 | [-0.32, 0.11] | 0.317 | 1.000 | 0.435 | False |  |
| gpu_semis | disp_h100 | 20 | 39 | 33 | n/a | -0.089 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | disp_b200 | 1 | 58 | 13 | 0.099 | 0.293 | [-0.10, 0.57] | 0.079 | 0.472 | 0.034 | False |  |
| gpu_semis | disp_b200 | 5 | 54 | 12 | 0.160 | 0.171 | [-0.04, 0.32] | 0.002 | 0.026 | 0.196 | False |  |
| gpu_semis | disp_b200 | 20 | 39 | 7 | n/a | 0.253 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_h100 | 1 | 58 | 17 | -0.001 | -0.018 | [-0.28, 0.30] | 0.908 | 1.000 | 0.914 | False |  |
| gpu_semis | avail_h100 | 5 | 54 | 16 | -0.008 | -0.071 | [-0.22, 0.06] | 0.198 | 0.890 | 0.217 | False |  |
| gpu_semis | avail_h100 | 20 | 39 | 6 | n/a | -0.044 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| gpu_semis | avail_b200 | 1 | 58 | 14 | -0.000 | -0.005 | [-0.27, 0.32] | 0.977 | 1.000 | 1.000 | False |  |
| gpu_semis | avail_b200 | 5 | 54 | 14 | -0.008 | -0.074 | [-0.22, 0.06] | 0.175 | 0.890 | 0.261 | False |  |
| gpu_semis | avail_b200 | 20 | 39 | 4 | n/a | -0.065 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_h100 | 1 | 58 | 24 | -0.262 | -0.096 | [-0.29, 0.11] | 0.475 | 1.000 | 0.534 | False |  |
| power_capacity | level_h100 | 5 | 54 | 21 | -0.183 | -0.024 | [-0.20, 0.26] | 0.796 | 1.000 | 0.804 | False |  |
| power_capacity | level_h100 | 20 | 39 | 10 | n/a | 0.102 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | level_b200 | 1 | 58 | 24 | -0.346 | -0.273 | [-0.43, -0.09] | 0.024 | 0.220 | 0.034 | False |  |
| power_capacity | level_b200 | 5 | 54 | 24 | -0.004 | -0.001 | [-0.30, 0.23] | 0.988 | 1.000 | 1.000 | False |  |
| power_capacity | level_b200 | 20 | 39 | 17 | n/a | -0.043 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_h100 | 1 | 58 | 47 | 0.116 | 0.143 | [-0.08, 0.36] | 0.245 | 1.000 | 0.293 | False |  |
| power_capacity | disp_h100 | 5 | 54 | 45 | -0.052 | -0.027 | [-0.29, 0.19] | 0.801 | 1.000 | 0.826 | False |  |
| power_capacity | disp_h100 | 20 | 39 | 33 | n/a | -0.189 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | disp_b200 | 1 | 58 | 13 | 0.110 | 0.185 | [-0.14, 0.33] | 0.054 | 0.364 | 0.172 | False |  |
| power_capacity | disp_b200 | 5 | 54 | 12 | 0.046 | 0.036 | [-0.21, 0.23] | 0.646 | 1.000 | 0.783 | False |  |
| power_capacity | disp_b200 | 20 | 39 | 7 | n/a | 0.007 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_h100 | 1 | 58 | 17 | 0.000 | 0.004 | [-0.18, 0.23] | 0.973 | 1.000 | 0.983 | False |  |
| power_capacity | avail_h100 | 5 | 54 | 16 | -0.009 | -0.062 | [-0.29, 0.16] | 0.417 | 1.000 | 0.304 | False |  |
| power_capacity | avail_h100 | 20 | 39 | 6 | n/a | 0.257 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |
| power_capacity | avail_b200 | 1 | 58 | 14 | 0.001 | 0.011 | [-0.17, 0.23] | 0.931 | 1.000 | 0.931 | False |  |
| power_capacity | avail_b200 | 5 | 54 | 14 | -0.007 | -0.052 | [-0.28, 0.18] | 0.505 | 1.000 | 0.435 | False |  |
| power_capacity | avail_b200 | 20 | 39 | 4 | n/a | 0.256 | n/a | n/a | n/a | n/a | False | too few windows for HAC at h=20 (n < 3h) |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k). k < 0: returns realized before the signal was known; k = 0 is the predictive test.

| k | level_b200 | level_h100 |
|---|---|---|
| -5 | 0.02 [-0.16, 0.22] | -0.03 [-0.24, 0.21] |
| -4 | -0.03 [-0.15, 0.10] | -0.34 [-0.52, -0.11] |
| -3 | -0.11 [-0.26, 0.04] | 0.18 [-0.19, 0.43] |
| -2 | -0.23 [-0.42, 0.01] | -0.06 [-0.34, 0.27] |
| -1 | 0.08 [-0.26, 0.41] | -0.17 [-0.34, 0.02] |
| 0 | -0.34 [-0.52, -0.14] | -0.14 [-0.43, 0.14] |
| 1 | -0.06 [-0.30, 0.25] | -0.07 [-0.39, 0.25] |
| 2 | 0.07 [-0.16, 0.23] | 0.18 [-0.13, 0.41] |
| 3 | 0.01 [-0.25, 0.33] | 0.09 [-0.09, 0.26] |
| 4 | -0.02 [-0.14, 0.08] | -0.15 [-0.38, -0.03] |
| 5 | -0.11 [-0.24, 0.02] | -0.06 [-0.28, 0.15] |

