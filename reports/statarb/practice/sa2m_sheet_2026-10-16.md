# SA2-M practice sheet for the session after 2026-10-16

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | SHORT | -0.632 | -6,324 | hedge |
| SMCI | LONG | +0.067 | +667 | 8 / 0 |
| TLN | SHORT | -0.067 | -667 | 0 / 8 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| CIFR | LONG | +0.050 | +500 | 6 / 0 |
| CRWV | LONG | +0.042 | +417 | 5 / 0 |
| APLD | LONG | +0.033 | +333 | 4 / 0 |
| WYFI | LONG | +0.033 | +333 | 4 / 0 |
| VST | SHORT | -0.025 | -250 | 0 / 3 |
| VRT | LONG | +0.025 | +250 | 3 / 0 |
| TSM | LONG | +0.017 | +167 | 2 / 0 |
| BE | LONG | +0.017 | +167 | 2 / 0 |
| NBIS | LONG | +0.017 | +167 | 2 / 0 |
| CORZ | SHORT | -0.017 | -167 | 0 / 2 |
| AMD | SHORT | -0.008 | -83 | 0 / 1 |
| MRVL | SHORT | -0.008 | -83 | 0 / 1 |

Gross stock exposure 0.48 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| CRWV | -1.23 |
| IREN | -0.88 |
| SMCI | -0.86 |
| APLD | -0.82 |
| NBIS | -0.18 |
| WYFI | -0.14 |
| NVDA | -0.07 |
| CIFR | -0.07 |
| BE | -0.05 |
| TSM | +0.14 |
| AVGO | +0.26 |
| MRVL | +0.40 |
| CEG | +0.52 |
| VRT | +0.61 |
| WULF | +0.61 |
| MU | +0.63 |
| AMD | +1.06 |
| CORZ | +1.50 |
| TLN | +1.75 |
| VST | +1.92 |
