# GPU1/GPU2 balance-of-month fair value

As of 2026-11-19. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 14/21 | 3.570 | 3.543 | 3.425-3.666 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.757-4.417 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.409-5.055 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.200-5.536 | - | - |

Daily volatility used: 0.0368 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 14/21 | 8.411 | 8.441 | 8.332-8.552 | - | - |
| 2026-12 | 0/23 | - | 8.500 | 7.767-9.302 | - | - |
| 2027-01 | 0/21 | - | 8.500 | 7.376-9.795 | - | - |
| 2027-02 | 0/20 | - | 8.500 | 7.124-10.142 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
