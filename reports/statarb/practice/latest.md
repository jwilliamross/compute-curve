# SA2-M practice sheet for the session after 2026-11-04

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | LONG | +0.092 | +920 | hedge |
| CORZ | SHORT | -0.075 | -750 | 0 / 9 |
| AVGO | SHORT | -0.067 | -667 | 0 / 8 |
| MRVL | LONG | +0.067 | +667 | 8 / 0 |
| WULF | SHORT | -0.058 | -583 | 0 / 7 |
| TLN | SHORT | -0.050 | -500 | 0 / 6 |
| SMCI | LONG | +0.042 | +417 | 5 / 0 |
| VRT | SHORT | -0.033 | -333 | 0 / 4 |
| NVDA | LONG | +0.033 | +333 | 4 / 0 |
| APLD | SHORT | -0.025 | -250 | 0 / 3 |
| CRWV | LONG | +0.025 | +250 | 3 / 0 |
| NBIS | LONG | +0.017 | +167 | 2 / 0 |
| IREN | LONG | +0.017 | +167 | 2 / 0 |
| CIFR | LONG | +0.017 | +167 | 2 / 0 |
| TSM | SHORT | -0.017 | -167 | 0 / 2 |
| MU | LONG | +0.008 | +83 | 4 / 3 |

Gross stock exposure 0.55 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| MRVL | -2.21 |
| MU | -2.00 |
| CRWV | -1.20 |
| CIFR | -1.13 |
| SMCI | -1.07 |
| IREN | -1.01 |
| NBIS | -0.91 |
| VST | -0.72 |
| NVDA | -0.70 |
| BE | -0.62 |
| TSM | -0.61 |
| CBRS | -0.59 |
| AMD | -0.55 |
| CEG | -0.16 |
| WYFI | +0.04 |
| APLD | +0.29 |
| WULF | +0.60 |
| VRT | +0.75 |
| CORZ | +0.97 |
| TLN | +1.14 |
| AVGO | +2.24 |
