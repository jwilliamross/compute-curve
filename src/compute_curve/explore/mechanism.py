"""Round-3 mechanism check: can CGI's aggregation alone produce the reversal?

docs/exploration_round3_plan.md section 9. CGI's published vote rule
(METHODOLOGY.md sections 6 and 7) is applied to SYNTHETIC seat prices from
:func:`compute_curve.synthetic.synthetic_cgi_panel`. Output is a mechanism
check, never a finding about CGI.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from compute_curve.config import Config
from compute_curve.synthetic import synthetic_cgi_panel

BANNER = "SYNTHETIC: mechanism check on simulated seat prices, not a result about CGI"
STEPS = 24  # 15-minute stamps in 6 hours


def trimmed_vote_mean(
    seat_prices: np.ndarray, sd_frac: float, lo: float = 1 / 3, hi: float = 2 / 3
) -> np.ndarray:
    """CGI's index per row: weighted mean of votes between the ``lo``/``hi`` weight quantiles.

    Each present seat (non-NaN) casts equal weight three times, at
    ``c(1 - sd_frac)``, ``c`` and ``c(1 + sd_frac)``; a vote straddling a
    quantile cut counts with the overlapping share of its weight.
    """
    c = np.asarray(seat_prices, dtype=float)
    votes = np.concatenate([c * (1 - sd_frac), c, c * (1 + sd_frac)], axis=1)
    w = np.where(np.isnan(votes), 0.0, 1.0)
    order = np.argsort(np.where(np.isnan(votes), np.inf, votes), axis=1)
    v = np.take_along_axis(np.nan_to_num(votes, nan=0.0), order, axis=1)
    ws = np.take_along_axis(w, order, axis=1)
    total = ws.sum(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        upper = np.cumsum(ws, axis=1) / total
        lower = upper - ws / total
        share = np.clip(np.minimum(upper, hi) - np.maximum(lower, lo), 0.0, None)
        out = (share * v).sum(axis=1) / share.sum(axis=1)
    return np.where(total[:, 0] > 0, out, np.nan)


def ewma(log_prices: np.ndarray, half_life_stamps: float) -> np.ndarray:
    """Per-seat exponentially weighted mean of log prices (CGI calc_v16, 1-hour half-life)."""
    a = 1.0 - 0.5 ** (1.0 / half_life_stamps)
    return pd.DataFrame(log_prices).ewm(alpha=a, adjust=False, ignore_na=True).mean().to_numpy()


def reversal_stats(log_index: np.ndarray) -> tuple[float, float, float]:
    """Hourly 6-hour-on-6-hour slope, VR(24) and ACF(1) of 15-minute changes."""
    v = pd.Series(log_index).ffill()
    hourly = v.iloc[::4].reset_index(drop=True)
    past, fut = hourly - hourly.shift(6), hourly.shift(-6) - hourly
    ok = past.notna() & fut.notna()
    beta = float(np.polyfit(past[ok], fut[ok], 1)[0])
    r = v.diff().dropna()
    vr = float((v - v.shift(STEPS)).dropna().var() / (STEPS * r.var()))
    acf1 = float(r.autocorr(1))
    return beta, vr, acf1


@dataclass(frozen=True)
class Scenario:
    name: str
    dropout: float = 0.0
    transient_sd: float = 0.0
    ewma: bool = False


SCENARIOS = (
    Scenario("S0 aggregation only"),
    Scenario("S1 + one-stamp seat drop-outs (2%)", dropout=0.02),
    Scenario("S2 + seat deviations (AR(1), 3h half-life, sd 0.03)", transient_sd=0.03),
    Scenario("S3 = S2 + 1-hour EWMA on seat prices", transient_sd=0.03, ewma=True),
)


def simulate(
    scenario: Scenario, n_seats: int, sd_frac: float, seeds: range, days: int = 60
) -> pd.DataFrame:
    rows = []
    for seed in seeds:
        panel = synthetic_cgi_panel(
            n_seats, days, seed, dropout=scenario.dropout, transient_sd=scenario.transient_sd
        )
        if not bool(panel["is_synthetic"].all()):
            raise ValueError("mechanism check accepts synthetic panels only")
        logp = panel.drop(columns="is_synthetic").to_numpy(float)
        if scenario.ewma:
            logp = np.where(np.isnan(logp), np.nan, ewma(logp, 4.0))
        idx = np.log(trimmed_vote_mean(np.exp(logp), sd_frac))
        beta, vr, acf1 = reversal_stats(idx)
        rows.append({"seed": seed, "beta": beta, "vr24": vr, "acf1": acf1})
    return pd.DataFrame(rows)


def verdict(s0: float, s1: float) -> str:
    if -0.10 <= s0 <= 0 and -0.10 <= s1 <= 0:
        return (
            "aggregation and drop-outs alone cannot produce the observed reversal; "
            "it needs seat-level deviations that last hours"
        )
    if s0 <= -0.25 or s1 <= -0.25:
        return "the aggregation rule alone can produce a reversal of the observed size"
    return "inconclusive"


def run_mechanism(cfg: Config, n_seeds: int = 20) -> Path:
    """Run every scenario for 17 and 9 seats and both sd floors; write the labelled report."""
    out = cfg.path("reports") / "exploration" / "round3_mechanism_simulation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Round 3: CGI aggregation mechanism check",
        "",
        f"**{BANNER}.** Plan: docs/exploration_round3_plan.md section 9.2.",
        f"{n_seeds} seeds x 60 days of 15-minute stamps per row; seeds from the project seed.",
        "Mean across seeds, with the 5th to 95th percentile in brackets.",
        "",
        "| Seats | sd floor | Scenario | beta (6h on 6h) | VR(24) | ACF(1), 15 min |",
        "|---|---|---|---|---|---|",
    ]
    base = cfg.project.seed
    means: dict[tuple[int, float, str], float] = {}
    for n_seats in (17, 9):
        for sd_frac in (0.03, 0.06):
            for sc in SCENARIOS:
                d = simulate(sc, n_seats, sd_frac, range(base, base + n_seeds))
                cells = []
                for col in ("beta", "vr24", "acf1"):
                    q5, q95 = d[col].quantile([0.05, 0.95])
                    cells.append(f"{d[col].mean():.3f} [{q5:.3f}, {q95:.3f}]")
                means[(n_seats, sd_frac, sc.name[:2])] = float(d["beta"].mean())
                lines.append(f"| {n_seats} | {sd_frac:g} | {sc.name} | " + " | ".join(cells) + " |")
    lines += ["", "## Pre-registered reading (section 9.2)", ""]
    for n_seats in (17, 9):
        for sd_frac in (0.03, 0.06):
            s0, s1 = means[(n_seats, sd_frac, "S0")], means[(n_seats, sd_frac, "S1")]
            lines.append(f"- {n_seats} seats, sd {sd_frac:g}: {verdict(s0, s1)}.")
    out.write_text("\n".join(lines) + "\n")
    return out
