# Pre-registration 2, written before vault read #2

Candidate: disjoint-levels v9. Each Row B level's criterion string carries that
level's own verbatim College Board decision bullets, discriminating bullets
first. Zero new prose; CB text relocated. Decoded with the SHIPPED quantile
thresholds, unchanged, k=9 averaged reads.

Picked from 51 measured variants across 5 agent lanes. Best guarded flip rate
with accuracy still within noise of control on the 36.

On the 36 working essays, k=9:
  control  flip 0.0796  SD 0.0076  acc 25/36  CB4 7/9
  v9       flip 0.0099  SD 0.0069  acc 22/36  CB4 5/9

Why this might not transfer, stated now: at k=9 both have the same per-read
noise, so v9's 8x lower flip rate is NOT noise reduction. It is the signal
sitting further from the cuts. That is the mechanism that reversed on this same
holdout in round 1 (gap-aware: 5x better on the 36, 2x worse on the 18). The
difference is that gap-aware FITTED cut positions to the 36 while v9 changes a
fixed question and fits nothing, so the relocation may be a property of the
question rather than of these essays.

Reads spent at time of writing: 1 of 3.

PREDICTIONS for the sealed 18 at k=9, stated before looking:

1. v9 flip rate < control flip rate on the sealed 18. If v9's relocation is a
   property of the question it transfers; if it was an accident of the 36 it
   reverses, as gap-aware did.
2. v9 accuracy within 3 essays of control.
3. v9 CB4 recall within 2 of control.

Failure of 1 means question-side relocation is as corpus-specific as
threshold-side relocation, and averaging remains the only transferable lever.

One read. No iterating afterwards.
