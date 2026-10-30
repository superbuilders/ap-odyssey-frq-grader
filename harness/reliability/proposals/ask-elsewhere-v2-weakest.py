"""ask-elsewhere v2: weakest link. Ask about the single worst body segment,
not the whole essay."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "ask-elsewhere v2 weakest link"
RATIONALE = ("A whole-essay judgement is an average over heterogeneous paragraphs, and an "
             "average of mixed things is exactly what lands between two rubric levels. A MIN "
             "over paragraphs is pinned to one concrete paragraph, which is a far more "
             "determinate object, so repeated reads should agree more often.")
K = 1


def _src(rec):
    return {"synthesis": "the provided sources",
            "rhetorical_analysis": "the passage",
            "argument": "the student's own examples"}[rec["frq_type"]]


def questions(rec, segs):
    src, n = _src(rec), len(segs)
    qs = {}
    qs.update(Q.row_a_q(rec))
    qs.update(Q.row_c_q(rec))
    qs["b_level"] = {"type": "score",
        "instructions": (
            "The student response has been divided into %d consecutive sections labelled SEGMENT 1 "
            "through SEGMENT %d. Among the segments that are meant to advance the argument "
            "(ignore an opening segment that only states the thesis and a closing segment that "
            "only restates it), find the ONE that does the LEAST to advance the argument -- the "
            "weakest link in the chain. Do NOT score the response as a whole and do NOT decide "
            "what grade it would receive. Describe only that single weakest segment. Specific "
            "evidence means particular quoted words, named details, figures or concrete examples "
            "from %s." % (n, n, src)),
        "criteria": [
            "The weakest such segment contributes nothing to the argument: it is off topic, "
            "incoherent, or pure restatement of the thesis.",
            "The weakest such segment asserts a claim but offers no evidence from %s for it." % src,
            "The weakest such segment offers evidence from %s but only summarizes or paraphrases "
            "it, without explaining how it supports the claim." % src,
            "The weakest such segment offers specific evidence from %s and gives some explanation "
            "of how it supports the claim, though the explanation is thin or partial." % src,
            "Even the weakest such segment offers specific evidence from %s and fully explains how "
            "that evidence supports the claim it is attached to." % src,
        ]}
    return qs
