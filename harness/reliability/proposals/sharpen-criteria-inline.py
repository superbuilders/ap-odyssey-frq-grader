"""V3. Placement test: where do the level descriptions belong?

The criteria array carries the sharpened descriptions in V1. Here the array
carries only short ordinal labels and the same five sharpened properties live
inside the instructions string, numbered. If placement matters to the score
head's variance, this and V1 will differ while saying the same words.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_axis", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sharpen-criteria-axis.py"))
_axis_mod = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_axis_mod)

NAME = "sharpen-inline: same five properties, moved into instructions"
RATIONALE = ("Placement ablation. Identical wording to V1, but the level descriptions sit "
             "in the instructions string and the criteria array holds bare ordinal labels. "
             "Tells us whether the score head reads the array or the string.")
K = 1


def questions(rec, segs):
    ax = _axis_mod.axis(rec)
    body = "\n".join("%d. %s" % (i, t) for i, t in enumerate(ax))
    qs = Q.variant_a(rec, segs)
    qs["b_level"] = {
        "type": "score",
        "instructions": (
            "Assign the College Board AP English Language Row B (Evidence and Commentary) score, "
            "0 to 4, to the section titled STUDENT RESPONSE (complete). The scale measures one "
            "thing: how far the response gets from merely presenting evidence to explaining, for "
            "every piece of evidence, how it supports one line of reasoning. Each numbered "
            "description states the single property that is true of a response at that level.\n"
            + body +
            "\nChoose the number whose description is true of STUDENT RESPONSE (complete). A "
            "response whose grammatical or mechanical errors interfere with communication cannot "
            "reach 4."),
        "criteria": ["Row B score of %d." % i for i in range(5)]}
    return qs
