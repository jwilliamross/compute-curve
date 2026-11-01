# GPU1/GPU2 balance-of-month fair value

As of 2026-11-01. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 0/21 | - | 3.490 | 3.027-4.024 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.601-4.683 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.354-5.174 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.187-5.570 | - | - |

Daily volatility used: 0.0337 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 0/21 | - | 8.345 | 7.748-8.987 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.159-9.727 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 6.797-10.245 | - | - |
| 2027-02 | 0/20 | - | 8.345 | 6.541-10.646 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
