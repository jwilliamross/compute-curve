# GPU1/GPU2 balance-of-month fair value

As of 2026-11-06. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 5/21 | 3.490 | 3.490 | 3.166-3.847 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.691-4.526 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.434-5.005 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.263-5.383 | - | - |

Daily volatility used: 0.0321 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 5/21 | 8.345 | 8.345 | 8.000-8.705 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.455-9.342 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 7.136-9.759 | - | - |
| 2027-02 | 0/20 | - | 8.345 | 6.914-10.072 | - | - |

Daily volatility used: 0.0139 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
