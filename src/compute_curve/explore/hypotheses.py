"""The 12 round-1 hypotheses as (signal, target) series (docs/exploration_plan.md section 6).

Each builder takes :class:`Round1Data` that has already been restricted to
one set, so every value it returns uses only that set. A builder returns a
:class:`Built`: a frame with columns ``t``, ``x`` (signal), ``y`` (target)
and ``ctrl`` (the target's own change over the signal window, for the echo
check), plus the number of distinct periods in which the signal's
underlying one-period series changed. H01 is a panel and returns one row
per (day, provider).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

from compute_curve.claim4.market_data import (
    basket_excess,
    sessions_from_calendar,
    window_returns,
)
from compute_curve.config import Claim4Config, ExplorationConfig
from compute_curve.explore.data import Round1Data

EPS = 1e-12
AWS_CLASSES = {
    "H100": ("p5.48xlarge", "p5.4xlarge"),
    "H200": ("p5e.48xlarge", "p5en.48xlarge"),
}


@dataclass(frozen=True)
class Spec:
    hid: str
    kind: str  # "ts" (time series) or "panel" (H01)
    data: str  # datasets used
    signal: str
    target: str
    horizon: str
    lag: int  # Newey-West lag, observation units
    min_shift: int  # circular-shift minimum = signal window + outcome window
    block: int  # bootstrap block length
    expected_sign: int
    echo: bool  # echo check applies


@dataclass(frozen=True)
class Built:
    frame: pd.DataFrame
    n_events: int


SPECS: dict[str, Spec] = {
    s.hid: s
    for s in (
        Spec(
            "H01",
            "panel",
            "L",
            "provider premium over the cross-provider median (H100 on-demand)",
            "provider's own matched 5-day change",
            "5 days",
            5,
            5,
            5,
            -1,
            False,
        ),
        Spec(
            "H02",
            "ts",
            "L",
            "leaders' 5-day mean change",
            "followers' next 5-day mean change",
            "5 days",
            5,
            10,
            10,
            1,
            True,
        ),
        Spec(
            "H03",
            "ts",
            "L",
            "H100 spot listings' 5-day mean change",
            "H100 on-demand next 5-day mean change",
            "5 days",
            5,
            10,
            10,
            1,
            True,
        ),
        Spec(
            "H04",
            "ts",
            "L",
            "B200 on-demand 5-day mean change",
            "H100 on-demand next 5-day mean change",
            "5 days",
            5,
            10,
            10,
            1,
            True,
        ),
        Spec(
            "H05",
            "ts",
            "C",
            "CGI H100 past 6-hour change",
            "CGI H100 next 6-hour change",
            "6 hours",
            6,
            12,
            12,
            -1,
            False,
        ),
        Spec(
            "H06",
            "ts",
            "G",
            "GetDeploying H100 spot weekly change",
            "GetDeploying H100 on-demand next-week change",
            "1 week",
            1,
            2,
            5,
            1,
            True,
        ),
        Spec(
            "H07",
            "ts",
            "G",
            "GetDeploying H100 on-demand offer-count change",
            "GetDeploying H100 on-demand next-week change",
            "1 week",
            1,
            2,
            5,
            -1,
            True,
        ),
        Spec(
            "H08",
            "ts",
            "G",
            "GetDeploying B200 on-demand offer-count change",
            "GetDeploying H100 on-demand next-week change",
            "1 week",
            1,
            2,
            5,
            -1,
            True,
        ),
        Spec(
            "H09",
            "ts",
            "A",
            "AWS H100 spot 7-day change",
            "AWS H100 spot next 7-day change",
            "7 days",
            7,
            14,
            14,
            1,
            False,
        ),
        Spec(
            "H10",
            "ts",
            "A",
            "AWS H200 minus H100 7-day change",
            "AWS H100 spot next 7-day change",
            "7 days",
            7,
            14,
            14,
            1,
            True,
        ),
        Spec(
            "H11",
            "ts",
            "A+E",
            "neocloud 5-session excess return over XLK",
            "AWS H100 spot change over the next 7 days",
            "about 5 sessions",
            5,
            10,
            10,
            1,
            True,
        ),
        Spec(
            "H12",
            "ts",
            "A+E",
            "AWS H100 20-day spot change",
            "neocloud minus GPU-semis excess return, next 5 sessions",
            "5 sessions",
            5,
            20,
            20,
            1,
            True,
        ),
    )
}


# ---------------------------------------------------------------------------
# Our listings
# ---------------------------------------------------------------------------
def _full_days(index: pd.Index) -> pd.DatetimeIndex:
    days = pd.to_datetime(pd.Series(index))
    return pd.date_range(days.min(), days.max(), freq="D")


def log_wide(listings: pd.DataFrame, gpu: str, term: str) -> tuple[pd.DataFrame, pd.Series]:
    """Log price per (calendar day, listing) and the listing -> provider map."""
    sub = listings.loc[(listings["gpu_model"] == gpu) & (listings["term"] == term)]
    if sub.empty:
        return pd.DataFrame(), pd.Series(dtype=object)
    w = sub.pivot_table(index="as_of_date", columns="listing_id", values="price", aggfunc="median")
    w.index = pd.to_datetime(w.index)
    w = np.log(w.reindex(_full_days(w.index)))
    owner = sub.drop_duplicates("listing_id").set_index("listing_id")["provider"]
    return w, owner.reindex(w.columns)


def provider_change(w: pd.DataFrame, owner: pd.Series, k: int) -> pd.DataFrame:
    """Matched change per provider: median listing log change over ``k`` days.

    ``k > 0`` looks back (value at ``d`` is ``ln p(d) - ln p(d-k)``);
    ``k < 0`` looks ahead (``ln p(d+|k|) - ln p(d)``). NaN where a provider
    has no listing priced on both days.
    """
    if w.empty:
        return pd.DataFrame()
    chg = w - w.shift(k) if k > 0 else w.shift(k) - w
    return chg.T.groupby(owner.to_numpy()).median().T


def group_mean(
    prov: pd.DataFrame, providers: Sequence[str] | None, min_providers: int
) -> pd.Series:
    """Equal-weighted mean across providers with a matched change; NaN if too few."""
    if prov.empty:
        return pd.Series(dtype=float)
    cols = list(prov.columns) if providers is None else [p for p in prov.columns if p in providers]
    sub = prov[cols]
    return sub.mean(axis=1).where(sub.notna().sum(axis=1) >= min_providers)


def _count_events(one_period: pd.Series, t: pd.Series, window: int) -> int:
    """Distinct periods with a one-period change inside the windows actually used."""
    if t.empty or one_period.empty:
        return 0
    lo = pd.Timestamp(t.min()) - pd.Timedelta(days=window - 1)
    hi = pd.Timestamp(t.max())
    s = one_period.loc[(one_period.index >= lo) & (one_period.index <= hi)]
    return int((s.abs() > EPS).sum())


def _frame(x: pd.Series, y: pd.Series, ctrl: pd.Series | None) -> pd.DataFrame:
    df = pd.DataFrame({"x": x, "y": y})
    df["ctrl"] = ctrl if ctrl is not None else np.nan
    df = df.dropna(subset=["x", "y"])
    return df.rename_axis("t").reset_index()


def _long(wide: pd.DataFrame, name: str) -> pd.DataFrame:
    """(day x provider) frame to rows ``t``, ``provider``, ``name``."""
    df = wide.rename_axis(index="t", columns=None).reset_index()
    return df.melt(id_vars="t", var_name="provider", value_name=name)


def h01(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    w, owner = log_wide(data.listings, "H100", "on_demand")
    if w.empty:
        return Built(pd.DataFrame(columns=["t", "provider", "x", "y"]), 0)
    # ln P_p(d): log of the median of the provider's listing prices on d
    level = np.log(np.exp(w).T.groupby(owner.to_numpy()).median().T)
    premium = level.sub(level.median(axis=1), axis=0)
    fwd = provider_change(w, owner, -5)
    long = _long(premium, "x").merge(_long(fwd, "y"), on=["t", "provider"]).dropna()
    one_day = provider_change(w, owner, 1)
    any_change = (one_day.abs() > EPS).any(axis=1).astype(float)
    events = _count_events(any_change, long["t"], 1) if not long.empty else 0
    return Built(long, events)


def _listing_ts(
    data: Round1Data,
    ecfg: ExplorationConfig,
    signal: tuple[str, str],
    signal_providers: Callable[[pd.Index], list[str] | None],
    target_providers: Callable[[pd.Index], list[str] | None],
    signal_min: int,
) -> Built:
    ws, os_ = log_wide(data.listings, *signal)
    wt, ot = log_wide(data.listings, "H100", "on_demand")
    if ws.empty or wt.empty:
        return Built(pd.DataFrame(columns=["t", "x", "y", "ctrl"]), 0)
    days = ws.index.union(wt.index)
    ws, wt = ws.reindex(days), wt.reindex(days)
    sig_prov = provider_change(ws, os_, 5)
    tgt_back, tgt_fwd = provider_change(wt, ot, 5), provider_change(wt, ot, -5)
    sp = signal_providers(sig_prov.columns)
    tp = target_providers(tgt_fwd.columns)
    x = group_mean(sig_prov, sp, signal_min)
    y = group_mean(tgt_fwd, tp, ecfg.min_group_providers)
    ctrl = group_mean(tgt_back, tp, ecfg.min_group_providers)
    frame = _frame(x, y, ctrl)
    one = group_mean(provider_change(ws, os_, 1), sp, signal_min)
    return Built(frame, _count_events(one, frame["t"], 5))


def h02(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    leaders = set(ecfg.leaders)
    return _listing_ts(
        data,
        ecfg,
        ("H100", "on_demand"),
        lambda cols: [c for c in cols if c in leaders],
        lambda cols: [c for c in cols if c not in leaders],
        ecfg.min_group_providers,
    )


def h03(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    return _listing_ts(
        data, ecfg, ("H100", "spot"), lambda _: None, lambda _: None, ecfg.min_spot_providers
    )


def h04(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    return _listing_ts(
        data, ecfg, ("B200", "on_demand"), lambda _: None, lambda _: None, ecfg.min_group_providers
    )


# ---------------------------------------------------------------------------
# CGI
# ---------------------------------------------------------------------------
def cgi_hourly(cgi: pd.DataFrame, gpu: str, max_age_minutes: int) -> pd.Series:
    """Log CGI value at each full hour: the latest value no older than ``max_age``."""
    c = cgi.loc[cgi["gpu_model"] == gpu].sort_values("as_of")
    if c.empty:
        return pd.Series(dtype=float)
    start = c["as_of"].min().ceil("h")
    end = c["as_of"].max().floor("h")
    grid = pd.DataFrame({"t": pd.date_range(start, end, freq="h")})
    m = pd.merge_asof(
        grid,
        c[["as_of", "value"]],
        left_on="t",
        right_on="as_of",
        direction="backward",
        tolerance=pd.Timedelta(minutes=max_age_minutes),
    )
    return pd.Series(np.log(m["value"].to_numpy(dtype=float)), index=pd.DatetimeIndex(m["t"]))


def h05(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    v = cgi_hourly(data.cgi, "H100", ecfg.cgi_max_age_minutes)
    if v.empty:
        return Built(pd.DataFrame(columns=["t", "x", "y", "ctrl"]), 0)
    v = v.asfreq("h")
    frame = _frame(v - v.shift(6), v.shift(-6) - v, None)
    one = (v - v.shift(1)).dropna()
    if frame.empty:
        return Built(frame, 0)
    lo, hi = frame["t"].min() - pd.Timedelta(hours=5), frame["t"].max()
    one = one.loc[(one.index >= lo) & (one.index <= hi)]
    return Built(frame, int((one.abs() > EPS).sum()))


# ---------------------------------------------------------------------------
# GetDeploying
# ---------------------------------------------------------------------------
def gd_series(gd: pd.DataFrame, gpu: str, term: str, col: str) -> pd.Series:
    """Log of a GetDeploying weekly column on a regular Monday grid (gaps are NaN)."""
    g = gd.loc[(gd["gpu_model"] == gpu) & (gd["term"] == term)].set_index("week")[col]
    if g.empty:
        return pd.Series(dtype=float)
    g.index = pd.to_datetime(g.index)
    grid = pd.date_range(g.index.min(), g.index.max(), freq="7D")
    g = g.reindex(grid).astype(float)
    return np.log(g.where(g > 0))


def _gd(data: Round1Data, signal: tuple[str, str, str]) -> Built:
    od = gd_series(data.gd, "H100", "on_demand", "value")
    sig = gd_series(data.gd, *signal)
    if od.empty or sig.empty:
        return Built(pd.DataFrame(columns=["t", "x", "y", "ctrl"]), 0)
    grid = od.index.union(sig.index)
    od, sig = od.reindex(grid), sig.reindex(grid)
    dx = sig - sig.shift(1)
    frame = _frame(dx, od.shift(-1) - od, od - od.shift(1))
    return Built(frame, int((frame["x"].abs() > EPS).sum()))


def h06(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    return _gd(data, ("H100", "spot", "value"))


def h07(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    return _gd(data, ("H100", "on_demand", "n_listings"))


def h08(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    return _gd(data, ("B200", "on_demand", "n_listings"))


# ---------------------------------------------------------------------------
# AWS spot
# ---------------------------------------------------------------------------
def aws_log_wide(aws: pd.DataFrame, gpu: str) -> pd.DataFrame:
    """Log price per (calendar day, pool) for one class; missing days are NaN."""
    sub = aws.loc[aws["instance_type"].isin(AWS_CLASSES[gpu])]
    if sub.empty:
        return pd.DataFrame()
    w = sub.pivot_table(
        index="day",
        columns=["az_id", "instance_type"],
        values="price_per_gpu_hour",
        aggfunc="median",
    )
    w.index = pd.to_datetime(w.index)
    return np.log(w.reindex(_full_days(w.index)))


def aws_change(w: pd.DataFrame, k: int, min_pools: int) -> pd.Series:
    """Matched-pool median log change over ``k`` days (``k > 0`` back, ``k < 0`` ahead)."""
    if w.empty:
        return pd.Series(dtype=float)
    chg = w - w.shift(k) if k > 0 else w.shift(k) - w
    return chg.median(axis=1).where(chg.notna().sum(axis=1) >= min_pools)


def _aws_events(w: pd.DataFrame, t: pd.Series, window: int, min_pools: int) -> int:
    return _count_events(aws_change(w, 1, min_pools), t, window)


def h09(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    w = aws_log_wide(data.aws, "H100")
    frame = _frame(aws_change(w, 7, ecfg.min_pools), aws_change(w, -7, ecfg.min_pools), None)
    return Built(frame, _aws_events(w, frame["t"], 7, ecfg.min_pools))


def h10(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    w1, w2 = aws_log_wide(data.aws, "H100"), aws_log_wide(data.aws, "H200")
    if w1.empty or w2.empty:
        return Built(pd.DataFrame(columns=["t", "x", "y", "ctrl"]), 0)
    days = w1.index.union(w2.index)
    w1, w2 = w1.reindex(days), w2.reindex(days)
    back1 = aws_change(w1, 7, ecfg.min_pools)
    x = aws_change(w2, 7, ecfg.min_pools) - back1
    frame = _frame(x, aws_change(w1, -7, ecfg.min_pools), back1)
    one = aws_change(w2, 1, ecfg.min_pools) - aws_change(w1, 1, ecfg.min_pools)
    return Built(frame, _count_events(one, frame["t"], 7))


# ---------------------------------------------------------------------------
# Equities joined with AWS
# ---------------------------------------------------------------------------
def sessions_from_bars(bars: pd.DataFrame) -> pd.DataFrame:
    """Sessions at 09:30-16:00 New York time from the bar dates (early closes ignored)."""
    days = sorted(set(bars["session"]))
    rows = [{"date": d.isoformat(), "open": "09:30", "close": "16:00"} for d in days]
    return sessions_from_calendar(rows)


def bucket_excess(bars: pd.DataFrame, c4: Claim4Config, bucket: str, h: int) -> pd.Series:
    """Bucket excess over the benchmark, open of ``t`` to close of ``t+h-1``, by session."""
    sessions = sessions_from_bars(bars)
    ret, _ = window_returns(bars, sessions, h)
    members = c4.universe.buckets()[bucket]
    return basket_excess(ret, members, c4.benchmark, c4.min_bucket_coverage)


def _session_index(s: pd.Series) -> pd.Series:
    out = s.copy()
    out.index = pd.to_datetime(pd.Index(s.index))
    return out


def h11(data: Round1Data, ecfg: ExplorationConfig, c4: Claim4Config) -> Built:
    if data.bars.empty or data.aws.empty:
        return Built(pd.DataFrame(columns=["t", "x", "y", "ctrl"]), 0)
    r5 = _session_index(bucket_excess(data.bars, c4, "neocloud", 5))
    x = r5.shift(4)  # the 5-session window ending at the close of t
    w = aws_log_wide(data.aws, "H100")
    fwd = aws_change(w, -7, ecfg.min_pools).reindex(x.index)
    back = aws_change(w, 7, ecfg.min_pools).reindex(x.index)
    frame = _frame(x, fwd, back)
    one = _session_index(bucket_excess(data.bars, c4, "neocloud", 1))
    return Built(frame, _count_events(one, frame["t"], 7))


def h12(data: Round1Data, ecfg: ExplorationConfig, c4: Claim4Config) -> Built:
    if data.bars.empty or data.aws.empty:
        return Built(pd.DataFrame(columns=["t", "x", "y", "ctrl"]), 0)
    spread = _session_index(
        bucket_excess(data.bars, c4, "neocloud", 5) - bucket_excess(data.bars, c4, "gpu_semis", 5)
    )
    w = aws_log_wide(data.aws, "H100")
    trend = aws_change(w, 20, ecfg.min_pools)
    dstar = spread.index - pd.Timedelta(days=1)  # the calendar day before the session
    x = pd.Series(trend.reindex(dstar).to_numpy(), index=spread.index)
    frame = _frame(x, spread, spread.shift(5))
    one = aws_change(w, 1, ecfg.min_pools)
    one.index = one.index + pd.Timedelta(days=1)  # align day d* with session d* + 1
    return Built(frame, _count_events(one, frame["t"], 21))


BUILDERS: dict[str, Callable[..., Built]] = {
    "H01": h01,
    "H02": h02,
    "H03": h03,
    "H04": h04,
    "H05": h05,
    "H06": h06,
    "H07": h07,
    "H08": h08,
    "H09": h09,
    "H10": h10,
    "H11": h11,
    "H12": h12,
}
EQUITY_BUILDERS = frozenset({"H11", "H12"})


def build(hid: str, data: Round1Data, ecfg: ExplorationConfig, c4: Claim4Config) -> Built:
    fn = BUILDERS[hid]
    return fn(data, ecfg, c4) if hid in EQUITY_BUILDERS else fn(data, ecfg)
