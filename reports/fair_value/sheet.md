# GPU1/GPU2 balance-of-month fair value

As of 2026-11-18. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 13/21 | 3.576 | 3.543 | 3.400-3.692 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.736-4.451 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.398-5.080 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.191-5.558 | - | - |

Daily volatility used: 0.0368 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 13/21 | 8.405 | 8.441 | 8.309-8.575 | - | - |
| 2026-12 | 0/23 | - | 8.500 | 7.745-9.329 | - | - |
| 2027-01 | 0/21 | - | 8.500 | 7.363-9.812 | - | - |
| 2027-02 | 0/20 | - | 8.500 | 7.114-10.156 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
