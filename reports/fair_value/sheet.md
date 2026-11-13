# GPU1/GPU2 balance-of-month fair value

As of 2026-11-13. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 10/21 | 3.602 | 3.543 | 3.321-3.781 | - | - |
| 2026-12 | 0/23 | - | 3.490 | 2.678-4.549 | - | - |
| 2027-01 | 0/21 | - | 3.490 | 2.363-5.154 | - | - |
| 2027-02 | 0/20 | - | 3.490 | 2.166-5.623 | - | - |

Daily volatility used: 0.0368 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 10/21 | 8.376 | 8.441 | 8.235-8.653 | - | - |
| 2026-12 | 0/23 | - | 8.500 | 7.682-9.405 | - | - |
| 2027-01 | 0/21 | - | 8.500 | 7.324-9.865 | - | - |
| 2027-02 | 0/20 | - | 8.500 | 7.084-10.199 | - | - |

Daily volatility used: 0.0141 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
