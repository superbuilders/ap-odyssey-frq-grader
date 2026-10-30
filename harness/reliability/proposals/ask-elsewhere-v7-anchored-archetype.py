"""ask-elsewhere v7: v6's portrait framing, bound to the verbatim rubric so the
ordering comes back."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "ask-elsewhere v7 anchored archetype"
RATIONALE = ("v6 was the only variant that lowered per-read SD (0.0177 vs baseline 0.0221) at "
             "unchanged resolving power, so 'identify which kind of response this is' really "
             "does peak Jev's mass where 'which level does it meet' smears it. v6 failed "
             "ordering at 0.779 because the portraits drifted off the rubric construct. Keep "
             "the portrait framing and the exactly-one-fits instruction, but bind each portrait "
             "to the verbatim College Board criterion for that rung, so the construct is "
             "identical to baseline and only the cognitive task changes.")
K = 1


def _src(rec):
    return {"synthesis": "the provided sources",
            "rhetorical_analysis": "the passage",
            "argument": "the student's own examples"}[rec["frq_type"]]


PORTRAIT = [
 "THE EMPTY RESPONSE. It restates its thesis, repeats what it was given, or wanders off topic; "
 "nothing in it functions as support.",
 "THE SUMMARY. It does go to the material, but reports it in general terms and then moves on. "
 "Having put the material on the page it treats the point as made, so it summarizes where it "
 "should explain.",
 "THE LIST OF POINTS. It mixes genuinely specific evidence with broad generalities and does say "
 "something about how some of it bears on the argument, but its points sit side by side rather "
 "than building: one may be made well, the rest do not connect or progress.",
 "THE ARGUMENT WITH GAPS. It runs a real line of reasoning with specific evidence behind its "
 "claims and explains how some of that evidence supports the reasoning, but the explaining is "
 "not sustained: a key claim is left for the reader to join up, or some evidence sits "
 "unintegrated.",
 "THE SUSTAINED ARGUMENT. Every claim in its line of reasoning is carried by specific evidence "
 "and each time it explains how that evidence does the work. Nothing is left for the reader "
 "to supply.",
]


def questions(rec, segs):
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    qs = {}
    qs.update(Q.row_a_q(rec))
    qs.update(Q.row_c_q(rec))
    qs["b_level"] = {"type": "score",
        "instructions": (
            "Below are five portraits of kinds of student response, each followed by the "
            "College Board criteria that describe that same kind, verbatim. They are kinds, not "
            "a checklist: exactly ONE of them describes the section titled STUDENT RESPONSE "
            "(complete), and a response belongs to one kind even when it shows a trace of a "
            "neighbouring one. Do NOT total up points. Identify which kind this response is. "
            "Specific evidence means particular quoted words, named details, figures or concrete "
            "examples from %s.\n%s" % (_src(rec), c["additional"])),
        "criteria": ["%s  The scoring criteria for this kind, verbatim: \"%s\"  Typical responses "
                     "of this kind: %s" % (PORTRAIT[i], c["criteria"][i], c["notes"][i])
                     for i in range(5)]}
    return qs
