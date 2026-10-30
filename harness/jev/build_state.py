"""Build the flat `state` string. Reads ONLY blind fields. All counts are STATED FACTS
(Jev cannot count), computed in Python from blind fields."""
import re
from segment import segments

STIM_CAP = 11000

def build(rec):
    tier, segs = segments(rec["essay_text"])
    cs = rec.get("cited_sources") or []
    titles = rec.get("source_titles") or []
    kind = {"synthesis": "AP English Language synthesis essay (Question 1)",
            "rhetorical_analysis": "AP English Language rhetorical analysis essay (Question 2)",
            "argument": "AP English Language argument essay (Question 3)"}[rec["frq_type"]]
    P = []
    P.append("TASK TYPE\n" + kind)
    P.append("PROMPT GIVEN TO THE STUDENT\n" + (rec.get("prompt_text") or "").strip())
    stim = (rec.get("stimulus_text") or "").strip()
    if stim:
        lbl = ("PROVIDED SOURCE PACKET" if rec["frq_type"] == "synthesis"
               else "PASSAGE THE STUDENT WAS ASKED TO ANALYZE")
        P.append(lbl + "\n" + stim[:STIM_CAP])
    facts = [
        "The student response below is %d words long." % rec["word_count"],
        "The student response body has been divided, by a computer program, into %d consecutive "
        "segments labelled SEGMENT 1 through SEGMENT %d. Together they are the whole response." % (len(segs), len(segs)),
    ]
    if rec["frq_type"] == "synthesis":
        facts.append("A computer program counted the distinct provided sources the student response explicitly "
                     "cites or references. The count is %d. The cited sources are: %s."
                     % (len(cs), ", ".join(cs) if cs else "none"))
        facts.append("The provided source packet contains %d sources: %s." % (len(titles), "; ".join(titles)))
    P.append("STATED FACTS (these are true; do not recount them)\n" + "\n".join("- " + f for f in facts))
    P.append("STUDENT RESPONSE (complete)\n" + re.sub(r"[ \t]+", " ", rec["essay_text"]).strip())
    for i, s in enumerate(segs, 1):
        P.append("SEGMENT %d\n%s" % (i, s))
    return "\n\n".join(P), segs, tier
