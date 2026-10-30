"""disjoint-levels v2: FULL treatment. Disjoint criteria array AND disjoint
decision notes in the instructions, plus an explicit exactly-one-level rule.

v1 changed only the criteria array and left the verbatim CB "typical responses"
notes in the instructions. Those notes are themselves near-identical between
levels 3 and 4 (both say "Uniformly offer evidence", both say "Organize an
argument as a line of reasoning composed of multiple supporting claims"), so
v1 removed the overlap from one place and left it in another. v2 removes it
from both and states the partition rule outright.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q
import importlib.util as _ilu

_v1 = _ilu.module_from_spec(_ilu.spec_from_file_location(
    "dl_v1", os.path.join(os.path.dirname(os.path.abspath(__file__)), "disjoint-levels-v1.py")))
_ilu.spec_from_file_location(
    "dl_v1", os.path.join(os.path.dirname(os.path.abspath(__file__)), "disjoint-levels-v1.py")
).loader.exec_module(_v1)

NAME = "disjoint-levels v2 (criteria + notes + partition rule)"
RATIONALE = ("v1 left the overlapping CB 'typical responses' notes in the instructions. "
             "Remove the overlap from the notes too and state that exactly one level applies.")
K = 1

# Disjoint replacements for the CB decision notes, keyed by the distinguishing test.
NOTES = [
 "The response offers no evidence of its own, or only evidence irrelevant to the prompt. It is "
 "opinion, restatement, or repetition of material it was handed.",

 "Evidence is present but un-worked. The response reports or summarizes what its evidence says "
 "and never states what that evidence does for its argument.",

 "The response does interpret some of its evidence, but its claims do not build on one another. "
 "It may make one point well while leaving other claims unsupported, or the progression it "
 "asserts between claims does not hold.",

 "The response builds a working chain of claims, each resting on specific evidence, and explains "
 "part of that evidence. Its commentary demonstrably skips something: at least one piece of "
 "evidence, or at least one claim, is left standing without explanation.",

 "The response builds a working chain of claims, each resting on specific evidence, and skips "
 "nothing: every piece of evidence it presents is accompanied by commentary saying how that "
 "piece supports the chain.",
]

HEAD = ("You are assigning the College Board AP English Language Row B (Evidence and Commentary, "
        "0-4 points) level to the section titled STUDENT RESPONSE (complete). The five levels below "
        "are mutually exclusive: each one states a condition that the other four rule out, so "
        "exactly one of them describes this response. Find the single level whose condition holds "
        "and do not blend it with its neighbours. Test to apply at each level: %s\n%s")


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["criteria"] = list(_v1.BY_TYPE[rec["frq_type"]])
    tests = " | ".join("%d -- %s" % (i, n) for i, n in enumerate(NOTES))
    extra = ("Writing whose grammatical or mechanical errors interfere with communication cannot "
             "reach level 4.")
    qs["b_level"]["instructions"] = HEAD % (tests, extra)
    return qs
