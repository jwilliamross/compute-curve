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

## D12. Vast.ai collection disabled; the Step 0 response was deleted

The data-source audit found Vast.ai's terms (version dated 2026-09-01) ban
automated retrieval and any use of its data to build an index or benchmark.
The one unauthenticated call in Step 0 was made because the brief asked for
it; its response sat only in the session scratchpad and was deleted. The
collector code is kept for the case of a future licence, but the snapshot
runner refuses it unless `vast` is listed in `collectors.licensed`.

## D13. Vast.ai and RunPod rows are dropped even when an aggregator supplies them

The audit suggested relying on aggregators' own licences for these
providers. The more conservative choice was taken: rows whose provider's own
terms prohibit automated collection or index use are dropped at collection
from every source. Cost: two large providers are missing from our index.

## D14. Silicon Data content is not stored

Its terms forbid storing site content in a database or retrieval system, and
history is paid. No collector exists. Only the latest public values (2.81 and
5.87 on 2026-10-05) are cited in prose. The seven-day series the audit saw was
removed from the archived notes, and scratch copies of Silicon Data pages were
deleted.

## D15. FLOPS Index is not collected

Its public catalog is keyless, but no public terms exist (`/terms` returns 401)
and its README calls the data proprietary. Collection waits for written
confirmation.

## D16. Together AI is not collected directly

Its terms prohibit "competitive analysis or benchmarking" using its Services.
Reading a public pricing page is arguably outside that clause, but the
conservative reading was taken. Together's prices still arrive through the
Computable GPU Index and gpurentalprices.com.

## D17. cftc.gov was read once for reference; no CFTC collection is automated

cftc.gov's robots.txt blocks ClaudeBot, anthropic-ai and Claude-Web under a
"Training crawlers" heading, and its general rule allows all paths with
`Content-Signal: ... ai-train=no, use=reference`. The research agent fetched
the GPU1/GPU2 filings once, under a generic research User-Agent, for reference
use. That matches the stated signal. No code in this repository fetches from
cftc.gov. If you prefer to treat the site as off-limits to agents entirely,
nothing depends on further access.

## D18. Fees: verified exchange fee plus an assumed broker and clearing charge

The non-member Globex fee (USD 5.50 per side) and cash-settlement fee (USD
1.35) are verified from the filing. Broker and clearing costs are not, so USD
2.50 per side is assumed. Non-member rates were chosen because they are higher.

## D19. Margins are placeholders at about 20% of notional

No margin figure was found. USD 400 (GPU1) and USD 900 (GPU2) per contract
are placeholders. Their only role is the paper account's margin check.

## D20. Index scope changes, made before any result existed

After the CFTC filing showed "Geography: United States" and neocloud scope:
hyperscalers are excluded, listings with an explicit non-US region are
excluded, unknown regions are kept, and the coverage minimum was raised to 3
providers and 5 listings. These were fixed before any comparison with any
other index was run.

## D21. Two index series; models use a fixed panel chosen from the first 30 days

The multi-source headline index changes composition whenever a source is
added. The single-publisher history (gpurentalprices.com) also widened its
coverage on 2026-10-03 and 2026-10-04. Models therefore use a fixed provider
panel chosen from the first 30 days only (presence of 90% or more), with those
days dropped, so panel choice uses no future information.

## D22. A snapshot is dated by its own publication time

Archived daily files carry stale rows with old fetch times. Dating rows
individually let a later file's stale rows displace an earlier full day. Each
snapshot now takes the latest observation time among its rows, and all its
rows take that date.

## D23. Archived history is treated as available at the publisher's time

Rows backfilled from gpurentalprices.com's append-only archive are usable in
backtests from the publisher's fetch time, not from our download time. They
were public then. This assumes the archive was not revised, which its
append-only design supports but does not prove.

## D24. Throughput ratio central value 2.5, range 1.8 to 3.0

Set after reading Bandi and Su's Table 2 (2.53 on dense 8-bit throughput),
before any relative-value test was run. Every relative-value statement must
hold across the range.

## D25. Priors from the SSRN 6926798 abstract; depreciation fixed, not estimated

Jump mean -0.22 log (standard deviation 0.10), depreciation 17.5% a year.
A constant depreciation rate is not separately identified from the drifts
(docs/term_structure_model.md), so it is fixed at the prior.

## D26. Nothing trades until validated, and validation requires futures

`var/validation.json` marks a signal validated only after its out-of-sample
test passes, and the nowcast signal also requires futures settlements. Until
then every signal runs in shadow mode. Shadow predictions are logged in the
paper ledger on trading days. Before listing there are no trading days, so
nothing is logged; every input carries its availability time, so the same
predictions can be rebuilt point-in-time when the evaluation runs.

## D27. Engine cost check holds trades fixed

With loss stops and margin active, a backtest's trade path changes with costs,
so PnL need not fall monotonically as costs rise. The engine check therefore
tests cost monotonicity with stops and margin made non-binding, and reports
both versions.

## D28. Research agents used WebSearch and WebFetch

These are built-in tools, not MCP connectors, so the no-connector instruction
did not exclude them. No MCP tool was called.

## D29. Alpaca market data is cached in `var/` only and never committed

Claim 4 uses daily bars from Alpaca's market data API. Alpaca's Terms and
Conditions limit Content (market data, and account positions, balances and
orders) to personal, non-commercial use, and forbid copying or uploading it to
another server "for publication or distribution". Alpaca's support pages
also say its API data may not be redistributed (docs/env_check_claim4.md).
This repository may become public. So bars are fetched at run time into the
git-ignored `var/market_data/` and never written under `data/raw/`. The
GitHub Actions workflow keeps them on the ephemeral runner, with no artifact
or cache. What is committed: a fetch manifest (symbols, dates, feed, row
counts, a content hash), our own signals and predictions, and aggregate test
statistics. Reports give no prices, no per-stock return series, no dollar
balances and no fill prices. This is a deliberate exception to the
immutable-raw-Parquet rule, the same exception as Silicon Data (D14).
Reproducibility rests on re-fetching. The manifest hash shows whether a
re-fetch returned identical data.

## D30. Alpaca paper adapter: a scoped exception to "no brokerage connectivity"

CLAUDE.md's scope said "no brokerage connectivity, no order routing". On
2026-10-05 the owner explicitly asked for an Alpaca paper adapter beside the
local engine, with simulation only, no real money and no live endpoint. The
conservative reading that satisfies both:

- The adapter lives in `compute_curve.claim4`, not in the local futures
  engine `compute_curve.paper`. The local engine still contains no
  broker code.
- Only Alpaca's paper endpoint is reachable. Every client hard-fails at
  construction unless `APCA_API_BASE_URL` is exactly the paper endpoint.
  Every request is re-checked against the allowed host, and redirects are
  not followed. Request URLs come from constants, not from the environment.
- Orders are sent only when the claim-4 validation gate passes and every
  risk limit holds. Otherwise the run is shadow mode and sends no order.
- CLAUDE.md's scope section is amended to record this single exception, so
  a later session does not remove the adapter as a violation.

## D31. Claim-4 signal timing matches the live cycle, not the publisher's clock

The gpurentalprices.com archive stamps each daily file within about two
minutes of its last offer fetch, mostly between 05:00 and 11:00 UTC. The
website served that snapshot all day, so the publisher-time assumption (D23)
is plausible. For claim 4 the more conservative rule was chosen anyway. Index
day `d` is usable at the later of its snapshot time plus 60 minutes and
23:30 UTC on `d`, the time the scheduled live cycle runs. A backtest
therefore acts on exactly what the live system would have had. In practice a
weekday's index reaches the market at the next session's open, never the
same day's.

## D32. Claim-4 universe frozen by a written rule; basket weighted by category

The universe rule (docs/claim4_plan.md section 2) needs judgment about which
companies depend on GPU compute. To keep that judgment from being tuned on
results, the list was frozen before any test-window return was fetched. The
liquidity screen used June and July 2026 only, which is before the test
window, and printed pass or fail without values. Cerebras (CBRS) was added
because a name search of Alpaca's asset list found it listed and it meets
the rule. The primary basket gives each of the three buckets one third.
Equal weight across all 21 names would give data-center power, the bucket
most loosely linked to rental prices, the largest weight only because it
has the most names. Per-stock tests are not run.

## D33. Claim-4 provider panels are frozen in config; formation days excluded

The fixed panels (19 H100 and 8 B200 providers) are recomputed by code from
the first 30 days of history. A future backfill of earlier days, such as the
Zenodo archive, would change that window and silently change the signal. So
the claim-4 panels are frozen in `config/default.toml`. As in D21, the 30
formation days are in-sample for the panel choice, so claim-4 signals start
at the first session whose index days are both after 2026-08-17, which is
2026-08-20.

## D34. Statistical guards added after the first claim-4 run (bug fixes, all stricter)

The first real run, on 2026-10-06, printed numbers that were artifacts of a
tiny sample. They were fixed before any result was written up. Each fix can
only make a test harder to pass, never easier:

1. **Block bootstrap with fewer than two blocks.** At `h = 20` there were 13
   windows against a block length of 20. Every resample was then a rotation
   of the whole sample, so the interval collapsed to a point, for example
   `[0.16, 0.16]`. Intervals now need at least two blocks; otherwise "n/a".
2. **Newey-West and Clark-West with the lag close to `n`.** A lag of 20 on
   13 windows, or 5 on 4, gave spurious p-values near 0. Both now need
   `n >= 3 × lag`; otherwise "too few windows".
3. **Sharpe interval for sparse strategies.** Resamples with no trade have
   zero variance. They were dropped as undefined. That kept only resamples
   containing the one or two profitable trades, and let two strategies with
   1 or 2 trades out of 12 windows "pass" G3. A strategy that never trades
   now scores a Sharpe of 0. Neither strategy passes G3 any more, and
   neither could have opened the gate, because G1, G2 and G4 failed.
4. **Holm and Benjamini-Hochberg family size.** Tests that could not be
   computed were left out of the adjustment, which shrinks the family. They
   now count as `p = 1`, so the family keeps its pre-registered size of 18,
   or 54 for family S.
5. **Event-study intervals** are shown only when there are at least 10
   events, the plan's minimum for inference. The sign-flip p-value is still
   shown.

No definition, threshold, signal, universe member or cost changed. The plan
treats bug fixes like these as decisions, not new variants (section 13).
