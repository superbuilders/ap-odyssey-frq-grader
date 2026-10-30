"""integer-compose v2 (the winner): variant_b's questions UNCHANGED, one gate moved
to where the College Board rubric actually puts it.

compose_b reaches level 1 only when NO segment explains anything, which almost
never happens, so 19 of 36 essays pile up at level 2 and the spread guard fails
at 0.755. It gets there by spending b_specific at the 2|3 boundary. But the CB
text for 1 point is "mostly general" evidence and the text for 2 points is "a mix
of specific evidence and broad generalities" -- specific-vs-general is the 1|2
distinction, not the 2|3 one. Moving that one gate down a rung is a rubric
correction, not a tuned threshold: no number changes anywhere.

Measured on a 90-read x 36-essay pool, k=1 R=10, against the A-arm decoded from
the SAME calls:

                       flip    unstable  spread  rho    acc
    A + shipped cuts   0.1333    11/36    0.980  +0.999  25/36
    compose_b as-is    0.0469     4/36    0.755! +0.907  15/36
    this              0.0500     4/36    0.952  +0.926  15/36

The flip win is real and it is not a moved threshold -- there is no threshold.
The accuracy is NOT: see the honest note at the bottom of this file.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "jev"))
sys.path.insert(0, os.path.join(HERE, ".."))
import questions as Q
from integer_compose_rules import r2_specific_low

NAME = "integer-compose v2: b_specific moved to the 1|2 rung the rubric puts it on"
RATIONALE = ("compose_b leaves level 1 unreachable and funnels 19/36 to level 2, failing spread "
             "at 0.755; the CB 1-point text is 'mostly general' evidence, so b_specific belongs at "
             "1|2. No number is tuned and no cut is moved -- the integer is still composed in code")
K = 1


def questions(rec, segs):
    return Q.variant_b(rec, segs)


compose = r2_specific_low

# HONEST NOTE, measured and not negotiable:
# the composed signal orders against gold Row B at rho +0.790, against +0.803 for
# the A-arm score on the same calls -- the decomposition keeps essentially all the
# ordering. The emitted INTEGER orders at only +0.673 and is exact on 15/36 against
# the A-arm's 25/36, under-scoring by a mean of -0.39. So the loss is entirely in
# where this hand-written ladder of 0.5 gates lands, not in what Jev knows.
# Removing the three quantile cuts did not remove the placement problem; it moved
# it somewhere harder to see and impossible to re-place without the 36-essay
# overfitting that decision.tsv 011 already reversed on the holdout.
