# SA2-M practice sheet for the session after 2026-11-18

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | LONG | +0.851 | +8,505 | hedge |
| NVDA | LONG | +0.100 | +1,000 | 12 / 0 |
| AVGO | SHORT | -0.083 | -833 | 0 / 10 |
| AMD | SHORT | -0.083 | -833 | 0 / 10 |
| WULF | SHORT | -0.075 | -750 | 0 / 9 |
| WYFI | SHORT | -0.075 | -750 | 0 / 9 |
| CORZ | SHORT | -0.067 | -667 | 0 / 8 |
| TLN | SHORT | -0.058 | -583 | 0 / 7 |
| SMCI | LONG | +0.050 | +500 | 6 / 0 |
| APLD | SHORT | -0.042 | -417 | 0 / 5 |
| VRT | SHORT | -0.033 | -333 | 0 / 4 |
| CBRS | SHORT | -0.025 | -250 | 0 / 3 |
| CIFR | SHORT | -0.025 | -250 | 0 / 3 |
| IREN | LONG | +0.025 | +250 | 3 / 0 |
| MU | SHORT | -0.008 | -83 | 0 / 1 |
| NBIS | LONG | +0.008 | +83 | 1 / 0 |

Gross stock exposure 0.76 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| NVDA | -2.04 |
| IREN | -0.96 |
| SMCI | -0.69 |
| NBIS | -0.41 |
| BE | -0.37 |
| CBRS | +0.04 |
| MRVL | +0.07 |
| TSM | +0.08 |
| VST | +0.11 |
| MU | +0.14 |
| CIFR | +0.32 |
| CRWV | +0.81 |
| CEG | +0.96 |
| WYFI | +1.09 |
| WULF | +1.26 |
| TLN | +1.27 |
| VRT | +1.27 |
| APLD | +1.38 |
| CORZ | +1.53 |
| AMD | +1.63 |
| AVGO | +1.65 |
