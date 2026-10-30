"""ask-elsewhere v9: v7 with the "typical responses" notes dropped.

Across v6 (portraits alone, SD 0.0177), v7 (portraits + criteria + notes, SD
0.0204) and the baseline (criteria + notes, SD 0.0221) per-read SD tracks the
length of the rung text. v9 keeps the verbatim criterion that holds ordering
and drops the bullet lists of typical responses, which are hedged with "may"
and "tend to" and are the most equivocal text in the rung."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "ask-elsewhere v9 lean anchored archetype"
RATIONALE = ("Per-read SD tracked rung verbosity across v6/v7/baseline. Keep v7's portrait "
             "framing and its verbatim criterion anchor, drop the hedged 'typical responses' "
             "bullets. Tests whether the equivocal notes are themselves a noise source.")
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
        "criteria": ["%s  The scoring criteria for this kind, verbatim: \"%s\""
                     % (PORTRAIT[i], c["criteria"][i]) for i in range(5)]}
    return qs
