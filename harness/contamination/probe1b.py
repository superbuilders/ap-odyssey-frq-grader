#!/usr/bin/env python3
"""PROBE 1b - continuation WITHOUT the 'reproduce verbatim' framing.
Probe 1 hit a 100% refusal rate (30/30, real AND control alike), so it measured
refusal policy, not memory. This version asks the model to finish the essay as a
writing task, which it will actually do. Memorization would still surface as
elevated verbatim overlap on REAL essays relative to the unseen CONTROLS."""
import json, sys
sys.path.insert(0, "/tmp/contam-probe/scripts")
import tfy
from concurrent.futures import ThreadPoolExecutor

blind = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/blind.jsonl"))}
meta  = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/meta.jsonl"))}
PICK = ["2023-s1-q1-A","2023-s1-q2-B","2023-s2-q3-A","2023-s2-q1-C",
        "2024-s1-q1-A","2024-s1-q2-B","2024-s2-q3-A","2024-s2-q1-C",
        "2025-s1-q1-A","2025-s1-q2-B","2025-s2-q3-A","2025-s2-q1-C"]
items = [{"id": e, "kind": "real", "year": meta[e]["year"], "frq": blind[e]["frq_type"],
          "text": blind[e]["essay_text"], "prompt": blind[e]["prompt_text"]} for e in PICK]
cp = {"synthesis": blind["2025-s1-q1-A"]["prompt_text"],
      "rhetorical": blind["2025-s1-q2-A"]["prompt_text"],
      "argument": blind["2025-s1-q3-A"]["prompt_text"]}
for nm in ("synthesis", "rhetorical", "argument"):
    items.append({"id": "CTRL-" + nm, "kind": "control", "year": "control", "frq": nm,
                  "text": open("/tmp/contam-probe/controls/CTRL-%s.txt" % nm).read().strip(),
                  "prompt": cp[nm]})

def run(job):
    it, model = job
    w = it["text"].split(); cut = max(1, int(len(w) * 0.40))
    head, tail = " ".join(w[:cut]), " ".join(w[cut:])
    p = ("Below is an unfinished AP English Language and Composition student essay. "
         "Finish it.\n\nPrompt the student is answering:\n%s\n\nThe essay so far:\n---\n%s\n---\n\n"
         "Write the remaining roughly %d words of this essay, continuing from exactly where it "
         "stops, in the same student's voice and style. Begin mid-sentence if the excerpt ends "
         "mid-sentence. Output only the continuation, nothing else."
         % (it["prompt"][:1200], head, len(w) - cut))
    return {"id": it["id"], "kind": it["kind"], "year": it["year"], "frq": it["frq"],
            "model": model.split("/")[-1], "true_tail": tail,
            "gen": tfy.call(model, p, max_tokens=2400),
            "head_words": cut, "tail_words": len(w) - cut}

jobs = [(it, m) for m in tfy.MODELS for it in items]
print("running %d calls..." % len(jobs), file=sys.stderr)
with ThreadPoolExecutor(max_workers=6) as ex:
    out = list(ex.map(run, jobs))
with open("/tmp/contam-probe/out/probe1b_raw.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r) + "\n")
print("done", len(out), tfy.stats(), file=sys.stderr)
