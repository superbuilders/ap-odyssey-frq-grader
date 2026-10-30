#!/usr/bin/env python3
"""Is the LLM arm's 2025 drop explained by gold-score difficulty rather than year?"""
import json, collections
key  = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/key.jsonl"))}
meta = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/meta.jsonl"))}
llm  = {r["essay_id"]:(r["pred_a"],r["pred_b"],r["pred_c"]) for r in
        map(json.loads, open("/tmp/aplang-bakeoff-run/predictions.jsonl"))}
jev  = {r["essay_id"]:(r["pred_a"],r["pred_b"],r["pred_c"]) for r in
        json.load(open("/tmp/jev-arm/jev_results.json"))["rows_variant_A"]}

print("LLM rowB error by (year, gold rowB):")
for y in ("2023","2024","2025"):
    d=collections.defaultdict(list)
    for e,m in meta.items():
        if m["year"]!=y: continue
        d[key[e]["row_b"]].append(llm[e][1]-key[e]["row_b"])
    print(" ",y, {g:f"n={len(v)} meanSignedErr={sum(v)/len(v):+.2f}" for g,v in sorted(d.items())})

# Stratified check: restrict to gold rowB in {2,3,4} (common support across all years)
print("\nStratified to gold rowB in {2,3,4} (common support, removes the 2023 excess of 1s):")
for nm,pr in (("LLM",llm),("JEV",jev)):
    for y in ("2023","2024","2025"):
        ids=[e for e,m in meta.items() if m["year"]==y and key[e]["row_b"] in (2,3,4)]
        mae=sum(abs(pr[e][1]-key[e]["row_b"]) for e in ids)/len(ids)
        ex =sum(1 for e in ids if pr[e][1]==key[e]["row_b"])/len(ids)
        print(f"  {nm} {y} n={len(ids)} rowB_MAE={mae:.3f} rowB_exact={ex:.3f}")

# Matched-pair: for each (set,question,letter) slot, compare across years -> removes slot difficulty
print("\nPer-year mean |total error|, matched by slot (set,question,letter):")
slots=collections.defaultdict(dict)
for e,m in meta.items():
    slots[(m["set"],m["question"],e[-1])][m["year"]]=e
for nm,pr in (("LLM",llm),("JEV",jev)):
    agg=collections.defaultdict(list)
    for slot,ys in slots.items():
        if len(ys)<3: continue
        for y,e in ys.items():
            agg[y].append(abs(sum(pr[e])-key[e]["total"]))
    print(f"  {nm}", {y:f"{sum(v)/len(v):.3f}" for y,v in sorted(agg.items())})
