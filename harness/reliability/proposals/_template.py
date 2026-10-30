"""Copy this. Keep the rationale honest: name the mechanism, not a hope."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "template, does nothing"
RATIONALE = "control: byte-identical to the baseline question"
K = 9


def questions(rec, segs):
    return Q.variant_a(rec, segs)
