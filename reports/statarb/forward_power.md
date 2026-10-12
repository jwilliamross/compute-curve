# Claim 6c forward test: power (design calculation, no test)

Joint circular block bootstrap (block 20, 2000 resamples, seed 20261005) of the spent confirmation series, each shifted to theta x its observed mean; the frozen forward rule is applied to each resample. Method: docs/statarb_forward_power.md.

| Series | Mean (bps/day) | Daily Sharpe | t (iid) | t (Newey-West) | t (5/10/20-day block means) | Sum of autocorrelations, lags 1-10 |
|---|---|---|---|---|---|---|
| SA2-M (weights) | 10.56 | 0.113 | 1.42 | 2.30 | 2.19/2.38/2.08 | -0.39 |
| SA2-M (shares) | 10.36 | 0.113 | 1.43 | 2.35 | 2.28/2.40/2.46 | -0.45 |
| SA2-L (weights) | 4.93 | 0.109 | 1.37 | 1.66 | 1.52/1.71/1.32 | -0.27 |
| SA2-L (shares) | 4.66 | 0.101 | 1.26 | 1.58 | 1.40/1.52/1.14 | -0.28 |

## P(forward pass under both accountings)

| Sessions | Strategy | theta = 0 | theta = 0.25 | theta = 0.5 | theta = 0.75 | theta = 1 |
|---|---|---|---|---|---|---|
| 60 | SA2-M | 0.015 | 0.042 | 0.093 | 0.167 | 0.279 |
| 60 | SA2-L | 0.057 | 0.097 | 0.151 | 0.227 | 0.301 |
| 120 | SA2-M | 0.006 | 0.041 | 0.118 | 0.273 | 0.493 |
| 120 | SA2-L | 0.043 | 0.098 | 0.170 | 0.275 | 0.393 |
| 250 | SA2-M | 0.004 | 0.045 | 0.224 | 0.562 | 0.845 |
| 250 | SA2-L | 0.036 | 0.099 | 0.221 | 0.411 | 0.602 |

theta = 0 is the false-pass rate if there is no edge; theta = 1 assumes the confirmation's edge persists in full.
