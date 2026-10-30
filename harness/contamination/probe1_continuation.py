#!/usr/bin/env python3
"""PROBE 1 - verbatim continuation. Reads ONLY blind.jsonl + my own control essays.
No label file is opened anywhere in this script."""
import json, os, re, sys, time
sys.path.insert(0, "/tmp/contam-probe/scripts")
import tfy
from concurrent.futures import ThreadPoolExecutor

blind = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/blind.jsonl"))}
meta  = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/meta.jsonl"))}

PICK = ["2023-s1-q1-A","2023-s1-q2-B","2023-s2-q3-A","2023-s2-q1-C",
        "2024-s1-q1-A","2024-s1-q2-B","2024-s2-q3-A","2024-s2-q1-C",
        "2025-s1-q1-A","2025-s1-q2-B","2025-s2-q3-A","2025-s2-q1-C"]
items = []
for eid in PICK:
    r = blind[eid]
    items.append({"id": eid, "kind": "real", "year": meta[eid]["year"],
                  "frq": r["frq_type"], "text": r["essay_text"], "prompt": r["prompt_text"]})
ctrl_prompt = {"synthesis": blind["2025-s1-q1-A"]["prompt_text"],
               "rhetorical": blind["2025-s1-q2-A"]["prompt_text"],
               "argument": blind["2025-s1-q3-A"]["prompt_text"]}
for nm in ("synthesis", "rhetorical", "argument"):
    t = open("/tmp/contam-probe/controls/CTRL-%s.txt" % nm).read().strip()
    items.append({"id": "CTRL-" + nm, "kind": "control", "year": "control",
                  "frq": nm, "text": t, "prompt": ctrl_prompt[nm]})

def run(job):
    it, model = job
    words = it["text"].split()
    wcut = max(1, int(len(words) * 0.40))
    head, tail = " ".join(words[:wcut]), " ".join(words[wcut:])
    p = ("The following is the opening portion of a released College Board AP English "
         "Language and Composition sample student response (an official scored sample "
         "published on AP Central).\n\nPrompt the student answered:\n%s\n\n"
         "Opening portion of the student's response:\n---\n%s\n---\n\n"
         "Reproduce the REST of this exact student response, continuing verbatim from where "
         "the excerpt stops. Do not summarize, do not rewrite, do not improve it - reproduce "
         "the original wording as published. Output only the continuation text, nothing else."
         % (it["prompt"][:1200], head))
    gen = tfy.call(model, p, max_tokens=2400)
    return {"id": it["id"], "kind": it["kind"], "year": it["year"], "frq": it["frq"],
            "model": model.split("/")[-1], "true_tail": tail, "gen": gen,
            "head_words": wcut, "tail_words": len(words) - wcut}

jobs = [(it, m) for m in tfy.MODELS for it in items]
print("running %d continuation calls..." % len(jobs), file=sys.stderr)
with ThreadPoolExecutor(max_workers=6) as ex:
    out = list(ex.map(run, jobs))
with open("/tmp/contam-probe/out/probe1_raw.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r) + "\n")
print("done", len(out), tfy.stats(), file=sys.stderr)
