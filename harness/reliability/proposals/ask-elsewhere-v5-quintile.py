"""ask-elsewhere v5: relative placement. Ask for a rank among the population of
responses, not for a rubric level."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "ask-elsewhere v5 peer quintile"
RATIONALE = ("The flips come from a dense clump of essays Jev judges nearly identically: seven "
             "sit within 1.2 SD of the 2.0656 cut. A rubric question has no pressure to separate "
             "them -- they all 'meet level 2'. A RANKING question does: quintiles are defined "
             "relative to each other, so near-identical essays must still be placed, which should "
             "spread the clump. Ranking is also the construct the ordering guard measures, so "
             "ordering should survive where the v1-v3 single-dimension proxies did not.")
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
            "Read the section titled STUDENT RESPONSE (complete). Do NOT assign it a College "
            "Board score. Place it instead against the whole population of responses real "
            "students write to this prompt, on one dimension only: how well its argument is "
            "supported by evidence from %s and how well it explains the work that evidence does. "
            "The five bands below are equal fifths of that population, so each band holds about "
            "the same number of responses. Place this response in its band." % src),
        "criteria": [
            "Bottom fifth: its evidence and explanation are weaker than roughly four out of five "
            "responses written to this prompt.",
            "Second fifth: weaker than most responses, but stronger than the bottom fifth.",
            "Middle fifth: squarely typical -- about as well supported and explained as the "
            "median response to this prompt.",
            "Fourth fifth: better supported and better explained than most responses, without "
            "being among the strongest.",
            "Top fifth: its evidence and explanation are stronger than roughly four out of five "
            "responses written to this prompt.",
        ]}
    return qs
