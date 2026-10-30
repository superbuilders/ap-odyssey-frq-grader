"""V12. V10 plus an explicit reader-agreement prime.

V10's mechanism is that a decision has one answer while a position on a
continuum does not. Push it: state that two readers applying these criteria to
this response must land on the same level. Still purely additive.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-decisive2: V10 + two-readers-agree prime"
RATIONALE = ("Strengthen V10's decisiveness with an explicit agreement constraint. If the "
             "mechanism is 'a decision has one answer', naming that answer as shared "
             "between readers should sharpen it further.")
K = 1

RULE = ("Each numbered level states an EVIDENCE requirement and a COMMENTARY requirement, joined "
        "by AND. STUDENT RESPONSE (complete) is at a level only when both requirements of that "
        "level are true of it; if either is only partly true, the response is below that level. "
        "STUDENT RESPONSE (complete) is at exactly one of the five levels. Decide which one. Do "
        "not report a position between two levels. Two readers applying these criteria to "
        "STUDENT RESPONSE (complete) reach the same level.")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["instructions"] = qs["b_level"]["instructions"] + "\n" + RULE
    return qs
