# GPU1/GPU2 balance-of-month fair value

As of 2026-11-23. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 16/21 | 3.595 | 3.606 | 3.522-3.692 | - | - |
| 2026-12 | 0/23 | - | 3.640 | 2.859-4.635 | - | - |
| 2027-01 | 0/21 | - | 3.640 | 2.448-5.413 | - | - |
| 2027-02 | 0/20 | - | 3.640 | 2.210-5.996 | - | - |

Daily volatility used: 0.0405 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 16/21 | 8.426 | 8.455 | 8.386-8.525 | - | - |
| 2026-12 | 0/23 | - | 8.550 | 7.860-9.300 | - | - |
| 2027-01 | 0/21 | - | 8.550 | 7.447-9.816 | - | - |
| 2027-02 | 0/20 | - | 8.550 | 7.187-10.172 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
