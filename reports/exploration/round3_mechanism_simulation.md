# Round 3: CGI aggregation mechanism check

**SYNTHETIC: mechanism check on simulated seat prices, not a result about CGI.** Plan: docs/exploration_round3_plan.md section 9.2.
20 seeds x 60 days of 15-minute stamps per row; seeds from the project seed.
Mean across seeds, with the 5th to 95th percentile in brackets.

| Seats | sd floor | Scenario | beta (6h on 6h) | VR(24) | ACF(1), 15 min |
|---|---|---|---|---|---|
| 17 | 0.03 | S0 aggregation only | -0.016 [-0.084, 0.061] | 0.997 [0.838, 1.073] | -0.003 [-0.021, 0.010] |
| 17 | 0.03 | S1 + one-stamp seat drop-outs (2%) | -0.377 [-0.423, -0.316] | 0.054 [0.048, 0.067] | -0.497 [-0.513, -0.481] |
| 17 | 0.03 | S2 + seat deviations (AR(1), 3h half-life, sd 0.03) | -0.311 [-0.352, -0.261] | 0.572 [0.521, 0.636] | -0.029 [-0.055, -0.007] |
| 17 | 0.03 | S3 = S2 + 1-hour EWMA on seat prices | -0.204 [-0.257, -0.149] | 5.484 [5.072, 5.878] | 0.788 [0.772, 0.802] |
| 17 | 0.06 | S0 aggregation only | -0.016 [-0.080, 0.056] | 0.995 [0.860, 1.061] | -0.005 [-0.022, 0.010] |
| 17 | 0.06 | S1 + one-stamp seat drop-outs (2%) | -0.377 [-0.422, -0.318] | 0.054 [0.048, 0.067] | -0.498 [-0.512, -0.484] |
| 17 | 0.06 | S2 + seat deviations (AR(1), 3h half-life, sd 0.03) | -0.303 [-0.339, -0.256] | 0.581 [0.527, 0.638] | -0.029 [-0.057, -0.007] |
| 17 | 0.06 | S3 = S2 + 1-hour EWMA on seat prices | -0.193 [-0.236, -0.141] | 5.517 [5.082, 5.929] | 0.789 [0.774, 0.803] |
| 9 | 0.03 | S0 aggregation only | -0.020 [-0.089, 0.076] | 0.985 [0.861, 1.096] | 0.002 [-0.013, 0.019] |
| 9 | 0.03 | S1 + one-stamp seat drop-outs (2%) | -0.404 [-0.455, -0.326] | 0.051 [0.046, 0.061] | -0.496 [-0.507, -0.484] |
| 9 | 0.03 | S2 + seat deviations (AR(1), 3h half-life, sd 0.03) | -0.341 [-0.392, -0.298] | 0.566 [0.514, 0.619] | -0.032 [-0.049, -0.010] |
| 9 | 0.03 | S3 = S2 + 1-hour EWMA on seat prices | -0.239 [-0.302, -0.194] | 5.460 [4.970, 5.931] | 0.786 [0.773, 0.801] |
| 9 | 0.06 | S0 aggregation only | -0.022 [-0.112, 0.099] | 0.988 [0.889, 1.100] | 0.003 [-0.009, 0.021] |
| 9 | 0.06 | S1 + one-stamp seat drop-outs (2%) | -0.407 [-0.455, -0.332] | 0.051 [0.046, 0.060] | -0.496 [-0.509, -0.483] |
| 9 | 0.06 | S2 + seat deviations (AR(1), 3h half-life, sd 0.03) | -0.338 [-0.390, -0.278] | 0.575 [0.521, 0.630] | -0.032 [-0.054, -0.008] |
| 9 | 0.06 | S3 = S2 + 1-hour EWMA on seat prices | -0.233 [-0.290, -0.166] | 5.498 [5.093, 5.966] | 0.786 [0.773, 0.798] |

## Pre-registered reading (section 9.2)

- 17 seats, sd 0.03: the aggregation rule alone can produce a reversal of the observed size.
- 17 seats, sd 0.06: the aggregation rule alone can produce a reversal of the observed size.
- 9 seats, sd 0.03: the aggregation rule alone can produce a reversal of the observed size.
- 9 seats, sd 0.06: the aggregation rule alone can produce a reversal of the observed size.
