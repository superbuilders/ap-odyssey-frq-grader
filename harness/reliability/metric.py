"""The frozen metric and its degeneracy guards.

OBJECTIVE: pairwise flip rate. Across R independent grades of the same essay
with the same question set, the probability that two of them disagree on the
discrete Row B level. Lower is better. Needs no answer key, so optimizing it
cannot overfit to College Board scores.

It can, however, be gamed. A question set that returns 3 for every essay has a
flip rate of zero and is worthless. Every guard below exists to make that
failure mode visible rather than winning.
"""
import math
from collections import Counter


def flip_rate(levels_by_essay):
    """levels_by_essay: {essay_id: [level per independent run]}.

    Returns P(two independent runs disagree), averaged over essays. Computed
    from counts rather than by enumerating pairs, so it is exact for any R.
    """
    per = {}
    for eid, lv in levels_by_essay.items():
        R = len(lv)
        if R < 2:
            raise ValueError("flip rate needs at least 2 runs for %s" % eid)
        pairs = R * (R - 1) / 2
        agree = sum(c * (c - 1) / 2 for c in Counter(lv).values())
        per[eid] = 1.0 - agree / pairs
    return sum(per.values()) / len(per), per


def unstable_count(levels_by_essay):
    """Essays that did not return the same level every single run."""
    return sum(1 for lv in levels_by_essay.values() if len(set(lv)) > 1)


def modal_levels(levels_by_essay):
    return {e: Counter(lv).most_common(1)[0][0] for e, lv in levels_by_essay.items()}


def spread(levels_by_essay):
    """Guard against collapse. Normalized entropy of the modal-level marginal.

    1.0 means the predictions are spread evenly across the levels seen; 0.0
    means every essay got the same level. A constant grader never flips, so
    without this guard it would win.
    """
    modes = list(modal_levels(levels_by_essay).values())
    n = len(modes)
    counts = Counter(modes)
    if len(counts) < 2:
        return 0.0, dict(counts)
    H = -sum((c / n) * math.log(c / n) for c in counts.values())
    return H / math.log(len(counts)), dict(sorted(counts.items()))


def _rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(a, b):
    """Rank correlation. Hand-rolled so the harness has no scipy dependency."""
    if len(a) != len(b) or len(a) < 3:
        raise ValueError("spearman needs equal-length inputs of at least 3")
    ra, rb = _rank(a), _rank(b)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else 0.0


def ordering_vs(signal_by_essay, baseline_by_essay):
    """Guard against destroying the signal.

    Jev's ordering correlates with gold at rho 0.90. That is the part of Jev
    that works, and a reliability search has no label with which to notice it
    breaking. So we hold the candidate's ordering against the BASELINE Jev
    ordering, not against gold. No answer key is touched.
    """
    ids = sorted(set(signal_by_essay) & set(baseline_by_essay))
    return spearman([signal_by_essay[i] for i in ids], [baseline_by_essay[i] for i in ids])


def commit_rate(levels_by_essay):
    """Guard for abstaining arms. Fraction of essays given a single level.

    Abstention trivially drives the flip rate to zero, so an arm that refuses
    to answer must show what it refused on.
    """
    modes = modal_levels(levels_by_essay)
    committed = sum(1 for v in modes.values() if "-" not in str(v))
    return committed / len(modes)


def summarize(levels_by_essay, signal_by_essay, baseline_signal=None):
    fr, per = flip_rate(levels_by_essay)
    sp, marg = spread(levels_by_essay)
    out = {"flip_rate": round(fr, 4),
           "unstable": unstable_count(levels_by_essay),
           "n_essays": len(levels_by_essay),
           "runs": len(next(iter(levels_by_essay.values()))),
           "spread": round(sp, 4),
           "commit_rate": round(commit_rate(levels_by_essay), 4),
           "marginal": marg,
           "per_essay_flip": {k: round(v, 3) for k, v in per.items()}}
    if baseline_signal:
        out["ordering_vs_baseline"] = round(ordering_vs(signal_by_essay, baseline_signal), 4)
    return out
