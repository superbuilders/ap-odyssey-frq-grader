"""trim-state CONTROL. Patches the state builder with a byte-identical
reimplementation, to prove the monkey-patch route is faithful before any
trim is attributed to a trim."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "jev"))
import questions as Q
import measure
from segment import segments

NAME = "trim-state-control (state unchanged)"
RATIONALE = "control: builder patched but output byte-identical to build_state.build"
K = 9

STIM_CAP = 11000


def _build(rec, stim_cap=STIM_CAP, keep_segments=True, keep_facts=True, keep_prompt=True):
    tier, segs = segments(rec["essay_text"])
    cs = rec.get("cited_sources") or []
    titles = rec.get("source_titles") or []
    kind = {"synthesis": "AP English Language synthesis essay (Question 1)",
            "rhetorical_analysis": "AP English Language rhetorical analysis essay (Question 2)",
            "argument": "AP English Language argument essay (Question 3)"}[rec["frq_type"]]
    P = ["TASK TYPE\n" + kind]
    if keep_prompt:
        P.append("PROMPT GIVEN TO THE STUDENT\n" + (rec.get("prompt_text") or "").strip())
    stim = (rec.get("stimulus_text") or "").strip()
    if stim and stim_cap > 0:
        lbl = ("PROVIDED SOURCE PACKET" if rec["frq_type"] == "synthesis"
               else "PASSAGE THE STUDENT WAS ASKED TO ANALYZE")
        P.append(lbl + "\n" + stim[:stim_cap])
    if keep_facts:
        facts = [
            "The student response below is %d words long." % rec["word_count"],
            "The student response body has been divided, by a computer program, into %d consecutive "
            "segments labelled SEGMENT 1 through SEGMENT %d. Together they are the whole response."
            % (len(segs), len(segs)),
        ]
        if rec["frq_type"] == "synthesis":
            facts.append("A computer program counted the distinct provided sources the student response explicitly "
                         "cites or references. The count is %d. The cited sources are: %s."
                         % (len(cs), ", ".join(cs) if cs else "none"))
            facts.append("The provided source packet contains %d sources: %s." % (len(titles), "; ".join(titles)))
        P.append("STATED FACTS (these are true; do not recount them)\n" + "\n".join("- " + f for f in facts))
    P.append("STUDENT RESPONSE (complete)\n" + re.sub(r"[ \t]+", " ", rec["essay_text"]).strip())
    if keep_segments:
        for i, s in enumerate(segs, 1):
            P.append("SEGMENT %d\n%s" % (i, s))
    return "\n\n".join(P), segs, tier


measure.build = _build


def questions(rec, segs):
    return Q.variant_a(rec, segs)
