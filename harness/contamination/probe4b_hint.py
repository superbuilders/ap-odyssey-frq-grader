#!/usr/bin/env python3
"""PROBE 4b - is the id leak UNEXPLOITABLE, or merely UNEXPLOITED?
Same 18 essays, id present, plus one extra sentence stating the A>B>C convention
explicitly. If accuracy jumps here but not in probe 4's id_present condition, the
leak is exploitable and the arms simply did not reach for it."""
import json, sys, re
sys.path.insert(0, "/tmp/contam-probe/scripts")
import tfy
from concurrent.futures import ThreadPoolExecutor
src = open("/tmp/contam-probe/scripts/probe4_idleak.py").read().split("jobs = [(e, c, m)")[0]
g = {}; exec(compile(src.replace("import tfy", ""), "p4", "exec"), g)

HINT = ("\nNOTE ON THE RESPONSE RECORD: this corpus follows College Board's publication "
        "convention, in which the released samples for a question are lettered in "
        "descending order of total score - the sample ending in A scored highest, B next, "
        "C lowest. The essay_id encodes that letter.\n")

def run(job):
    eid, model = job
    p = g["build"](eid, "id_present")
    p = p.replace("\n=== STUDENT RESPONSE ===", HINT + "\n=== STUDENT RESPONSE ===")
    out = tfy.call(model, p, max_tokens=1500)
    return {"essay_id": eid, "cond": "id_present_hinted", "model": model.split("/")[-1],
            "year": g["meta"][eid]["year"], "letter": eid[-1],
            "frq_type": g["blind"][eid]["frq_type"], "raw": out, "parsed": g["jparse"](out)}

jobs = [(e, m) for m in tfy.MODELS for e in g["PICK"]]
print("probe4b: %d calls" % len(jobs), file=sys.stderr)
with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(run, jobs))
with open("/tmp/contam-probe/out/probe4b_raw.jsonl", "w") as f:
    for r in res: f.write(json.dumps(r) + "\n")
print("done", len(res), tfy.stats(), file=sys.stderr)
