"""Sweep k offline from the pool. No Jev calls.

Partitions each essay's 90 independent reads into R disjoint groups of k, so no
read is shared between two runs and the resulting flip rate is honest rather
than a bootstrap artefact.

Answers the question averaging raises: is there a floor? If flips persist as k
grows, those essays have a true signal sitting ON a cut, where no amount of
noise reduction helps and only a different question would.
"""
import json, os, statistics, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))
import thresholds as TH

POOL = "/tmp/jev-reliability/pool.json"


def partition(pool, k):
    """R disjoint groups of k reads per essay. R = floor(90/k)."""
    R = min(len(v) for v in pool.values()) // k
    return {e: [statistics.fmean(v[i * k:(i + 1) * k]) for i in range(R)] for e, v in pool.items()}, R


def evaluate(sig, cuts):
    per, modes = {}, {}
    for e, runs in sig.items():
        lv = [TH.decode(s, cuts) for s in runs]
        R = len(lv)
        pairs = R * (R - 1) / 2
        agree = sum(c * (c - 1) / 2 for c in Counter(lv).values())
        per[e] = 1.0 - agree / pairs
        modes[e] = Counter(lv).most_common(1)[0][0]
    return (sum(per.values()) / len(per), sum(1 for v in per.values() if v > 0), modes, per)


if __name__ == "__main__":
    d = json.load(open(POOL))
    pool = d["pool"]
    gold = {}
    for l in open("/tmp/jev-arm/keys/labels.jsonl", encoding="utf-8"):
        r = json.loads(l)
        gold[r["essay_id"]] = r["row_b"]
    ids = sorted(pool)
    print("pool: %d essays x %d reads\n" % (len(pool), d["n_reads"]))
    print("%-6s %-4s %9s %10s %8s  %s" % ("k", "R", "flip", "unstable", "acc/36", "marginal"))
    prev = None
    for k in (1, 2, 3, 5, 6, 9, 10, 15, 18, 30, 45):
        sig, R = partition(pool, k)
        if R < 2:
            continue
        f, u, modes, per = evaluate(sig, TH.SHIPPED)
        acc = sum(1 for e in ids if modes[e] == gold[e])
        print("%-6d %-4d %9.4f %7d/36 %7d/36  %s" % (k, R, f, u, acc, dict(sorted(Counter(modes.values()).items()))))
        prev = (k, u, per)
    print()
    sig45, _ = partition(pool, 45)
    f, u, modes, per = evaluate(sig45, TH.SHIPPED)
    stuck = sorted([e for e, v in per.items() if v > 0])
    print("still unstable at k=45 (45 reads averaged per grade): %d essays" % len(stuck))
    for e in stuck:
        m = statistics.fmean(pool[e])
        d2 = min(abs(m - c) for c in TH.SHIPPED)
        print("   %-18s mean %.4f, %.4f from nearest cut (pooled SD of a 45-read mean = %.4f)"
              % (e, m, d2, statistics.stdev(pool[e]) / (45 ** 0.5)))
