"""Unsupervised drift detection on the anomaly-score stream (Phase 5).

ADWIN from River, default delta=0.002. The detector never sees labels.
"""
from __future__ import annotations

try:
    from river.drift import ADWIN
    import river
    RIVER_VERSION = river.__version__
except ImportError:  # pragma: no cover
    ADWIN = None
    RIVER_VERSION = None


class AdwinDetector:
    def __init__(self, delta: float = 0.002):
        if ADWIN is None:
            raise ImportError("river is required: pip install river")
        self.delta = delta
        self.reset()

    def reset(self):
        self._adwin = ADWIN(delta=self.delta)

    def update(self, value: float) -> bool:
        self._adwin.update(float(value))
        return bool(self._adwin.drift_detected)


class FixedDetections:
    """Replays a frozen list of detection indices (used only to replicate
    Phase 7/8 exactly when the installed River version behaves differently)."""

    def __init__(self, indices):
        self.indices = set(int(i) for i in indices)
        self.t = -1

    def reset(self):
        pass

    def update(self, value: float) -> bool:
        self.t += 1
        return self.t in self.indices


def detect_all(scores, delta: float = 0.002) -> list[int]:
    det = AdwinDetector(delta)
    return [t for t, s in enumerate(scores) if det.update(s)]
