# SA2-M practice sheet for the session after 2026-11-25

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| SMCI | LONG | +0.050 | +500 | 6 / 0 |
| IREN | LONG | +0.050 | +500 | 6 / 0 |
| NBIS | LONG | +0.050 | +500 | 6 / 0 |
| VRT | SHORT | -0.033 | -333 | 0 / 4 |
| CBRS | SHORT | -0.025 | -250 | 0 / 3 |
| CIFR | SHORT | -0.025 | -250 | 0 / 3 |
| AMD | SHORT | -0.025 | -250 | 0 / 3 |
| TLN | SHORT | -0.025 | -250 | 0 / 3 |
| WULF | SHORT | -0.025 | -250 | 0 / 3 |
| CORZ | SHORT | -0.017 | -167 | 0 / 2 |
| CRWV | SHORT | -0.008 | -83 | 0 / 1 |
| CEG | LONG | +0.008 | +83 | 1 / 0 |
| AVGO | SHORT | -0.008 | -83 | 0 / 1 |
| VST | SHORT | -0.008 | -83 | 0 / 1 |
| XLK | SHORT | -0.005 | -47 | hedge |

Gross stock exposure 0.36 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| NBIS | -1.83 |
| IREN | -1.07 |
| AMD | -0.98 |
| MRVL | -0.93 |
| BE | -0.65 |
| SMCI | -0.60 |
| MU | -0.57 |
| WYFI | -0.13 |
| NVDA | -0.01 |
| CIFR | +0.03 |
| TSM | +0.04 |
| VST | +0.06 |
| APLD | +0.28 |
| CBRS | +0.30 |
| CORZ | +0.32 |
| CEG | +0.45 |
| CRWV | +0.50 |
| WULF | +0.54 |
| TLN | +0.85 |
| VRT | +0.96 |
| AVGO | +1.00 |
