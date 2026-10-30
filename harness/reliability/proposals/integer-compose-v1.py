"""integer-compose v1: the holistic "is the evidence specific" judgment becomes a
per-segment existential, counted in Python.

MEASURED, not assumed. In a 90-read x 36-essay pool of variant_b:

    existential per-segment gates   seg_ev     mean 0.732  median SD 0.0046
    judgment gates                  seg_expl   mean 0.524  median SD 0.0101
                                    b_specific mean 0.679, but 0.497 and 0.489
                                    on the two essays that stay unstable at k=9

b_specific asks for one verdict over a whole multi-paragraph essay whose evidence
is genuinely mixed, so for a mixed essay the honest answer IS 0.5 and the gate is
a coin. seg_ev shows Jev is decisive when the question is existential and local.
So ask the local question K times and let Python decide "mostly general", which is
the rubric's own word for a majority.

The harness in try_proposal.py can only decode ONE score question through the
shipped quantile cuts, which is the construction this lane exists to avoid, so
b_level is carried here to keep this file valid under that harness and to give a
paired A-arm read from the same call. The integer is produced by
integer_compose_rules.v1_* and measured with integer_compose_runner.py.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "integer-compose v1: per-segment specificity, counted in code"
RATIONALE = ("holistic b_specific sits at 0.497/0.489 on the essays that flip; replacing it "
             "with K local existential nouls and a majority count in Python removes the "
             "near-0.5 gate instead of averaging over it")
K = 1


def questions(rec, segs):
    qs = Q.variant_b(rec, segs)
    syn = rec["frq_type"] == "synthesis"
    rhet = rec["frq_type"] == "rhetorical_analysis"
    src = "the provided sources" if syn else ("the passage" if rhet else "the student's own examples")
    for i in range(1, len(segs) + 1):
        qs["seg%d_spec" % i] = {"type": "noul",
            "instructions": ("College Board's Row B 1-point decision rule describes evidence that is "
              "\"mostly general\"; the 3-point and 4-point rules require \"specific\" evidence. Read ONLY "
              "the section titled SEGMENT %d. Ignore every other section. This is a question about what "
              "is physically on the page in SEGMENT %d, not about how good the argument is." % (i, i)),
            "criteria": {"true": "SEGMENT %d contains at least one of: a phrase quoted from %s, a named "
                                 "person, place, title or date, a number or statistic, or one concrete "
                                 "particular example." % (i, src),
                         "false": "SEGMENT %d refers to %s only in general terms, or presents no evidence "
                                  "at all." % (i, src)}}
    qs.update(Q.variant_a(rec, segs))   # carries b_level for the paired A read
    return qs
