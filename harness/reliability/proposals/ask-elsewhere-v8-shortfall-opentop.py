"""ask-elsewhere v8: v4's shortfall diagnosis with an attainable top rung.

Honesty probe. v4 passed both guards but emitted no level 4 at all: its signal
never crossed the 2.8359 cut, so one of the three cuts could not fire and one
third of the flip opportunities vanished for free. If v4's advantage is really
about the DIAGNOSTIC FORM of the ask it should survive making the top rung
reachable; if the advantage evaporates, v4 was buying stability by quietly
dropping the top of the scale and does not deserve to be shipped.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "ask-elsewhere v8 shortfall, attainable top"
RATIONALE = ("Controls v4 for the dead third cut. Same diagnostic framing, but the top rung is "
             "stated as a reachable standard ('the explaining is sustained') rather than a "
             "perfection standard ('no substantial shortfall'), so level 4 is attainable and all "
             "three cuts are live. Isolates form from position.")
K = 1


def _src(rec):
    return {"synthesis": "the provided sources",
            "rhetorical_analysis": "the passage",
            "argument": "the student's own examples"}[rec["frq_type"]]


def questions(rec, segs):
    src = _src(rec)
    qs = {}
    qs.update(Q.row_a_q(rec))
    qs.update(Q.row_c_q(rec))
    qs["b_level"] = {"type": "score",
        "instructions": (
            "Read the section titled STUDENT RESPONSE (complete). Do NOT assign it a score. "
            "Answer a diagnostic question instead: what is the ONE biggest thing standing between "
            "this response and a fully supported, fully explained argument? Exactly one of the "
            "descriptions below is the principal shortfall. The last description is for responses "
            "that have no such shortfall left; it is a standard competent writers reach, not a "
            "counsel of perfection, and a response meets it even if a sentence here or there "
            "could have been explained better. Specific evidence means particular quoted words, "
            "named details, figures or concrete examples drawn from %s." % src),
        "criteria": [
            "The principal shortfall is that there is no argument to support: the response only "
            "restates its thesis, repeats what it was given, or goes off topic.",
            "The principal shortfall is specificity. The response refers to %s, but in general "
            "terms -- summary and description rather than particular details -- and it summarizes "
            "that material instead of explaining how it supports the argument." % src,
            "The principal shortfall is the through-line. Some evidence is specific and some is "
            "broad generality, and some of it is related to the argument, but the claims do not "
            "connect and progress into a line of reasoning, or the connection offered is faulty.",
            "The principal shortfall is consistency of commentary. Specific evidence from %s "
            "supports the claims of a genuine line of reasoning, but the explanation of how that "
            "evidence does the work is clearly uneven: at least one whole claim is supported by "
            "evidence that is never explained at all." % src,
            "There is no such shortfall. The response runs a line of reasoning, supports its "
            "claims with specific evidence from %s, and explains how that evidence supports the "
            "reasoning each time it is used." % src,
        ]}
    return qs
