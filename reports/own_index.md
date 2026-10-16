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
| 2026-10-16 | H100 | 3.490 | provider_weighted_median | 56 | 27 | True |
| 2026-10-16 | B200 | 6.840 | provider_weighted_median | 28 | 15 | True |

## History panel, last 10 days

| as_of_date | gpu_model | value | method | n_listings | n_providers | meets_coverage |
|---|---|---|---|---|---|---|
| 2026-10-06 | B200 | 7.659 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-06 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-07 | B200 | 7.694 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-07 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-08 | B200 | 7.730 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-08 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-09 | B200 | 7.766 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-09 | H100 | 3.889 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-10 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-10 | B200 | 7.803 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-11 | B200 | 7.877 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-11 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-12 | B200 | 7.915 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-12 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-13 | B200 | 7.953 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-13 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-14 | B200 | 7.992 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-14 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-15 | H100 | 3.490 | provider_weighted_median|panel12 | 57 | 12 | True |
| 2026-10-15 | B200 | 8.030 | provider_weighted_median|panel6 | 27 | 6 | True |

## H100 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| lium | lium | 2 | 1.345 | 1.300 | 1.390 |
| voltagepark | cgi | 2 | 1.990 | 1.990 | 1.990 |
| deepinfra | fastgpu | 2 | 2.200 | 2.200 | 2.200 |
| theta | fastgpu | 2 | 2.290 | 2.290 | 2.290 |
| quantacloud | fastgpu | 2 | 2.590 | 2.590 | 2.590 |
| gmi | fastgpu | 2 | 2.600 | 2.600 | 2.600 |
| hyperstack | hyperstack | 3 | 2.600 | 2.500 | 3.200 |
| northflank | fastgpu | 2 | 2.740 | 2.740 | 2.740 |
| civo | cgi | 2 | 2.990 | 2.990 | 2.990 |
| ovhcloud | fastgpu | 2 | 2.990 | 2.990 | 2.990 |
| massedcompute | cgi | 2 | 3.140 | 3.140 | 3.140 |
| thundercompute | fastgpu | 2 | 3.200 | 3.200 | 3.200 |
| hyperbolic | cgi | 2 | 3.490 | 3.490 | 3.490 |
| jarvislabs | fastgpu | 2 | 3.490 | 3.490 | 3.490 |
| modal | fastgpu | 2 | 3.949 | 3.949 | 3.949 |
| daytona | fastgpu | 2 | 3.949 | 3.949 | 3.949 |
| together | cgi | 2 | 3.990 | 3.990 | 3.990 |
| lambda | lambda | 5 | 4.090 | 3.290 | 4.290 |
| verda | verda | 1 | 4.170 | 4.170 | 4.170 |
| paperspace | fastgpu | 2 | 4.410 | 4.410 | 4.410 |
| digitalocean | cgi | 2 | 4.410 | 4.410 | 4.410 |
| nebius | fastgpu | 2 | 4.500 | 4.500 | 4.500 |
| crusoe | cgi | 2 | 4.500 | 4.500 | 4.500 |
| fal | fastgpu | 2 | 4.500 | 4.500 | 4.500 |
| replicate | fastgpu | 2 | 5.490 | 5.490 | 5.490 |
| coreweave | coreweave | 1 | 6.155 | 6.155 | 6.155 |
| baseten | fastgpu | 2 | 6.500 | 6.500 | 6.500 |

## B200 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| deepinfra | fastgpu | 2 | 3.690 | 3.690 | 3.690 |
| gmi | fastgpu | 2 | 5.000 | 5.000 | 5.000 |
| massedcompute | cgi | 2 | 5.433 | 5.433 | 5.433 |
| lium | lium | 1 | 5.600 | 5.600 | 5.600 |
| northflank | fastgpu | 2 | 5.870 | 5.870 | 5.870 |
| hyperstack | hyperstack | 1 | 6.000 | 6.000 | 6.000 |
| modal | fastgpu | 2 | 6.250 | 6.250 | 6.250 |
| lambda | lambda | 4 | 6.840 | 6.690 | 6.990 |
| verda | verda | 1 | 7.870 | 7.870 | 7.870 |
| fal | fastgpu | 2 | 7.990 | 7.990 | 7.990 |
| together | cgi | 2 | 8.190 | 8.190 | 8.190 |
| crusoe | fastgpu | 2 | 8.500 | 8.500 | 8.500 |
| nebius | nebius | 2 | 8.500 | 8.500 | 8.500 |
| coreweave | coreweave | 1 | 8.600 | 8.600 | 8.600 |
| baseten | fastgpu | 2 | 9.980 | 9.980 | 9.980 |
