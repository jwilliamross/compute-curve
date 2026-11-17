# GPU1/GPU2 balance-of-month fair value

As of 2026-11-17. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 12/21 | 3.583 | 3.543 | 3.375-3.720 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.716-4.484 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.386-5.105 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.183-5.580 | - | - |

Daily volatility used: 0.0368 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 12/21 | 8.397 | 8.441 | 8.286-8.599 | - | - |
| 2026-12 | 0/23 | - | 8.500 | 7.724-9.354 | - | - |
| 2027-01 | 0/21 | - | 8.500 | 7.351-9.829 | - | - |
| 2027-02 | 0/20 | - | 8.500 | 7.105-10.169 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
