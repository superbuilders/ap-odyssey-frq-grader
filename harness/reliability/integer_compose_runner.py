"""Live runner for integer-composed proposals.

try_proposal.py hardwires decode = calibrate_row_b(mean b_level score), which is
precisely the continuous-to-discrete step this lane exists to remove, so it
cannot express an integer composed in Python. Everything else here is the same:
same measure.measure, same frozen metric.py, same A1 ordering baseline.

    python3 -I integer_compose_runner.py proposals/<file>.py <K> [R]

The proposal module supplies questions(rec, segs) and compose(g, meta).
"""
import importlib.util, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import measure, metric
from arms import ARMS, _mean_nouls
from integer_compose_offline import accuracy

BASE = {1: (0.1463, 11), 9: (0.0704, 7)}


def load(path):
    spec = importlib.util.spec_from_file_location("proposal", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for a in ("NAME", "RATIONALE", "questions", "compose"):
        if not hasattr(m, a):
            raise SystemExit("proposal is missing %s" % a)
    return m


def main(path, K, R=10):
    m = load(path)

    def decode(rec, segs, answers):
        g = {k: v["noul"] for k, v in _mean_nouls(answers).items()}
        meta = {"n_seg": len(segs), "frq_type": rec["frq_type"],
                "cited": len(rec.get("cited_sources") or [])}
        return m.compose(g, meta)

    ARMS["_ic"] = dict(k=K, questions=m.questions, decode=decode, note=m.NAME)
    base = json.load(open("/tmp/jev-reliability/runs/A1.json"))["mean_signal"]
    res = measure.measure("_ic", R)
    mt = metric.summarize(res["levels"], res["mean_signal"], base)
    sd = statistics.median(res["signal_sd"].values())
    ex, w1 = accuracy(res["levels"])
    bf, bu = BASE.get(K, BASE[1])
    ok_s = mt["spread"] >= 0.80
    ok_o = mt.get("ordering_vs_baseline", 0) >= 0.80
    print("\n%s  (k=%d, R=%d)" % (m.NAME, K, R))
    print("rationale: %s" % m.RATIONALE)
    print("  flip rate        %.4f   (baseline k=%d %.4f)" % (mt["flip_rate"], K, bf))
    print("  unstable         %d/%d      (baseline %d)" % (mt["unstable"], mt["n_essays"], bu))
    print("  per-read SD      %.4f   (of the COMPOSED signal, not of b_level)" % sd)
    print("  GUARD spread     %.3f %s  marginal %s" % (mt["spread"], "OK " if ok_s else "FAIL", mt["marginal"]))
    print("  GUARD ordering   %+.3f %s" % (mt["ordering_vs_baseline"], "OK " if ok_o else "FAIL"))
    print("  TRIPWIRE acc     %s/36 exact, %s within 1   (A-arm control 25/36)" % (ex, w1))
    print("  jev calls        %d   errors %d   %.0fs" % (res["jev"]["calls"], res["errors"], res["elapsed_s"]))
    print("  VERDICT          %s" % ("BEATS BASELINE on flip, guards intact"
          if (mt["flip_rate"] < bf and ok_s and ok_o) else "guard tripped or no improvement"))
    out = "/tmp/jev-reliability/proposals/%s.k%d.json" % (os.path.basename(path), K)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"name": m.NAME, "k": K, "metrics": mt, "sd": sd, "acc": ex,
               "levels": res["levels"], "signals": res["signals"]}, open(out, "w"))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 10)
