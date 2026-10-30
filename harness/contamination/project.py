#!/usr/bin/env python3
"""Blind projection. Reads the full corpus (which contains the answer key),
emits TWO disjoint files:
  blind.jsonl  -- ONLY grader-legitimate fields. No row_a/row_b/row_c/total/commentary.
  key.jsonl    -- essay_id + labels only. Never read by any grading/probe code.
Any field not on ALLOW is dropped. Assertion-checked both ways.
"""
import json, os, sys

ALLOW = ["essay_id","essay_text","prompt_text","stimulus_text","frq_type",
         "source_titles","word_count","cited_sources"]
# year is derivable from essay_id and is needed for the year-gradient analysis,
# but it is NOT a score, so it is carried in a separate meta file, not in blind.jsonl.
FORBIDDEN = {"row_a","row_b","row_c","total","commentary","sample_letter"}

root = "/tmp/aplang-bakeoff"
out = "/tmp/contam-probe/data"
blind, key, meta = [], [], []
for y in ("2023","2024","2025"):
    for line in open(f"{root}/{y}/corpus.jsonl"):
        if not line.strip(): continue
        r = json.loads(line)
        b = {k: r[k] for k in ALLOW if k in r}
        assert not (set(b) & FORBIDDEN), f"LEAK in blind row {r['essay_id']}"
        assert "essay_id" in b and "essay_text" in b
        blind.append(b)
        key.append({"essay_id": r["essay_id"], "row_a": r["row_a"],
                    "row_b": r["row_b"], "row_c": r["row_c"], "total": r["total"]})
        meta.append({"essay_id": r["essay_id"], "year": r["year"], "set": r["set"],
                     "question": r["question"], "frq_type": r["frq_type"]})

def dump(path, rows):
    with open(path,"w") as f:
        for r in rows: f.write(json.dumps(r)+"\n")

dump(f"{out}/blind.jsonl", blind)
dump(f"{out}/key.jsonl", key)
dump(f"{out}/meta.jsonl", meta)

# Independent re-read audit of the written artifact: grep-level proof of no leak.
raw = open(f"{out}/blind.jsonl").read()
for tok in ('"row_a"','"row_b"','"row_c"','"commentary"','"total"','"sample_letter"'):
    assert tok not in raw, f"LEAK token {tok} present in blind.jsonl"
print(f"blind={len(blind)} key={len(key)} meta={len(meta)}")
print("blind fields:", sorted({k for r in blind for k in r}))
print("NO-LEAK AUDIT PASSED on /tmp/contam-probe/data/blind.jsonl")
