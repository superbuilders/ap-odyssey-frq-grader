"""V5. Purely additive. Baseline byte-identical plus one rule for partial conjunctions.

The hypothesis says a literal reader faced with a partly-satisfied conjunction
has no stable answer. This variant does not remove or reword anything: it adds
the missing rule that makes a partly-satisfied conjunction determinate. If the
mechanism is real, SD falls with nothing else changed.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-tiebreak: baseline + a rule for partly-satisfied conjunctions"
RATIONALE = ("Minimal additive test of the stated mechanism. Nothing removed, nothing "
             "reworded; one sentence added telling the reader what a partly-met AND means. "
             "If instability comes from undetermined conjunctions, SD falls here alone.")
K = 1

RULE = (" Each level's criteria join several requirements with AND. A response is at a level "
        "only when every requirement of that level is true of it. If one requirement of a level "
        "is only partly true of the response, the response is below that level. Choose the "
        "highest level every one of whose requirements is true of STUDENT RESPONSE (complete).")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["instructions"] = qs["b_level"]["instructions"] + "\n" + RULE.strip()
    return qs
