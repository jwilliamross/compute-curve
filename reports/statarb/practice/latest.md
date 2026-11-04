# SA2-M practice sheet for the session after 2026-11-03

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | LONG | +0.438 | +4,381 | hedge |
| CORZ | SHORT | -0.075 | -750 | 0 / 9 |
| AVGO | SHORT | -0.067 | -667 | 0 / 8 |
| MRVL | LONG | +0.067 | +667 | 8 / 0 |
| WULF | SHORT | -0.058 | -583 | 0 / 7 |
| VRT | SHORT | -0.050 | -500 | 0 / 6 |
| APLD | SHORT | -0.050 | -500 | 0 / 6 |
| TLN | SHORT | -0.050 | -500 | 0 / 6 |
| SMCI | LONG | +0.033 | +333 | 4 / 0 |
| NVDA | LONG | +0.025 | +250 | 3 / 0 |
| AMD | LONG | +0.017 | +167 | 2 / 0 |
| CEG | SHORT | -0.017 | -167 | 0 / 2 |
| MU | SHORT | -0.017 | -167 | 1 / 3 |
| IREN | LONG | +0.017 | +167 | 2 / 0 |
| TSM | SHORT | -0.017 | -167 | 0 / 2 |
| NBIS | SHORT | -0.008 | -83 | 2 / 3 |
| BE | SHORT | -0.008 | -83 | 0 / 1 |
| WYFI | SHORT | -0.008 | -83 | 0 / 1 |

Gross stock exposure 0.58 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| MRVL | -2.11 |
| SMCI | -1.04 |
| MU | -0.92 |
| NBIS | -0.88 |
| AMD | -0.69 |
| IREN | -0.59 |
| CRWV | -0.50 |
| BE | -0.35 |
| CIFR | -0.33 |
| TSM | -0.12 |
| NVDA | +0.21 |
| CEG | +0.31 |
| WYFI | +0.37 |
| VST | +0.48 |
| APLD | +0.48 |
| WULF | +0.74 |
| VRT | +1.21 |
| CORZ | +1.26 |
| TLN | +1.83 |
| AVGO | +2.75 |
