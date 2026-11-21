# SA2-M practice sheet for the session after 2026-11-20

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | LONG | +0.499 | +4,987 | hedge |
| NVDA | LONG | +0.100 | +1,000 | 12 / 0 |
| AVGO | SHORT | -0.083 | -833 | 0 / 10 |
| WULF | SHORT | -0.075 | -750 | 0 / 9 |
| CORZ | SHORT | -0.067 | -667 | 0 / 8 |
| AMD | SHORT | -0.058 | -583 | 0 / 7 |
| TLN | SHORT | -0.058 | -583 | 0 / 7 |
| SMCI | LONG | +0.050 | +500 | 6 / 0 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| VRT | SHORT | -0.033 | -333 | 0 / 4 |
| NBIS | LONG | +0.033 | +333 | 4 / 0 |
| APLD | SHORT | -0.025 | -250 | 0 / 3 |
| CBRS | SHORT | -0.025 | -250 | 0 / 3 |
| CIFR | SHORT | -0.025 | -250 | 0 / 3 |
| WYFI | SHORT | -0.017 | -167 | 0 / 2 |
| MU | SHORT | -0.017 | -167 | 0 / 2 |

Gross stock exposure 0.72 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| NVDA | -1.85 |
| IREN | -1.62 |
| NBIS | -1.34 |
| SMCI | -0.82 |
| TSM | -0.64 |
| BE | -0.49 |
| MRVL | -0.35 |
| MU | -0.28 |
| VST | -0.06 |
| CBRS | -0.04 |
| CIFR | +0.25 |
| WYFI | +0.29 |
| CRWV | +0.40 |
| CEG | +0.65 |
| APLD | +0.67 |
| AMD | +0.73 |
| CORZ | +0.95 |
| WULF | +0.97 |
| TLN | +1.03 |
| VRT | +1.12 |
| AVGO | +1.70 |
