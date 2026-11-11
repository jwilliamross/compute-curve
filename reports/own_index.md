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
| 2026-11-11 | H100 | 3.200 | provider_weighted_median | 31 | 24 | True |
| 2026-11-11 | B200 | 6.250 | provider_weighted_median | 17 | 13 | True |

## History panel, last 10 days

| as_of_date | gpu_model | value | method | n_listings | n_providers | meets_coverage |
|---|---|---|---|---|---|---|
| 2026-10-30 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-30 | H100 | 3.900 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-10-31 | B200 | 8.345 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-31 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-11-03 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-03 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-04 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-04 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-05 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-05 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-06 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-06 | H100 | 3.640 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-07 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-07 | H100 | 3.640 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-08 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-08 | H100 | 3.640 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-09 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-09 | H100 | 3.640 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-10 | H100 | 3.900 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-10 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |

## H100 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| clore | fastgpu | 1 | 0.984 | 0.984 | 0.984 |
| lium | lium | 2 | 1.345 | 1.300 | 1.390 |
| voltagepark | cgi | 1 | 1.990 | 1.990 | 1.990 |
| theta | fastgpu | 1 | 2.290 | 2.290 | 2.290 |
| openrelay | fastgpu | 1 | 2.600 | 2.600 | 2.600 |
| gmi | fastgpu | 1 | 2.600 | 2.600 | 2.600 |
| hyperstack | hyperstack | 3 | 2.600 | 2.500 | 3.200 |
| northflank | fastgpu | 1 | 2.740 | 2.740 | 2.740 |
| deepinfra | fastgpu | 1 | 2.900 | 2.900 | 2.900 |
| ovhcloud | fastgpu | 1 | 2.990 | 2.990 | 2.990 |
| civo | cgi | 1 | 2.990 | 2.990 | 2.990 |
| massedcompute | cgi | 1 | 3.140 | 3.140 | 3.140 |
| thundercompute | fastgpu | 1 | 3.200 | 3.200 | 3.200 |
| hyperbolic | cgi | 1 | 3.490 | 3.490 | 3.490 |
| daytona | fastgpu | 1 | 3.949 | 3.949 | 3.949 |
| modal | fastgpu | 1 | 3.949 | 3.949 | 3.949 |
| together | cgi | 1 | 3.990 | 3.990 | 3.990 |
| paperspace | fastgpu | 1 | 4.410 | 4.410 | 4.410 |
| digitalocean | cgi | 1 | 4.410 | 4.410 | 4.410 |
| nebius | fastgpu | 1 | 4.500 | 4.500 | 4.500 |
| lambda | lambda | 5 | 4.690 | 3.790 | 4.890 |
| verda | verda | 1 | 5.037 | 5.037 | 5.037 |
| replicate | fastgpu | 1 | 5.490 | 5.490 | 5.490 |
| coreweave | coreweave | 1 | 6.155 | 6.155 | 6.155 |

## B200 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| deepinfra | fastgpu | 1 | 4.890 | 4.890 | 4.890 |
| gmi | fastgpu | 1 | 5.000 | 5.000 | 5.000 |
| massedcompute | cgi | 1 | 5.433 | 5.433 | 5.433 |
| lium | lium | 1 | 5.600 | 5.600 | 5.600 |
| northflank | fastgpu | 1 | 5.870 | 5.870 | 5.870 |
| hyperstack | hyperstack | 1 | 6.000 | 6.000 | 6.000 |
| modal | fastgpu | 1 | 6.250 | 6.250 | 6.250 |
| openrelay | fastgpu | 1 | 6.300 | 6.300 | 6.300 |
| lambda | lambda | 4 | 7.840 | 7.690 | 7.990 |
| together | cgi | 1 | 8.190 | 8.190 | 8.190 |
| nebius | fastgpu | 1 | 8.500 | 8.500 | 8.500 |
| coreweave | coreweave | 1 | 8.600 | 8.600 | 8.600 |
| verda | verda | 2 | 9.229 | 9.138 | 9.320 |
