# GPU1/GPU2 balance-of-month fair value

As of 2026-10-22. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 16/22 | 3.452 | 3.463 | 3.398-3.529 | - | - |
| 2026-11 | 0/21 | - | 3.490 | 2.974-4.095 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.697-4.517 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.510-4.854 | - | - |

Daily volatility used: 0.0264 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 16/22 | 7.796 | 7.903 | 7.805-8.003 | - | - |
| 2026-11 | 0/21 | - | 8.190 | 7.366-9.106 | - | - |
| 2026-12 | 0/23 | - | 8.190 | 6.902-9.718 | - | - |
| 2027-01 | 0/21 | - | 8.190 | 6.581-10.193 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
