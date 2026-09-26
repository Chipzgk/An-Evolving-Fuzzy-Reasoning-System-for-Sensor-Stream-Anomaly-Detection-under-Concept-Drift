"""Mamdani fuzzy inference system (frozen Phase 2 knowledge base).

Two membership evaluation paths, both identical to the notebooks:
- analytic : exact triangular / trapezoidal formulas (Static FIS, Phases 2-8)
- grid     : np.interp over 1000-point universes (Evolving FIS, Phases 7-8),
             needed because adapted MFs are translated on the grid.
"""
from __future__ import annotations

import copy

import numpy as np

from .data import SENSOR_COLUMNS

TAU = 0.67  # frozen threshold, selected on Validation by max F1 (Phase 3)
VARIABLES = ["air_temp", "process_temp", "rpm", "torque", "tool_wear"]
TERMS = ["low", "medium", "high"]

UNIVERSES = {
    "air_temp": np.linspace(295.3, 304.5, 1000),
    "process_temp": np.linspace(305.7, 313.8, 1000),
    "rpm": np.linspace(1168, 2886, 1000),
    "torque": np.linspace(3.8, 76.2, 1000),
    "tool_wear": np.linspace(0, 253, 1000),
}
OUTPUT_UNIVERSE = np.linspace(0, 1, 1000)

MF_PARAMS = {
    "air_temp": {
        "low": ("trap", [295.3, 295.3, 298.0, 300.4]),
        "medium": ("tri", [298.0, 300.4, 302.5]),
        "high": ("trap", [300.4, 302.5, 304.5, 304.5]),
    },
    "process_temp": {
        "low": ("trap", [305.7, 305.7, 308.0, 309.7]),
        "medium": ("tri", [308.0, 309.7, 311.5]),
        "high": ("trap", [309.7, 311.5, 313.8, 313.8]),
    },
    "rpm": {
        "low": ("trap", [1168, 1168, 1350, 1500]),
        "medium": ("tri", [1350, 1504, 1800]),
        "high": ("trap", [1600, 1880, 2886, 2886]),
    },
    "torque": {
        "low": ("trap", [3.8, 3.8, 25.0, 40.0]),
        "medium": ("tri", [25.0, 40.0, 55.0]),
        "high": ("trap", [40.0, 55.0, 76.2, 76.2]),
    },
    "tool_wear": {
        "low": ("trap", [0, 0, 54, 109]),
        "medium": ("tri", [54, 109, 164]),
        "high": ("trap", [109, 164, 253, 253]),
    },
}

_u = OUTPUT_UNIVERSE
OUTPUT_MFS = {
    "low": np.maximum(np.minimum((0.50 - _u) / 0.25, 1.0), 0.0),
    "medium": np.maximum(np.minimum((_u - 0.25) / 0.25, (0.75 - _u) / 0.25), 0.0),
    "high": np.maximum(np.minimum((_u - 0.50) / 0.25, 1.0), 0.0),
}

# (rule_id, [(variable, term), ...], consequent)  -- exact Phase 2 rule base
RULES = [
    ("R1", [("rpm", "low"), ("torque", "high"), ("air_temp", "high")], "high"),
    ("R2", [("torque", "high"), ("air_temp", "high"), ("tool_wear", "high")], "high"),
    ("R3", [("rpm", "low"), ("torque", "high"), ("process_temp", "high")], "high"),
    ("R4", [("rpm", "low"), ("torque", "high"), ("tool_wear", "high")], "high"),
    ("R5", [("rpm", "low"), ("torque", "high")], "medium"),
    ("R6", [("rpm", "low"), ("air_temp", "high")], "medium"),
    ("R7", [("torque", "high"), ("air_temp", "high")], "medium"),
    ("R8", [("torque", "high"), ("tool_wear", "high")], "medium"),
    ("R9", [("torque", "high"), ("process_temp", "high")], "medium"),
    ("R10", [("rpm", "medium"), ("torque", "medium")], "low"),
    ("R11", [("rpm", "medium"), ("torque", "low")], "low"),
    ("R12", [("rpm", "high"), ("torque", "low")], "low"),
]

TERM_LABELS_VI = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH"}


def eval_mf(x: float, mf_type: str, params) -> float:
    """Exact analytic MF evaluator (identical to notebooks 02/08)."""
    if mf_type == "tri":
        a, b, c = params
        if x <= a or x >= c:
            return 0.0
        if x == b:
            return 1.0
        if x < b:
            return (x - a) / (b - a)
        return (c - x) / (c - b)
    if mf_type == "trap":
        a, b, c, d = params
        if x < a or x > d:
            return 0.0
        if b <= x <= c:
            return 1.0
        if a <= x < b:
            return (x - a) / (b - a) if b != a else 1.0
        return (d - x) / (d - c) if d != c else 1.0
    raise ValueError(mf_type)


def build_grid_mfs(mf_params=MF_PARAMS) -> dict:
    """Sample every analytic MF on its 1000-point universe."""
    return {
        var: {
            term: np.array([eval_mf(x, t, p) for x in UNIVERSES[var]])
            for term, (t, p) in terms.items()
        }
        for var, terms in mf_params.items()
    }


STATIC_GRID_MFS = build_grid_mfs()


def sample_values(row) -> dict[str, float]:
    return {var: float(row[col]) for var, col in SENSOR_COLUMNS.items()}


def analytic_memberships(values: dict[str, float]) -> dict:
    return {
        var: {term: eval_mf(values[var], t, p) for term, (t, p) in MF_PARAMS[var].items()}
        for var in VARIABLES
    }


def grid_memberships(values: dict[str, float], grid_mfs: dict) -> dict:
    return {
        var: {
            term: float(np.interp(values[var], UNIVERSES[var], grid_mfs[var][term]))
            for term in TERMS
        }
        for var in VARIABLES
    }


def infer(memberships: dict, rules=RULES, weights=None, return_details=False):
    """Mamdani: AND=min, implication=min, aggregation=max, centroid."""
    activations = {}
    implied = []
    for i, (rid, antecedents, consequent) in enumerate(rules):
        alpha = min(memberships[v][t] for v, t in antecedents)
        if weights is not None:
            alpha = alpha * weights[i]
        activations[rid] = alpha
        implied.append(np.fmin(alpha, OUTPUT_MFS[consequent]))
    if implied:
        aggregated = np.max(np.vstack(implied), axis=0)
    else:
        aggregated = np.zeros_like(OUTPUT_UNIVERSE)
    area = np.trapezoid(aggregated, OUTPUT_UNIVERSE)
    score = 0.0 if area == 0 else float(
        np.trapezoid(OUTPUT_UNIVERSE * aggregated, OUTPUT_UNIVERSE) / area)
    if return_details:
        return {"score": score, "activations": activations,
                "aggregated": aggregated, "memberships": memberships}
    return score


class FuzzySystem:
    """Mamdani FIS.

    grid_mfs=None -> analytic memberships (Static FIS, frozen Phase 2).
    grid_mfs=dict -> grid memberships (used once MFs have been adapted).
    rules / weights may be changed by rule-level evolution (bonus).
    """

    def __init__(self, grid_mfs: dict | None = None, rules=None, weights=None):
        self.grid_mfs = grid_mfs
        self.rules = list(rules) if rules is not None else list(RULES)
        self.weights = list(weights) if weights is not None else None

    @property
    def n_rules(self) -> int:
        return len(self.rules)

    def copy(self) -> "FuzzySystem":
        return FuzzySystem(copy.deepcopy(self.grid_mfs), list(self.rules),
                           None if self.weights is None else list(self.weights))

    def memberships(self, values: dict[str, float]) -> dict:
        if self.grid_mfs is None:
            return analytic_memberships(values)
        return grid_memberships(values, self.grid_mfs)

    def score_values(self, values: dict[str, float]) -> float:
        return infer(self.memberships(values), self.rules, self.weights)

    def score(self, row) -> float:
        return self.score_values(sample_values(row))

    def score_stream(self, stream) -> np.ndarray:
        return np.array([self.score(r) for _, r in stream.iterrows()])

    def explain(self, row, top_k: int = 5) -> dict:
        """Linguistic explanation: dominant term per input, fired rules."""
        values = sample_values(row)
        m = self.memberships(values)
        d = infer(m, self.rules, self.weights, return_details=True)
        dominant = {v: max(m[v].items(), key=lambda kv: kv[1]) for v in VARIABLES}
        fired = sorted(
            [(rid, a, cons, ants) for (rid, ants, cons), a in
             zip(self.rules, d["activations"].values()) if a > 0],
            key=lambda x: -x[1])[:top_k]
        return {"score": d["score"], "values": values, "memberships": m,
                "dominant_terms": dominant, "fired_rules": fired,
                "aggregated": d["aggregated"]}


def format_rule(antecedents, consequent) -> str:
    cond = " AND ".join(f"{v} is {TERM_LABELS_VI[t]}" for v, t in antecedents)
    return f"IF {cond} THEN anomaly is {TERM_LABELS_VI[consequent]}"
