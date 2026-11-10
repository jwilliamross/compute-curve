# SA2-M practice sheet for the session after 2026-11-09

Practice only: paper-trade by hand or in a simulator, never with real money. The forward test that would allow paper trading is still running (docs/statarb_paper_readiness.md).

How to use it: at the next open, hold these positions (dollar amounts for a USD 10,000 practice account). Hold until the sheet drops the name. XLK is the hedge leg. Write every trade in your journal.

| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |
|---|---|---|---|---|
| XLK | LONG | +0.540 | +5,397 | hedge |
| NVDA | LONG | +0.092 | +917 | 11 / 0 |
| AVGO | SHORT | -0.067 | -667 | 0 / 8 |
| MRVL | LONG | +0.067 | +667 | 8 / 0 |
| WULF | SHORT | -0.058 | -583 | 0 / 7 |
| TLN | SHORT | -0.058 | -583 | 0 / 7 |
| CORZ | SHORT | -0.050 | -500 | 0 / 6 |
| VRT | SHORT | -0.042 | -417 | 0 / 5 |
| APLD | SHORT | -0.033 | -333 | 0 / 4 |
| MU | LONG | +0.033 | +333 | 4 / 0 |
| WYFI | SHORT | -0.033 | -333 | 0 / 4 |
| AMD | SHORT | -0.033 | -333 | 0 / 4 |
| CEG | SHORT | -0.025 | -250 | 0 / 3 |
| BE | SHORT | -0.025 | -250 | 0 / 3 |
| TSM | SHORT | -0.025 | -250 | 0 / 3 |
| NBIS | SHORT | -0.017 | -167 | 0 / 2 |
| IREN | SHORT | -0.008 | -83 | 0 / 1 |
| SMCI | LONG | +0.008 | +83 | 1 / 0 |
| CIFR | LONG | +0.008 | +83 | 1 / 0 |

Gross stock exposure 0.68 of capital; positions are 0.1 of capital per position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; entries 1.0-2.0).

## Today's 60-day s-scores (how stretched each stock is against XLK)

Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.

| Symbol | s-score |
|---|---|
| MRVL | -1.67 |
| NVDA | -1.64 |
| MU | -1.41 |
| SMCI | -0.74 |
| IREN | -0.49 |
| CIFR | -0.39 |
| BE | -0.33 |
| TSM | -0.15 |
| CBRS | -0.01 |
| CRWV | +0.40 |
| VST | +0.55 |
| CEG | +0.97 |
| WULF | +1.04 |
| APLD | +1.11 |
| AMD | +1.14 |
| VRT | +1.16 |
| CORZ | +1.26 |
| NBIS | +1.36 |
| AVGO | +1.73 |
| TLN | +2.04 |
| WYFI | +2.22 |
