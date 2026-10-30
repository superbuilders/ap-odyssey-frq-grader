"""disjoint-levels v7: v6, minus the now-duplicated notes in the instructions.

v6 inlines each level's CB decision bullets into that level's criterion, which
leaves the same bullets present twice -- once inside the criteria array and
once in the instructions blob. v7 deletes the second copy. Nothing else
changes, and no new prose is written: the framing sentence and the Additional
Notes stay verbatim. If the v6 gain comes from each criterion being
self-contained, removing the redundant global copy should not hurt and may
sharpen further.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "disjoint-levels v7 (v6, notes deduplicated out of instructions)"
RATIONALE = "v6 states each level's decision rule twice; delete the global copy."
K = 1

HEAD = ("You are applying the College Board AP English Language Row B (Evidence and Commentary, "
        "0-4 points) scoring criteria to the section titled STUDENT RESPONSE (complete). Choose "
        "the level whose verbatim criteria the response meets.\n%s")


def _bullets(note):
    return [p.strip() for p in re.split(r"\s*•\s*", note)[1:] if p.strip()]


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    qs["b_level"]["criteria"] = [
        t + (" " + " ".join(_bullets(c["notes"][i])) if _bullets(c["notes"][i]) else "")
        for i, t in enumerate(c["criteria"])]
    qs["b_level"]["instructions"] = HEAD % c["additional"]
    return qs
