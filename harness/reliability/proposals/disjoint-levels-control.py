"""Same-session control: byte-identical to variant_a, K=1, calibrated decode.

Exists so my variants are compared against a baseline measured in the same
session on the same corpus, not against a number from someone else's run.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "disjoint control (= variant_a, k=1)"
RATIONALE = "control: byte-identical to the shipped Row B question"
K = 1


def questions(rec, segs):
    return Q.variant_a(rec, segs)
