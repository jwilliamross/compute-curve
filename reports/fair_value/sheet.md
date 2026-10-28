# GPU1/GPU2 balance-of-month fair value

As of 2026-10-28. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 20/22 | 3.501 | 3.537 | 3.520-3.555 | - | - |
| 2026-11 | 0/21 | - | 3.900 | 3.350-4.541 | - | - |
| 2026-12 | 0/23 | - | 3.900 | 2.961-5.137 | - | - |
| 2027-01 | 0/21 | - | 3.900 | 2.718-5.595 | - | - |

Daily volatility used: 0.0300 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 20/22 | 7.902 | 7.942 | 7.919-7.966 | - | - |
| 2026-11 | 0/21 | - | 8.345 | 7.634-9.122 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.103-9.805 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 6.756-10.307 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
