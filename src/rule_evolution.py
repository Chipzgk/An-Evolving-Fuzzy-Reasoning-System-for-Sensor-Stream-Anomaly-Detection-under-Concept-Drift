"""Bonus (Phase 12): rule-level evolution -- add / remove Mamdani rules.

Unlike the MF adaptation of Phase 7 (fully unsupervised), rule evolution
needs *delayed label feedback*: in predictive maintenance the true state of
a machine is known some time after the prediction (inspection, repair log).
Protocol (prequential): the label of x_t becomes available at t + delay and
is only used to change the rule base from that moment on; x_t itself was
already scored with the old rule base.

ADD    : a failure that was missed (score < tau) proposes candidate rules
         IF <subset of 2-3 of its dominant non-MEDIUM terms> THEN anomaly is HIGH.
         A candidate is inserted only if, on the *past* labelled samples kept
         in a history window, it fired strongly (alpha >= alpha_attr) at least
         `min_add_fires` times with >= `min_add_tp` failures and a precision
         >= `min_add_precision` (best candidate by precision, then support).
         Without this quality gate, single-sample rules over-fit (tested:
         13-16 rules added, FPR 0.09-0.20).
REMOVE : a rule with consequent MEDIUM/HIGH is pruned when, among the
         labelled samples where it fired strongly (alpha >= alpha_attr) and the
         system raised an alarm, it reached `min_support` alarms with a
         precision below `min_precision` (it mostly produces false alarms).
LOW-consequent rules are never removed; at most `max_rules` rules.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations

from .evolving import PrequentialRunner
from .fuzzy import VARIABLES, infer


class RuleEvolvingRunner(PrequentialRunner):
    def __init__(self, label_delay: int = 0, add_rules: bool = True,
                 remove_rules: bool = True, min_support: int = 20,
                 min_precision: float = 0.05, alpha_attr: float = 0.5,
                 max_rules: int = 30, min_add_fires: int = 3,
                 min_add_tp: int = 2, min_add_precision: float = 0.3,
                 history: int = 1000, quality_gate: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.label_delay = label_delay
        self.add_rules = add_rules
        self.remove_rules = remove_rules
        self.min_support = min_support
        self.min_precision = min_precision
        self.alpha_attr = alpha_attr
        self.max_rules = max_rules
        self.min_add_fires = min_add_fires
        self.min_add_tp = min_add_tp
        self.min_add_precision = min_add_precision
        self.quality_gate = quality_gate
        self.history: deque = deque(maxlen=history)
        self.pending: deque = deque()
        self.stats: dict[str, dict] = {}
        self.rule_log: list[dict] = []
        self._next_id = 1

    # --- helpers -------------------------------------------------------
    def _rule_ids(self):
        return {r[0] for r in self.fis.rules}

    def _candidate(self, memberships):
        """Candidate antecedent sets from the dominant non-MEDIUM terms."""
        dominant = {v: max(memberships[v].items(), key=lambda kv: kv[1])[0] for v in VARIABLES}
        ants = [(v, term) for v, term in dominant.items() if term != "medium"]
        if len(ants) < 2:
            return []
        if not self.quality_gate:
            return [ants]
        return [list(c) for n in (2, 3) for c in combinations(ants, n)]

    def _quality(self, ants):
        fires = tp = 0
        for memberships, label in self.history:
            if min(memberships[v][t] for v, t in ants) >= self.alpha_attr:
                fires += 1
                tp += label
        return fires, tp

    def _apply(self, t_now, item):
        t, memberships, strong, pred, label = item
        # statistics for pruning
        if pred == 1:
            for rid in strong:
                st = self.stats.setdefault(rid, {"alarms": 0, "tp": 0})
                st["alarms"] += 1
                st["tp"] += label
        # ADD: missed failure
        self.history.append((memberships, label))
        if self.add_rules and label == 1 and pred == 0 and self.fis.n_rules < self.max_rules:
            existing = {frozenset(r[1]) for r in self.fis.rules}
            best = None
            for ants in self._candidate(memberships):
                if frozenset(ants) in existing:
                    continue
                if not self.quality_gate:
                    best = (ants, None, None)
                    break
                fires, tp = self._quality(ants)
                if fires >= self.min_add_fires and tp >= self.min_add_tp and tp / fires >= self.min_add_precision:
                    key = (tp / fires, fires)
                    if best is None or key > best[1]:
                        best = (ants, key, (fires, tp))
            if best is not None:
                ants = best[0]
                rid = f"N{self._next_id}"
                self._next_id += 1
                self.fis.rules.append((rid, ants, "high"))
                self.rule_log.append({"t": t_now, "sample_t": t, "action": "add", "rule": rid,
                                      "antecedents": ants, "consequent": "high",
                                      "hist_fires": best[2][0] if best[2] else None,
                                      "hist_tp": best[2][1] if best[2] else None})
        # REMOVE: rules that mostly cause false alarms
        if self.remove_rules:
            for rid, ants, cons in list(self.fis.rules):
                st = self.stats.get(rid)
                if cons == "low" or st is None or st["alarms"] < self.min_support:
                    continue
                if st["tp"] / st["alarms"] < self.min_precision:
                    self.fis.rules.remove((rid, ants, cons))
                    self.rule_log.append({"t": t_now, "sample_t": t, "action": "remove", "rule": rid,
                                          "antecedents": ants, "consequent": cons,
                                          "alarms": st["alarms"], "tp": st["tp"]})

    # --- hook -----------------------------------------------------------
    def _feedback(self, t, values, score, pred, label):
        memberships = self.fis.memberships(values)
        d = infer(memberships, self.fis.rules, self.fis.weights, return_details=True)
        strong = [rid for rid, a in d["activations"].items() if a >= self.alpha_attr]
        self.pending.append((t, memberships, strong, pred, label))
        while self.pending and self.pending[0][0] + self.label_delay <= t:
            self._apply(t, self.pending.popleft())
