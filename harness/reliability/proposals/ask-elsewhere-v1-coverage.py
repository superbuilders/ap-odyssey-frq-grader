"""ask-elsewhere v1: coverage. Do not ask which rubric level; ask how much of
the argument is carried by specific evidence, on an invented 5-point scale."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "ask-elsewhere v1 coverage"
RATIONALE = ("Row B asks Jev to pick a rubric level; the level descriptors are long "
             "conjunctions (EVIDENCE: ... AND COMMENTARY: ...) that an essay can half-satisfy, "
             "so Jev's mass smears over adjacent indices and the expectation lands mid-cluster. "
             "A single-dimension quantity question -- what FRACTION of the argument is carried "
             "by specific evidence -- is satisfiable or not, so the mass should peak and the "
             "expectation should sit nearer an integer, farther from the cuts.")
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
            "would receive. Judge ONE thing: how much of the argument the response makes is "
            "carried by SPECIFIC evidence drawn from %s, rather than by general assertion. "
            "Specific evidence means particular quoted words, named details, figures or concrete "
            "examples. General assertion means a claim stated without such support, or a vague "
            "gesture at what %s say. Choose the description that fits the response as a whole."
            % (src, src)),
        "criteria": [
            "None of the argument is carried by specific evidence from %s. The response is "
            "assertion, restatement or summary from beginning to end." % src,
            "A small part of the argument is carried by specific evidence from %s. Most claims "
            "rest on general statements." % src,
            "About half of the argument is carried by specific evidence from %s; the other half "
            "rests on broad generalities." % src,
            "Most of the argument is carried by specific evidence from %s, and the response "
            "explains how that evidence supports its claims, though a few claims are left "
            "general or unexplained." % src,
            "The whole argument is carried by specific evidence from %s, and the response "
            "explains for every piece how that evidence supports its line of reasoning." % src,
        ]}
    return qs
