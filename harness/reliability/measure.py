"""Frozen measurement harness. One command, one arm, one metric.

Runs R independent grades of an arm over the 36 working essays. Each grade
costs `k` Jev calls, so an arm that buys stability with repeats pays for it
visibly in the call count printed at the end.

Never touches the sealed 2025 essays and never reads a gold label.
"""
import json, os, statistics, sys, time, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import jev, metric, vault
from arms import ARMS
from build_state import build

OUT_DIR = "/tmp/jev-reliability/runs"
WORKERS = 12


def one_grade(arm, rec, state, segs):
    qs = arm["questions"](rec, segs)
    answers = []
    for _ in range(arm["k"]):
        a = jev.ask(state, qs)["answers"]
        missing = set(qs) - set(a)
        if missing:
            raise RuntimeError("missing answers %s for %s" % (sorted(missing)[:3], rec["essay_id"]))
        answers.append(a)
    return arm["decode"](rec, segs, answers)


def measure(arm_name, R, essays=None):
    arm = ARMS[arm_name]
    rows = essays if essays is not None else vault.working_set()
    prepared = {r["essay_id"]: (r, *build(r)[:2]) for r in rows}

    levels = {e: [None] * R for e in prepared}
    signals = {e: [] for e in prepared}
    errors = []
    t0 = time.time()

    def unit(eid, run_i):
        rec, state, segs = prepared[eid]
        return eid, run_i, one_grade(arm, rec, state, segs)

    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(unit, e, i) for e in prepared for i in range(R)]
        for f in cf.as_completed(futs):
            try:
                eid, i, (lvl, sig) = f.result()
            except Exception as exc:
                errors.append(repr(exc)[:200])
                continue
            levels[eid][i] = lvl
            signals[eid].append(sig)

    dropped = [e for e, lv in levels.items() if any(x is None for x in lv)]
    for e in dropped:
        levels[e] = [x for x in levels[e] if x is not None]
    levels = {e: lv for e, lv in levels.items() if len(lv) >= 2}

    mean_signal = {e: sum(v) / len(v) for e, v in signals.items() if v}
    signal_sd = {e: (statistics.stdev(v) if len(v) > 1 else 0.0) for e, v in signals.items() if v}
    return {"arm": arm_name, "k": arm["k"], "R": R, "note": arm["note"],
            "levels": levels, "mean_signal": mean_signal,
            "signal_sd": signal_sd, "signals": signals,
            "errors": len(errors), "error_samples": errors[:3],
            "dropped_essays": dropped,
            "elapsed_s": round(time.time() - t0, 1),
            "jev": jev.stats()}


def run_and_score(arm_name, R, baseline_signal=None):
    res = measure(arm_name, R)
    res["metrics"] = metric.summarize(res["levels"], res["mean_signal"], baseline_signal)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, arm_name + ".json"), "w") as f:
        json.dump(res, f, indent=1)
    m = res["metrics"]
    print("%-9s k=%-2d R=%-2d  flip=%.4f  unstable=%2d/%d  commit=%.2f  spread=%.3f  marginal=%s  calls=%d errors=%d  %.0fs"
          % (arm_name, res["k"], R, m["flip_rate"], m["unstable"], m["n_essays"],
             m["commit_rate"], m["spread"], m["marginal"], res["jev"]["calls"], res["errors"], res["elapsed_s"]))
    if "ordering_vs_baseline" in m:
        print("%-9s   ordering vs baseline rho = %+.3f" % ("", m["ordering_vs_baseline"]))
    return res


if __name__ == "__main__":
    name = sys.argv[1]
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    base = None
    bp = os.path.join(OUT_DIR, "A1.json")
    if name != "A1" and os.path.exists(bp):
        base = json.load(open(bp))["mean_signal"]
    run_and_score(name, R, base)
