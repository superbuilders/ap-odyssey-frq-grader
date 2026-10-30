#!/usr/bin/env python3
"""BLINDNESS GATE. Reads the labeled corpora; emits two disjoint files:

  blind.jsonl  -- ONLY the fields a grader legitimately receives.
  labels.jsonl -- essay_id + the answer key (row_a/row_b/row_c/total/commentary).

The grader reads blind.jsonl. Nothing in the grading path ever opens
corpus.jsonl or labels.jsonl. Enforced, not promised: this script asserts the
allow-list is exactly the emitted key set and that no banned key leaks through.
"""
import json, pathlib, sys

ALLOW = ["essay_id", "essay_text", "prompt_text", "stimulus_text", "frq_type",
         "source_titles", "word_count", "cited_sources"]
# Routing-only fields the grader needs to pick the right verbatim rubric file.
# They are question identity, NOT score information.
ROUTE = ["year", "set", "question"]
BANNED = {"row_a", "row_b", "row_c", "total", "commentary", "sample_letter"}

root = pathlib.Path("/tmp/aplang-bakeoff")
out = pathlib.Path("/Users/jackjiang-work/Documents/GitHub/APPLAT/_bakeoff_baconwrite/data")
blind, labels = [], []
for year in ("2023", "2024", "2025"):
    for line in (root / year / "corpus.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        b = {k: rec.get(k) for k in ALLOW}
        b.update({k: rec[k] for k in ROUTE})
        assert set(b) & BANNED == set(), "answer key leaked into projection"
        assert BANNED <= set(rec), f"{rec['essay_id']} missing expected label keys"
        blind.append(b)
        labels.append({"essay_id": rec["essay_id"], "row_a": rec["row_a"],
                       "row_b": rec["row_b"], "row_c": rec["row_c"],
                       "total": rec["total"], "sample_letter": rec["sample_letter"]})

(out / "blind.jsonl").write_text("".join(json.dumps(r) + "\n" for r in blind))
(out / "labels.jsonl").write_text("".join(json.dumps(r) + "\n" for r in labels))
print(f"blind={len(blind)} labels={len(labels)} keys={sorted(blind[0])}")
