# Claim 5 evaluation: do AWS GPU spot prices lead compute-linked equities?

Generated 2026-10-06T18:40:55.574250+00:00. Pre-registration: `docs/claim5_plan.md`. Tests and evaluations declared for claim 5: 78; variant entries project-wide: 21.

Signal data: Eric Pauley (University of Wisconsin-Madison), "AWS Spot Price History", Zenodo, version 2026-09, https://doi.org/10.5281/zenodo.23082767, CC BY 4.0. Filtered to GPU instance types in US availability zones on Linux/UNIX (`reports/claim5/aws_spot_manifest.json`).

Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends; not stored (D29). Manifest `reports/claim5/data_manifest.json`, SHA-256 `bd80ca5cf6d23869...`. Outcome: claim 4's category-balanced basket of 21 stocks minus XLK, open after the signal to the close h sessions later. Aggregate statistics only.

## Verdict

- **No signal passed the validation gate (unchanged from claim 4).**
- Family P (primary lead-lag): 0 of 12 pass after Holm and the permutation check.
- Family E (event study): 0 of 6 pass; events per GPU and horizon: 11 to 64 (minimum for inference 10).
- Family W (walk-forward): 0 of 12 pass; up to 382 out-of-sample forecasts (minimum 120).
- Family S (bucket baskets, secondary): 0 of 36 pass at a false discovery rate of 10%.

## Sample and power

| horizon (sessions) | windows | first | last | MDE |rho|, alpha 0.05 | MDE |rho|, Holm first step |
|---|---|---|---|---|---|
| 1 | 402 | 2024-10-21 | 2026-10-01 | 0.14 | 0.18 |
| 5 | 400 | 2024-10-21 | 2026-09-29 | 0.14 | 0.18 |
| 20 | 385 | 2024-10-21 | 2026-09-08 | 0.14 | 0.19 |

### Member history used

| symbol | first bar used |
|---|---|
| CRWV | 2025-03-28 |
| NBIS | 2024-10-21 |
| IREN | 2024-09-03 |
| WYFI | 2025-08-07 |
| NVDA | 2024-09-03 |
| AMD | 2024-09-03 |
| AVGO | 2024-09-03 |
| TSM | 2024-09-03 |
| MU | 2024-09-03 |
| MRVL | 2024-09-03 |
| SMCI | 2024-09-03 |
| CBRS | 2026-05-14 |
| VST | 2024-09-03 |
| CEG | 2024-09-03 |
| TLN | 2024-09-03 |
| VRT | 2024-09-03 |
| BE | 2024-09-03 |
| APLD | 2024-09-03 |
| CORZ | 2024-09-03 |
| CIFR | 2024-09-03 |
| WULF | 2024-09-03 |

## Family P: lead-lag, basket minus benchmark (primary)

Slope: excess return in % for a signal change of 0.01. p adj: Holm over the 12 tests. p perm: circular-shift permutation.

| signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_a100 | 1 | 402 | 397 | 0.092 | 0.067 | [-0.04, 0.17] | 0.181 | 1.000 | 0.174 | False |  |
| level_a100 | 5 | 400 | 395 | 0.215 | 0.063 | [-0.05, 0.17] | 0.284 | 1.000 | 0.480 | False |  |
| level_a100 | 20 | 385 | 380 | 0.160 | 0.022 | [-0.18, 0.20] | 0.830 | 1.000 | 0.876 | False |  |
| level_h100 | 1 | 402 | 324 | -0.090 | -0.082 | [-0.19, 0.03] | 0.138 | 1.000 | 0.082 | False |  |
| level_h100 | 5 | 400 | 324 | -0.136 | -0.049 | [-0.19, 0.11] | 0.514 | 1.000 | 0.495 | False |  |
| level_h100 | 20 | 385 | 324 | -0.631 | -0.107 | [-0.30, 0.12] | 0.238 | 1.000 | 0.369 | False |  |
| disp_a100 | 1 | 402 | 402 | -0.010 | -0.014 | [-0.10, 0.08] | 0.749 | 1.000 | 0.781 | False |  |
| disp_a100 | 5 | 400 | 400 | -0.187 | -0.107 | [-0.21, 0.00] | 0.062 | 0.749 | 0.082 | False |  |
| disp_a100 | 20 | 385 | 385 | -0.604 | -0.160 | [-0.33, 0.02] | 0.084 | 0.920 | 0.023 | False |  |
| disp_h100 | 1 | 402 | 402 | -0.003 | -0.008 | [-0.07, 0.10] | 0.811 | 1.000 | 0.881 | False |  |
| disp_h100 | 5 | 400 | 400 | 0.050 | 0.051 | [-0.02, 0.18] | 0.328 | 1.000 | 0.380 | False |  |
| disp_h100 | 20 | 385 | 385 | 0.225 | 0.107 | [-0.02, 0.27] | 0.126 | 1.000 | 0.161 | False |  |

## Family E: event study on spot moves of 2% or more

| GPU | h | events | mean signed CAR % | 95% CI % | p sign-flip | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|
| A100 | 1 | 58 | 0.038 | [-0.65, 0.73] | 0.916 | 1.000 | False |  |
| A100 | 5 | 32 | 1.031 | [-1.07, 3.16] | 0.370 | 1.000 | False |  |
| A100 | 20 | 14 | -3.637 | [-9.48, 1.98] | 0.253 | 1.000 | False |  |
| H100 | 1 | 64 | -0.338 | [-0.97, 0.29] | 0.297 | 1.000 | False |  |
| H100 | 5 | 24 | 0.361 | [-2.44, 3.10] | 0.814 | 1.000 | False |  |
| H100 | 20 | 11 | 5.849 | [-2.93, 13.93] | 0.243 | 1.000 | False |  |

## Family W: walk-forward forecasts against naive baselines

| signal | h | OOS | R2 OS vs B0 | R2 OS vs B1 | CW p B0 | CW p B1 | hit rate | p Holm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| level_a100 | 1 | 382 | -0.041 | -0.030 | 0.459 | 0.336 | 0.487 | 1.000 | False |  |
| level_a100 | 5 | 376 | -0.052 | -0.022 | 0.272 | 0.555 | 0.569 | 1.000 | False |  |
| level_a100 | 20 | 346 | -0.119 | -0.034 | 0.173 | 0.851 | 0.584 | 1.000 | False |  |
| level_h100 | 1 | 382 | -0.021 | -0.010 | 0.675 | 0.513 | 0.484 | 1.000 | False |  |
| level_h100 | 5 | 376 | -0.058 | -0.029 | 0.250 | 0.739 | 0.580 | 1.000 | False |  |
| level_h100 | 20 | 346 | -0.096 | -0.013 | 0.132 | 0.195 | 0.601 | 1.000 | False |  |
| disp_a100 | 1 | 382 | -0.022 | -0.011 | 0.747 | 0.534 | 0.453 | 1.000 | False |  |
| disp_a100 | 5 | 376 | -0.032 | -0.003 | 0.210 | 0.331 | 0.564 | 1.000 | False |  |
| disp_a100 | 20 | 346 | -0.101 | -0.017 | 0.120 | 0.184 | 0.572 | 1.000 | False |  |
| disp_h100 | 1 | 382 | -0.038 | -0.026 | 0.939 | 0.959 | 0.445 | 1.000 | False |  |
| disp_h100 | 5 | 376 | -0.063 | -0.033 | 0.229 | 0.612 | 0.574 | 1.000 | False |  |
| disp_h100 | 20 | 346 | -0.110 | -0.026 | 0.111 | 0.139 | 0.584 | 1.000 | False |  |

## Gate G3: long-short strategy, net of claim 4's costs

| signal | h | windows | trades | Sharpe | 95% CI | passes | 0x | 0.5x | 1x | 2x | 4x |
|---|---|---|---|---|---|---|---|---|---|---|---|
| level_a100 | 1 | 382 | 81 | -0.198 | [-2.10, 1.37] | False | 0.067 | 0.025 | -0.016 | -0.099 | -0.264 |
| level_a100 | 5 | 376 | 356 | 0.366 | [-0.84, 1.62] | False | 0.687 | 0.501 | 0.315 | -0.057 | -0.801 |
| level_a100 | 20 | 346 | 333 | 0.953 | [-0.44, 2.29] | False | 3.972 | 3.767 | 3.562 | 3.152 | 2.332 |
| level_h100 | 1 | 382 | 32 | -0.127 | [-1.31, 1.14] | False | 0.026 | 0.010 | -0.006 | -0.039 | -0.103 |
| level_h100 | 5 | 376 | 367 | 0.604 | [-0.62, 1.86] | False | 0.907 | 0.716 | 0.525 | 0.144 | -0.618 |
| level_h100 | 20 | 346 | 344 | 1.034 | [-0.24, 2.28] | False | 4.454 | 4.243 | 4.031 | 3.607 | 2.760 |
| disp_a100 | 1 | 382 | 40 | -0.573 | [-1.72, 1.07] | False | 0.001 | -0.019 | -0.040 | -0.081 | -0.162 |
| disp_a100 | 5 | 376 | 347 | 0.395 | [-0.80, 1.64] | False | 0.699 | 0.519 | 0.338 | -0.022 | -0.743 |
| disp_a100 | 20 | 346 | 339 | 0.951 | [-0.39, 2.22] | False | 4.078 | 3.868 | 3.658 | 3.239 | 2.400 |
| disp_h100 | 1 | 382 | 16 | -0.256 | [-1.13, 0.64] | False | 0.006 | -0.002 | -0.010 | -0.026 | -0.059 |
| disp_h100 | 5 | 376 | 351 | 0.407 | [-0.78, 1.66] | False | 0.712 | 0.529 | 0.346 | -0.019 | -0.750 |
| disp_h100 | 20 | 346 | 339 | 0.800 | [-0.27, 1.87] | False | 3.575 | 3.362 | 3.148 | 2.722 | 1.868 |

## Gate

| pair | G1 | G2 | G3 | G4 | validated |
|---|---|---|---|---|---|
| level_a100|h1 | False | False | False | True | False |
| level_a100|h5 | False | False | False | True | False |
| level_a100|h20 | False | False | False | True | False |
| level_h100|h1 | False | False | False | True | False |
| level_h100|h5 | False | False | False | True | False |
| level_h100|h20 | False | False | False | True | False |
| disp_a100|h1 | False | False | False | True | False |
| disp_a100|h5 | False | False | False | True | False |
| disp_a100|h20 | False | False | False | True | False |
| disp_h100|h1 | False | False | False | True | False |
| disp_h100|h5 | False | False | False | True | False |
| disp_h100|h20 | False | False | False | True | False |

## Family S: bucket baskets (secondary; cannot open the gate)

p adj: Benjamini-Hochberg over the 36 tests.

| target | signal | h | n | non-zero | slope | rho | rho 95% CI | p HAC | p adj | p perm | passes | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neocloud | level_a100 | 1 | 402 | 397 | 0.112 | 0.045 | [-0.06, 0.14] | 0.397 | 0.579 | 0.393 | False |  |
| neocloud | level_a100 | 5 | 400 | 395 | 0.163 | 0.026 | [-0.09, 0.14] | 0.661 | 0.771 | 0.788 | False |  |
| neocloud | level_a100 | 20 | 385 | 380 | 0.761 | 0.054 | [-0.15, 0.23] | 0.603 | 0.748 | 0.738 | False |  |
| neocloud | level_h100 | 1 | 402 | 324 | -0.130 | -0.065 | [-0.17, 0.04] | 0.208 | 0.467 | 0.174 | False |  |
| neocloud | level_h100 | 5 | 400 | 324 | -0.154 | -0.031 | [-0.18, 0.13] | 0.695 | 0.782 | 0.691 | False |  |
| neocloud | level_h100 | 20 | 385 | 324 | -0.937 | -0.083 | [-0.27, 0.13] | 0.311 | 0.509 | 0.582 | False |  |
| neocloud | disp_a100 | 1 | 402 | 402 | -0.042 | -0.033 | [-0.13, 0.07] | 0.481 | 0.642 | 0.535 | False |  |
| neocloud | disp_a100 | 5 | 400 | 400 | -0.333 | -0.104 | [-0.22, 0.02] | 0.089 | 0.427 | 0.087 | False |  |
| neocloud | disp_a100 | 20 | 385 | 385 | -1.224 | -0.170 | [-0.34, 0.01] | 0.096 | 0.427 | 0.006 | False |  |
| neocloud | disp_h100 | 1 | 402 | 402 | -0.033 | -0.047 | [-0.11, 0.07] | 0.148 | 0.450 | 0.299 | False |  |
| neocloud | disp_h100 | 5 | 400 | 400 | -0.007 | -0.004 | [-0.09, 0.12] | 0.921 | 0.947 | 0.946 | False |  |
| neocloud | disp_h100 | 20 | 385 | 385 | 0.325 | 0.081 | [-0.05, 0.23] | 0.176 | 0.450 | 0.363 | False |  |
| gpu_semis | level_a100 | 1 | 402 | 397 | 0.033 | 0.047 | [-0.04, 0.13] | 0.255 | 0.494 | 0.303 | False |  |
| gpu_semis | level_a100 | 5 | 400 | 395 | 0.117 | 0.058 | [-0.05, 0.17] | 0.293 | 0.502 | 0.439 | False |  |
| gpu_semis | level_a100 | 20 | 385 | 380 | -0.270 | -0.083 | [-0.24, 0.07] | 0.288 | 0.502 | 0.516 | False |  |
| gpu_semis | level_h100 | 1 | 402 | 324 | -0.024 | -0.042 | [-0.14, 0.06] | 0.419 | 0.579 | 0.346 | False |  |
| gpu_semis | level_h100 | 5 | 400 | 324 | 0.030 | 0.018 | [-0.12, 0.16] | 0.798 | 0.871 | 0.796 | False |  |
| gpu_semis | level_h100 | 20 | 385 | 324 | -0.179 | -0.069 | [-0.22, 0.11] | 0.350 | 0.548 | 0.562 | False |  |
| gpu_semis | disp_a100 | 1 | 402 | 402 | -0.001 | -0.004 | [-0.08, 0.08] | 0.917 | 0.947 | 0.925 | False |  |
| gpu_semis | disp_a100 | 5 | 400 | 400 | -0.062 | -0.061 | [-0.16, 0.04] | 0.256 | 0.494 | 0.380 | False |  |
| gpu_semis | disp_a100 | 20 | 385 | 385 | -0.250 | -0.150 | [-0.28, 0.00] | 0.034 | 0.427 | 0.035 | False |  |
| gpu_semis | disp_h100 | 1 | 402 | 402 | 0.010 | 0.049 | [-0.06, 0.11] | 0.117 | 0.427 | 0.281 | False |  |
| gpu_semis | disp_h100 | 5 | 400 | 400 | 0.016 | 0.028 | [-0.06, 0.15] | 0.513 | 0.659 | 0.643 | False |  |
| gpu_semis | disp_h100 | 20 | 385 | 385 | 0.084 | 0.091 | [-0.03, 0.24] | 0.150 | 0.450 | 0.187 | False |  |
| power_capacity | level_a100 | 1 | 402 | 397 | 0.131 | 0.088 | [-0.01, 0.18] | 0.063 | 0.427 | 0.057 | False |  |
| power_capacity | level_a100 | 5 | 400 | 395 | 0.364 | 0.100 | [-0.01, 0.20] | 0.077 | 0.427 | 0.196 | False |  |
| power_capacity | level_a100 | 20 | 385 | 380 | -0.012 | -0.002 | [-0.18, 0.17] | 0.986 | 0.986 | 0.991 | False |  |
| power_capacity | level_h100 | 1 | 402 | 324 | -0.116 | -0.097 | [-0.21, 0.02] | 0.119 | 0.427 | 0.037 | False |  |
| power_capacity | level_h100 | 5 | 400 | 324 | -0.283 | -0.096 | [-0.26, 0.08] | 0.261 | 0.494 | 0.199 | False |  |
| power_capacity | level_h100 | 20 | 385 | 324 | -0.777 | -0.130 | [-0.30, 0.10] | 0.173 | 0.450 | 0.308 | False |  |
| power_capacity | disp_a100 | 1 | 402 | 402 | 0.014 | 0.019 | [-0.06, 0.11] | 0.664 | 0.771 | 0.734 | False |  |
| power_capacity | disp_a100 | 5 | 400 | 400 | -0.166 | -0.089 | [-0.19, 0.01] | 0.100 | 0.427 | 0.128 | False |  |
| power_capacity | disp_a100 | 20 | 385 | 385 | -0.338 | -0.088 | [-0.24, 0.04] | 0.188 | 0.450 | 0.216 | False |  |
| power_capacity | disp_h100 | 1 | 402 | 402 | 0.014 | 0.033 | [-0.02, 0.14] | 0.414 | 0.579 | 0.455 | False |  |
| power_capacity | disp_h100 | 5 | 400 | 400 | 0.141 | 0.135 | [0.06, 0.29] | 0.097 | 0.427 | 0.026 | False |  |
| power_capacity | disp_h100 | 20 | 385 | 385 | 0.268 | 0.125 | [0.02, 0.28] | 0.098 | 0.427 | 0.035 | False |  |

## Diagnostic: cross-correlogram (descriptive, not a test)

corr(signal at session t, basket excess return of session t+k); k < 0: returns before the signal was known.

| k | level_a100 | level_h100 |
|---|---|---|
| -5 | -0.04 [-0.14, 0.07] | -0.05 [-0.16, 0.08] |
| -4 | 0.01 [-0.08, 0.09] | -0.02 [-0.10, 0.07] |
| -3 | -0.00 [-0.09, 0.08] | -0.04 [-0.14, 0.06] |
| -2 | 0.03 [-0.06, 0.11] | -0.05 [-0.14, 0.04] |
| -1 | 0.03 [-0.05, 0.12] | -0.00 [-0.10, 0.09] |
| 0 | 0.07 [-0.04, 0.17] | -0.08 [-0.19, 0.03] |
| 1 | 0.04 [-0.05, 0.12] | -0.03 [-0.12, 0.06] |
| 2 | 0.02 [-0.07, 0.10] | -0.03 [-0.12, 0.07] |
| 3 | -0.03 [-0.11, 0.04] | -0.09 [-0.20, 0.04] |
| 4 | -0.01 [-0.10, 0.08] | -0.02 [-0.11, 0.06] |
| 5 | -0.01 [-0.09, 0.08] | -0.09 [-0.20, 0.01] |

