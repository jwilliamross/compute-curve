# Our H100 / B200 on-demand index

Built from collected listings only; no Silicon Data values are used.
Method: `provider_weighted_median`. Methodology and caveats: `docs/index_methodology.md`.
A value is used only if `meets_coverage` is true (at least 3 providers and 5 listings).

Two series are kept (full history in `reports/own_index.csv`):

- **headline**: every approved source, one source per provider per day. Its composition changes when sources are added, so it is not used for time-series models.
- **history_panel**: the gpurentalprices.com archive and live feed only, restricted to a provider panel fixed from the first 30 days. Models and evaluations use this series.

## Headline, latest day

| as_of_date | gpu_model | value | method | n_listings | n_providers | meets_coverage |
|---|---|---|---|---|---|---|
| 2026-10-09 | H100 | 3.245 | provider_weighted_median | 21 | 14 | True |
| 2026-10-09 | B200 | 7.165 | provider_weighted_median | 12 | 8 | True |

## History panel, last 10 days

| as_of_date | gpu_model | value | method | n_listings | n_providers | meets_coverage |
|---|---|---|---|---|---|---|
| 2026-09-29 | B200 | 6.345 | provider_weighted_median|panel8 | 8 | 8 | True |
| 2026-09-29 | H100 | 3.095 | provider_weighted_median|panel19 | 24 | 19 | True |
| 2026-09-30 | B200 | 6.345 | provider_weighted_median|panel8 | 8 | 8 | True |
| 2026-09-30 | H100 | 3.170 | provider_weighted_median|panel19 | 24 | 19 | True |
| 2026-10-01 | B200 | 6.345 | provider_weighted_median|panel8 | 8 | 8 | True |
| 2026-10-01 | H100 | 3.170 | provider_weighted_median|panel19 | 24 | 19 | True |
| 2026-10-02 | B200 | 6.345 | provider_weighted_median|panel8 | 8 | 8 | True |
| 2026-10-02 | H100 | 3.170 | provider_weighted_median|panel19 | 24 | 19 | True |
| 2026-10-03 | H100 | 3.209 | provider_weighted_median|panel19 | 27 | 18 | True |
| 2026-10-03 | B200 | 7.024 | provider_weighted_median|panel8 | 11 | 8 | True |
| 2026-10-04 | B200 | 7.041 | provider_weighted_median|panel8 | 11 | 8 | True |
| 2026-10-04 | H100 | 3.209 | provider_weighted_median|panel19 | 27 | 18 | True |
| 2026-10-05 | B200 | 7.041 | provider_weighted_median|panel8 | 11 | 8 | True |
| 2026-10-05 | H100 | 3.209 | provider_weighted_median|panel19 | 27 | 18 | True |
| 2026-10-06 | B200 | 7.059 | provider_weighted_median|panel8 | 22 | 8 | True |
| 2026-10-06 | H100 | 3.206 | provider_weighted_median|panel19 | 54 | 18 | True |
| 2026-10-07 | B200 | 7.094 | provider_weighted_median|panel8 | 11 | 8 | True |
| 2026-10-07 | H100 | 3.215 | provider_weighted_median|panel19 | 27 | 18 | True |
| 2026-10-08 | H100 | 3.202 | provider_weighted_median|panel19 | 27 | 18 | True |
| 2026-10-08 | B200 | 7.130 | provider_weighted_median|panel8 | 11 | 8 | True |

## H100 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| lium | lium | 2 | 1.345 | 1.300 | 1.390 |
| tensorpool | cgi | 1 | 1.990 | 1.990 | 1.990 |
| voltagepark | cgi | 1 | 1.990 | 1.990 | 1.990 |
| hyperstack | hyperstack | 3 | 2.600 | 2.500 | 3.200 |
| civo | cgi | 1 | 2.990 | 2.990 | 2.990 |
| massedcompute | cgi | 1 | 3.140 | 3.140 | 3.140 |
| hyperbolic | cgi | 1 | 3.190 | 3.190 | 3.190 |
| nebius | cgi | 1 | 3.850 | 3.850 | 3.850 |
| verda | verda | 1 | 3.890 | 3.890 | 3.890 |
| crusoe | cgi | 1 | 3.900 | 3.900 | 3.900 |
| together | cgi | 1 | 3.990 | 3.990 | 3.990 |
| lambda | lambda | 5 | 4.090 | 3.290 | 4.290 |
| digitalocean | cgi | 1 | 4.410 | 4.410 | 4.410 |
| coreweave | coreweave | 1 | 6.155 | 6.155 | 6.155 |

## B200 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| massedcompute | cgi | 1 | 5.433 | 5.433 | 5.433 |
| lium | lium | 1 | 5.600 | 5.600 | 5.600 |
| hyperstack | hyperstack | 1 | 6.000 | 6.000 | 6.000 |
| lambda | lambda | 4 | 6.840 | 6.690 | 6.990 |
| verda | verda | 1 | 7.340 | 7.340 | 7.340 |
| together | cgi | 1 | 8.190 | 8.190 | 8.190 |
| nebius | nebius | 2 | 8.500 | 8.500 | 8.500 |
| coreweave | coreweave | 1 | 8.600 | 8.600 | 8.600 |
