# CME settlements (manual, git-ignored CSVs; D59)

Download GPU1/GPU2 daily settlements yourself and save them here as `*.csv`.
Do not automate cmegroup.com. The CSVs are git-ignored and stay on your
machine, because their licence is unverified.

Columns (header row required):

    product,contract_month,trade_date,settle_price
    GPU1,2026-12,2026-11-10,2.95

- `product`: GPU1 or GPU2.
- `contract_month`: YYYY-MM.
- `trade_date`: YYYY-MM-DD.
- `settle_price`: USD per GPU-hour.

Optional columns: `volume`, `open_interest`. The claim-7 premium model
(`compute-curve futures-premium`) reads these files.
