# GPU1/GPU2 balance-of-month fair value

As of 2026-11-26. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 19/21 | 3.602 | 3.606 | 3.580-3.631 | - | - |
| 2026-12 | 0/23 | - | 3.640 | 2.944-4.501 | - | - |
| 2027-01 | 0/21 | - | 3.640 | 2.490-5.321 | - | - |
| 2027-02 | 0/20 | - | 3.640 | 2.240-5.915 | - | - |

Daily volatility used: 0.0405 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 19/21 | 8.445 | 8.455 | 8.434-8.476 | - | - |
| 2026-12 | 0/23 | - | 8.550 | 7.940-9.207 | - | - |
| 2027-01 | 0/21 | - | 8.550 | 7.490-9.760 | - | - |
| 2027-02 | 0/20 | - | 8.550 | 7.219-10.127 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
