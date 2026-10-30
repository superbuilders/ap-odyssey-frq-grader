"""V1. One observable property per level, in the criteria array. Notes wall deleted.

Baseline shows Jev TWO parallel multi-clause descriptions of the same five levels:
the verbatim CB criteria ("EVIDENCE: ... AND COMMENTARY: ...") in the criteria
array, and the verbatim CB decision-rule bullets (level 2 alone has four) inside
instructions. Every one of those is a conjunction a real essay satisfies only
partly, so a literal reader has no stable answer and the posterior over adjacent
levels stays flat. Flat posterior -> high-variance expectation -> high SD.

This variant states ONE observable property per level, declaratively, and deletes
the second description entirely.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "sharpen-axis: one property per level, no notes wall"
RATIONALE = ("Replace five multi-clause conjunctions plus a redundant second wall of "
             "decision-rule bullets with five single declarative properties on one axis. "
             "A conjunction that is partly satisfied has no literal answer; a single "
             "observable property does.")
K = 1


def _src(rec):
    return {"synthesis": "the provided sources",
            "rhetorical_analysis": "the passage",
            "argument": "its own examples"}[rec["frq_type"]]


def axis(rec):
    s = _src(rec)
    return [
        "The response presents no relevant evidence from %s. It only restates its own thesis, "
        "repeats what it was given, or discusses something the prompt did not ask about." % s,

        "The response presents evidence from %s but only summarizes that evidence. It never "
        "states how the evidence supports its own argument." % s,

        "The response states how some of its evidence relates to its argument, but those "
        "statements do not connect into a single line of reasoning.",

        "The response explains how some of its specific evidence supports a single line of "
        "reasoning, and leaves some of its evidence or one of its claims unexplained.",

        "The response explains, for every piece of evidence it uses, how that evidence supports "
        "its single line of reasoning.",
    ]


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"] = {
        "type": "score",
        "instructions": (
            "Assign the College Board AP English Language Row B (Evidence and Commentary) score, "
            "0 to 4, to the section titled STUDENT RESPONSE (complete). The scale measures one "
            "thing: how far the response gets from merely presenting evidence to explaining, for "
            "every piece of evidence, how it supports one line of reasoning. Each numbered "
            "description below states the single property that is true of a response at that "
            "level. Choose the number whose description is true of STUDENT RESPONSE (complete). "
            "A response whose grammatical or mechanical errors interfere with communication "
            "cannot reach 4."),
        "criteria": axis(rec)}
    return qs
