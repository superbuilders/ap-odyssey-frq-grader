# AP Lang FRQ grader — feasibility study

Can we automatically grade AP English Language free-response essays well enough to show a
student? This repo is the answer to that question, plus the harness that produced it and UI
mockups for what the feature would look like.

**There is no working application here yet.** What exists is a measured result, a reproducible
test harness, and clickable mockups. The build decision comes after reading the result.

---

## The finding

Four graders, 54 essays — every AP Lang sample response College Board has published with an
official score (2023, 2024, 2025). Each grader saw the essay, the prompt, the source material
and the verbatim rubric. None saw the score.

| Grader | Evidence row exact | Ranking accuracy | Cost/essay | Time/essay |
|---|---|---|---|---|
| BaconWrite AP panel (Opus, 5 calls) | 33/54 · 61% | 83% | $0.223 | 15.1 s |
| Claude Sonnet (our control, 1 call) | 25/54 · 46% | 82% | $0.030 | 14.3 s |
| Jev (TypeSafe System One) | 24/54 · 44% | 82% | ~$0.0005 | 0.84 s |
| **Reads only the filename** | **39/54 · 72%** | **100%** | $0 | 0 s |

Read `findings/index.html` for the full writeup. The short version:

- **Nothing here is a grade of record.** The best grader got all three rubric rows right on
  24 of 54 essays.
- **All of them rank equally well.** 82–83% at telling a stronger essay from a weaker one, with
  every pairwise difference inside noise. That is the capability a coach needs, and the
  half-second classifier delivers it as well as the fifteen-second Opus panel.
- **The test set is compromised.** College Board labels its three samples per question A, B and
  C, and A is always the best — in all 18 question sets. A script that reads nothing but that
  letter beats every real grader. No grader saw the letter; they just cannot beat a cheat sheet.
  Absolute-accuracy numbers from this corpus measure its design as much as anyone's skill.
- **Jev never awarded a 4** — 0 of the 16 essays that earned one, because its internal signal
  topped out at 3.38 and the decode rounds. We fixed it (see below). The fix is worth about
  +3 essays net, not the +7 the headline suggests.
- **No training contamination.** Zero shared eight-word runs across 30 continuation attempts,
  zero self-reported recall across 108 asks, below-chance accuracy at naming an essay's year.

### Two corrections worth carrying forward

A fourth arm — BaconWrite's criteria-mode production grader — scored 8/54 and has been dropped.
That was **our adapter's fault, not theirs**: `harness/baconwrite/run.ts` modelled the whole 0–4
evidence row as one pass/fail criterion, so it could only ever emit 0 or 4. Their system does
proportional partial credit across weighted criteria; we never gave it more than one criterion
to weigh. Their AP panel was our best performer.

Jev is **18×** faster than that panel, not the 64× quoted in earlier notes — that figure came
from a different task and was repeated before being measured here.

---

## The calibration fix, and what it cost

Jev's level-4 blindness was a decode defect: the signal lived in `[1.24, 3.38]`, so rounding
could never produce a 4, and 16 of 54 essays were wrong before the grader read a word.

**Asking better does not work.** Four source-side variants on all 54 essays, live — worked
anchors with their official scores, a flat statement that 4s are common, a four-rung yes/no
ladder composed in code, and a comparison against a known level-3 anchor. None opened the
range by more than 0.03. A byte-identical control re-run reproduced the ceiling to within
**0.01**, so it is structural, not noise. The yes/no head declines the top of the scale exactly
as the score head does: `P(at least a 4)` never exceeds 0.670 anywhere in the corpus.

**So the fix is post-hoc.** Quantile matching — rank the signal, cut it so the spread of grades
matches the real spread. Three frozen thresholds, zero tuned parameters.

| | Row B exact | Level-4 recall |
|---|---|---|
| Jev as shipped | 24/54 | 0/16 |
| Calibrated, year-holdout | 31/54 | 12/16 |
| **Calibrated, frozen thresholds on a fresh run** | **29–30/54** | **10/16** |

Three caveats that matter more than the headline:

1. **The middle collapses.** Level 2 goes 12/13 → 5/13, level 3 goes 11/17 → 7/17. Net +3, not
   +7. Telling a 2 from a 3 is the most common real distinction in AP Lang scoring, and at that
   job this is a regression. If you need the middle, keep the uncalibrated head.
2. **Run-to-run noise exceeds the gain.** The same mapping scores 27 on the archived signal and
   32 on a fresh re-run of the identical request. Average three reads before mapping.
3. **This is a better ruler, not a better reader.** The mapping is monotone — Jev ranks all 54
   essays in exactly the order it did before. Only the boundaries moved.

It also voids the one safety property we liked: uncalibrated Jev errs low, calibrated Jev runs
slightly hot. Ship the raw head for coaching one student; use the thresholds for batch stats.

On the comparison everyone asks about: we could not run McNemar against the Opus panel (only its
33/54 summary survives, not per-essay calls), so we bounded it. On 54 essays you need a gap near
**nine** before any arrangement reaches significance. 24, 31 and 33 are three numbers this
corpus cannot tell apart — and the panel was never significantly ahead of uncalibrated Jev
either, at p = 0.136.

---

## Layout

```
findings/index.html        the writeup, standalone page
mockups/                   clickable UI directions
  feedback-shape.html        three ways feedback could reach a student
  feedback-combined.html     the chosen direction — marked-up essay, rubric one click away
harness/
  corpus/                  fetch and parse College Board's published samples
  jev/                     the Jev arm — question sets, state assembly, scoring
  baconwrite/              adapter for BaconWrite's graders (see the correction above)
  contamination/           memorization and id-leak probes
results/                   per-essay predictions, scores only
```

## Reproducing it

Requires `TFY_API_KEY` in the environment (the TrueFoundry gateway fronts both Jev and Claude)
and `pdftotext` for PDF extraction.

```bash
python3 -I harness/corpus/build.py      # fetch + parse; writes corpus/ (gitignored)
python3 -I harness/jev/run.py           # grade through Jev
python3 -I harness/jev/score.py         # agreement against official scores
```

Jev speaks a decisions protocol, not chat — `POST /v1/systemone` with a `state` and a map of
typed questions, returning calibrated probabilities and never prose. `harness/jev/jev.py` is the
whole client.

## What is not in this repo, and why

Essay text, the verbatim scoring guidelines, and the exam PDFs are College Board copyright.
Their published grant covers limited reproduction by AP teachers for face-to-face teaching, not
electronic redistribution — and git history is permanent, so this is not a mistake that can be
undone later. The harness fetches all of it on demand into a gitignored `corpus/`.

The one deliberate exception is roughly six rubric criteria quoted on-screen in the mockups,
attributed there to the scoring guidelines. Showing what the rubric looks like inside the
product is the point of a mockup.

## If we build it

Jev for the formative student-facing coach, **uncalibrated**: it ranks as well as anything
tested, returns in under a second, costs essentially nothing, and errs low rather than high — a
coach that under-rates never tells a student a weak draft is excellent. Apply the calibrated
thresholds only where you need the top of the scale across a batch. Not as a grade of record;
nothing tested is close to that, including the expensive options.

Before trusting any accuracy number, build the 2026 corpus with the sample letters scrambled.
College Board has published the 2026 prompts and rubric but not yet its sample responses. That
set would be post-cutoff for every model in the comparison and free of the filename leak, which
makes it the only clean measurement available.
