# SA2-M practice sheet for the session after 2026-10-19

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | SHORT | -0.609 | -6,089 | hedge |
| SMCI | LONG | +0.067 | +667 | 8 / 0 |
| TLN | SHORT | -0.067 | -667 | 0 / 8 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| CIFR | LONG | +0.050 | +500 | 6 / 0 |
| CRWV | LONG | +0.042 | +417 | 5 / 0 |
| APLD | LONG | +0.033 | +333 | 4 / 0 |
| WYFI | LONG | +0.033 | +333 | 4 / 0 |
| VST | SHORT | -0.025 | -250 | 0 / 3 |
| VRT | LONG | +0.025 | +250 | 3 / 0 |
| BE | LONG | +0.017 | +167 | 2 / 0 |
| NBIS | LONG | +0.017 | +167 | 2 / 0 |
| CORZ | SHORT | -0.017 | -167 | 0 / 2 |
| MRVL | SHORT | -0.017 | -167 | 0 / 2 |
| CBRS | LONG | +0.008 | +83 | 1 / 0 |
| AMD | SHORT | -0.008 | -83 | 0 / 1 |

Gross stock exposure 0.48 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| CRWV | -1.84 |
| IREN | -0.99 |
| SMCI | -0.89 |
| WYFI | -0.88 |
| APLD | -0.85 |
| NBIS | -0.84 |
| BE | -0.81 |
| CIFR | -0.27 |
| NVDA | -0.02 |
| TSM | -0.02 |
| CEG | +0.11 |
| MRVL | +0.13 |
| VRT | +0.32 |
| AVGO | +0.33 |
| WULF | +0.48 |
| MU | +0.51 |
| AMD | +0.76 |
| CORZ | +1.30 |
| TLN | +1.47 |
| VST | +1.49 |
