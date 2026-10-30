"""disjoint-levels v4: SINGLE-AXIS reframe.

v1-v3 keep CB's two-clause shape (EVIDENCE ... AND COMMENTARY ...), which gives
the head two partly-independent dimensions to trade off against each other. A
response strong on evidence and weak on commentary genuinely lies between two
criteria, and no amount of exclusion wording fixes that -- the levels are not a
scale, they are a grid read diagonally.

v4 collapses the rubric onto the one variable that actually orders it: how much
of the response's evidence is tied, by explanation, to a working chain of
claims. Five bins on one axis, uniform in shape and length so adjacent bins sit
the same distance apart, each one excluding the rest.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "disjoint-levels v4 (one ordered axis, not a grid)"
RATIONALE = ("CB's levels are a 2-D grid (evidence x commentary) read as a scale, so mixed "
             "responses sit between criteria by construction. Collapse to one axis.")
K = 1

SRC = {"synthesis": "the provided sources",
       "rhetorical_analysis": "the passage",
       "argument": "its own examples"}

AXIS = [
 "None of it. The response offers no evidence drawn from {s}, only restatement, repetition, or "
 "material that does not bear on the prompt.",

 "Evidence, but no explaining. The response presents evidence drawn from {s} and reports what "
 "that evidence says, and it stops there: it never states what any piece of it does for the "
 "argument.",

 "Explaining, but no chain. The response interprets at least one piece of its evidence from {s}, "
 "but its claims stand side by side instead of building toward the thesis, or the progression it "
 "asserts between them does not hold.",

 "A chain, explained in part. The response's claims build toward the thesis and each rests on "
 "specific evidence from {s}, and some of that evidence is explained. Some of it is not: at "
 "least one piece is presented and left to speak for itself.",

 "A chain, explained throughout. The response's claims build toward the thesis and each rests on "
 "specific evidence from {s}, and no piece of that evidence is left to speak for itself: every "
 "one is accompanied by commentary saying how it supports the chain.",
]

HEAD = ("Read the section titled STUDENT RESPONSE (complete). Rate one thing only: how much of "
        "the evidence it presents is tied, by the response's own explanation, to a working chain "
        "of claims that builds toward its thesis. The five points of the scale below are mutually "
        "exclusive -- each rules the others out -- and they are ordered by that single quantity. "
        "Writing whose grammatical or mechanical errors interfere with communication cannot reach "
        "the top point.")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    s = SRC[rec["frq_type"]]
    qs["b_level"]["criteria"] = [t.format(s=s) for t in AXIS]
    qs["b_level"]["instructions"] = HEAD
    return qs
