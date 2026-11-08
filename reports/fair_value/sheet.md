# GPU1/GPU2 balance-of-month fair value

As of 2026-11-08. Method: docs/bom_plan.md. Driftless random walk for the days not yet averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own index, not Silicon Data's: its level differs (basis risk). Research only; no orders.

### GPU1 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 5/21 | 3.520 | 3.611 | 3.298-3.955 | - | - |
| 2026-12 | 0/23 | - | 3.640 | 2.813-4.710 | - | - |
| 2027-01 | 0/21 | - | 3.640 | 2.537-5.223 | - | - |
| 2027-02 | 0/20 | - | 3.640 | 2.355-5.626 | - | - |

Daily volatility used: 0.0325 (60 daily changes).

### GPU2 (proxy: our own index)

| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |
|---|---|---|---|---|---|---|
| 2026-11 | 5/21 | 8.345 | 8.345 | 8.026-8.676 | - | - |
| 2026-12 | 0/23 | - | 8.345 | 7.472-9.320 | - | - |
| 2027-01 | 0/21 | - | 8.345 | 7.148-9.742 | - | - |
| 2027-02 | 0/20 | - | 8.345 | 6.924-10.058 | - | - |

Daily volatility used: 0.0139 (60 daily changes).

FP-C (balance-of-month trade, needs licensed SD values): 0 settled traded decisions. No CME settlements yet; waiting.
