"""V9. Both determinacy rules together: which description governs, and what a
half-met conjunction means. Still purely additive; nothing removed or reworded."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-both: binding rule + EVIDENCE/COMMENTARY half-met rule"
RATIONALE = ("Compose the two additive determinacy rules. Each removes one place where a "
             "literal reader currently has no determined answer: which of the two "
             "descriptions governs, and what a partly-met EVIDENCE-AND-COMMENTARY means.")
K = 1

RULE = ("The decision rules above describe what responses at each level typically look like. "
        "They are indicators, not requirements. The numbered criteria are the binding rule; "
        "where the two point at different levels, follow the numbered criteria. Each numbered "
        "level states an EVIDENCE requirement and a COMMENTARY requirement, joined by AND. "
        "STUDENT RESPONSE (complete) is at a level only when both requirements of that level "
        "are true of it; if either one is only partly true, the response is below that level. "
        "Choose the highest level whose EVIDENCE requirement and COMMENTARY requirement are "
        "both true of STUDENT RESPONSE (complete).")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["instructions"] = qs["b_level"]["instructions"] + "\n" + RULE
    return qs
