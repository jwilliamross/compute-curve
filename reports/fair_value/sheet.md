# GPU1/GPU2 balance-of-month fair value

As of 2026-11-12. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 9/21 | 3.660 | 3.797 | 3.551-4.061 | - | - |
| 2026-12 | 0/23 | - | 3.900 | 3.042-5.000 | - | - |
| 2027-01 | 0/21 | - | 3.900 | 2.719-5.593 | - | - |
| 2027-02 | 0/20 | - | 3.900 | 2.513-6.053 | - | - |

Daily volatility used: 0.0336 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 9/21 | 8.345 | 8.345 | 8.116-8.581 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.528-9.251 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 7.185-9.692 | - | - |
| 2027-02 | 0/20 | - | 8.345 | 6.954-10.015 | - | - |

Daily volatility used: 0.0139 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
