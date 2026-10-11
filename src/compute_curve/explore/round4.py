"""Exploration round 4: forward one-shot replication of H01 (docs/exploration_round4_plan.md).

H01's frozen round-1 specification runs once on listing days 2026-10-07 to
2026-12-31, which no test has used. Listings are truncated to the window
before anything is computed, so every 5-day outcome lies inside it.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from compute_curve.config import Config, ExplorationConfig, Round4Config
from compute_curve.explore.data import Round1Data
from compute_curve.explore.hypotheses import h01
from compute_curve.explore.run import confirm_one, finish_confirmation

HID = "R4-01"


def in_window(listings: pd.DataFrame, window: tuple[date, date]) -> pd.DataFrame:
    d = pd.to_datetime(listings["as_of_date"]).dt.date
    return listings.loc[(d >= window[0]) & (d <= window[1])].reset_index(drop=True)


def window_complete(r4: Round4Config, today: date) -> bool:
    return today > r4.h01_forward[1]


def confirm_forward(
    data: Round1Data, frozen: dict[str, Any], ecfg: ExplorationConfig, r4: Round4Config
) -> dict[str, Any]:
    """H01 (frozen) on the forward window only: C1 one-sided, C2 out-of-sample R2."""
    fwd = replace(data, listings=in_window(data.listings, r4.h01_forward))
    built = h01(fwd, ecfg)
    row = finish_confirmation([confirm_one(built, frozen, ecfg)], ecfg)[0]
    out = asdict(row) | {"hid": HID, "replicates": "H01", "frozen": frozen}
    days = pd.to_datetime(built.frame["t"]) if not built.frame.empty else pd.Series(dtype=object)
    out["window"] = [str(days.min().date()), str(days.max().date())] if len(days) else []
    return out


def _clean(v: Any) -> Any:
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v


def run_confirmation4(cfg: Config, today: date | None = None) -> Path:  # pragma: no cover
    """Count days until the window closes; then run R4-01 once."""
    from compute_curve.explore.data import load_round1  # noqa: PLC0415
    from compute_curve.timeutil import utc_now  # noqa: PLC0415

    ecfg, r4 = cfg.exploration, cfg.exploration4
    if ecfg is None or r4 is None:
        raise RuntimeError("[exploration] and [exploration4] config are required")
    d = cfg.path("reports") / "exploration"
    out_json, out_md = d / "round4_confirmation.json", d / "round4_confirmation.md"
    today = today or utc_now().date()
    lines = ["# Exploration round 4: R4-01 status", "", f"Checked {today} (UTC)."]
    if out_json.exists():
        lines.append("\nDone earlier; see round4_confirmation.json.")
    else:
        data = load_round1(cfg)
        win = in_window(data.listings, r4.h01_forward)
        n_days = win["as_of_date"].nunique() if len(win) else 0
        if not window_complete(r4, today):
            lines += [
                "",
                f"Waiting for listings to {r4.h01_forward[1]} (runs from "
                f"{r4.h01_forward[1] + timedelta(days=1)}). No statistic is computed before then.",
                f"Listing days collected in the window so far: {n_days}.",
            ]
        else:
            rep = json.loads((d / "round2_replication.json").read_text())
            res = confirm_forward(data, rep["frozen"], ecfg, r4)
            res["generated"] = str(today)
            out_json.write_text(json.dumps(_clean(res), indent=2, default=str))
            lines += ["", f"- {HID} (H01 forward): {res['verdict']}, p {res['p_one_sided']:.3f}."]
    out_md.write_text("\n".join(lines) + "\n")
    return out_md
