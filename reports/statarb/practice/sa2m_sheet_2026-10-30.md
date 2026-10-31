# SA2-M practice sheet for the session after 2026-10-30

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | SHORT | -0.207 | -2,070 | hedge |
| AVGO | SHORT | -0.067 | -667 | 0 / 8 |
| MRVL | LONG | +0.058 | +583 | 7 / 0 |
| CIFR | LONG | +0.050 | +500 | 6 / 0 |
| CORZ | SHORT | -0.050 | -500 | 0 / 6 |
| VRT | SHORT | -0.042 | -417 | 0 / 5 |
| SMCI | LONG | +0.033 | +333 | 4 / 0 |
| CRWV | LONG | +0.033 | +333 | 4 / 0 |
| BE | LONG | +0.025 | +250 | 4 / 1 |
| TLN | SHORT | -0.025 | -250 | 0 / 3 |
| WULF | SHORT | -0.025 | -250 | 0 / 3 |
| NVDA | LONG | +0.025 | +250 | 3 / 0 |
| AMD | LONG | +0.017 | +167 | 2 / 0 |
| NBIS | LONG | +0.017 | +167 | 2 / 0 |
| MU | SHORT | -0.017 | -167 | 1 / 3 |
| IREN | LONG | +0.017 | +167 | 2 / 0 |
| APLD | SHORT | -0.017 | -167 | 0 / 2 |
| CEG | SHORT | -0.008 | -83 | 0 / 1 |

Gross stock exposure 0.53 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| MRVL | -1.50 |
| NBIS | -1.26 |
| CIFR | -1.11 |
| SMCI | -0.99 |
| IREN | -0.95 |
| CRWV | -0.94 |
| MU | -0.77 |
| TSM | -0.51 |
| BE | -0.49 |
| NVDA | -0.14 |
| AMD | -0.12 |
| CEG | -0.12 |
| APLD | -0.12 |
| WYFI | +0.02 |
| VST | +0.03 |
| WULF | +0.61 |
| VRT | +0.90 |
| TLN | +1.16 |
| CORZ | +1.48 |
| AVGO | +2.20 |
