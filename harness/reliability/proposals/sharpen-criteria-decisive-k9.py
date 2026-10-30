"""V10. Ask for a decision, not a blend.

Diagnosis from V1-V9: flip rate tracks how many essays sit within ~2 SD of a
fixed cut, and the additive rules only shave ~10% off SD, which barely moves
that count. But the three cuts (2.0656, 2.3061, 2.8359) all sit AWAY from the
integers: just above 2, midway between 2 and 3, and just below 3. So a signal
that resolves toward whole levels puts essays in the sparse regions by
construction, without collapsing the scale -- essays still spread over 1-4 and
keep their order, so neither guard is being gamed.

This is the lane's hypothesis in its strongest form: the reader is being asked
for one decision among five, not for a position on a continuum.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-decisive: one level, not a position between levels"
RATIONALE = ("Add the EVIDENCE/COMMENTARY determinacy rule and then ask for a decision "
             "rather than a blend. The cuts all sit away from whole levels, so resolving "
             "toward one level moves essays off the boundaries without collapsing spread "
             "or reordering them.")
K = 9

RULE = ("Each numbered level states an EVIDENCE requirement and a COMMENTARY requirement, joined "
        "by AND. STUDENT RESPONSE (complete) is at a level only when both requirements of that "
        "level are true of it; if either is only partly true, the response is below that level. "
        "STUDENT RESPONSE (complete) is at exactly one of the five levels. Decide which one. Do "
        "not report a position between two levels.")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["instructions"] = qs["b_level"]["instructions"] + "\n" + RULE
    return qs
