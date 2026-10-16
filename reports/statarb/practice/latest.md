# SA2-M practice sheet for the session after 2026-10-15

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | SHORT | -0.755 | -7,545 | hedge |
| SMCI | LONG | +0.067 | +667 | 8 / 0 |
| TLN | SHORT | -0.067 | -667 | 0 / 8 |
| MU | LONG | +0.058 | +583 | 7 / 0 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| CIFR | LONG | +0.050 | +500 | 6 / 0 |
| CRWV | LONG | +0.042 | +417 | 5 / 0 |
| APLD | LONG | +0.033 | +333 | 4 / 0 |
| WYFI | LONG | +0.033 | +333 | 4 / 0 |
| TSM | LONG | +0.025 | +250 | 3 / 0 |
| VST | SHORT | -0.025 | -250 | 0 / 3 |
| VRT | LONG | +0.025 | +250 | 3 / 0 |
| BE | LONG | +0.017 | +167 | 2 / 0 |
| AMD | SHORT | -0.008 | -83 | 0 / 1 |
| CORZ | SHORT | -0.008 | -83 | 0 / 1 |
| NBIS | LONG | +0.008 | +83 | 1 / 0 |
| MRVL | SHORT | -0.008 | -83 | 0 / 1 |

Gross stock exposure 0.52 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| CRWV | -0.96 |
| SMCI | -0.96 |
| IREN | -0.78 |
| APLD | -0.71 |
| NVDA | -0.35 |
| WYFI | -0.27 |
| NBIS | -0.22 |
| CIFR | -0.14 |
| BE | -0.07 |
| TSM | +0.02 |
| VRT | +0.22 |
| MRVL | +0.26 |
| WULF | +0.28 |
| CEG | +0.33 |
| AVGO | +0.36 |
| MU | +0.41 |
| CORZ | +1.08 |
| AMD | +1.09 |
| TLN | +1.84 |
| VST | +2.00 |
