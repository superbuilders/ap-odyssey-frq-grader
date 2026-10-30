# The reliability loop

A search loop over Jev decode and question designs, built so that it cannot
quietly overfit the 54-essay corpus.

## Why it is shaped like this

A search over 54 essays finds whatever those 54 essays happen to contain. An
earlier threshold search scored 36/54 in-sample and 24/54 held out. So two
properties are structural here rather than left to discipline:

**A vault.** `vault.py` seals 2025's 18 essays behind a read counter on disk
(`/tmp/jev-reliability/vault/reads.jsonl`). The loop works on the 36 from
2023-24. `open_vault()` refuses past the budget and records every read with its
stated reason.

**A label-free objective.** `metric.py` measures how often the same essay gets
a different Row B level on an identical re-run. No answer key is touched, so
optimizing it cannot overfit to College Board scores.

The objective is gameable, so it is guarded. A grader that answers 3 for every
essay never flips and is worthless:

| guard | why |
|---|---|
| `spread` >= 0.80 | predictions must keep using the scale |
| `ordering` vs baseline rho >= +0.80 | Jev's ranking matches real scores at 0.90; don't destroy it |
| `commit_rate` | an abstaining arm must show what it refused on |
| reversed-rubric canary | a nonsense rubric is *as stable* as the real one. Stability is not validity. |

## Reading the numbers

**Flip rate is the metric.** It is the probability two independent runs
disagree, and it does not depend on how many runs you did: measured at
0.1321-0.1335 for R from 5 to 90.

**"n/36 unstable" means "flipped at least once" and therefore grows with R**
(9.4 at R=5, 15.0 at R=90 for the same arm). Never quote it without its R. For
a structural count that does not depend on R, use essays within two standard
errors of a cut.

## Running it

```bash
python3 -I vault.py                      # seal, or report the seal and reads spent
python3 -I measure.py A1 10              # one arm, 10 independent runs over the 36
python3 -I pool.py 90                    # 90 independent reads/essay, once (3240 calls)
python3 -I sweep.py                      # sweep k offline from the pool, no Jev calls
python3 -I try_proposal.py proposals/x.py 10
python3 -I verdict.py                    # SPENDS A VAULT READ
```

`pool.py` then `sweep.py` is the cheap path: collect reads once, partition them
into disjoint groups offline, and any k is free after that.

## What it found

`decision.tsv` has every attempt, kept or rejected. `PREREGISTERED.md` holds a
prediction written before the one vault read that has been spent.

The short version: calibration caused the instability (1 essay in 36 becomes 11
once the quantile thresholds are applied, because those cuts land where essays
are densest). Averaging k reads is the fix that survives, because reducing
noise by sqrt(k) fits nothing. Moving the cuts into gaps in the distribution
looked five times better on the 36 it was derived from and came back twice as
unstable on the sealed 18.

Averaging has a floor. At k=9, 8 of 36 essays still sit within two standard
errors of a cut; as k grows that falls to 2, and those two sit 0.0003 and
0.0011 from a threshold. They are genuinely on the line, and no number of
reads resolves them. `is_near_boundary(raw_b, k)` flags them.

Round 2 put five agent lanes on the question itself: 51 variants across
mutually exclusive level descriptions, stripped state, integer composition,
one-property-per-level, and asking a different question entirely. The best of
them cut per-read noise by about 15% (0.0187 against a 0.0220 control). At k=9
that is invisible, because averaging has already taken both to ~0.007.

The second vault read settled it. On the sealed 18 at k=9 the untouched
question is ALREADY perfectly stable, 0 of 18. The best of the 51 bought no
stability on top of that, matched accuracy at 7/18, and halved level-4 recall
from 4/7 to 2/7. There was nothing to improve.

The number that matters: the sealed 18 goes from 4 of 18 unstable at one read
to 0 of 18 at nine. Averaging is the only lever that survived a holdout, and
it survived twice.
