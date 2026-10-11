"""Proxy-calibrated Monte Carlo fair-value strip for GPU1/GPU2 (docs/montecarlo_fair_value.md).

MODEL OUTPUT ON A PROXY. The settlement index's history cannot be stored
(B7), so the short-term factor is fitted on the Computable GPU Index daily
close and the long-term factor on the GetDeploying weekly median. Results are
reported relative to today's spot (F / S0) beside a random-walk scenario; the
gap between the two is model risk. Nothing here is a trading signal (D26, D55).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.backtest.bootstrap import circular_block_indices
from compute_curve.config import Config, ContractSpec
from compute_curve.contracts import listed_contracts, settlement_days
from compute_curve.models import montecarlo as mc
from compute_curve.models.schwartz_smith import SSParams
from compute_curve.timeutil import utc_now

BANNER = "MODEL OUTPUT ON A PROXY: not the settlement index, not a forecast to trade on"
GD_TERM = "on_demand"


@dataclass(frozen=True)
class ShortTermFit:
    kappa: float
    sigma_chi: float
    half_life_days: float
    half_life_ci: tuple[float, float]
    chi0: float
    n: int


@dataclass(frozen=True)
class LongTermFit:
    mu_xi: float
    sigma_xi: float
    n: int

    @property
    def drift_ci(self) -> tuple[float, float]:
        """95% CI of the annual drift: mean +/- 1.96 sigma / sqrt(years of data)."""
        half = 1.96 * self.sigma_xi / np.sqrt(self.n / 52)
        return (self.mu_xi - half, self.mu_xi + half)


def daily_log_close(cgi: pd.DataFrame, gpu: str) -> pd.Series:
    """Log of the last CGI value of each UTC day."""
    c = cgi.loc[cgi["gpu_model"] == gpu].sort_values("as_of")
    if c.empty:
        return pd.Series(dtype=float)
    day = pd.to_datetime(c["as_of"], utc=True).dt.date
    last = c.groupby(day)["value"].last()
    return np.log(last.astype(float))


def _ar1_ou(resid: np.ndarray) -> tuple[float, float] | None:
    """(kappa per year, sigma_chi) from an AR(1) on daily residuals; None if not mean-reverting."""
    x0, x1 = resid[:-1], resid[1:]
    b = float(np.dot(x0 - x0.mean(), x1 - x1.mean()) / np.dot(x0 - x0.mean(), x0 - x0.mean()))
    if not 0 < b < 1:
        return None
    e = x1 - (x1.mean() - b * x0.mean()) - b * x0
    kappa = -np.log(b) * mc.DAYS_PER_YEAR
    sigma = float(np.sqrt(np.var(e, ddof=2) * 2 * kappa / (1 - b**2)))
    return float(kappa), sigma


def fit_short_term(log_daily: pd.Series, seed: int, n_boot: int = 1000) -> ShortTermFit | None:
    """Detrended AR(1) mapped exactly to OU; block-bootstrap CI for the half-life."""
    y = log_daily.to_numpy(float)
    if y.size < 20:
        return None
    t = np.arange(y.size, dtype=float)
    slope, icept = np.polyfit(t, y, 1)
    resid = y - (icept + slope * t)
    fit = _ar1_ou(resid)
    if fit is None:
        return None
    kappa, sigma = fit
    rng = np.random.default_rng(seed)
    hls = []
    for _ in range(n_boot):
        idx = circular_block_indices(resid.size - 1, 5, rng)
        pairs = np.column_stack([resid[:-1][idx], resid[1:][idx]])
        x0, x1 = pairs[:, 0], pairs[:, 1]
        den = float(np.dot(x0 - x0.mean(), x0 - x0.mean()))
        if den <= 0:
            continue
        b = float(np.dot(x0 - x0.mean(), x1 - x1.mean()) / den)
        if 0 < b < 1:
            hls.append(np.log(2) / -np.log(b))
    lo, hi = np.quantile(hls, [0.025, 0.975]) if hls else (np.nan, np.nan)
    return ShortTermFit(
        kappa,
        sigma,
        float(np.log(2) / kappa * mc.DAYS_PER_YEAR),
        (float(lo), float(hi)),
        float(resid[-1]),
        int(y.size),
    )


def fit_long_term(log_weekly: pd.Series) -> LongTermFit | None:
    d = np.diff(log_weekly.to_numpy(float))
    d = d[np.isfinite(d)]
    if d.size < 10:
        return None
    return LongTermFit(float(d.mean() * 52), float(d.std(ddof=1) * np.sqrt(52)), int(d.size))


def scenarios(st: ShortTermFit, lt: LongTermFit, daily_sd: float) -> dict[str, SSParams]:
    """Fitted two-factor model and a random walk with the same daily volatility and drift."""
    fitted = SSParams(
        kappa=st.kappa, sigma_chi=st.sigma_chi, sigma_xi=lt.sigma_xi, mu_xi=lt.mu_xi, rho=0.0
    )
    rw_sigma = max(daily_sd * np.sqrt(mc.DAYS_PER_YEAR), 1e-4)
    random_walk = SSParams(kappa=50.0, sigma_chi=1e-6, sigma_xi=rw_sigma, mu_xi=lt.mu_xi, rho=0.0)
    zero = SSParams(
        kappa=st.kappa, sigma_chi=st.sigma_chi, sigma_xi=lt.sigma_xi, mu_xi=0.0, rho=0.0
    )
    return {
        "two-factor (fitted)": fitted,
        "two-factor, zero drift": zero,
        "random walk": random_walk,
    }


def strip(
    spec: ContractSpec,
    p: SSParams,
    x0: mc.State,
    trade_date: date,
    n_months: int,
    n_paths: int,
    seed: int,
    strikes_rel: tuple[float, ...] = (1.0,),
) -> list[mc.MonthResult]:
    """Per contract month: statistics of the business-day average of future days only."""
    months = [c.month for c in listed_contracts(spec, trade_date)[:n_months]]
    day_sets = []
    for m in months:
        days = [(d - trade_date).days for d in settlement_days(spec, m) if d > trade_date]
        day_sets.append(days)
    horizon = max((max(d) for d in day_sets if d), default=0)
    if horizon == 0:
        return []
    paths = mc.simulate_log_spot(p, x0, horizon, n_paths, seed)
    return [
        mc.month_result(m.strftime("%Y-%m"), paths, days, p, x0, [], strikes_rel)
        for m, days in zip(months, day_sets, strict=True)
        if days
    ]


# ---------------------------------------------------------------------------
# Runner (reads local data)
# ---------------------------------------------------------------------------
def _f(v: float, nd: int = 3) -> str:
    return "n/a" if not np.isfinite(v) else f"{v:.{nd}f}"


def render(rows: list[dict[str, Any]], trade_date: date, n_paths: int) -> str:
    lines = [
        "# Monte Carlo fair-value strip (GPU1, GPU2)",
        "",
        f"**{BANNER}.** As of {trade_date}. Method: docs/montecarlo_fair_value.md (D55).",
        f"{n_paths} antithetic paths per scenario; Kemna-Vorst geometric control variate. "
        "Values are relative to today's proxy spot S0 (F/S0), so they can be applied to the "
        "settlement index's level once known. Real-world expectations: a futures price "
        "different from these is a risk premium or information, not automatically a mispricing.",
        "",
    ]
    for r in rows:
        stf, ltf = r["short_term"], r["long_term"]
        lines += [
            f"## {r['product']} ({r['gpu']})",
            "",
            f"- Short-term factor from CGI daily close ({stf['n']} days): half-life "
            f"{_f(stf['half_life_days'], 1)} days, 95% bootstrap CI "
            f"[{_f(stf['half_life_ci'][0], 1)}, {_f(stf['half_life_ci'][1], 1)}]; "
            f"sigma_chi {_f(stf['sigma_chi'])}/yr.",
            f"- Long-term factor from GetDeploying weekly median ({ltf['n']} weekly changes): "
            f"drift {_f(ltf['mu_xi'])}/yr (95% CI [{_f(ltf['drift_ci'][0])}, "
            f"{_f(ltf['drift_ci'][1])}]: not distinguishable from zero if the CI spans it), "
            f"sigma_xi {_f(ltf['sigma_xi'])}/yr. The slope of the strip comes from this drift, "
            "so it is model risk, not a finding; compare the zero-drift scenario.",
            "",
        ]
        for name, months in r["scenarios"].items():
            lines += [
                f"### Scenario: {name}",
                "",
                "| Month | Days | F/S0 (analytic) | MC mean (CV), SE | 5% | 50% | 95% "
                "| 95% VaR, one long contract (% of F) | ATM Asian call (% of F) |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
            for m in months:
                f = m["analytic_mean"]
                lines.append(
                    f"| {m['label']} | {m['n_days']} | {_f(f)} | {_f(m['mc_mean_cv'])} "
                    f"({m['mc_se_cv']:.1e}) | {_f(m['quantiles']['q05'])} | "
                    f"{_f(m['quantiles']['q50'])} | {_f(m['quantiles']['q95'])} | "
                    f"{_f(100 * m['var95_long_per_contract'] / (mc.GPU_HOURS * f), 1)} | "
                    f"{_f(100 * m['asian_calls']['1'] / f, 2)} |"
                )
            lines.append("")
    return "\n".join(lines) + "\n"


def run_fairvalue(
    cfg: Config, n_months: int = 12, n_paths: int = 20000
) -> Path:  # pragma: no cover
    from compute_curve.explore.data import load_round1  # noqa: PLC0415

    data = load_round1(cfg)
    trade_date = utc_now().date()
    rows = []
    for product, spec in cfg.contracts.items():
        gpu = spec.gpu_model
        logd = daily_log_close(data.cgi, gpu)
        gd = data.gd.loc[(data.gd["gpu_model"] == gpu) & (data.gd["term"] == GD_TERM)]
        logw = np.log(gd.sort_values("week")["value"].astype(float))
        stf = fit_short_term(logd, cfg.project.seed)
        ltf = fit_long_term(logw)
        if stf is None or ltf is None:
            continue
        daily_sd = float(np.diff(logd.to_numpy(float)).std(ddof=1))
        x0 = mc.State(chi=stf.chi0, xi=-stf.chi0)  # ln S0 = 0: results are F/S0
        out: dict[str, Any] = {}
        for name, p in scenarios(stf, ltf, daily_sd).items():
            state = x0 if name.startswith("two") else mc.State(chi=0.0, xi=0.0)  # RW: ln S0 = 0
            res = strip(spec, p, state, trade_date, n_months, n_paths, cfg.project.seed)
            out[name] = [asdict(m) for m in res]
        rows.append(
            {
                "product": product,
                "gpu": gpu,
                "short_term": asdict(stf),
                "long_term": asdict(ltf) | {"drift_ci": ltf.drift_ci},
                "scenarios": out,
            }
        )
    d = cfg.path("reports") / "fairvalue"
    d.mkdir(parents=True, exist_ok=True)
    path = d / "strip.md"
    path.write_text(render(rows, trade_date, n_paths))
    return path
