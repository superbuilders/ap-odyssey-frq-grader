"""Measure one proposed question design against the frozen metric.

    python3 -I try_proposal.py proposals/my_idea.py [R]

The proposal module must define:

    NAME        str, short label
    RATIONALE   str, the MECHANISM you expect to reduce variance
    K           int, independent Jev calls per grade (use 9 to match baseline)
    questions(rec, segs) -> dict   the Jev question map, must contain "b_level"

Baseline to beat is A9_cal: 9 averaged reads through the shipped quantile
thresholds. flip 0.0704, 7/36 unstable, ordering rho +0.998.

Guards are reported alongside, and a proposal that trips one does not count
however good its flip rate looks. A grader that always says 3 never flips.
"""
import importlib.util, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import jev, measure, metric, vault
from arms import ARMS, _mean_score
from row_b_calibration import calibrate_row_b

BASELINE = {"flip": 0.0704, "unstable": 7, "arm": "A9_cal"}


def load(path):
    spec = importlib.util.spec_from_file_location("proposal", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for attr in ("NAME", "RATIONALE", "K", "questions"):
        if not hasattr(m, attr):
            raise SystemExit("proposal is missing %s" % attr)
    return m


def main(path, R=10):
    m = load(path)
    ARMS["_proposal"] = dict(
        k=m.K, questions=m.questions,
        decode=lambda rec, segs, ans: (calibrate_row_b(_mean_score(ans)), _mean_score(ans)),
        note=m.NAME)

    base_path = "/tmp/jev-reliability/runs/A1.json"
    base = json.load(open(base_path))["mean_signal"] if os.path.exists(base_path) else None

    res = measure.measure("_proposal", R)
    mt = metric.summarize(res["levels"], res["mean_signal"], base)
    sd = statistics.median(res["signal_sd"].values()) if res["signal_sd"] else float("nan")

    print("\n%s  (k=%d, R=%d)" % (m.NAME, m.K, R))
    print("rationale: %s" % m.RATIONALE)
    print("  flip rate        %.4f   (baseline %s %.4f)" % (mt["flip_rate"], BASELINE["arm"], BASELINE["flip"]))
    print("  unstable         %d/%d      (baseline %d)" % (mt["unstable"], mt["n_essays"], BASELINE["unstable"]))
    print("  per-read SD      %.4f" % sd)
    print("  GUARD spread     %.3f   marginal %s" % (mt["spread"], mt["marginal"]))
    print("  GUARD ordering   %s" % mt.get("ordering_vs_baseline", "n/a"))
    print("  jev calls        %d   errors %d   %.0fs" % (res["jev"]["calls"], res["errors"], res["elapsed_s"]))

    ok_spread = mt["spread"] >= 0.80
    ok_order = abs(mt.get("ordering_vs_baseline", 0)) >= 0.80 and mt.get("ordering_vs_baseline", 0) > 0
    better = mt["flip_rate"] < BASELINE["flip"]
    print("  VERDICT          %s" % (
        "BEATS BASELINE" if (better and ok_spread and ok_order)
        else ("guard tripped: " + ("spread " if not ok_spread else "") + ("ordering" if not ok_order else ""))
        if not (ok_spread and ok_order) else "no improvement"))
    out = os.path.join("/tmp/jev-reliability/proposals", os.path.basename(path) + ".json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"name": m.NAME, "rationale": m.RATIONALE, "k": m.K, "metrics": mt,
               "sd": sd, "levels": res["levels"], "signals": res["signals"]}, open(out, "w"))
    return mt


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10)
