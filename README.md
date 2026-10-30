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
- **Jev never awards a 4** — 0 of the 16 essays that earned one. Its underlying score separates
  those 16 from the rest cleanly, so this is a scale that needs rebasing, not a model that
  cannot read.
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

Jev for the formative student-facing coach: it ranks as well as anything tested, returns in
under a second, costs essentially nothing, and errs low rather than high — a coach that
under-rates never tells a student a weak draft is excellent. Not as a grade of record;
nothing tested is close to that, including the expensive options.

Before trusting any accuracy number, build the 2026 corpus with the sample letters scrambled.
College Board has published the 2026 prompts and rubric but not yet its sample responses. That
set would be post-cutoff for every model in the comparison and free of the filename leak, which
makes it the only clean measurement available.
