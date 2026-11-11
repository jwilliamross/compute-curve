# GPU1/GPU2 balance-of-month fair value

As of 2026-11-11. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 8/21 | 3.630 | 3.797 | 3.521-4.094 | - | - |
| 2026-12 | 0/23 | - | 3.900 | 3.024-5.030 | - | - |
| 2027-01 | 0/21 | - | 3.900 | 2.708-5.617 | - | - |
| 2027-02 | 0/20 | - | 3.900 | 2.504-6.074 | - | - |

Daily volatility used: 0.0336 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 8/21 | 8.345 | 8.345 | 8.088-8.610 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.509-9.274 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 7.173-9.709 | - | - |
| 2027-02 | 0/20 | - | 8.345 | 6.944-10.029 | - | - |

Daily volatility used: 0.0139 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
