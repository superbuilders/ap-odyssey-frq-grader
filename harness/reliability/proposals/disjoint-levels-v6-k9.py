"""disjoint-levels v6: every level carries its own full CB decision rule inline.

v5 sharpens one pair. v6 is the broad version of the same in-distribution move:
append each level's complete verbatim "typical responses that earn N points"
bullets to that level's criterion, so every criterion is self-contained and
the head never has to hold the criteria array and the decision notes apart.

Still zero new prose -- only CB text, relocated.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "disjoint-levels v6-K9 (all levels self-contained, CB verbatim)"
RATIONALE = ("same in-distribution move as v5 but applied to every level: each criterion "
             "carries its own decision rule so none has to be read against the others.")
K = 9


def _bullets(note):
    return [p.strip() for p in re.split(r"\s*•\s*", note)[1:] if p.strip()]


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    crit = []
    for i, t in enumerate(c["criteria"]):
        bs = _bullets(c["notes"][i])
        crit.append(t + (" " + " ".join(bs) if bs else ""))
    qs["b_level"]["criteria"] = crit
    return qs
