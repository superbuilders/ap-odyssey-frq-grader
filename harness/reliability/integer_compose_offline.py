"""Score any composition rule against the frozen metric, offline, from a pool.

Partitions each essay's N independent reads into R disjoint groups of k and
averages the nouls inside each group, exactly as arms._b_compose does live. No
read is shared between two runs, so the flip rate is honest.
"""
import json, os, statistics, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))
import metric

A1 = json.load(open("/tmp/jev-reliability/runs/A1.json"))["mean_signal"]


def load(path):
    d = json.load(open(path))
    return d["pool"], d["meta"]


def groups(pool, k, R):
    """R disjoint averaged gate-vectors per essay."""
    out = {}
    for e, reads in pool.items():
        assert len(reads) >= k * R, "%s has %d reads, need %d" % (e, len(reads), k * R)
        gs = []
        for i in range(R):
            chunk = reads[i * k:(i + 1) * k]
            keys = chunk[0].keys()
            gs.append({q: statistics.fmean(c[q] for c in chunk) for q in keys})
        out[e] = gs
    return out


def score(compose, pool, meta, k=1, R=10, label=""):
    gs = groups(pool, k, R)
    levels, sigs = {}, {}
    for e, runs in gs.items():
        lv, sg = [], []
        for g in runs:
            a, b = compose(g, meta[e])
            lv.append(a); sg.append(b)
        levels[e] = lv
        sigs[e] = statistics.fmean(sg)
    mt = metric.summarize(levels, sigs, A1)
    mt["label"] = label
    mt["k"] = k
    # per-read SD of the continuous signal, k=1 reads, median over essays
    sd = statistics.median([
        statistics.stdev([compose(g, meta[e])[1] for g in pool[e][:30]]) for e in pool])
    mt["sd"] = round(sd, 4)
    return mt, levels


def line(mt):
    ok_s = mt["spread"] >= 0.80
    ok_o = mt.get("ordering_vs_baseline", 0) >= 0.80
    return ("%-34s k=%-2d flip %.4f  unst %2d/36  spread %.3f%s  rho %+.3f%s  SD %.4f  %s"
            % (mt["label"], mt["k"], mt["flip_rate"], mt["unstable"], mt["spread"],
               " " if ok_s else "!", mt.get("ordering_vs_baseline", 0), " " if ok_o else "!",
               mt["sd"], mt["marginal"]))
