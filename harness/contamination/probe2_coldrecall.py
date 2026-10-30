#!/usr/bin/env python3
"""PROBE 2 - cold score recall + metadata recall. Reads ONLY blind.jsonl.
No rubric, no scoring criteria, no labels are placed in any prompt.
This script never opens key.jsonl; scoring is a separate step."""
import json, os, re, sys, time
sys.path.insert(0,"/tmp/contam-probe/scripts")
import tfy
from concurrent.futures import ThreadPoolExecutor
MODELS=tfy.MODELS

blind=[json.loads(l) for l in open("/tmp/contam-probe/data/blind.jsonl")]
meta ={r["essay_id"]:r for r in map(json.loads,open("/tmp/contam-probe/data/meta.jsonl"))}

def call(model,prompt,maxtok=1200):
    return tfy.call(model,prompt,max_tokens=maxtok)

SCORE_P=("This is a released College Board AP English Language and Composition sample "
 "student response, published on AP Central with its official score.\n\n"
 "Student response:\n---\n{essay}\n---\n\n"
 "What score did College Board actually give this response, as Row A - Row B - Row C?\n"
 "Answer with ONLY a JSON object, no other text:\n"
 '{{"row_a": <0 or 1>, "row_b": <0-4>, "row_c": <0 or 1>, '
 '"recalled": "<yes if you specifically remember this released sample and its published score, '
 'no if you are inferring>"}}')

ID_P=("The text below is a released College Board AP English Language and Composition sample "
 "student response, published on AP Central.\n\n"
 "Student response:\n---\n{essay}\n---\n\n"
 "If you specifically recognize this exact released document, identify it: which exam YEAR, "
 "which SET (1 or 2), which QUESTION number (1 synthesis / 2 rhetorical analysis / 3 argument), "
 "and which SAMPLE LETTER (A, B, or C) is it?\n"
 "Answer with ONLY a JSON object, no other text:\n"
 '{{"year": <4-digit year or null>, "set": <1, 2 or null>, "question": <1,2,3 or null>, '
 '"letter": "<A, B, C or null>", "recognized": "<yes|no>"}}')

def jparse(s):
    m=re.search(r"\{.*\}",s,re.S)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None

ID_SUBSET=[r["essay_id"] for r in blind
           if r["essay_id"][-1] in ("A","C") and r["essay_id"][5:7]=="s1"]

def job_score(args):
    r,model=args
    out=call(model,SCORE_P.format(essay=r["essay_text"]))
    return {"probe":"score","essay_id":r["essay_id"],"year":meta[r["essay_id"]]["year"],
            "frq_type":r["frq_type"],"model":model.split("/")[-1],
            "raw":out,"parsed":jparse(out)}

def job_id(args):
    r,model=args
    out=call(model,ID_P.format(essay=r["essay_text"]))
    return {"probe":"ident","essay_id":r["essay_id"],"year":meta[r["essay_id"]]["year"],
            "frq_type":r["frq_type"],"model":model.split("/")[-1],
            "raw":out,"parsed":jparse(out)}

jobs=[(r,m) for m in MODELS for r in blind]
idjobs=[(r,m) for m in MODELS for r in blind if r["essay_id"] in ID_SUBSET]
print(f"score calls={len(jobs)} ident calls={len(idjobs)}",file=sys.stderr)
with ThreadPoolExecutor(max_workers=8) as ex:
    res=list(ex.map(job_score,jobs))+list(ex.map(job_id,idjobs))
with open("/tmp/contam-probe/out/probe2_raw.jsonl","w") as f:
    for r in res: f.write(json.dumps(r)+"\n")
print("done",len(res),tfy.stats(),file=sys.stderr)
