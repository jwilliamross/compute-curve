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
| 2026-10-14 | H100 | 3.490 | provider_weighted_median | 35 | 29 | True |
| 2026-10-14 | B200 | 6.470 | provider_weighted_median | 18 | 14 | True |

## History panel, last 10 days

| as_of_date | gpu_model | value | method | n_listings | n_providers | meets_coverage |
|---|---|---|---|---|---|---|
| 2026-10-04 | B200 | 7.641 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-04 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-05 | B200 | 7.641 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-05 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-06 | B200 | 7.659 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-06 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-07 | B200 | 7.694 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-07 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-08 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-08 | B200 | 7.730 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-09 | B200 | 7.766 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-09 | H100 | 3.889 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-10 | B200 | 7.803 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-10 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-11 | B200 | 7.877 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-10-11 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-12 | B200 | 7.915 | provider_weighted_median|panel6 | 18 | 6 | True |
| 2026-10-12 | H100 | 3.490 | provider_weighted_median|panel12 | 38 | 12 | True |
| 2026-10-13 | H100 | 3.490 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-10-13 | B200 | 7.953 | provider_weighted_median|panel6 | 9 | 6 | True |

## H100 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| clore | fastgpu | 1 | 0.984 | 0.984 | 0.984 |
| lium | lium | 1 | 1.390 | 1.390 | 1.390 |
| voltagepark | cgi | 1 | 1.990 | 1.990 | 1.990 |
| tensorpool | cgi | 1 | 1.990 | 1.990 | 1.990 |
| deepinfra | fastgpu | 1 | 2.200 | 2.200 | 2.200 |
| theta | fastgpu | 1 | 2.290 | 2.290 | 2.290 |
| quantacloud | fastgpu | 1 | 2.590 | 2.590 | 2.590 |
| gmi | fastgpu | 1 | 2.600 | 2.600 | 2.600 |
| hyperstack | hyperstack | 3 | 2.600 | 2.500 | 3.200 |
| northflank | fastgpu | 1 | 2.740 | 2.740 | 2.740 |
| ovhcloud | fastgpu | 1 | 2.990 | 2.990 | 2.990 |
| civo | cgi | 1 | 2.990 | 2.990 | 2.990 |
| massedcompute | cgi | 1 | 3.140 | 3.140 | 3.140 |
| thundercompute | fastgpu | 1 | 3.200 | 3.200 | 3.200 |
| hyperbolic | cgi | 1 | 3.490 | 3.490 | 3.490 |
| jarvislabs | fastgpu | 1 | 3.490 | 3.490 | 3.490 |
| nebius | cgi | 1 | 3.850 | 3.850 | 3.850 |
| crusoe | cgi | 1 | 3.900 | 3.900 | 3.900 |
| modal | fastgpu | 1 | 3.949 | 3.949 | 3.949 |
| daytona | fastgpu | 1 | 3.949 | 3.949 | 3.949 |
| together | cgi | 1 | 3.990 | 3.990 | 3.990 |
| lambda | lambda | 5 | 4.090 | 3.290 | 4.290 |
| verda | verda | 1 | 4.090 | 4.090 | 4.090 |
| digitalocean | cgi | 1 | 4.410 | 4.410 | 4.410 |
| paperspace | fastgpu | 1 | 4.410 | 4.410 | 4.410 |
| fal | fastgpu | 1 | 4.500 | 4.500 | 4.500 |
| replicate | fastgpu | 1 | 5.490 | 5.490 | 5.490 |
| coreweave | coreweave | 1 | 6.155 | 6.155 | 6.155 |
| baseten | fastgpu | 1 | 6.500 | 6.500 | 6.500 |

## B200 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| deepinfra | fastgpu | 1 | 3.690 | 3.690 | 3.690 |
| gmi | fastgpu | 1 | 5.000 | 5.000 | 5.000 |
| massedcompute | cgi | 1 | 5.433 | 5.433 | 5.433 |
| lium | lium | 1 | 5.600 | 5.600 | 5.600 |
| northflank | fastgpu | 1 | 5.870 | 5.870 | 5.870 |
| hyperstack | hyperstack | 1 | 6.000 | 6.000 | 6.000 |
| modal | fastgpu | 1 | 6.250 | 6.250 | 6.250 |
| lambda | lambda | 4 | 6.840 | 6.690 | 6.990 |
| verda | verda | 1 | 7.720 | 7.720 | 7.720 |
| fal | fastgpu | 1 | 7.990 | 7.990 | 7.990 |
| together | cgi | 1 | 8.190 | 8.190 | 8.190 |
| nebius | nebius | 2 | 8.500 | 8.500 | 8.500 |
| coreweave | coreweave | 1 | 8.600 | 8.600 | 8.600 |
| baseten | fastgpu | 1 | 9.980 | 9.980 | 9.980 |
