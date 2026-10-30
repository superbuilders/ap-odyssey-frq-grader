"""The hypothesis space: candidate ways of asking Jev for a Row B level.

An arm is a question set plus a decode. `k` is how many independent Jev calls
make up ONE grade; the harness then repeats whole grades R times to measure how
much that grade wobbles. So arm A9 costs 9 calls per grade and is compared
against A1 on equal footing: both produce one level, A9 just pays more for it.
"""
import os, statistics, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import questions as Q
from rubric import cell
from row_b_calibration import calibrate_row_b, THRESHOLDS
from run import compose_b

T = 0.5


def _mean_score(answers, key="b_level"):
    return statistics.fmean(float(a[key]["score"]) for a in answers)


def _mean_nouls(answers):
    """Average every noul across independent calls, keeping the answer shape."""
    out = {}
    for k in answers[0]:
        vals = [float(a[k]["noul"]) for a in answers if k in a and a[k]["type"] == "noul"]
        if vals:
            out[k] = {"type": "noul", "noul": statistics.fmean(vals)}
    return out


# ---------- variant A: one holistic score question ----------
def _a_questions(rec, segs):
    return Q.variant_a(rec, segs)


def _a_round(rec, segs, answers):
    s = _mean_score(answers)
    return int(round(s)), s


def _a_calibrated(rec, segs, answers):
    s = _mean_score(answers)
    return calibrate_row_b(s), s


def _a_vote(rec, segs, answers):
    """Majority vote over independently rounded decodes, not an averaged score."""
    lv = [int(round(float(a["b_level"]["score"]))) for a in answers]
    return Counter(lv).most_common(1)[0][0], _mean_score(answers)


# ---------- variant A with the level descriptors reversed ----------
def _a_reversed_questions(rec, segs):
    """Validity canary. If reversing which text describes which level leaves the
    flip rate unchanged, the flip rate is not responding to rubric content."""
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["criteria"] = list(reversed(qs["b_level"]["criteria"]))
    return qs


# ---------- variant B: nouls composed in code ----------
def _b_questions(rec, segs):
    return Q.variant_b(rec, segs)


def _b_compose(rec, segs, answers):
    merged = _mean_nouls(answers)
    lvl, raw, _used, _diag = compose_b(rec, segs, merged)
    return lvl, raw


ARMS = {
    "A1":      dict(k=1, questions=_a_questions, decode=_a_round,
                    note="shipped baseline: one score question, round()"),
    "A1_dup":  dict(k=1, questions=_a_questions, decode=_a_round,
                    note="byte-identical duplicate of A1. Its gap from A1 IS the metric's noise floor."),
    "A1_rev":  dict(k=1, questions=_a_reversed_questions, decode=_a_round,
                    note="validity canary: level descriptors reversed"),
    "A1_cal":  dict(k=1, questions=_a_questions, decode=_a_calibrated,
                    note="one call, quantile thresholds instead of round()"),
    "A3":      dict(k=3, questions=_a_questions, decode=_a_round,
                    note="average 3 independent reads, then round"),
    "A9":      dict(k=9, questions=_a_questions, decode=_a_round,
                    note="average 9 independent reads, then round"),
    "A9_vote": dict(k=9, questions=_a_questions, decode=_a_vote,
                    note="9 reads, majority vote on the rounded level"),
    "A9_cal":  dict(k=9, questions=_a_questions, decode=_a_calibrated,
                    note="average 9 reads, quantile thresholds"),
    "A3_cal":  dict(k=3, questions=_a_questions, decode=_a_calibrated,
                    note="average 3 reads, quantile thresholds"),
    "A5_cal":  dict(k=5, questions=_a_questions, decode=_a_calibrated,
                    note="average 5 reads, quantile thresholds"),
    "B1":      dict(k=1, questions=_b_questions, decode=_b_compose,
                    note="noul decomposition, integer composed in code"),
    "B3":      dict(k=3, questions=_b_questions, decode=_b_compose,
                    note="noul decomposition, each noul averaged over 3 reads"),
}


# ---------- abstain rather than emit a number that would change on refresh ----------

def _abstain_decode(m):
    """Emit a band like "2-3" when the signal is within m of a cut point.

    Averaging buys little here because much of the instability is essays whose
    true signal sits ON a threshold, where no amount of noise reduction helps.
    Refusing to pick is the honest output for those.
    """
    def decode(rec, segs, answers):
        s = _mean_score(answers)
        lvl = calibrate_row_b(s)
        for t in THRESHOLDS:
            if abs(s - t) < m:
                lo = calibrate_row_b(t - 1e-9)
                hi = calibrate_row_b(t + 1e-9)
                return "%d-%d" % (lo, hi), s
        return str(lvl), s
    return decode


for _m in (0.05, 0.10, 0.15):
    ARMS["A1_ab%02d" % int(_m * 100)] = dict(
        k=1, questions=_a_questions, decode=_abstain_decode(_m),
        note="1 read, quantile thresholds, abstain within %.2f of a cut" % _m)
    ARMS["A3_ab%02d" % int(_m * 100)] = dict(
        k=3, questions=_a_questions, decode=_abstain_decode(_m),
        note="avg 3 reads, quantile thresholds, abstain within %.2f of a cut" % _m)
