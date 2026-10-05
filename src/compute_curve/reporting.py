"""Small, dependency-free helpers for markdown reports."""

from __future__ import annotations

import math

import pandas as pd


def fmt(v: object, digits: int = 4) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return "n/a"
        return f"{v:,.{digits}f}"
    return str(v)


def frame_to_md(df: pd.DataFrame, digits: int = 4) -> str:
    """Render a DataFrame as a GitHub-flavoured markdown table."""
    if df.empty:
        return "_(no rows)_"
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(fmt(v, digits) for v in row) + " |")
    return "\n".join(lines)
