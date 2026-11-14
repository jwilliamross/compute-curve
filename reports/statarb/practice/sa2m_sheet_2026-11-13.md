# SA2-M practice sheet for the session after 2026-11-13

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | LONG | +0.828 | +8,277 | hedge |
| NVDA | LONG | +0.092 | +917 | 11 / 0 |
| AVGO | SHORT | -0.067 | -667 | 0 / 8 |
| CORZ | SHORT | -0.067 | -667 | 0 / 8 |
| WULF | SHORT | -0.067 | -667 | 0 / 8 |
| AMD | SHORT | -0.067 | -667 | 0 / 8 |
| VRT | SHORT | -0.058 | -583 | 0 / 7 |
| TLN | SHORT | -0.058 | -583 | 0 / 7 |
| WYFI | SHORT | -0.058 | -583 | 0 / 7 |
| BE | SHORT | -0.050 | -500 | 0 / 6 |
| SMCI | LONG | +0.050 | +500 | 6 / 0 |
| MRVL | LONG | +0.033 | +333 | 4 / 0 |
| APLD | SHORT | -0.033 | -333 | 0 / 4 |
| TSM | SHORT | -0.033 | -333 | 0 / 4 |
| CBRS | SHORT | -0.017 | -167 | 0 / 2 |
| IREN | LONG | +0.008 | +83 | 1 / 0 |

Gross stock exposure 0.76 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| NVDA | -1.71 |
| SMCI | -1.32 |
| NBIS | -1.12 |
| IREN | -0.79 |
| BE | -0.64 |
| MRVL | -0.18 |
| CIFR | +0.01 |
| VST | +0.22 |
| CBRS | +0.63 |
| CRWV | +0.72 |
| MU | +0.89 |
| WYFI | +0.89 |
| TSM | +0.99 |
| CEG | +1.02 |
| WULF | +1.03 |
| VRT | +1.05 |
| APLD | +1.10 |
| AMD | +1.11 |
| CORZ | +1.53 |
| TLN | +1.62 |
| AVGO | +1.82 |
