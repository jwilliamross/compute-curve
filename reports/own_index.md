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
| 2026-10-31 | H100 | 3.200 | provider_weighted_median | 31 | 25 | True |
| 2026-10-31 | B200 | 6.275 | provider_weighted_median | 18 | 14 | True |

## History panel, last 10 days

| as_of_date | gpu_model | value | method | n_listings | n_providers | meets_coverage |
|---|---|---|---|---|---|---|
| 2026-10-20 | B200 | 8.149 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-20 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-21 | B200 | 8.190 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-21 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-22 | B200 | 8.231 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-22 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-24 | B200 | 8.314 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-24 | H100 | 3.490 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-10-25 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-25 | B200 | 8.314 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-26 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-26 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-27 | B200 | 8.345 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-27 | H100 | 3.900 | provider_weighted_median|panel12 | 36 | 11 | True |
| 2026-10-28 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-28 | H100 | 3.900 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-10-29 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-29 | H100 | 3.990 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-10-30 | H100 | 3.900 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-10-30 | B200 | 8.345 | provider_weighted_median|panel6 | 9 | 6 | True |

## H100 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| lium | lium | 1 | 1.390 | 1.390 | 1.390 |
| voltagepark | cgi | 1 | 1.990 | 1.990 | 1.990 |
| theta | fastgpu | 1 | 2.290 | 2.290 | 2.290 |
| quantacloud | fastgpu | 1 | 2.590 | 2.590 | 2.590 |
| hyperstack | hyperstack | 3 | 2.600 | 2.500 | 3.200 |
| gmi | fastgpu | 1 | 2.600 | 2.600 | 2.600 |
| openrelay | fastgpu | 1 | 2.600 | 2.600 | 2.600 |
| northflank | fastgpu | 1 | 2.740 | 2.740 | 2.740 |
| deepinfra | fastgpu | 1 | 2.900 | 2.900 | 2.900 |
| ovhcloud | fastgpu | 1 | 2.990 | 2.990 | 2.990 |
| civo | cgi | 1 | 2.990 | 2.990 | 2.990 |
| massedcompute | cgi | 1 | 3.140 | 3.140 | 3.140 |
| thundercompute | fastgpu | 1 | 3.200 | 3.200 | 3.200 |
| daytona | fastgpu | 1 | 3.949 | 3.949 | 3.949 |
| modal | fastgpu | 1 | 3.949 | 3.949 | 3.949 |
| together | cgi | 1 | 3.990 | 3.990 | 3.990 |
| lambda | lambda | 5 | 4.090 | 3.290 | 4.290 |
| digitalocean | cgi | 1 | 4.410 | 4.410 | 4.410 |
| paperspace | fastgpu | 1 | 4.410 | 4.410 | 4.410 |
| nebius | fastgpu | 1 | 4.500 | 4.500 | 4.500 |
| verda | verda | 1 | 4.793 | 4.793 | 4.793 |
| hyperbolic | cgi | 1 | 4.850 | 4.850 | 4.850 |
| replicate | fastgpu | 1 | 5.490 | 5.490 | 5.490 |
| coreweave | coreweave | 1 | 6.155 | 6.155 | 6.155 |
| baseten | fastgpu | 1 | 6.500 | 6.500 | 6.500 |

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
| lambda | lambda | 4 | 6.840 | 6.690 | 6.990 |
| together | cgi | 1 | 8.190 | 8.190 | 8.190 |
| nebius | fastgpu | 1 | 8.500 | 8.500 | 8.500 |
| coreweave | coreweave | 1 | 8.600 | 8.600 | 8.600 |
| verda | verda | 2 | 8.957 | 8.869 | 9.045 |
| baseten | fastgpu | 1 | 9.980 | 9.980 | 9.980 |
