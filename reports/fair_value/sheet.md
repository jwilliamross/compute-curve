# GPU1/GPU2 balance-of-month fair value

As of 2026-11-21. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 15/21 | 3.592 | 3.680 | 3.589-3.773 | - | - |
| 2026-12 | 0/23 | - | 3.900 | 3.083-4.933 | - | - |
| 2027-01 | 0/21 | - | 3.900 | 2.652-5.736 | - | - |
| 2027-02 | 0/20 | - | 3.900 | 2.401-6.335 | - | - |

Daily volatility used: 0.0394 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 15/21 | 8.417 | 8.441 | 8.366-8.517 | - | - |
| 2026-12 | 0/23 | - | 8.500 | 7.814-9.246 | - | - |
| 2027-01 | 0/21 | - | 8.500 | 7.404-9.759 | - | - |
| 2027-02 | 0/20 | - | 8.500 | 7.145-10.112 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
