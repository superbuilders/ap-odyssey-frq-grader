"""disjoint-levels v5: disjoin the 2|3 pair ONLY, and do it in CB's own words.

Two corrections to the lane's premise, both measured:

1. The 3|4 pair is not where the variance is. All three shipped cuts (2.0656,
   2.3061, 2.8359) lie between criteria index 2 and index 3, and every unstable
   essay in the corpus has a raw mean in [2.0, 2.9]. Every flip is a two-way
   softmax contest between criteria 2 and 3. The byte-identical 3|4 text the
   lane points at is never in play.

2. Paraphrasing raises variance. v1/v2/v3/v4 all RAISED per-read SD above the
   verbatim control's 0.0220, monotonically in how much text they replaced.

So v5 adds no new prose at all. It appends to criteria 2 and 3 the College
Board decision-note bullets that already distinguish them, verbatim:
"Consist of a mix of specific evidence and broad generalities" against
"Uniformly offer evidence to support claims", and "Do not explain the
connections or progression between the student's claims" against "Organize an
argument as a line of reasoning composed of multiple supporting claims".
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "disjoint-levels v5 (2|3 disjoined, CB verbatim bullets)"
RATIONALE = ("every flip is a criteria-2-vs-3 softmax contest, and paraphrase raises SD. "
             "Sharpen only that pair, using only CB's own decision-note wording.")
K = 1

PICK = {2: ("mix of specific evidence", "connections or progression"),
        3: ("Uniformly offer evidence", "Organize an argument")}


def _bullets(note):
    parts = re.split(r"\s*•\s*", note)
    return [p.strip() for p in parts[1:] if p.strip()]


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    crit = list(c["criteria"])
    for i, keys in PICK.items():
        chosen = [b for b in _bullets(c["notes"][i]) if any(k in b for k in keys)]
        if chosen:
            crit[i] = crit[i] + " " + " ".join(chosen)
    qs["b_level"]["criteria"] = crit
    return qs
