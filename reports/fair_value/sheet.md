# GPU1/GPU2 balance-of-month fair value

As of 2026-10-20. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 14/22 | 3.447 | 3.463 | 3.366-3.562 | - | - |
| 2026-11 | 0/21 | - | 3.490 | 2.938-4.145 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.674-4.555 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.491-4.889 | - | - |

Daily volatility used: 0.0266 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 14/22 | 7.738 | 7.880 | 7.734-8.029 | - | - |
| 2026-11 | 0/21 | - | 8.130 | 7.256-9.108 | - | - |
| 2026-12 | 0/23 | - | 8.130 | 6.818-9.693 | - | - |
| 2027-01 | 0/21 | - | 8.130 | 6.507-10.156 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
