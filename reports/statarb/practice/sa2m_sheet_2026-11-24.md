# SA2-M practice sheet for the session after 2026-11-24

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| SMCI | LONG | +0.050 | +500 | 6 / 0 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| NBIS | LONG | +0.050 | +500 | 6 / 0 |
| VRT | SHORT | -0.033 | -333 | 0 / 4 |
| WULF | SHORT | -0.033 | -333 | 0 / 4 |
| CBRS | SHORT | -0.025 | -250 | 0 / 3 |
| CIFR | SHORT | -0.025 | -250 | 0 / 3 |
| AMD | SHORT | -0.025 | -250 | 0 / 3 |
| TLN | SHORT | -0.025 | -250 | 0 / 3 |
| AVGO | SHORT | -0.017 | -167 | 0 / 2 |
| CRWV | SHORT | -0.008 | -83 | 0 / 1 |
| CORZ | SHORT | -0.008 | -83 | 0 / 1 |
| XLK | LONG | +0.007 | +66 | hedge |

Gross stock exposure 0.35 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| NBIS | -1.98 |
| IREN | -1.48 |
| SMCI | -1.34 |
| MRVL | -0.98 |
| AMD | -0.94 |
| BE | -0.76 |
| VST | -0.30 |
| MU | -0.29 |
| TSM | -0.14 |
| CIFR | -0.11 |
| WYFI | +0.02 |
| APLD | +0.03 |
| NVDA | +0.09 |
| CBRS | +0.12 |
| CORZ | +0.15 |
| CRWV | +0.38 |
| WULF | +0.42 |
| CEG | +0.45 |
| TLN | +0.63 |
| VRT | +0.78 |
| AVGO | +0.92 |
