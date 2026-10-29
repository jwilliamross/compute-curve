# GPU1/GPU2 balance-of-month fair value

As of 2026-10-29. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 21/22 | 3.520 | 3.537 | 3.529-3.545 | - | - |
| 2026-11 | 0/21 | - | 3.900 | 3.377-4.504 | - | - |
| 2026-12 | 0/23 | - | 3.900 | 2.974-5.114 | - | - |
| 2027-01 | 0/21 | - | 3.900 | 2.728-5.576 | - | - |

Daily volatility used: 0.0300 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 21/22 | 7.923 | 7.942 | 7.932-7.953 | - | - |
| 2026-11 | 0/21 | - | 8.345 | 7.671-9.078 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.121-9.779 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 6.770-10.287 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
