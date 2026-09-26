"""Binary detection metrics (minority class = failure)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _div(a, b):
    return a / b if b > 0 else 0.0


def confusion(y_true, y_pred) -> dict[str, int]:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    return {
        "TP": int(((y_true == 1) & (y_pred == 1)).sum()),
        "TN": int(((y_true == 0) & (y_pred == 0)).sum()),
        "FP": int(((y_true == 0) & (y_pred == 1)).sum()),
        "FN": int(((y_true == 1) & (y_pred == 0)).sum()),
    }


def metrics_from_confusion(c: dict) -> dict[str, float]:
    tp, tn, fp, fn = c["TP"], c["TN"], c["FP"], c["FN"]
    precision = _div(tp, tp + fp)
    recall = _div(tp, tp + fn)
    specificity = _div(tn, tn + fp)
    return {
        **c,
        "Precision": precision,
        "Recall": recall,
        "F1": _div(2 * precision * recall, precision + recall),
        "FPR": _div(fp, fp + tn),
        "FNR": _div(fn, fn + tp),
        "Specificity": specificity,
        "Balanced Accuracy": (recall + specificity) / 2,
    }


def evaluate(y_true, scores, tau: float = 0.67) -> dict[str, float]:
    y_pred = (np.asarray(scores) >= tau).astype(int)
    return metrics_from_confusion(confusion(y_true, y_pred))


def metrics_table(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def detection_delay(detections, drift_start: int):
    after = [d for d in detections if d >= drift_start]
    return (after[0] - drift_start) if after else None
