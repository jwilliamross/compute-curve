# GPU1/GPU2 balance-of-month fair value

As of 2026-11-03. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 2/21 | 3.490 | 3.490 | 3.061-3.979 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.614-4.659 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.363-5.154 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.194-5.552 | - | - |

Daily volatility used: 0.0337 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 2/21 | 8.345 | 8.345 | 7.794-8.935 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.179-9.700 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 6.811-10.225 | - | - |
| 2027-02 | 0/20 | - | 8.345 | 6.552-10.628 | - | - |

Daily volatility used: 0.0175 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
