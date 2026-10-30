#!/usr/bin/env python3
"""Extract VERBATIM College Board row text per (year, set, question, row).

The three years ship three different markdown layouts, so the only structure
relied on is: `## Question N ...` sections, each containing ```text fences whose
body carries a `Row A|B|C   0 points ...` header line. Each fence is copied
byte-for-byte -- nothing is paraphrased, reordered, or summarized.
"""
import json, pathlib, re

root = pathlib.Path("/tmp/aplang-bakeoff")
out = pathlib.Path("/Users/jackjiang-work/Documents/GitHub/APPLAT/_bakeoff_baconwrite/data")
QSEC = re.compile(r"^## Question (\d+)[^\n]*$", re.M)
FENCE = re.compile(r"```text\n(.*?)\n```", re.S)
ROWMARK = {r: re.compile(rf"^\s*Row {r}\s+0 points", re.M) for r in "ABC"}

rubrics = {}
for year in ("2023", "2024", "2025"):
    for s in (1, 2):
        md = (root / year / f"rubric-set{s}.md").read_text()
        marks = list(QSEC.finditer(md))
        assert len(marks) == 3, f"{year} set{s}: {len(marks)} question sections"
        for i, m in enumerate(marks):
            q = int(m.group(1))
            body = md[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(md)]
            entry = {"titles": {}}
            for r in "ABC":
                hits = [f.group(1) for f in FENCE.finditer(body) if ROWMARK[r].search(f.group(1))]
                assert len(hits) == 1, f"{year}/s{s}/q{q}/Row{r}: {len(hits)} fences"
                entry[f"row_{r.lower()}"] = hits[0]
            rubrics[f"{year}|{s}|{q}"] = entry
assert len(rubrics) == 18, len(rubrics)
(out / "rubrics.json").write_text(json.dumps(rubrics, indent=1))
print(f"{len(rubrics)} rubrics")
for k in sorted(rubrics):
    print(k, {r: len(rubrics[k][f"row_{r}"]) for r in "abc"})
