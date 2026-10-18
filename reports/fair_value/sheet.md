# GPU1/GPU2 balance-of-month fair value

As of 2026-10-18. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 12/22 | 3.440 | 3.463 | 3.345-3.585 | - | - |
| 2026-11 | 0/21 | - | 3.490 | 2.922-4.168 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.664-4.572 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.484-4.903 | - | - |

Daily volatility used: 0.0266 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-10 | 12/22 | 7.673 | 7.862 | 7.684-8.044 | - | - |
| 2026-11 | 0/21 | - | 8.089 | 7.194-9.096 | - | - |
| 2026-12 | 0/23 | - | 8.089 | 6.768-9.669 | - | - |
| 2027-01 | 0/21 | - | 8.089 | 6.463-10.126 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
