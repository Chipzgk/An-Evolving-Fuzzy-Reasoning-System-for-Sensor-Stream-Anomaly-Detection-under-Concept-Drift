"""Dataset loading, sequential split and controlled stream scenarios.

All constants are identical to Phase 1.5 / Phase 4 / Phase 8.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SENSOR_COLUMNS = {
    "air_temp": "Air temperature [K]",
    "process_temp": "Process temperature [K]",
    "rpm": "Rotational speed [rpm]",
    "torque": "Torque [Nm]",
    "tool_wear": "Tool wear [min]",
}
LABEL_COLUMN = "Machine failure"
# Failure-mode columns: labels, never model inputs (label leakage).
LEAKAGE_COLUMNS = ["TWF", "HDF", "PWF", "OSF", "RNF"]

# Sequential split (Phase 1.5): 6000 / 2000 / 2000
TRAIN_END = 6000
VAL_END = 8000

# Controlled drift (Phase 4)
SUDDEN_DRIFT_POINT = 1000
GRADUAL_DRIFT_START = 800
GRADUAL_DRIFT_END = 1200
RPM_SHIFT = -150
TORQUE_SHIFT = 8
RPM_RANGE = (1168, 2886)
TORQUE_RANGE = (3.8, 76.2)

# Physical / universe bounds of every sensor (Phase 2 universes)
SENSOR_BOUNDS = {
    "air_temp": (295.3, 304.5),
    "process_temp": (305.7, 313.8),
    "rpm": RPM_RANGE,
    "torque": TORQUE_RANGE,
    "tool_wear": (0.0, 253.0),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    path = Path(path) if path else repo_root() / "data" / "ai4i2020.csv"
    df = pd.read_csv(path)
    assert df.shape == (10000, 14), df.shape
    return df


def sequential_split(df: pd.DataFrame):
    """Return (train, val, test) in chronological (UDI) order."""
    train = df.iloc[:TRAIN_END].copy()
    val = df.iloc[TRAIN_END:VAL_END].copy()
    test = df.iloc[VAL_END:].copy().reset_index(drop=True)
    return train, val, test


def make_base_stream(df: pd.DataFrame) -> pd.DataFrame:
    stream = df.iloc[VAL_END:].copy().reset_index(drop=True)
    assert len(stream) == 2000 and stream["UDI"].iloc[0] == 8001
    return stream


def inject_sudden(stream: pd.DataFrame, point: int = SUDDEN_DRIFT_POINT,
                  rpm_shift: float = RPM_SHIFT,
                  torque_shift: float = TORQUE_SHIFT) -> pd.DataFrame:
    out = stream.copy()
    rpm, tq = SENSOR_COLUMNS["rpm"], SENSOR_COLUMNS["torque"]
    out.loc[point:, rpm] = (out.loc[point:, rpm] + rpm_shift).clip(*RPM_RANGE)
    out.loc[point:, tq] = (out.loc[point:, tq] + torque_shift).clip(*TORQUE_RANGE)
    return out


def drift_alpha(n: int, start: int = GRADUAL_DRIFT_START,
                end: int = GRADUAL_DRIFT_END) -> np.ndarray:
    idx = np.arange(n)
    alpha = np.zeros(n)
    mask = (idx >= start) & (idx < end)
    alpha[mask] = (idx[mask] - start) / (end - start)
    alpha[idx >= end] = 1.0
    return alpha


def inject_gradual(stream: pd.DataFrame, start: int = GRADUAL_DRIFT_START,
                   end: int = GRADUAL_DRIFT_END, rpm_shift: float = RPM_SHIFT,
                   torque_shift: float = TORQUE_SHIFT) -> pd.DataFrame:
    out = stream.copy()
    alpha = drift_alpha(len(out), start, end)
    rpm, tq = SENSOR_COLUMNS["rpm"], SENSOR_COLUMNS["torque"]
    out[rpm] = (stream[rpm] + alpha * rpm_shift).clip(*RPM_RANGE)
    out[tq] = (stream[tq] + alpha * torque_shift).clip(*TORQUE_RANGE)
    return out


def make_scenarios(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    base = make_base_stream(df)
    return {
        "Control": base.copy(),
        "Sudden Drift": inject_sudden(base),
        "Gradual Drift": inject_gradual(base),
    }


def train_sensor_std(df: pd.DataFrame) -> dict[str, float]:
    train, _, _ = sequential_split(df)
    return {k: float(train[c].std()) for k, c in SENSOR_COLUMNS.items()}


def add_gaussian_noise(stream: pd.DataFrame, noise_frac: float,
                       ref_std: dict[str, float], seed: int = 0,
                       variables=None) -> pd.DataFrame:
    """Additive N(0, (noise_frac * train_std)^2) sensor noise, clipped to
    the physical/universe bounds. Labels are untouched."""
    rng = np.random.default_rng(seed)
    out = stream.copy()
    for var in variables or SENSOR_COLUMNS:
        col = SENSOR_COLUMNS[var]
        noise = rng.normal(0.0, noise_frac * ref_std[var], len(out))
        out[col] = (out[col].astype(float) + noise).clip(*SENSOR_BOUNDS[var])
    return out


def inject_missing(stream: pd.DataFrame, rate: float, seed: int = 0,
                   variables=None) -> pd.DataFrame:
    """MCAR missingness: each sensor reading is independently set to NaN
    with probability `rate`."""
    rng = np.random.default_rng(seed)
    out = stream.copy()
    for var in variables or SENSOR_COLUMNS:
        col = SENSOR_COLUMNS[var]
        mask = rng.random(len(out)) < rate
        out[col] = out[col].astype(float)
        out.loc[mask, col] = np.nan
    return out


def impute_locf(stream: pd.DataFrame, fallback: dict[str, float]) -> pd.DataFrame:
    """Causal imputation: last observation carried forward (uses only past
    values); the very first missing values fall back to train medians."""
    out = stream.copy()
    for var, col in SENSOR_COLUMNS.items():
        out[col] = out[col].ffill().fillna(fallback[var])
    return out


def train_sensor_median(df: pd.DataFrame) -> dict[str, float]:
    train, _, _ = sequential_split(df)
    return {k: float(train[c].median()) for k, c in SENSOR_COLUMNS.items()}


def scenarios_from_base(base: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Control / Sudden / Gradual built from any 2000-sample base stream."""
    base = base.copy().reset_index(drop=True)
    return {"Control": base.copy(), "Sudden Drift": inject_sudden(base),
            "Gradual Drift": inject_gradual(base)}


def make_validation_scenarios(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Same drift protocol on the Validation partition (UDI 6001-8000).
    Used only for hyper-parameter selection of bonus mechanisms."""
    return scenarios_from_base(df.iloc[TRAIN_END:VAL_END])
