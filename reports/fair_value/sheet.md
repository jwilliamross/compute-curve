# GPU1/GPU2 balance-of-month fair value

As of 2026-10-23. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 17/22 | 3.455 | 3.463 | 3.412-3.514 | - | - |
| 2026-11 | 0/21 | - | 3.490 | 2.992-4.070 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.707-4.500 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.517-4.840 | - | - |

Daily volatility used: 0.0264 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 17/22 | 7.824 | 7.916 | 7.840-7.994 | - | - |
| 2026-11 | 0/21 | - | 8.231 | 7.433-9.115 | - | - |
| 2026-12 | 0/23 | - | 8.231 | 6.954-9.743 | - | - |
| 2027-01 | 0/21 | - | 8.231 | 6.627-10.224 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
