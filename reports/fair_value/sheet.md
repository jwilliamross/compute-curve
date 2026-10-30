# GPU1/GPU2 balance-of-month fair value

As of 2026-10-30. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 22/22 | 3.545 | 3.545 | 3.545-3.545 | - | - |
| 2026-11 | 0/21 | - | 3.990 | 3.484-4.570 | - | - |
| 2026-12 | 0/23 | - | 3.990 | 3.054-5.213 | - | - |
| 2027-01 | 0/21 | - | 3.990 | 2.797-5.692 | - | - |

Daily volatility used: 0.0301 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 22/22 | 7.942 | 7.942 | 7.942-7.942 | - | - |
| 2026-11 | 0/21 | - | 8.345 | 7.710-9.032 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.140-9.753 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 6.783-10.266 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
