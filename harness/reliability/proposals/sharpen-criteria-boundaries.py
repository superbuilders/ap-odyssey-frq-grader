"""V6. Fewer decisions, literally: four boundaries instead of five descriptions.

Five level descriptions ask the reader to evaluate five overlapping conjunctions.
Four ordered boundary questions ask four independent yes/no facts, and a rule
that makes the first 'no' decisive. Criteria array stays verbatim so the ordering
signal is untouched.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "sharpen-boundaries: four ordered boundary decisions, verbatim criteria"
RATIONALE = ("Replace five overlapping level descriptions with the four boundary facts that "
             "actually separate them, plus 'the first decision the response fails fixes its "
             "level'. Fewer, independent, determinate decisions.")
K = 1


def questions(rec, segs):
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    rhet = rec["frq_type"] == "rhetorical_analysis"
    b34 = ("whether the response explains how the evidence supports that reasoning for every "
           "piece of evidence it uses, rather than for only some of it")
    if rhet:
        b34 += (", and explains how multiple rhetorical choices in the passage contribute to "
                "the writer's argument, purpose, or message")
    decisions = [
        "0 or higher: whether the response uses any relevant evidence at all, rather than only "
        "restating its thesis or repeating what it was given.",
        "1 or higher: whether the response states how any of its evidence bears on its argument, "
        "rather than only summarizing that evidence.",
        "2 or higher: whether the response's explanations connect into a single line of "
        "reasoning, with specific evidence behind each claim.",
        "3 or 4: " + b34 + ".",
    ]
    qs = Q.variant_a(rec, segs)
    qs["b_level"] = {
        "type": "score",
        "instructions": (
            "You are applying the College Board AP English Language Row B (Evidence and "
            "Commentary, 0-4 points) scoring criteria to the section titled STUDENT RESPONSE "
            "(complete). The five levels are ordered, and exactly four decisions separate "
            "them:\n" + "\n".join(decisions) +
            "\nThe first of these decisions that STUDENT RESPONSE (complete) fails fixes its "
            "level.\n" + c["additional"]),
        "criteria": list(c["criteria"])}
    return qs
