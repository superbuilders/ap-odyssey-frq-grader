"""integer-compose v3 (runner-up): the holistic "is the evidence specific" noul is
replaced by K local existential nouls, and "mostly general" is decided by a
majority count in Python.

Motivated by a measured contrast in the 90-read pool, not by a hunch:

    seg_ev   (existential, local)  mean 0.732  median SD 0.0046   7/154 flip
    seg_expl (judgment,   local)   mean 0.524  median SD 0.0101   7/154 flip
    b_specific (judgment, global)  0.497 and 0.489 on the two essays that are
                                   still unstable at k=9 under v2

A single verdict over a whole multi-paragraph essay whose evidence is genuinely
mixed has 0.5 as its honest answer, so that gate is a coin no matter how many
times it is read. Asking the local question K times and counting in Python is the
same move run.py already makes for "uniformly" and "consistently".

It works on the objective and it is NOT the variant to ship: flip falls to 0.0340
at k=1, but that is one essay, which is the metric's own noise floor, and it is
paid for with ordering (+0.852 vs +0.926) and accuracy (13/36 vs 15/36).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "jev"))
sys.path.insert(0, os.path.join(HERE, ".."))
from integer_compose_rules import v1_majority

import importlib.util as _iu
_spec = _iu.spec_from_file_location("_icv1", os.path.join(HERE, "integer-compose-v1.py"))
_m = _iu.module_from_spec(_spec); _spec.loader.exec_module(_m)

NAME = "integer-compose v3: per-segment specificity, majority counted in code"
RATIONALE = ("b_specific is a global judgment that honestly reads 0.5 on mixed essays, so it is a "
             "coin; K local existential nouls plus a majority count replace the near-0.5 gate "
             "rather than averaging over it")
K = 1
questions = _m.questions
compose = v1_majority
