"""Bonus (Phase 13): multi-stream monitoring with cross-stream knowledge transfer.

Several machines are monitored in lock-step (one global clock). Each stream
has its own FIS copy, its own ADWIN and its own buffer. A shared knowledge
base stores the MF shift vector learned by the first stream that completed
an adaptation. Modes:

- "independent"   : Phase 7 per stream (detect -> buffer W -> adapt).
- "transfer"      : on its own drift alarm, a stream immediately applies the
                    shared shift vector (if one exists), then still collects
                    its own W-sample buffer and applies the residual shift
                    (refinement). Falls back to "independent" if the
                    knowledge base is empty.
- "transfer_only" : like "transfer" but without own refinement (ablation).

A stream never uses another stream's *labels*; only unlabeled shift vectors
are shared. Adapted variables are fixed to RPM/Torque as in Phase 7.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .drift import AdwinDetector
from .evolving import ORACLE_ADAPTIVE_VARS, adapt_mfs, estimate_shifts
from .fuzzy import STATIC_GRID_MFS, TAU, FuzzySystem, sample_values


class _StreamState:
    def __init__(self, name, stream):
        self.name = name
        self.stream = stream.reset_index(drop=True)
        self.values = [sample_values(r) for _, r in self.stream.iterrows()]
        self.rows = [r for _, r in self.stream.iterrows()]
        self.labels = self.stream["Machine failure"].to_numpy()
        self.fis = FuzzySystem()
        self.grid = STATIC_GRID_MFS
        self.det = AdwinDetector()
        self.buffering = False
        self.buffer = []
        self.n_adapt = 0
        self.events = []
        self.log = []


class MultiStreamMonitor:
    def __init__(self, streams: dict[str, pd.DataFrame], mode: str = "independent",
                 window: int = 200, tau: float = TAU, variables=ORACLE_ADAPTIVE_VARS):
        assert mode in ("independent", "transfer", "transfer_only")
        self.mode, self.window, self.tau = mode, window, tau
        self.variables = list(variables)
        self.states = {k: _StreamState(k, s) for k, s in streams.items()}
        self.knowledge: dict | None = None  # shared shift vector
        self.knowledge_source = None

    def _apply(self, st: _StreamState, shifts: dict, t: int, kind: str):
        st.grid = adapt_mfs(st.grid, shifts)
        st.fis = FuzzySystem(st.grid)
        st.n_adapt += 1
        st.events.append({"t": t, "event": kind, "shifts": shifts})
        st.det.reset()

    def run(self) -> dict[str, pd.DataFrame]:
        n = max(len(s.stream) for s in self.states.values())
        for t in range(n):
            for st in self.states.values():
                if t >= len(st.stream):
                    continue
                v = st.values[t]
                score = st.fis.score_values(v)
                pred = int(score >= self.tau)
                drift = st.det.update(score) if st.n_adapt == 0 or st.buffering else False
                if drift:
                    st.events.append({"t": t, "event": "drift_detected"})
                if st.buffering:
                    st.buffer.append(st.rows[t])
                    if len(st.buffer) == self.window:
                        buf = pd.DataFrame(st.buffer)
                        shifts = estimate_shifts(buf, st.grid, self.variables)
                        kind = "refined" if st.n_adapt > 0 else "adapted"
                        self._apply(st, shifts, t, kind)
                        st.buffering, st.buffer = False, []
                        if self.knowledge is None:
                            total = estimate_shifts(buf, STATIC_GRID_MFS, self.variables)
                            self.knowledge, self.knowledge_source = total, (st.name, t)
                elif drift and st.n_adapt == 0:
                    if self.mode != "independent" and self.knowledge is not None:
                        self._apply(st, dict(self.knowledge), t, "transferred")
                        if self.mode == "transfer":
                            st.buffering, st.buffer = True, []
                    else:
                        st.buffering, st.buffer = True, []
                st.log.append({"t": t, "score": score, "pred": pred, "label": int(st.labels[t]),
                               "n_adapt": st.n_adapt})
        return {k: pd.DataFrame(s.log) for k, s in self.states.items()}
