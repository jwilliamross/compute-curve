# GPU1/GPU2 balance-of-month fair value

As of 2026-11-16. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 11/21 | 3.592 | 3.543 | 3.349-3.749 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.697-4.517 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.375-5.129 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.174-5.602 | - | - |

Daily volatility used: 0.0368 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 11/21 | 8.387 | 8.441 | 8.261-8.625 | - | - |
| 2026-12 | 0/23 | - | 8.500 | 7.702-9.380 | - | - |
| 2027-01 | 0/21 | - | 8.500 | 7.337-9.847 | - | - |
| 2027-02 | 0/20 | - | 8.500 | 7.094-10.184 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
