# GPU1/GPU2 balance-of-month fair value

As of 2026-10-25. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 17/22 | 3.455 | 3.463 | 3.420-3.506 | - | - |
| 2026-11 | 0/21 | - | 3.490 | 3.011-4.045 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.717-4.483 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.524-4.826 | - | - |

Daily volatility used: 0.0264 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 17/22 | 7.824 | 7.935 | 7.870-8.001 | - | - |
| 2026-11 | 0/21 | - | 8.314 | 7.539-9.170 | - | - |
| 2026-12 | 0/23 | - | 8.314 | 7.041-9.819 | - | - |
| 2027-01 | 0/21 | - | 8.314 | 6.705-10.310 | - | - |

Daily volatility used: 0.0176 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
