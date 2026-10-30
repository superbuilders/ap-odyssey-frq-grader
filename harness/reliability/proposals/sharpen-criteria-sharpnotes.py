"""V4. Array verbatim; the notes wall REWRITTEN sharp rather than deleted.

V2 showed that deleting the decision-rule wall raises SD (0.0248 -> 0.0332), so
the wall is load-bearing. V3 showed the criteria array is what carries ordering.
So: keep the verbatim array, keep a second description, but make that second
description five parallel single-property declaratives instead of fifteen
bullets of partly-satisfiable conjunctions.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "sharpen-notes: verbatim criteria + one-property-per-level decision rules"
RATIONALE = ("Keep the verbatim criteria array (it carries the ordering) and keep a second "
             "description (deleting it raised SD), but replace fifteen multi-clause bullets "
             "with five parallel single-property declaratives.")
K = 1

RULES = [
    "0 -- The response presents no relevant evidence. It only restates its own thesis, repeats "
    "what it was given, or discusses something the prompt did not ask about.",
    "1 -- The response presents evidence but only summarizes it. It never states how that "
    "evidence supports its own argument.",
    "2 -- The response states how some of its evidence relates to its argument, but those "
    "statements do not connect into a single line of reasoning.",
    "3 -- The response explains how some of its specific evidence supports a single line of "
    "reasoning, and leaves some evidence or one of its claims unexplained.",
    "4 -- The response explains, for every piece of evidence it uses, how that evidence supports "
    "its single line of reasoning.",
]


def questions(rec, segs):
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    qs = Q.variant_a(rec, segs)
    qs["b_level"] = {
        "type": "score",
        "instructions": (
            "You are applying the College Board AP English Language Row B (Evidence and "
            "Commentary, 0-4 points) scoring criteria to the section titled STUDENT RESPONSE "
            "(complete). Choose the level whose verbatim criteria the response meets. Each "
            "decision rule below states the single property that is true of a response at that "
            "level.\n" + "\n".join(RULES) + "\n" + c["additional"]),
        "criteria": list(c["criteria"])}
    return qs
