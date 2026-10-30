"""V2. Isolate the redundancy. Verbatim CB criteria kept; the notes wall deleted.

V1 changes two things at once (criteria wording AND deleting the notes). This
variant changes only the second: the criteria array stays byte-identical to
baseline, and the five-bullet decision-rule wall in instructions is replaced by
one sentence naming what separates adjacent levels. If stability improves here,
the destabilizer is the SECOND, redundant description, not the criteria wording.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "sharpen-nonotes: verbatim criteria, decision-rule wall removed"
RATIONALE = ("Ablation isolating the redundant second description. Criteria array is "
             "byte-identical to baseline; only the five-bullet notes wall is replaced by "
             "one sentence naming the discriminating axis.")
K = 1


def questions(rec, segs):
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    qs = Q.variant_a(rec, segs)
    qs["b_level"] = {
        "type": "score",
        "instructions": (
            "You are applying the College Board AP English Language Row B (Evidence and "
            "Commentary, 0-4 points) scoring criteria to the section titled STUDENT RESPONSE "
            "(complete). Choose the level whose verbatim criteria the response meets. What "
            "separates one level from the next is how much of the response's evidence it "
            "explains, and whether those explanations form one line of reasoning. A response "
            "whose grammatical or mechanical errors interfere with communication cannot earn "
            "the fourth point."),
        "criteria": list(c["criteria"])}
    return qs
