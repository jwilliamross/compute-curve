# Decisions

Each decision was taken autonomously while the owner was away. The rule
applied every time: pick the most conservative reasonable option and record
why.

## D1. Raw Parquet is committed; DuckDB is derived and git-ignored

The container is ephemeral, so raw snapshots that exist only on its disk are
lost. Raw snapshots are small Parquet files and are committed under
`data/raw/`. The DuckDB warehouse and the paper ledger live in `var/` and are
git-ignored because they are rebuildable from raw inputs and binary diffs do
not belong in git.

## D2. The Vast.ai collector does not send `VAST_API_KEY`

The search-offers endpoint returned data without this session adding a key.
Least privilege: a secret that is not needed is not used. If the endpoint
later requires auth, the collector fails loudly and the blocker is logged.

## D3. Vast price basis and provider weighting

The price is `dph_base / num_gpus`: GPUs plus bundled CPU and RAM, excluding
storage and bandwidth. That is the closest match to neocloud list prices,
which also exclude storage. `dph_total` is retained in `raw_json`. The whole
marketplace counts as one provider in the index so its listing count cannot
outvote providers that publish one list price.

## D4. Host-identifying fields are dropped at collection

Vast offers include public IP addresses and hostnames of individual hosts.
They are not needed and are personal or operational data of third parties.
They are removed before anything is written.

## D5. No mypy; ruff `ANN` rules enforce full annotations

The brief limits dependencies. Ruff's `ANN` rules enforce that every
function is annotated. A type checker would add assurance but is not
"clearly necessary"; this can be revisited.

## D6. No pyarrow; DuckDB reads and writes Parquet

DuckDB is already in the core stack and handles Parquet I/O, so pyarrow is
not added.

## D7. Index primary method pre-registered as provider-weighted median

Chosen before seeing any comparison with the published index, to avoid
tuning toward a good-looking tracking error. `pooled_median` and
`trimmed_mean` are declared robustness variants and are counted in
`docs/variants_log.md` when run.

## D8. Contract parameters are unverified placeholders with conservative costs

cmegroup.com cannot be accessed by automation (blocker B2). Tick size, fees
and margin in `config/default.toml` are placeholders marked `verified =
false`. Trading costs default to wide values for a thin new market: 5 ticks
half-spread, 2 ticks slippage, USD 5 per contract per side.

## D9. Published index availability lag is 1 day

A published index value for date `d` is treated as usable from 00:00 UTC on
`d + 1`. This is an assumption until the publication schedule is verified;
it errs toward later availability, which can only understate an edge.

## D10. CME settlements usable from 23:59:59 UTC on the trade date

Orders decided at the end of day `d` fill at the settlement of the next
trade date. A fill can never use a price known at decision time.

## D11. No MCP tools are called, including the environment documentation tool

The owner asked that no MCP connector tools be called. The session's
documentation helper is also exposed as an MCP tool, so it was not used
either. Environment guidance links to the public docs page instead.
