# SA2-M practice sheet for the session after 2026-11-27

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| SMCI | LONG | +0.050 | +500 | 6 / 0 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| NBIS | LONG | +0.050 | +500 | 6 / 0 |
| VRT | SHORT | -0.033 | -333 | 0 / 4 |
| WULF | SHORT | -0.033 | -333 | 0 / 4 |
| XLK | SHORT | -0.028 | -278 | hedge |
| CBRS | SHORT | -0.025 | -250 | 0 / 3 |
| CIFR | SHORT | -0.025 | -250 | 0 / 3 |
| TLN | SHORT | -0.025 | -250 | 0 / 3 |
| CEG | LONG | +0.017 | +167 | 2 / 0 |
| CORZ | SHORT | -0.017 | -167 | 0 / 2 |
| CRWV | SHORT | -0.008 | -83 | 0 / 1 |
| AMD | SHORT | -0.008 | -83 | 2 / 3 |
| AVGO | SHORT | -0.008 | -83 | 0 / 1 |
| VST | SHORT | -0.008 | -83 | 0 / 1 |

Gross stock exposure 0.36 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| NBIS | -1.77 |
| AMD | -1.32 |
| MRVL | -0.91 |
| IREN | -0.91 |
| SMCI | -0.82 |
| BE | -0.51 |
| WYFI | -0.31 |
| TSM | -0.10 |
| NVDA | -0.09 |
| MU | +0.06 |
| VST | +0.18 |
| CIFR | +0.23 |
| CRWV | +0.39 |
| CEG | +0.41 |
| APLD | +0.45 |
| CBRS | +0.54 |
| CORZ | +0.56 |
| TLN | +0.79 |
| AVGO | +0.80 |
| WULF | +0.83 |
| VRT | +0.95 |
