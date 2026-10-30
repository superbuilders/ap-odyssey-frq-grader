"""disjoint-levels v9: v6 with the distinguishing clause moved to the FRONT.

v6 appends each level's CB decision bullets after the criterion text, so every
criterion opens with the same "EVIDENCE: ... AND COMMENTARY: ..." boilerplate
and the clause that actually separates it from its neighbour arrives last.
v9 reverses that order. Identical text, identical set of levels -- only the
position of the distinguishing material changes. If what helped in v6 was that
each level carries its own discriminator, leading with the discriminator
should help at least as much.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "disjoint-levels v9-K9 (v6, discriminator first)"
RATIONALE = "same CB text as v6, distinguishing bullets moved ahead of the shared boilerplate."
K = 9


def _bullets(note):
    return [p.strip() for p in re.split(r"\s*•\s*", note)[1:] if p.strip()]


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    qs["b_level"]["criteria"] = [
        " ".join(_bullets(c["notes"][i]) + [t]) for i, t in enumerate(c["criteria"])]
    return qs
