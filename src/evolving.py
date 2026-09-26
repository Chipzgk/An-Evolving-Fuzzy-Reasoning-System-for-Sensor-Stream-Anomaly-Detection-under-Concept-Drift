"""Evolving Fuzzy System: buffer-based MF translation (Phase 7) and a
prequential test-then-adapt runner.

Adaptation rule (unchanged from Phase 7):
    after a drift alarm at t_d, collect W unlabeled samples (t_d+1 .. t_d+W),
    for each adaptive variable v:  delta_v = mean(buffer_v) - centroid(MEDIUM_v)
    translate LOW/MEDIUM/HIGH of v by delta_v on the grid; rules/threshold frozen.
New samples are always scored with the knowledge available *before* they
arrive (test-then-adapt); labels are never used for MF adaptation.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from .data import SENSOR_COLUMNS
from .drift import AdwinDetector
from .fuzzy import (TAU, UNIVERSES, VARIABLES, STATIC_GRID_MFS, FuzzySystem,
                    sample_values)

ORACLE_ADAPTIVE_VARS = ("rpm", "torque")  # Phase 6/7 choice (known drift channels)


def mf_centroid(universe, mf):
    area = np.trapezoid(mf, universe)
    return None if area == 0 else float(np.trapezoid(universe * mf, universe) / area)


def shift_mf(mf, shift, universe):
    """mu_new(u) = mu_old(u - shift); outside the universe -> 0 (Phase 7)."""
    return np.interp(universe - shift, universe, mf, left=0.0, right=0.0)


def estimate_shifts(buffer_df: pd.DataFrame, grid_mfs: dict, variables) -> dict:
    shifts = {}
    for var in variables:
        mean = float(buffer_df[SENSOR_COLUMNS[var]].mean())
        shifts[var] = mean - mf_centroid(UNIVERSES[var], grid_mfs[var]["medium"])
    return shifts


def select_variables_auto(buffer_df: pd.DataFrame, grid_mfs: dict,
                          ref_std: dict, k: float = 0.5) -> tuple[list, dict]:
    """Label-free, oracle-free variable selection: adapt variable v only if
    |mean(buffer_v) - centroid(MEDIUM_v)| > k * train_std_v."""
    all_shifts = estimate_shifts(buffer_df, grid_mfs, VARIABLES)
    z = {v: abs(s) / ref_std[v] for v, s in all_shifts.items()}
    return [v for v in VARIABLES if z[v] > k], z


def adapt_mfs(grid_mfs: dict, shifts: dict) -> dict:
    new = {v: {t: mf.copy() for t, mf in terms.items()} for v, terms in grid_mfs.items()}
    for var, s in shifts.items():
        for term in new[var]:
            new[var][term] = shift_mf(new[var][term], s, UNIVERSES[var])
    return new


class PrequentialRunner:
    """Streams samples one by one: score -> predict -> detector -> (buffer/adapt).

    evolve=False gives the Static baseline (detector still runs, for logging).
    adapt_vars: tuple of variables, or "auto" (select_variables_auto).
    detector: object with update(score)->bool and reset(); default ADWIN.
    """

    def __init__(self, evolve: bool = True, tau: float = TAU, window: int = 200,
                 adapt_vars=ORACLE_ADAPTIVE_VARS, ref_std: dict | None = None,
                 auto_k: float = 0.5, max_adaptations: int = 1,
                 detector=None, fis: FuzzySystem | None = None,
                 measure_latency: bool = False):
        self.evolve = evolve
        self.tau = tau
        self.window = window
        self.adapt_vars = adapt_vars
        self.ref_std = ref_std
        self.auto_k = auto_k
        self.max_adaptations = max_adaptations
        self.detector = detector if detector is not None else AdwinDetector()
        self.fis = fis if fis is not None else FuzzySystem()
        self.measure_latency = measure_latency
        self.grid_mfs = STATIC_GRID_MFS
        self.events: list[dict] = []

    def run(self, stream: pd.DataFrame) -> pd.DataFrame:
        records = []
        buffer_rows: list = []
        buffering = False
        n_adapt = 0
        labels = stream["Machine failure"].to_numpy()
        for t, (_, row) in enumerate(stream.iterrows()):
            values = sample_values(row)
            t0 = time.perf_counter() if self.measure_latency else 0.0
            score = self.fis.score_values(values)          # 1. test
            lat = (time.perf_counter() - t0) if self.measure_latency else np.nan
            pred = int(score >= self.tau)                    # 2. predict
            drift = self.detector.update(score)              # 3. monitor
            if drift:
                self.events.append({"t": t, "event": "drift_detected"})
            adapted_now = False
            if self.evolve and buffering:                    # 4. adapt (after test)
                buffer_rows.append(row)
                if len(buffer_rows) == self.window:
                    buf = pd.DataFrame(buffer_rows)
                    if self.adapt_vars == "auto":
                        variables, z = select_variables_auto(
                            buf, self.grid_mfs, self.ref_std, self.auto_k)
                    else:
                        variables, z = list(self.adapt_vars), None
                    shifts = estimate_shifts(buf, self.grid_mfs, variables)
                    self.grid_mfs = adapt_mfs(self.grid_mfs, shifts)
                    self.fis = FuzzySystem(self.grid_mfs, self.fis.rules, self.fis.weights)
                    n_adapt += 1
                    buffering = False
                    buffer_rows = []
                    adapted_now = True
                    self.events.append({"t": t, "event": "adapted",
                                        "variables": variables, "shifts": shifts,
                                        "z": z})
                    self.detector.reset()
            elif self.evolve and drift and n_adapt < self.max_adaptations:
                buffering = True
                buffer_rows = []
                self.events.append({"t": t, "event": "buffer_start"})
            records.append({"t": t, "UDI": int(row["UDI"]), "score": score,
                            "pred": pred, "label": int(labels[t]),
                            "drift": drift, "adapted_now": adapted_now,
                            "n_adaptations": n_adapt, "latency_s": lat})
        return pd.DataFrame(records)
