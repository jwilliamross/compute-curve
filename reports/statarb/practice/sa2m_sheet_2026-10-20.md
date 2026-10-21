# SA2-M practice sheet for the session after 2026-10-20

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | SHORT | -0.610 | -6,101 | hedge |
| SMCI | LONG | +0.067 | +667 | 8 / 0 |
| TLN | SHORT | -0.067 | -667 | 0 / 8 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| CIFR | LONG | +0.050 | +500 | 6 / 0 |
| CRWV | LONG | +0.042 | +417 | 5 / 0 |
| MRVL | SHORT | -0.033 | -333 | 0 / 4 |
| APLD | LONG | +0.033 | +333 | 4 / 0 |
| WYFI | LONG | +0.033 | +333 | 4 / 0 |
| VST | SHORT | -0.025 | -250 | 0 / 3 |
| VRT | LONG | +0.025 | +250 | 3 / 0 |
| BE | LONG | +0.017 | +167 | 2 / 0 |
| NBIS | LONG | +0.017 | +167 | 2 / 0 |
| CBRS | LONG | +0.017 | +167 | 2 / 0 |
| CORZ | SHORT | -0.017 | -167 | 0 / 2 |
| CEG | LONG | +0.008 | +83 | 1 / 0 |

Gross stock exposure 0.50 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| CRWV | -1.52 |
| IREN | -1.05 |
| NVDA | -0.94 |
| BE | -0.76 |
| SMCI | -0.76 |
| WYFI | -0.75 |
| NBIS | -0.57 |
| APLD | -0.54 |
| CIFR | -0.27 |
| CEG | -0.16 |
| MRVL | +0.19 |
| MU | +0.35 |
| VRT | +0.36 |
| TSM | +0.40 |
| AMD | +0.56 |
| WULF | +0.60 |
| AVGO | +0.70 |
| CORZ | +1.10 |
| TLN | +1.20 |
| VST | +1.37 |
