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
| 2026-11-24 | H100 | 3.382 | provider_weighted_median | 34 | 27 | True |
| 2026-11-24 | B200 | 6.300 | provider_weighted_median | 17 | 13 | True |

## History panel, last 10 days

| as_of_date | gpu_model | value | method | n_listings | n_providers | meets_coverage |
|---|---|---|---|---|---|---|
| 2026-11-14 | B200 | 8.500 | provider_weighted_median|panel6 | 8 | 5 | True |
| 2026-11-14 | H100 | 3.490 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-11-15 | B200 | 8.500 | provider_weighted_median|panel6 | 8 | 5 | True |
| 2026-11-15 | H100 | 3.490 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-11-16 | B200 | 8.500 | provider_weighted_median|panel6 | 8 | 5 | True |
| 2026-11-16 | H100 | 3.490 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-11-17 | B200 | 8.500 | provider_weighted_median|panel6 | 8 | 5 | True |
| 2026-11-17 | H100 | 3.490 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-11-18 | H100 | 3.490 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-11-18 | B200 | 8.500 | provider_weighted_median|panel6 | 8 | 5 | True |
| 2026-11-19 | B200 | 8.500 | provider_weighted_median|panel6 | 8 | 5 | True |
| 2026-11-19 | H100 | 3.490 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-11-20 | B200 | 8.500 | provider_weighted_median|panel6 | 8 | 5 | True |
| 2026-11-20 | H100 | 3.900 | provider_weighted_median|panel12 | 18 | 11 | True |
| 2026-11-21 | B200 | 8.550 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-21 | H100 | 3.640 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-22 | B200 | 8.550 | provider_weighted_median|panel6 | 9 | 6 | True |
| 2026-11-22 | H100 | 3.640 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-23 | H100 | 3.640 | provider_weighted_median|panel12 | 19 | 12 | True |
| 2026-11-23 | B200 | 8.550 | provider_weighted_median|panel6 | 9 | 6 | True |

## H100 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| clore | fastgpu | 1 | 0.919 | 0.919 | 0.919 |
| voltagepark | cgi | 1 | 1.990 | 1.990 | 1.990 |
| theta | fastgpu | 1 | 2.290 | 2.290 | 2.290 |
| gmi | fastgpu | 1 | 2.600 | 2.600 | 2.600 |
| hyperstack | hyperstack | 3 | 2.600 | 2.500 | 3.200 |
| openrelay | fastgpu | 1 | 2.600 | 2.600 | 2.600 |
| quantacloud | fastgpu | 1 | 2.700 | 2.700 | 2.700 |
| northflank | fastgpu | 1 | 2.740 | 2.740 | 2.740 |
| deepinfra | fastgpu | 1 | 2.900 | 2.900 | 2.900 |
| civo | cgi | 1 | 2.990 | 2.990 | 2.990 |
| ovhcloud | fastgpu | 1 | 2.990 | 2.990 | 2.990 |
| massedcompute | cgi | 1 | 3.140 | 3.140 | 3.140 |
| thundercompute | fastgpu | 1 | 3.200 | 3.200 | 3.200 |
| hyperbolic | cgi | 1 | 3.490 | 3.490 | 3.490 |
| lium | cgi | 1 | 3.750 | 3.750 | 3.750 |
| fluence | fastgpu | 2 | 3.886 | 3.274 | 4.499 |
| crusoe | fastgpu | 1 | 3.900 | 3.900 | 3.900 |
| modal | fastgpu | 1 | 3.949 | 3.949 | 3.949 |
| together | fastgpu | 1 | 3.990 | 3.990 | 3.990 |
| daytona | fastgpu | 1 | 4.290 | 4.290 | 4.290 |
| paperspace | fastgpu | 1 | 4.410 | 4.410 | 4.410 |
| digitalocean | cgi | 1 | 4.410 | 4.410 | 4.410 |
| nebius | fastgpu | 1 | 4.500 | 4.500 | 4.500 |
| lambda | lambda | 5 | 4.690 | 3.790 | 4.890 |
| replicate | fastgpu | 1 | 5.490 | 5.490 | 5.490 |
| verda | verda | 1 | 5.563 | 5.563 | 5.563 |
| coreweave | coreweave | 1 | 6.155 | 6.155 | 6.155 |

## B200 by provider, latest day

| provider | source | n | median | min | max |
|---|---|---|---|---|---|
| deepinfra | fastgpu | 1 | 4.890 | 4.890 | 4.890 |
| gmi | fastgpu | 1 | 5.000 | 5.000 | 5.000 |
| lium | lium | 1 | 5.600 | 5.600 | 5.600 |
| northflank | fastgpu | 1 | 5.870 | 5.870 | 5.870 |
| hyperstack | hyperstack | 1 | 6.000 | 6.000 | 6.000 |
| modal | fastgpu | 1 | 6.250 | 6.250 | 6.250 |
| openrelay | fastgpu | 1 | 6.300 | 6.300 | 6.300 |
| fluence | fastgpu | 1 | 6.922 | 6.922 | 6.922 |
| lambda | lambda | 4 | 7.840 | 7.690 | 7.990 |
| nebius | fastgpu | 1 | 8.500 | 8.500 | 8.500 |
| coreweave | coreweave | 1 | 8.600 | 8.600 | 8.600 |
| together | fastgpu | 1 | 9.290 | 9.290 | 9.290 |
| verda | verda | 2 | 9.843 | 9.747 | 9.940 |
