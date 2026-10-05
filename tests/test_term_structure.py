"""Term-structure walk-forward pipeline on SYNTHETIC data (engine validation, not a result)."""

from datetime import date

import numpy as np
import pytest

from compute_curve.config import HardwareLaunch
from compute_curve.models.schwartz_smith import SSParams
from compute_curve.models.term_structure import (
    build_panel,
    jumps_between,
    launch_dates,
    score,
    walk_forward,
)
from compute_curve.paper.market import MarketData
from compute_curve.synthetic import synthetic_config, synthetic_market


def test_jumps_between_counts_launches_in_window():
    launches = [date(2027, 1, 10), date(2027, 6, 1)]
    out = jumps_between(
        date(2027, 1, 1), [date(2027, 1, 5), date(2027, 1, 10), date(2027, 7, 1)], launches
    )
    assert out.tolist() == [0.0, 1.0, 2.0]


def test_launch_dates_filter_by_model():
    ls = [
        HardwareLaunch(
            name="a",
            window_start=date(2027, 7, 1),
            affects=["H100", "B200"],
            kind="announced",
            source="x",
        ),
        HardwareLaunch(
            name="b",
            window_start=date(2026, 8, 26),
            affects=["B200"],
            kind="volume_shipments",
            source="y",
        ),
    ]
    assert launch_dates(ls, "H100") == [date(2027, 7, 1)]
    assert launch_dates(ls, "B200") == [date(2026, 8, 26), date(2027, 7, 1)]


def _market(cfg, n_days, params, seed):
    scfg = synthetic_config(cfg)
    spec = scfg.contracts["GPU1"]
    sm = synthetic_market(spec, date(2025, 1, 1), n_days, params, seed=seed)
    return (
        scfg,
        spec,
        MarketData.build(settlements=sm.settlements, published_index=sm.published_index),
    )


def test_panel_uses_calendar_grid_and_future_months_only(cfg):
    scfg, spec, md = _market(cfg, 60, SSParams(), seed=1)
    panel = build_panel(md.settlements, spec, [])
    assert panel is not None
    assert (panel.trade_dates[1] - panel.trade_dates[0]).days == 1
    weekend = [i for i, d in enumerate(panel.trade_dates) if d.weekday() >= 5]
    assert np.all(np.isnan(panel.y[weekend]))
    for d, months in zip(panel.trade_dates, panel.months, strict=True):
        assert all(m is None or m > f"{d:%Y-%m}" for m in months)


@pytest.mark.slow
def test_model_learns_risk_premium_on_synthetic(cfg):
    # Futures embed a large risk premium (mu* far below mu): the model, which
    # estimates the real-world drift, should beat the futures price at long
    # horizons. SYNTHETIC: validates the pipeline, says nothing about markets.
    p = SSParams(
        kappa=2.0,
        sigma_chi=0.3,
        sigma_xi=0.1,
        rho=0.0,
        mu_xi=0.0,
        mu_xi_star=-0.6,
        lambda_chi=0.0,
        meas_std=0.003,
    )
    scfg, spec, md = _market(cfg, 420, p, seed=7)
    rows = walk_forward(md, spec, [], SSParams(), min_observations=150, max_horizon=4, maxiter=600)
    assert not rows.empty
    sc = score(rows)
    far = sc[sc["horizon_months"] >= 3].groupby("method")["mse_log"].mean()
    assert far["model"] < far["futures"]
