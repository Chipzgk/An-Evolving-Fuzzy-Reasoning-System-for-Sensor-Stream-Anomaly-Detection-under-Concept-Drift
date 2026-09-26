"""Reproduce the core experiment matrix (E1-E5b) from scratch in ~10 s.

usage (from repo root):  python scripts/reproduce_core.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.data import load_dataset, make_scenarios  # noqa: E402
from src.evaluation import evaluate  # noqa: E402
from src.evolving import PrequentialRunner  # noqa: E402

EXPECTED = {  # frozen (TP, TN, FP, FN)
    ("Control", "Static"): (13, 1927, 34, 26),
    ("Control", "Evolving"): (13, 1927, 34, 26),
    ("Sudden Drift", "Static"): (18, 1847, 114, 21),
    ("Sudden Drift", "Evolving"): (15, 1905, 56, 24),
    ("Gradual Drift", "Static"): (18, 1848, 113, 21),
    ("Gradual Drift", "Evolving"): (14, 1900, 61, 25),
}


def main():
    scenarios = make_scenarios(load_dataset())
    rows, ok = [], True
    for (scen, model), cm in EXPECTED.items():
        runner = PrequentialRunner(evolve=(model == "Evolving"))
        log = runner.run(scenarios[scen])
        m = evaluate(log.label, log.score)
        got = (m["TP"], m["TN"], m["FP"], m["FN"])
        ok &= got == cm
        det = [e["t"] for e in runner.events if e["event"] == "drift_detected"]
        rows.append({"Scenario": scen, "Model": model, **{k: m[k] for k in ["TP", "TN", "FP", "FN"]},
                     "F1": round(m["F1"], 4), "FPR": round(m["FPR"], 4), "ADWIN": det,
                     "match": "PASS" if got == cm else "FAIL"})
    print(pd.DataFrame(rows).to_string(index=False))
    print("\nALL FROZEN RESULTS REPRODUCED" if ok else "\nMISMATCH")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
