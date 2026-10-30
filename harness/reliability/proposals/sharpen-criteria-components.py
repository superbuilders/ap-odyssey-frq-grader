"""V7. The tiebreak rule stated against the actual conjunction structure.

V5 (tiebreak) was the only variant whose per-read SD FELL (0.0248 -> 0.0222) with
the distribution and ordering intact. Its rule was generic ("several requirements
joined by AND"). The CB criteria have a specific two-part shape: an EVIDENCE
clause and a COMMENTARY clause. Name that shape and resolve both half-met cases.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-components: EVIDENCE/COMMENTARY half-met rule"
RATIONALE = ("V5 showed an additive determinacy rule is the only thing that lowered SD. "
             "Sharpen it onto the real conjunction shape: each level is EVIDENCE AND "
             "COMMENTARY, and either half unmet puts the response below that level.")
K = 1

RULE = ("Each numbered level states an EVIDENCE requirement and a COMMENTARY requirement, joined "
        "by AND. STUDENT RESPONSE (complete) is at a level only when both requirements of that "
        "level are true of it. A response that meets a level's EVIDENCE requirement but not its "
        "COMMENTARY requirement is below that level, and a response that meets the COMMENTARY "
        "requirement but not the EVIDENCE requirement is also below that level. Choose the "
        "highest level whose EVIDENCE requirement and COMMENTARY requirement are both true of "
        "STUDENT RESPONSE (complete).")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["instructions"] = qs["b_level"]["instructions"] + "\n" + RULE
    return qs
