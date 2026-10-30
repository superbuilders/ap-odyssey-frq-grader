"""ask-elsewhere v7: ask which KIND of response this is, not which level it meets.

Five whole-essay portraits, each bound to the verbatim College Board criterion
and notes for that rung, with the instruction that exactly one kind fits.

MEASURED MECHANISM, which is NOT the one this started from. It does not make
Jev quieter: at k=9 the per-read SD is 0.0069 against the baseline's 0.0077,
and at k=1 it is 0.0204 against 0.0221, an 8% difference that cannot explain an
81% drop in flips. What it does is break up a DEGENERACY. The baseline Row B
question returns near-identical numbers for a block of essays -- nine of the 36
land inside a 0.05-wide band at 2.04-2.09 -- and the 2.0656 quantile cut is
fitted to the gold marginal, which puts it inside that block by construction.
Those nine essays are coin flips no amount of averaging fixes. Asking for a
kind rather than a level spreads the same nine essays over 0.18, leaving three
within +-0.05 of that cut instead of nine, so the cut lands between essays.

CAVEAT, stated because the harness has been burned by exactly this shape
before (decision.tsv 011): the de-clustering was measured on the same 36 essays
the cuts were fitted to. Unlike the gap-aware thresholds of 011, nothing here
was fitted -- the rungs are the verbatim rubric and the cuts were never looked
at while writing them -- but selection over nine variants on 36 essays is still
selection. The transfer claim is untested; the vault was not opened.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "ask-elsewhere v7 anchored archetype"
RATIONALE = ("Do not ask which rubric level the response meets; ask which of five kinds of "
             "response it IS, each kind bound to the verbatim criterion for that rung. "
             "Measured: this does not lower Jev's noise (k=9 SD 0.0069 vs 0.0077 baseline). "
             "It de-clusters. The baseline question piles nine of 36 essays into a 0.05-wide "
             "band straddling the 2.0656 cut, which quantile-matching put there by "
             "construction; the portrait question spreads those nine over 0.18 and leaves "
             "three near the cut. k=9 flip 0.0130/0.0099 over two runs vs 0.0698 baseline, "
             "1/36 unstable vs 7/36, spread 0.954, ordering rho +0.952.")
K = 9


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
