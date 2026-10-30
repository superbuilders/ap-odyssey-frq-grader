"""ask-elsewhere v6: archetype. Ask which kind of essay this IS, not which
level it earns. Same five rungs, forced mutual exclusivity."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "ask-elsewhere v6 archetype match"
RATIONALE = ("Each Row B level is a conjunction (EVIDENCE: ... AND COMMENTARY: ...), and an "
             "essay that satisfies one conjunct and not the other is partly true of two adjacent "
             "levels at once -- that smear is the per-read noise. Recast the same five rungs as "
             "five whole-essay portraits and state that exactly one fits, so the conjunction "
             "becomes a single identification. Same construct and same ordering as the rubric, "
             "different cognitive task.")
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
            "Below are five portraits of kinds of student response. They are written so that "
            "exactly ONE of them describes the section titled STUDENT RESPONSE (complete) -- they "
            "are kinds, not a checklist, and a response belongs to one kind even when it shows a "
            "trace of a neighbouring one. Do NOT assign a score. Identify which kind this "
            "response is. Specific evidence means particular quoted words, named details, figures "
            "or concrete examples from %s." % src),
        "criteria": [
            "THE EMPTY RESPONSE. It restates its thesis, repeats what it was given, or wanders "
            "off topic. Nothing in it functions as support.",
            "THE SUMMARY. It does go to %s, but it reports what is there in general terms and "
            "then moves on. Having put the material on the page it treats the point as made, so "
            "it summarizes where it should explain." % src,
            "THE LIST OF POINTS. It mixes some genuinely specific evidence with broad "
            "generalities, and it does say something about how some of that material bears on its "
            "argument. But its points sit side by side rather than building: one may be made "
            "well, and the rest do not connect or progress.",
            "THE ARGUMENT WITH GAPS. It runs a real line of reasoning, with specific evidence "
            "from %s behind its claims, and it explains how some of that evidence supports the "
            "reasoning. The explaining is not sustained: at least one key claim is left for the "
            "reader to join up, or some evidence is dropped in unintegrated." % src,
            "THE SUSTAINED ARGUMENT. Every claim in its line of reasoning is carried by specific "
            "evidence from %s, and each time it explains how that evidence does the work. "
            "Nothing is left for the reader to supply." % src,
        ]}
    return qs
