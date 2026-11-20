# GPU1/GPU2 balance-of-month fair value

As of 2026-11-20. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 15/21 | 3.565 | 3.543 | 3.447-3.642 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.779-4.383 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.421-5.030 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.209-5.514 | - | - |

Daily volatility used: 0.0368 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 15/21 | 8.417 | 8.441 | 8.353-8.530 | - | - |
| 2026-12 | 0/23 | - | 8.500 | 7.790-9.275 | - | - |
| 2027-01 | 0/21 | - | 8.500 | 7.389-9.777 | - | - |
| 2027-02 | 0/20 | - | 8.500 | 7.134-10.128 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
