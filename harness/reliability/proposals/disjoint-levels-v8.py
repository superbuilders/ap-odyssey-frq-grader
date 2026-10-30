"""disjoint-levels v8: v6 PLUS the lane's exclusion clauses.

v6 (each criterion self-contained, all CB verbatim) is the current best. v8
layers the lane's actual hypothesis on top of it: one appended sentence per
level naming the condition that rules the neighbouring level out. This is the
clean test of whether explicit disjointness buys anything ONCE the criteria are
already self-contained, or whether self-containment was the whole effect.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
from rubric import cell
import importlib.util as _ilu

_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "disjoint-levels-v3.py")
_v3 = _ilu.module_from_spec(_ilu.spec_from_file_location("dl_v3", _p))
_ilu.spec_from_file_location("dl_v3", _p).loader.exec_module(_v3)

NAME = "disjoint-levels v8 (v6 self-contained + exclusion clauses)"
RATIONALE = "does explicit disjointness add anything once each criterion is self-contained?"
K = 1


def _bullets(note):
    return [p.strip() for p in re.split(r"\s*•\s*", note)[1:] if p.strip()]


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    c = cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), "B")
    ex = _v3.EXCL[rec["frq_type"]]
    qs["b_level"]["criteria"] = [
        " ".join([t] + _bullets(c["notes"][i]) + [ex[i]]) for i, t in enumerate(c["criteria"])]
    return qs
