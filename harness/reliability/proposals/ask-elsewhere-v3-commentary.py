"""ask-elsewhere v3: commentary only. Drop the EVIDENCE half of Row B and ask
only how often the response explains HOW its evidence works."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "ask-elsewhere v3 commentary frequency"
RATIONALE = ("Each Row B level is a CONJUNCTION of an evidence condition and a commentary "
             "condition. An essay that satisfies one half and not the other puts Jev between "
             "two indices, and that is where the cuts are. Asking only about the commentary "
             "half removes the conjunction, so there is one thing to be uncertain about "
             "instead of two, and the answer should be more peaked.")
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
            "Read the section titled STUDENT RESPONSE (complete). Do NOT decide what score it "
            "would receive and do NOT judge how much evidence it has. Judge ONE thing: when the "
            "response puts a piece of evidence from %s on the page, how often does it then "
            "explain HOW that evidence supports the claim it is attached to? Restating the "
            "evidence in other words, summarizing it, or asserting that it proves the point is "
            "NOT explaining how. Explaining how means saying what about the evidence makes the "
            "claim follow." % src),
        "criteria": [
            "Never. The response either presents no evidence at all, or presents evidence and "
            "never explains how any of it supports a claim.",
            "Once, or almost never. One piece of evidence gets an explanation; the rest are "
            "dropped in and left to speak for themselves.",
            "For some of the evidence. Several pieces are explained and several are left "
            "unexplained, in roughly comparable measure.",
            "For most of the evidence. The response usually explains how a piece of evidence "
            "supports its claim, with one or two pieces left unexplained.",
            "For every piece of evidence. The response consistently explains how each piece "
            "supports the claim it is attached to.",
        ]}
    return qs
