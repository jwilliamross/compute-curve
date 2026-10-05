# Hardware launch calendar

Used by the term-structure model as scheduled jump dates in the long-run
factor (docs/term_structure_model.md). Each entry gives the date the model
uses, what happened, and the source status. Full notes:
`docs/audit/2026-10-05_contract_and_literature.md`, section 4.

The size of each jump is uncertain (prior mean -0.22 log, standard deviation
0.10). The timing of the price effect is also uncertain: announcement, volume
shipment and cloud availability are months apart. We place the jump at the
first verified cloud availability or volume-shipment date, and at the
announced window start for future generations.

## In the model (`config/default.toml`, `[[launches]]`)

| Date used | Event | Affects | Kind | Source status |
|---|---|---|---|---|
| 2024-04-01 | H200 available from partners (announced on 2023-11-13 for Q2 2024) | H100 | announced window | verified (NVIDIA newsroom) |
| 2025-02-04 | Blackwell GB200 NVL72 generally available at CoreWeave | H100 | cloud GA | verified (NVIDIA blog) |
| 2025-07-03 | Blackwell Ultra GB300 NVL72 first cloud deployment (CoreWeave) | H100, B200 | cloud GA | verified (press release) |
| 2026-08-26 | Vera Rubin racks running at CoreWeave, Google Cloud, Azure, OCI and Nebius (Q2 FY27 results) | H100, B200 | volume shipments | verified (NVIDIA newsroom) |
| 2027-07-01 | Rubin Ultra systems, announced for the second half of 2027 | H100, B200 | announced window | verified wording, but the GTC 2025 blog mixes "Rubin" and "Rubin Ultra" |

## Context, not in the model

| Date | Event | Status |
|---|---|---|
| 2022-03-22 | H100 announced | verified |
| 2022-09-20 | H100 in full production | verified |
| 2023-03-21 | H100 in the cloud (Azure preview, OCI limited, Cirrascale and CoreWeave GA) | verified |
| 2023-07-26 | AWS P5 (H100) generally available | verified |
| 2024-03-18 | Blackwell announced | verified |
| 2025-02-26 | Blackwell volume ramp ("billions of dollars in sales" in its first quarter) | verified |
| 2025-03-18 | Blackwell in full production; Blackwell Ultra announced for H2 2025 | verified |
| 2025-05-15 | AWS P6-B200 generally available | verified |
| 2026-01-05 | Rubin in full production; partner products from H2 2026 | verified |
| 2028 | Feynman generation | snippet only, not used |

## Interaction with the index history

Silicon Data's H100 history starts on 2024-09-01, after the H200 window, and
spans the Blackwell and Blackwell Ultra windows. A licensed history would
allow a first estimate of the jump size around 2025-02-04 and 2025-07-03.
Silicon Data's own methodology changes (2025-12-04 restatement; provider
changes on 2026-04-06, 2026-07-15 and 2026-09-25) are level breaks that must
not be mistaken for launch jumps.
