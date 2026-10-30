#!/usr/bin/env python3
"""Does the COLD-RECALL probe show the same old>new gradient as the Arms phase?
If the Arms gradient were score memorization, cold recall should show it too."""
import json, random, statistics, collections
key  = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/key.jsonl"))}
rows = [json.loads(l) for l in open("/tmp/contam-probe/out/probe2_raw.jsonl")
        if json.loads(l)["probe"] == "score" and json.loads(l)["parsed"]]
def mT(rs):
    return statistics.mean(abs(r["parsed"]["row_a"]+r["parsed"]["row_b"]+r["parsed"]["row_c"]
                               - key[r["essay_id"]]["total"]) for r in rs)
for m in sorted({r["model"] for r in rows}):
    sub = [r for r in rows if r["model"] == m]
    old = [r for r in sub if r["year"] in ("2023","2024")]; new = [r for r in sub if r["year"] == "2025"]
    obs = mT(new) - mT(old)
    pool = old + new; rnd = random.Random(7); c = 0; R = 20000
    for _ in range(R):
        s = pool[:]; rnd.shuffle(s)
        if mT(s[len(old):]) - mT(s[:len(old)]) >= obs: c += 1
    print(f"  COLD {m:18s} totalMAE old={mT(old):.3f} new={mT(new):.3f} delta={obs:+.3f} "
          f"perm p(new worse)={c/R:.4f}")

print("\nArms-phase LLM 2025 dip - where does it come from?")
meta = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/meta.jsonl"))}
llm = {r["essay_id"]: r for r in map(json.loads, open("/tmp/aplang-bakeoff-run/predictions.jsonl"))}
by = collections.defaultdict(list)
for e, p in llm.items():
    by[(meta[e]["year"], meta[e]["frq_type"])].append(abs(p["pred_b"] - key[e]["row_b"]))
for y in ("2023","2024","2025"):
    print("  ", y, {t: round(statistics.mean(by[(y,t)]),3) for t in
                    ("synthesis","rhetorical_analysis","argument")})
print("\n  signed rowB bias (pred - gold) by year:")
for y in ("2023","2024","2025"):
    d = [llm[e]["pred_b"] - key[e]["row_b"] for e in llm if meta[e]["year"] == y]
    print(f"    {y} mean={statistics.mean(d):+.3f}  dist={dict(sorted(collections.Counter(d).items()))}")
