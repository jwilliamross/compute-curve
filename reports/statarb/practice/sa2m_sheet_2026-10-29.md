# SA2-M practice sheet for the session after 2026-10-29

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | SHORT | -0.557 | -5,572 | hedge |
| AVGO | SHORT | -0.058 | -583 | 0 / 7 |
| MRVL | LONG | +0.058 | +583 | 7 / 0 |
| CIFR | LONG | +0.050 | +500 | 6 / 0 |
| NBIS | LONG | +0.050 | +500 | 6 / 0 |
| CORZ | SHORT | -0.042 | -417 | 0 / 5 |
| NVDA | LONG | +0.042 | +417 | 5 / 0 |
| BE | LONG | +0.033 | +333 | 4 / 0 |
| SMCI | LONG | +0.033 | +333 | 4 / 0 |
| CRWV | LONG | +0.033 | +333 | 4 / 0 |
| CBRS | LONG | +0.025 | +250 | 3 / 0 |
| VRT | SHORT | -0.025 | -250 | 0 / 3 |
| IREN | LONG | +0.025 | +250 | 3 / 0 |
| WULF | SHORT | -0.025 | -250 | 0 / 3 |
| AMD | LONG | +0.017 | +167 | 2 / 0 |
| MU | LONG | +0.008 | +83 | 1 / 0 |
| TLN | SHORT | -0.008 | -83 | 0 / 1 |
| APLD | SHORT | -0.008 | -83 | 0 / 1 |

Gross stock exposure 0.54 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| SMCI | -1.72 |
| MRVL | -1.60 |
| IREN | -1.46 |
| CRWV | -1.22 |
| CIFR | -1.02 |
| NBIS | -0.96 |
| MU | -0.91 |
| NVDA | -0.73 |
| TSM | -0.70 |
| BE | -0.41 |
| CEG | -0.40 |
| VST | -0.31 |
| APLD | -0.27 |
| WYFI | -0.16 |
| AMD | +0.05 |
| WULF | +0.52 |
| TLN | +0.78 |
| VRT | +0.96 |
| CORZ | +1.56 |
| AVGO | +1.98 |
