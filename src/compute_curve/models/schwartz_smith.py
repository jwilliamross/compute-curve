"""Schwartz-Smith (2000) two-factor model with depreciation and launch jumps.

Log spot index::

    ln S_t = g(t) + chi_t + xi_t
    d chi = -kappa chi dt + sigma_chi dZ_chi                 (short-term, mean reverting)
    d xi  =  mu_xi dt     + sigma_xi  dZ_xi  + sum_k J_k dN_k(t)   (long-term level)
    dZ_chi dZ_xi = rho dt

* ``g(t) = -delta * t`` is a deterministic depreciation drift (t in years from
  the model's reference date). With spot data alone ``delta`` and ``mu_xi``
  are not separately identifiable, so estimation fixes one of them.
* ``N_k`` is a scheduled jump at hardware-launch date ``tau_k`` with size
  ``J_k ~ N(m_J, s_J^2)``: timing known, size uncertain, permanent effect.

Risk-neutral dynamics replace ``mu_xi`` by ``mu_xi_star`` and add
``-lambda_chi`` to the chi drift. Futures on the spot (Schwartz and Smith
2000, eq. 9, extended)::

    ln F(t, T) = g(T) + e^{-kappa tau} chi_t + xi_t + A(tau)
                 + sum_{t < tau_k <= T} (m_J + s_J^2 / 2)

    A(tau) = mu_xi_star tau - (1 - e^{-kappa tau}) lambda_chi / kappa
             + 0.5 [ (1 - e^{-2 kappa tau}) sigma_chi^2 / (2 kappa)
                     + sigma_xi^2 tau
                     + 2 (1 - e^{-kappa tau}) rho sigma_chi sigma_xi / kappa ]

Full derivation: ``docs/term_structure_model.md``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace

import numpy as np
from scipy import optimize

LOG_2PI = float(np.log(2 * np.pi))


@dataclass(frozen=True)
class SSParams:
    kappa: float = 2.0
    sigma_chi: float = 0.3
    sigma_xi: float = 0.15
    rho: float = 0.0
    mu_xi: float = 0.0
    mu_xi_star: float = 0.0
    lambda_chi: float = 0.0
    delta: float = 0.0
    jump_mean: float = 0.0
    jump_std: float = 0.0
    meas_std: float = 0.01

    def __post_init__(self) -> None:
        if self.kappa <= 0 or self.sigma_chi <= 0 or self.sigma_xi <= 0 or self.meas_std <= 0:
            raise ValueError("kappa, sigmas and meas_std must be positive")
        if not -1 < self.rho < 1:
            raise ValueError("rho must lie in (-1, 1)")
        if self.jump_std < 0:
            raise ValueError("jump_std must be non-negative")


def a_tau(p: SSParams, tau: float | np.ndarray) -> np.ndarray:
    """Deterministic term of the log futures price (Schwartz-Smith 2000, eq. 9)."""
    t = np.asarray(tau, dtype=float)
    k = p.kappa
    e1 = 1 - np.exp(-k * t)
    e2 = 1 - np.exp(-2 * k * t)
    var = (
        e2 * p.sigma_chi**2 / (2 * k)
        + p.sigma_xi**2 * t
        + 2 * e1 * p.rho * p.sigma_chi * p.sigma_xi / k
    )
    return p.mu_xi_star * t - e1 * p.lambda_chi / k + 0.5 * var


def futures_log_price(
    p: SSParams,
    chi: float,
    xi: float,
    tau: float,
    t_years: float = 0.0,
    n_jumps: int = 0,
) -> float:
    """ln F(t, t + tau) given the state at t. ``t_years`` positions g(.)."""
    g_T = -p.delta * (t_years + tau)
    jumps = n_jumps * (p.jump_mean + 0.5 * p.jump_std**2)
    return float(g_T + np.exp(-p.kappa * tau) * chi + xi + a_tau(p, tau) + jumps)


def transition(
    p: SSParams, dt: float, jump: bool = False
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact discrete transition x_t = c + G x_{t-1} + w, w ~ N(0, W) (real-world)."""
    k = p.kappa
    a = np.exp(-k * dt)
    G = np.array([[a, 0.0], [0.0, 1.0]])
    c = np.array([0.0, p.mu_xi * dt + (p.jump_mean if jump else 0.0)])
    var_c = p.sigma_chi**2 * (1 - np.exp(-2 * k * dt)) / (2 * k)
    var_x = p.sigma_xi**2 * dt + (p.jump_std**2 if jump else 0.0)
    cov = p.rho * p.sigma_chi * p.sigma_xi * (1 - a) / k
    W = np.array([[var_c, cov], [cov, var_x]])
    return c, G, W


@dataclass(frozen=True)
class KalmanOutput:
    loglik: float
    n_obs: int
    filtered_mean: np.ndarray  # (T, 2)
    filtered_cov: np.ndarray  # (T, 2, 2)
    pred_obs_mean: np.ndarray  # (T, n) one-step-ahead predictions of y
    pred_obs_var: np.ndarray  # (T, n) diagonal of predicted y variance


def kalman_filter(
    y: np.ndarray,
    d: np.ndarray,
    Z: np.ndarray,
    p: SSParams,
    dt: float,
    jumps: Sequence[bool] | None = None,
    x0: np.ndarray | None = None,
    P0: np.ndarray | None = None,
) -> KalmanOutput:
    """Linear Gaussian Kalman filter with missing observations (NaN in ``y``).

    y: (T, n) observations; d: (T, n) intercepts; Z: (T, n, 2) loadings on
    (chi, xi). Measurement noise is iid N(0, meas_std^2) per observation.
    The prediction-error decomposition gives the exact Gaussian log-likelihood.
    """
    T, n = y.shape
    x = np.array([0.0, float(np.nanmean(y[: max(1, min(T, 5))]) if np.isfinite(y).any() else 0.0)])
    if x0 is not None:
        x = np.asarray(x0, dtype=float)
    P = np.diag([p.sigma_chi**2 / (2 * p.kappa), 1.0]) if P0 is None else np.asarray(P0, float)
    jumps = list(jumps) if jumps is not None else [False] * T
    c0, G0, W0 = transition(p, dt, False)
    c1, G1, W1 = transition(p, dt, True)
    ll = 0.0
    n_obs = 0
    fm = np.zeros((T, 2))
    fc = np.zeros((T, 2, 2))
    pm = np.full((T, n), np.nan)
    pv = np.full((T, n), np.nan)
    r2 = p.meas_std**2
    for t in range(T):
        if t > 0:
            c, G, W = (c1, G1, W1) if jumps[t] else (c0, G0, W0)
            x = c + G @ x
            P = G @ P @ G.T + W
        obs = np.isfinite(y[t])
        Zt = Z[t]
        pm[t] = d[t] + Zt @ x
        pv[t] = np.einsum("ij,jk,ik->i", Zt, P, Zt) + r2
        if obs.any():
            Zo = Zt[obs]
            v = y[t, obs] - (d[t, obs] + Zo @ x)
            F = Zo @ P @ Zo.T + r2 * np.eye(int(obs.sum()))
            try:
                Fi = np.linalg.inv(F)
                sign, logdet = np.linalg.slogdet(F)
            except np.linalg.LinAlgError:
                return KalmanOutput(-np.inf, n_obs, fm, fc, pm, pv)
            if sign <= 0:
                return KalmanOutput(-np.inf, n_obs, fm, fc, pm, pv)
            K = P @ Zo.T @ Fi
            x = x + K @ v
            P = (np.eye(2) - K @ Zo) @ P
            P = 0.5 * (P + P.T)
            ll += -0.5 * (obs.sum() * LOG_2PI + logdet + v @ Fi @ v)
            n_obs += int(obs.sum())
        fm[t] = x
        fc[t] = P
    return KalmanOutput(float(ll), n_obs, fm, fc, pm, pv)


# ----------------------------------------------------------------------------
# Spot-only estimation (published index history, no futures)
# ----------------------------------------------------------------------------
def spot_measurement(
    log_spot: np.ndarray, t_years: np.ndarray, delta: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """y_t = g(t) + chi_t + xi_t + e_t with g(t) = -delta t."""
    T = log_spot.size
    y = log_spot.reshape(T, 1)
    d = (-delta * t_years).reshape(T, 1)
    Z = np.tile(np.array([[[1.0, 1.0]]]), (T, 1, 1))
    return y, d, Z


def spot_loglik(
    log_spot: np.ndarray,
    p: SSParams,
    dt: float,
    t_years: np.ndarray | None = None,
    jumps: Sequence[bool] | None = None,
) -> float:
    """Exact Gaussian log-likelihood of a spot-only series (scalar fast path).

    Numerically identical to :func:`kalman_filter` with
    :func:`spot_measurement`, written with Python floats because the 2x2
    algebra is faster that way inside an optimizer loop.
    """
    y = np.asarray(log_spot, float)
    T = y.size
    ty = np.arange(T) * dt if t_years is None else np.asarray(t_years, float)
    jl = list(jumps) if jumps is not None else [False] * T
    c0, G0, W0 = transition(p, dt, False)
    c1, _, W1 = transition(p, dt, True)
    a = float(G0[0, 0])
    first = y[: max(1, min(T, 5))]
    x0 = 0.0
    x1 = float(np.nanmean(first)) if np.isfinite(first).any() else 0.0
    p00, p01, p11 = p.sigma_chi**2 / (2 * p.kappa), 0.0, 1.0
    r2 = p.meas_std**2
    ll = 0.0
    for t in range(T):
        if t > 0:
            c, W = (c1, W1) if jl[t] else (c0, W0)
            x0, x1 = a * x0 + float(c[0]), x1 + float(c[1])
            p00, p01, p11 = (
                a * a * p00 + float(W[0, 0]),
                a * p01 + float(W[0, 1]),
                p11 + float(W[1, 1]),
            )
        yt = y[t]
        if not np.isfinite(yt):
            continue
        g = -p.delta * ty[t]
        v = yt - (g + x0 + x1)
        f = p00 + 2 * p01 + p11 + r2
        if f <= 0:
            return -np.inf
        k0 = (p00 + p01) / f
        k1 = (p01 + p11) / f
        x0 += k0 * v
        x1 += k1 * v
        h0, h1 = p00 + p01, p01 + p11
        p00, p01, p11 = p00 - k0 * h0, p01 - k0 * h1, p11 - k1 * h1
        ll += -0.5 * (LOG_2PI + np.log(f) + v * v / f)
    return float(ll)


_SPOT_FREE = ("kappa", "sigma_chi", "sigma_xi", "rho", "mu_xi", "meas_std")


def _pack(p: SSParams) -> np.ndarray:
    return np.array(
        [
            np.log(p.kappa),
            np.log(p.sigma_chi),
            np.log(p.sigma_xi),
            np.arctanh(p.rho),
            p.mu_xi,
            np.log(p.meas_std),
        ]
    )


def _unpack(theta: np.ndarray, base: SSParams) -> SSParams:
    return replace(
        base,
        kappa=float(np.exp(np.clip(theta[0], -5, 5))),
        sigma_chi=float(np.exp(np.clip(theta[1], -8, 2))),
        sigma_xi=float(np.exp(np.clip(theta[2], -8, 2))),
        rho=float(np.tanh(np.clip(theta[3], -3, 3))),
        mu_xi=float(theta[4]),
        meas_std=float(np.exp(np.clip(theta[5], -10, 0))),
    )


@dataclass(frozen=True)
class FitResult:
    params: SSParams
    loglik: float
    n_obs: int
    n_params: int
    converged: bool
    message: str

    @property
    def aic(self) -> float:
        return 2 * self.n_params - 2 * self.loglik


def fit_spot_only(
    log_spot: np.ndarray,
    dt: float,
    base: SSParams | None = None,
    jumps: Sequence[bool] | None = None,
    min_observations: int = 180,
) -> FitResult | None:
    """Maximum-likelihood fit of the real-world dynamics to a spot series.

    ``delta``, jump parameters and risk-neutral parameters are held at the
    values in ``base`` (they are not identified from spot data alone). Returns
    None if there are fewer than ``min_observations`` finite observations:
    the caller must then report "insufficient history" instead of a fit.
    """
    y_all = np.asarray(log_spot, float)
    if int(np.isfinite(y_all).sum()) < min_observations:
        return None
    base = base or SSParams()
    t_years = np.arange(y_all.size) * dt
    y, d, Z = spot_measurement(y_all, t_years, base.delta)

    def nll(theta: np.ndarray) -> float:
        try:
            p = _unpack(theta, base)
        except ValueError:
            return 1e12
        ll = spot_loglik(y_all, p, dt, t_years, jumps)
        return -ll if np.isfinite(ll) else 1e12

    starts = [_pack(base)]
    for k0 in (0.5, 5.0):
        starts.append(_pack(replace(base, kappa=k0)))
    best: optimize.OptimizeResult | None = None
    for s in starts:
        res = optimize.minimize(
            nll, s, method="Nelder-Mead", options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-6}
        )
        if best is None or res.fun < best.fun:
            best = res
    if best is None:
        raise RuntimeError("optimizer did not run")
    p_hat = _unpack(best.x, base)
    out = kalman_filter(y, d, Z, p_hat, dt, jumps)
    return FitResult(
        p_hat, out.loglik, out.n_obs, len(_SPOT_FREE), bool(best.success), str(best.message)
    )


# ----------------------------------------------------------------------------
# Forecasting
# ----------------------------------------------------------------------------
def forecast_log_spot(
    p: SSParams,
    x: np.ndarray,
    P: np.ndarray,
    t_years: float,
    horizons_days: Sequence[int],
    dt: float,
    jump_days: Sequence[int] = (),
) -> tuple[np.ndarray, np.ndarray]:
    """Real-world mean and variance of ln S at t + h days for each h.

    ``jump_days`` lists horizons (in days from t) at which a scheduled jump
    occurs. Measurement noise is not added: this forecasts the index itself.
    """
    hs = sorted(set(int(h) for h in horizons_days))
    if not hs:
        return np.array([]), np.array([])
    jd = set(int(j) for j in jump_days)
    c0, G0, W0 = transition(p, dt, False)
    c1, G1, W1 = transition(p, dt, True)
    m, V = np.asarray(x, float).copy(), np.asarray(P, float).copy()
    means: dict[int, float] = {}
    vars_: dict[int, float] = {}
    one = np.array([1.0, 1.0])
    for step in range(1, hs[-1] + 1):
        c, G, W = (c1, G1, W1) if step in jd else (c0, G0, W0)
        m = c + G @ m
        V = G @ V @ G.T + W
        if step in hs:
            means[step] = float(-p.delta * (t_years + step * dt) + one @ m)
            vars_[step] = float(one @ V @ one)
    req = [int(h) for h in horizons_days]
    return np.array([means[h] for h in req]), np.array([vars_[h] for h in req])


def expected_average_level(means: np.ndarray, variances: np.ndarray) -> float:
    """E[(1/N) sum S_d] when ln S_d ~ N(m_d, v_d): (1/N) sum exp(m_d + v_d / 2)."""
    return float(np.mean(np.exp(np.asarray(means) + 0.5 * np.asarray(variances))))


# ----------------------------------------------------------------------------
# Futures-panel estimation (monthly average-price contracts)
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class PanelDesign:
    """Averaging-day grids for each (time, slot) cell of the measurement panel.

    ``seg_t``/``seg_slot`` identify the cell of each segment; ``tau`` holds the
    averaging-day horizons in years for all segments concatenated, with
    ``seg_start`` the offset of each segment; ``n_jumps`` counts scheduled
    launches in (t, t + tau] for each grid point.
    """

    T: int
    n_slots: int
    t_years: np.ndarray
    seg_t: np.ndarray
    seg_slot: np.ndarray
    seg_start: np.ndarray
    tau: np.ndarray
    n_jumps: np.ndarray


def build_panel_design(
    t_years: np.ndarray,
    cells: Sequence[tuple[int, int, np.ndarray, np.ndarray]],
    n_slots: int,
) -> PanelDesign:
    """``cells``: (t_index, slot, tau_grid_years, n_jumps_grid) for observed contracts.

    Only contracts whose averaging month has *not* started are included; the
    current month mixes known index values with expectations and is handled by
    the nowcast model instead (see docs/term_structure_model.md).
    """
    seg_t, seg_slot, seg_start, taus, jumps = [], [], [], [], []
    off = 0
    for t, j, grid, nj in cells:
        if grid.size == 0 or np.any(grid <= 0):
            raise ValueError("averaging grid must be non-empty and strictly in the future")
        seg_t.append(t)
        seg_slot.append(j)
        seg_start.append(off)
        taus.append(np.asarray(grid, float))
        jumps.append(np.asarray(nj, float))
        off += grid.size
    return PanelDesign(
        T=len(t_years),
        n_slots=n_slots,
        t_years=np.asarray(t_years, float),
        seg_t=np.asarray(seg_t, int),
        seg_slot=np.asarray(seg_slot, int),
        seg_start=np.asarray(seg_start, int),
        tau=np.concatenate(taus) if taus else np.zeros(0),
        n_jumps=np.concatenate(jumps) if jumps else np.zeros(0),
    )


def panel_measurement(p: SSParams, des: PanelDesign) -> tuple[np.ndarray, np.ndarray]:
    """Intercepts d (T, n) and loadings Z (T, n, 2) for log average-price futures.

    ln F_avg(t, M) is approximated by the mean over averaging days of
    ln F(t, T_d). The neglected Jensen term is half the cross-day variance of
    ln F within one month, below 1e-4 for plausible parameters (derivation in
    docs/term_structure_model.md).
    """
    d = np.full((des.T, des.n_slots), np.nan)
    Z = np.zeros((des.T, des.n_slots, 2))
    Z[:, :, 1] = 1.0
    if des.tau.size == 0:
        return d, Z
    seg_t_rep = np.repeat(des.seg_t, np.diff(np.append(des.seg_start, des.tau.size)))
    tT = des.t_years[seg_t_rep] + des.tau
    inter = -p.delta * tT + a_tau(p, des.tau) + des.n_jumps * (p.jump_mean + 0.5 * p.jump_std**2)
    load = np.exp(-p.kappa * des.tau)
    lens = np.diff(np.append(des.seg_start, des.tau.size))
    inter_mean = np.add.reduceat(inter, des.seg_start) / lens
    load_mean = np.add.reduceat(load, des.seg_start) / lens
    d[des.seg_t, des.seg_slot] = inter_mean
    Z[des.seg_t, des.seg_slot, 0] = load_mean
    return d, Z


_PANEL_FREE = (
    "kappa",
    "sigma_chi",
    "sigma_xi",
    "rho",
    "mu_xi",
    "meas_std",
    "mu_xi_star",
    "lambda_chi",
)


def _pack_panel(p: SSParams) -> np.ndarray:
    return np.concatenate([_pack(p), [p.mu_xi_star, p.lambda_chi]])


def _unpack_panel(theta: np.ndarray, base: SSParams) -> SSParams:
    return replace(_unpack(theta[:6], base), mu_xi_star=float(theta[6]), lambda_chi=float(theta[7]))


def fit_panel(
    y: np.ndarray,
    des: PanelDesign,
    dt: float,
    base: SSParams | None = None,
    jumps: Sequence[bool] | None = None,
    min_observations: int = 180,
    maxiter: int = 3000,
) -> FitResult | None:
    """MLE of real-world and risk-neutral parameters from a futures panel.

    ``y`` is (T, n_slots) log futures prices with NaN where unobserved.
    Returns None when fewer than ``min_observations`` time steps carry data.
    """
    if int(np.isfinite(y).any(axis=1).sum()) < min_observations:
        return None
    base = base or SSParams()

    def nll(theta: np.ndarray) -> float:
        try:
            p = _unpack_panel(theta, base)
        except ValueError:
            return 1e12
        d, Z = panel_measurement(p, des)
        out = kalman_filter(y, np.nan_to_num(d), Z, p, dt, jumps)
        return -out.loglik if np.isfinite(out.loglik) else 1e12

    res = optimize.minimize(
        nll,
        _pack_panel(base),
        method="Nelder-Mead",
        options={"maxiter": maxiter, "xatol": 1e-5, "fatol": 1e-5, "adaptive": True},
    )
    p_hat = _unpack_panel(res.x, base)
    d, Z = panel_measurement(p_hat, des)
    out = kalman_filter(y, np.nan_to_num(d), Z, p_hat, dt, jumps)
    return FitResult(
        p_hat, out.loglik, out.n_obs, len(_PANEL_FREE), bool(res.success), str(res.message)
    )
