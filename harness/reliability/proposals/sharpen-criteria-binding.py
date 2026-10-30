"""V8. Resolve the hedge, not the conjunction.

The instructions wall is headed "Typical responses that earn N points". "Typical"
is itself undetermined: a response can be atypical of its level and still be at
it. So Jev is shown two descriptions that can disagree and is told nothing about
which governs. State which governs. Nothing removed.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-binding: criteria govern, decision rules are indicators"
RATIONALE = ("Baseline shows two descriptions of the same five levels and no rule for which "
             "wins. The decision rules are hedged ('typical responses'), the criteria are "
             "not. Say so. Removes a conflict the reader currently has to resolve arbitrarily.")
K = 1

RULE = ("The decision rules above describe what responses at each level typically look like. "
        "They are indicators, not requirements: a response can be at a level without matching "
        "every bullet. The numbered criteria are the binding rule. Where a decision rule and "
        "the numbered criteria point at different levels for STUDENT RESPONSE (complete), "
        "follow the numbered criteria.")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["instructions"] = qs["b_level"]["instructions"] + "\n" + RULE
    return qs
