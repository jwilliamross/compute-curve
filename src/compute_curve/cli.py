"""Command-line entry point: ``uv run compute-curve <command>``.

Commands
--------
snapshot   collect today's raw listings from approved sources (idempotent)
backfill   one-off import of a source's archived history (idempotent)
index      rebuild our H100/B200 index and write reports/own_index.md
status     show the forward paper account
daily      daily cycle: snapshot, index, signals, simulated fills, report
evaluate   test the three claims on real data; write reports/evaluation.md
backtest   engine validation on SYNTHETIC data, and real-data backtests when
           CME settlement history exists
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

from compute_curve.config import load_config
from compute_curve.timeutil import utc_now


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="compute-curve", description=__doc__.split("\n")[0])
    p.add_argument("--config", type=Path, default=None, help="TOML config path")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("snapshot", help="collect today's raw listings")
    s.add_argument("--source", action="append", help="limit to source id (repeatable)")
    s.add_argument("--force", action="store_true", help="append another snapshot today")

    bf = sub.add_parser("backfill", help="one-off backfill of archived source history")
    bf.add_argument("source", choices=["gpurentalprices", "cgi"])
    bf.add_argument("--start", type=date.fromisoformat, required=True)
    bf.add_argument("--end", type=date.fromisoformat, required=True)

    sub.add_parser("index", help="rebuild our index from raw data")
    sub.add_parser("status", help="show the forward paper account")

    d = sub.add_parser("daily", help="run the daily cycle")
    d.add_argument("--date", type=date.fromisoformat, default=None, help="UTC date (default today)")
    d.add_argument("--no-snapshot", action="store_true", help="skip collection")

    sub.add_parser("evaluate", help="test the claims on real data")

    b = sub.add_parser("backtest", help="engine validation and real-data backtests")
    b.add_argument(
        "--synthetic-engine-check",
        action="store_true",
        help="run the labelled synthetic engine validation",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    cfg = load_config(args.config)

    if args.command == "snapshot":
        from compute_curve.snapshot import run_snapshot

        for o in run_snapshot(cfg, args.source, args.force):
            print(
                f"{o.source}: {o.status} listings={o.n_listings} index_rows={o.n_indices} "
                f"dropped={o.n_dropped} {o.detail}"
            )
        return 0
    if args.command == "backfill":
        from datetime import UTC, datetime, time

        from compute_curve.snapshot import backfill_cgi, backfill_gpurentalprices

        if args.source == "cgi":
            outs = backfill_cgi(
                cfg,
                datetime.combine(args.start, time(0, 0), tzinfo=UTC),
                datetime.combine(args.end, time(23, 45), tzinfo=UTC),
            )
        else:
            outs = backfill_gpurentalprices(cfg, args.start, args.end)
        for o in outs:
            print(f"{o.detail}: {o.status} listings={o.n_listings} dropped={o.n_dropped}")
        return 0
    if args.command == "index":
        from compute_curve.pipeline import load_inputs, write_own_index_outputs

        out = write_own_index_outputs(cfg, load_inputs(cfg))
        print(f"wrote {out}")
        return 0
    if args.command == "status":
        from compute_curve.pipeline import status

        print(status(cfg))
        return 0
    if args.command == "daily":
        from compute_curve.pipeline import daily

        today = args.date or utc_now().date()
        print(f"wrote {daily(cfg, today, not args.no_snapshot)}")
        return 0
    if args.command == "evaluate":
        from compute_curve.evaluation import run_evaluation

        print(f"wrote {run_evaluation(cfg)}")
        return 0
    if args.command == "backtest":
        from compute_curve.evaluation import run_backtests

        for path in run_backtests(cfg, engine_check=args.synthetic_engine_check):
            print(f"wrote {path}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
