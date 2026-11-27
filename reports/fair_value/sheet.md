# GPU1/GPU2 balance-of-month fair value

As of 2026-11-27. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 20/21 | 3.604 | 3.606 | 3.594-3.617 | - | - |
| 2026-12 | 0/23 | - | 3.640 | 2.975-4.453 | - | - |
| 2027-01 | 0/21 | - | 3.640 | 2.505-5.289 | - | - |
| 2027-02 | 0/20 | - | 3.640 | 2.250-5.888 | - | - |

Daily volatility used: 0.0405 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 20/21 | 8.451 | 8.455 | 8.446-8.465 | - | - |
| 2026-12 | 0/23 | - | 8.550 | 7.969-9.173 | - | - |
| 2027-01 | 0/21 | - | 8.550 | 7.505-9.741 | - | - |
| 2027-02 | 0/20 | - | 8.550 | 7.230-10.112 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
