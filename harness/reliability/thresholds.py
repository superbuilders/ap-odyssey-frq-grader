"""Threshold placement, evaluated offline against stored per-run signals.

Quantile matching puts each cut at a point that reproduces the gold marginal.
That point is, by construction, wherever essays are densest -- which is the
worst place to stand if you care whether the same essay scores the same twice.
On the 36 working essays the shipped 1|2 cut at 2.0656 has nine essays within
two standard deviations of it, while the widest gap in the whole distribution
sits unused 0.14 below.

This module nudges each cut to the middle of the nearest sizeable gap, trading
marginal fidelity for stability. The window `w` is the whole knob: w=0 is the
shipped behaviour.

Nothing here calls Jev. It re-decodes signals already measured, so a threshold
sweep is free and leaves the Jev call count untouched.
"""
import json
from collections import Counter

RUNS = "/tmp/jev-reliability/runs/A1.json"
SHIPPED = (2.0656, 2.3061, 2.8359)


def load_signals(path=RUNS):
    d = json.load(open(path))
    if "signals" not in d:
        raise RuntimeError("%s has no per-run signals; re-run measure.py for this arm" % path)
    return d["signals"]


def decode(sig, cuts):
    lvl = 1
    for c in cuts:
        if sig > c:
            lvl += 1
    return lvl


def evaluate(signals, cuts):
    """Flip rate and marginal for a threshold triple, from stored signals."""
    per = {}
    for eid, runs in signals.items():
        lv = [decode(s, cuts) for s in runs]
        R = len(lv)
        pairs = R * (R - 1) / 2
        agree = sum(c * (c - 1) / 2 for c in Counter(lv).values())
        per[eid] = 1.0 - agree / pairs
    modes = {e: Counter([decode(s, cuts) for s in r]).most_common(1)[0][0]
             for e, r in signals.items()}
    return {"flip_rate": sum(per.values()) / len(per),
            "unstable": sum(1 for v in per.values() if v > 0),
            "marginal": dict(sorted(Counter(modes.values()).items())),
            "modes": modes}


def gap_aware(signals, base=SHIPPED, w=0.10):
    """Move each cut to the midpoint of the widest gap within +/-w of it."""
    xs = sorted(sum(signals.values(), []))
    out = []
    for c in base:
        best, best_gap = c, -1.0
        for i in range(len(xs) - 1):
            mid = (xs[i] + xs[i + 1]) / 2.0
            gap = xs[i + 1] - xs[i]
            if abs(mid - c) <= w and gap > best_gap:
                best, best_gap = mid, gap
        out.append(round(best, 4))
    return tuple(out)


if __name__ == "__main__":
    sg = load_signals()
    base = evaluate(sg, SHIPPED)
    print("shipped  cuts=%s" % (SHIPPED,))
    print("         flip=%.4f unstable=%2d/%d marginal=%s"
          % (base["flip_rate"], base["unstable"], len(sg), base["marginal"]))
    print()
    for w in (0.05, 0.10, 0.15, 0.20):
        cuts = gap_aware(sg, w=w)
        r = evaluate(sg, cuts)
        print("w=%.2f    cuts=%s" % (w, cuts))
        print("         flip=%.4f unstable=%2d/%d marginal=%s  (shift %s)"
              % (r["flip_rate"], r["unstable"], len(sg), r["marginal"],
                 [round(a - b, 3) for a, b in zip(cuts, SHIPPED)]))
