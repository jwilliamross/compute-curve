# GPU1/GPU2 balance-of-month fair value

As of 2026-11-24. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 17/21 | 3.598 | 3.606 | 3.544-3.669 | - | - |
| 2026-12 | 0/23 | - | 3.640 | 2.885-4.592 | - | - |
| 2027-01 | 0/21 | - | 3.640 | 2.462-5.382 | - | - |
| 2027-02 | 0/20 | - | 3.640 | 2.220-5.969 | - | - |

Daily volatility used: 0.0405 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 17/21 | 8.433 | 8.455 | 8.404-8.506 | - | - |
| 2026-12 | 0/23 | - | 8.550 | 7.886-9.270 | - | - |
| 2027-01 | 0/21 | - | 8.550 | 7.462-9.797 | - | - |
| 2027-02 | 0/20 | - | 8.550 | 7.198-10.156 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
