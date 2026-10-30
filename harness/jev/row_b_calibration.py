"""Row B (Evidence & Commentary) calibration for the Jev AP Lang grader.

Jev's continuous `raw_b` signal orders essays well but is compressed into
[1.24, 3.38]; its own argmax decode never emits a 4, so it scored 24/54 on the
54-essay gold corpus with 0/16 recall on College Board level 4.

This module is the post-hoc monotone rescaling that fixes the range problem.
The three thresholds are quantile / marginal-matching cut points: raw_b's rank
is mapped onto the gold Row B level marginal ({1:8, 2:13, 3:17, 4:16}) over the
54-essay corpus (2023/2024/2025, 18 per year). Fitted offline, hardcoded here.
No fitting happens at runtime. There are no free parameters beyond that
marginal -- unlike a cut-point grid search, nothing here is tuned to maximise
accuracy on the corpus.

Row B exact match, n=54 (raw counts, not rates):

    shipped argmax, no calibration      24/54   CB4 recall  0/16
    this mapping, leave-one-out         27/54   CB4 recall 10/16
    this mapping, year-holdout          31/54   CB4 recall 12/16
    (same-data fit, NOT a claim)        27/54   CB4 recall 10/16

Quote the year-holdout: fit on two exam years, score the third, rotated over
all three. Per fold it is 11/18, 11/18, 9/18. Note it is HIGHER than the
leave-one-out 27/54; with only three folds and n=54 the standard error is about
+/-3.7 essays, so the defensible claim is "about 28-30 of 54", not 31. Do not
quote the optimal-cut-point oracle of 35/54 that a grid search reaches on this
same corpus -- it does not survive either holdout.

The gain over the shipped 24 is real but narrow, and it is not free: it is
bought entirely at the top of the scale. Per gold level, before -> after, scored
with the FROZEN thresholds below rather than refit per fold (i.e. what this
module actually does): CB1 1/8 -> 5/8, CB2 12/13 -> 5/13, CB3 11/17 -> 7/17,
CB4 0/16 -> 10/16. Net +3 essays, not +7. Level 2 falls from 92% to 38%.
Telling a 2 from a 3 is the most common real distinction in AP Lang scoring and
at that job this mapping is a REGRESSION -- if you need the middle of the scale,
call Jev's argmax directly and do not use this module.

Deployment estimate: these frozen thresholds score 29-30/54 when fed raw_b from
a fresh Jev run rather than the archived one they were fitted on. That, not the
31, is what production delivers.

Fixing this at the source does not work and was tried: four prompt-side variants
(worked anchors, stated marginal, a cumulative yes/no ladder, pairwise against an
anchor) moved the top of the raw range by at most 0.03, and a byte-identical
control re-run reproduced the ceiling to within 0.01. The compression is a
property of Jev's calibrated heads, not an information deficit.

STABILITY, MEASURED RATHER THAN ASSUMED (harness/reliability):

Earlier notes put Jev's run-to-run drift at 0.18 and inferred from that that 37
of 54 essays were coin flips. Both figures were wrong. Ten independent runs over
36 essays put the per-essay standard deviation at 0.0237 (0.0272 on a sealed
2025 holdout), roughly 7.6x smaller than the assumed 0.18.

What IS true is that these thresholds cost stability. Measured end to end, same
essay, repeated identical runs:

    argmax round()      1 of 36 essays unstable    0 of 18 sealed
    these thresholds   11 of 36 essays unstable    4 of 18 sealed

Quantile matching places each cut where it reproduces the gold marginal, which
is by construction where essays are densest. The 1|2 cut has nine of the 36
working essays within two standard deviations of it. So calibration did not
inherit an instability from Jev; it introduced one.

Averaging k independent reads of raw_b before mapping is the fix that holds up:
flip rate falls 0.146 -> 0.070 at k=9 on the working set and to zero on the
sealed set, with accuracy unchanged. It reduces variance by sqrt(k) and fits
nothing to the corpus, so it carries across populations.

Moving the cuts into the gaps between essays does NOT hold up, and the attempt
is recorded because it looked convincing: it was five times more stable on the
36 essays it was derived from and twice as UNSTABLE on the sealed 18. Gaps in a
36-point sample are mostly sampling noise.

If per-essay stability matters, average several reads, or use the argmax decode
and give up the top of the scale. Do not re-place these cuts on a sample this
small.
"""

THRESHOLDS = (2.0656, 2.3061, 2.8359)

# Per-essay standard deviation of raw_b across independent identical calls,
# measured over 10 runs x 36 essays (harness/reliability). A previous value of
# 0.18 here was an assumption, not a measurement, and was 7.6x too large.
DRIFT = 0.0237


def calibrate_row_b(raw_b: float) -> int:
    """Map Jev's continuous raw_b onto a College Board Row B level in 0-4."""
    level = 1
    for cut in THRESHOLDS:
        if raw_b > cut:
            level += 1
    return 0 if level < 0 else (4 if level > 4 else level)


def is_near_boundary(raw_b: float, k: int = 1, drift: float = None) -> bool:
    """True when raw_b is within two standard errors of a cut point.

    `k` is how many independent reads were averaged to produce raw_b. The
    standard error of that mean is DRIFT / sqrt(k), so the warning band shrinks
    as the caller pays for more reads. A fixed band would over-warn at k=9 and
    under-warn at k=1.

    Callers that surface a single essay's Row B score should treat a flagged
    essay as low-confidence rather than reporting a definite level. Two essays
    in the 36-essay working set stay flagged at any k, because their signal
    sits within 0.001 of a cut; those are genuinely on the line and no amount
    of reading resolves them.
    """
    if drift is None:
        drift = 2.0 * DRIFT / (k ** 0.5)
    return min(abs(raw_b - cut) for cut in THRESHOLDS) < drift
