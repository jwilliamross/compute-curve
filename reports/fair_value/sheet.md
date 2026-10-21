# GPU1/GPU2 balance-of-month fair value

As of 2026-10-21. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 15/22 | 3.450 | 3.463 | 3.382-3.545 | - | - |
| 2026-11 | 0/21 | - | 3.490 | 2.956-4.121 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.685-4.537 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.500-4.872 | - | - |

Daily volatility used: 0.0265 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 15/22 | 7.767 | 7.889 | 7.767-8.012 | - | - |
| 2026-11 | 0/21 | - | 8.149 | 7.301-9.096 | - | - |
| 2026-12 | 0/23 | - | 8.149 | 6.851-9.694 | - | - |
| 2027-01 | 0/21 | - | 8.149 | 6.536-10.162 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
