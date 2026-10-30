"""Fresh k=1 control. Byte-identical to variant_a. Establishes today's baseline."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "control: variant_a verbatim, k=1"
RATIONALE = "control. Any movement here is the metric's own noise floor, not a mechanism."
K = 1


def questions(rec, segs):
    return Q.variant_a(rec, segs)
