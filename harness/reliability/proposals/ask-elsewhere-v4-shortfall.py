"""ask-elsewhere v4: shortfall. Ask what is MISSING, not which level is met."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "ask-elsewhere v4 shortfall diagnosis"
RATIONALE = ("v1-v3 showed a single-dimension proxy loses the baseline ordering (rho 0.27-0.59). "
             "Keep the whole Row B construct but invert the ask: name the ONE biggest thing "
             "keeping the response from full marks. A deficiency diagnosis is mutually exclusive "
             "by construction -- only one thing can be the biggest problem -- where 'which level "
             "does it meet' lets two adjacent levels both be partly true. Mutual exclusivity "
             "should peak the mass and shrink per-read SD.")
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
            "descriptions below is the principal shortfall; the earlier ones describe deeper "
            "problems and the later ones shallower problems, so choose the first description that "
            "is NOT true of this response's deepest problem. Specific evidence means particular "
            "quoted words, named details, figures or concrete examples drawn from %s." % src),
        "criteria": [
            "The principal shortfall is that there is no argument to support: the response only "
            "restates its thesis, repeats what it was given, or goes off topic.",
            "The principal shortfall is specificity. The response refers to %s, but in general "
            "terms -- summary and description rather than particular details -- and it summarizes "
            "that material instead of explaining how it supports the argument." % src,
            "The principal shortfall is the through-line. Some evidence is specific and some is "
            "broad generality, and some of it is related to the argument, but the claims do not "
            "connect and progress into a line of reasoning, or the connection that is offered is "
            "faulty.",
            "The principal shortfall is consistency of commentary. Specific evidence from %s "
            "supports the claims of a genuine line of reasoning, but the explanation of how that "
            "evidence does the work is uneven: it is present for some evidence and missing, thin "
            "or merely assertive for the rest." % src,
            "There is no substantial shortfall. Specific evidence from %s supports every claim in "
            "a line of reasoning and the response consistently explains how each piece of "
            "evidence supports that reasoning." % src,
        ]}
    return qs
