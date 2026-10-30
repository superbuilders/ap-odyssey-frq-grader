"""disjoint-levels v3: MINIMAL EDIT. Keep every CB criterion byte-for-byte and
append exactly one exclusion sentence to each.

v1 rewrote the criteria wholesale, which risks the ordering guard and makes it
impossible to tell whether the gain came from disjointness or from some other
change in the prose. v3 is the surgical version: the verbatim rubric is intact
and the ONLY addition is the sentence that rules the neighbouring level out.
If disjointness is the active ingredient, this should capture most of v1's
gain at a fraction of the perturbation.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell

NAME = "disjoint-levels v3 (verbatim CB + one exclusion clause each)"
RATIONALE = ("isolate disjointness: keep the CB criteria byte-identical and add only the "
             "sentence that rules out the adjacent level.")
K = 1

EXCL = {
 "synthesis": [
   "This level does not apply if the response references two or more of the provided sources.",
   "This level does not apply if the response explains how any piece of its evidence supports its argument.",
   "This level does not apply if the response establishes a line of reasoning that is not faulty.",
   "This level does not apply if every piece of evidence the response presents is explained; it requires that at least one piece is left unexplained.",
   "This level does not apply if any piece of evidence the response presents is left unexplained.",
 ],
 "rhetorical_analysis": [
   "This level does not apply if the response presents any evidence of its own from the passage.",
   "This level does not apply if the response explains how any piece of its evidence supports its argument.",
   "This level does not apply if the response establishes a line of reasoning that is not faulty.",
   "This level does not apply if the response both leaves no evidence unexplained and explains two or more distinct rhetorical choices.",
   "This level does not apply if any piece of evidence is left unexplained, or if only one rhetorical choice is explained.",
 ],
 "argument": [
   "This level does not apply if the response presents any evidence of its own.",
   "This level does not apply if the response explains how any piece of its evidence supports its argument.",
   "This level does not apply if the response establishes a line of reasoning that is not faulty.",
   "This level does not apply if every piece of evidence the response presents is explained; it requires that at least one piece is left unexplained.",
   "This level does not apply if any piece of evidence the response presents is left unexplained.",
 ],
}


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    ex = EXCL[rec["frq_type"]]
    qs["b_level"]["criteria"] = ["%s %s" % (t, e) for t, e in zip(c["criteria"], ex)]
    return qs
