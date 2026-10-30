"""V11. Ablation of V10: the decisiveness sentence ALONE, no conjunction rule.

V10 added two things at once. If the win is decisiveness ("one level, not a
position between levels") and not the EVIDENCE/COMMENTARY determinacy rule,
this reproduces V10. If it does not, the conjunction rule was load-bearing.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-decisive-only: decisiveness sentence alone"
RATIONALE = ("Ablation isolating which half of V10 works: decisiveness, or the half-met "
             "conjunction rule. One sentence added to the byte-identical baseline.")
K = 1

RULE = ("STUDENT RESPONSE (complete) is at exactly one of the five levels. Decide which one. "
        "Do not report a position between two levels.")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["instructions"] = qs["b_level"]["instructions"] + "\n" + RULE
    return qs
