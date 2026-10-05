# GPU1 and GPU2 contract specifications

Checked on 2026-10-05 against primary documents filed with the CFTC.
cmegroup.com itself could not be read: its edge blocks automated access and
its terms prohibit it (docs/blockers.md B2). Full notes with page references:
`docs/audit/2026-10-05_contract_and_literature.md`.

## Are the contracts trading?

**No.** NYMEX filed both contracts on 2026-08-11 under CFTC Regulation
40.3(a), a voluntary submission for Commission *approval*, not a
self-certification. On 2026-09-21 the CFTC Division of Market Oversight
extended its review by 45 days, "until the end of November 9, 2026", citing
"novel or complex issues" and its pending Request for Comment on compute
derivatives (comments due 2026-10-20). On 2026-10-05 the CFTC product records
for both contracts read "Approval Pending". The intended first trade date of
2026-10-05 has therefore passed without a listing. No new listing date from
CME was found.

Sources:
- NYMEX Submission 26-370: https://www.cftc.gov/filings/ptc/ptc08112615405.pdf
- Exhibit B (limits): https://www.cftc.gov/filings/ptc/ptc08112615406.xlsx
- CFTC extension letter: https://www.cftc.gov/filings/documents/2026/orgdcmnymexcompcontr260921.pdf
- CFTC product records: https://www.cftc.gov/IndustryOversight/IndustryFilings/TradingOrganizationProducts/62544 and .../62545
- Request for Comment: 91 FR 54259, https://www.govinfo.gov/content/pkg/FR-2026-08-21/pdf/2026-17163.pdf

## Terms

| Item | GPU1 | GPU2 | Status |
|---|---|---|---|
| Title | Silicon Data H100 Rental Index Futures | Silicon Data B200 Rental Index Futures | verified |
| Exchange, rule chapter | NYMEX, Chapter 1045 | NYMEX, Chapter 1047 | verified |
| Contract unit | 730 GPU-hours | 730 GPU-hours | verified |
| Quotation | USD and cents per GPU-hour | same | verified |
| Minimum tick | USD 0.01/GPU-hour = USD 7.30 per contract; USD 0.005 for Globex inter-commodity spreads | same | verified |
| Settlement | Financial (cash) | same | verified |
| Floating price | Arithmetic average of SD-H100 "on-demand settlement prices" for each **Business Day** of the contract month | Same on SD-B200 | verified |
| Index configuration | Geography: United States | same | verified |
| Termination of trading | Last Business Day of the contract month | same | verified |
| Listing schedule | 36 consecutive months; first listing October 2026 | same | verified |
| Spot-month position limit | 7,500 contracts, from close 3 business days before last trading day | 5,500 | verified |
| Accountability (single / all months) | 15,000 / 22,500 | 11,000 / 16,500 | verified |
| Reportable level | 25 | 25 | verified |
| Block minimum | 5 contracts, 15-minute reporting | same | verified |
| Exchange fees | Globex USD 3.65 member, USD 5.50 non-member; cash settlement USD 0.90 / 1.35 | same | verified |
| Margins | not in the filing | not in the filing | **not confirmed** |
| Missing index day | no fallback clause in the filed chapters | same | **not confirmed** |
| Index publication time | not disclosed | not disclosed | **not confirmed** |

## How the simulation uses these terms

`config/default.toml` lists, for each contract, which fields are verified.

| Term | Value used | Basis |
|---|---|---|
| Contract value | price x 730 | verified |
| Tick | USD 0.01 | verified |
| Final settlement | mean of the index over Monday-Friday days of the month | verified Business Days; exchange holidays not modelled (assumption) |
| Missing index day | carry forward the last published value; more than 3 carried days means no settlement in simulation | assumption |
| Last trading day | last Monday-Friday day of the month | verified rule, holidays not modelled |
| Exchange fee | USD 5.50 per side (non-member) | verified |
| Broker and clearing | USD 2.50 per side | assumption |
| Cash-settlement fee | USD 1.35 per contract at expiry | verified (non-member) |
| Half-spread | 5 ticks per side | assumption for a new, thin market |
| Slippage | 2 ticks per side | assumption |
| Initial margin | USD 400 (GPU1), USD 900 (GPU2) per contract | assumption, about 20% of notional |
| Position limits (paper account) | 5 per month, 10 gross | our own risk limits, far inside the exchange limits |

## What the floating price is not

The public SDH100RT number on silicondata.com is described as a neocloud
index without a stated geography, and it carries values on weekend dates. The
contracts settle on the US-geography configuration, on Business Days only.
These may differ. Licensed history of the exact settlement series is needed
before any tracking-error or nowcast claim can be tested (docs/blockers.md B7).
