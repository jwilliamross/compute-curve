# GPU1/GPU2 balance-of-month fair value

As of 2026-10-16. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 12/22 | 3.440 | 3.463 | 3.330-3.600 | - | - |
| 2026-11 | 0/21 | - | 3.490 | 2.907-4.190 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.655-4.588 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.477-4.916 | - | - |

Daily volatility used: 0.0266 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 12/22 | 7.665 | 7.813 | 7.615-8.017 | - | - |
| 2026-11 | 0/21 | - | 7.992 | 7.082-9.018 | - | - |
| 2026-12 | 0/23 | - | 7.992 | 6.670-9.574 | - | - |
| 2027-01 | 0/21 | - | 7.992 | 6.372-10.022 | - | - |

Daily volatility used: 0.0176 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
