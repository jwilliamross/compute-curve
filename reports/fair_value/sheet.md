# GPU1/GPU2 balance-of-month fair value

As of 2026-11-10. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 7/21 | 3.554 | 3.611 | 3.330-3.917 | - | - |
| 2026-12 | 0/23 | - | 3.640 | 2.829-4.683 | - | - |
| 2027-01 | 0/21 | - | 3.640 | 2.547-5.202 | - | - |
| 2027-02 | 0/20 | - | 3.640 | 2.363-5.607 | - | - |

Daily volatility used: 0.0325 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 7/21 | 8.345 | 8.345 | 8.060-8.641 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.490-9.297 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 7.161-9.725 | - | - |
| 2027-02 | 0/20 | - | 8.345 | 6.934-10.043 | - | - |

Daily volatility used: 0.0139 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
