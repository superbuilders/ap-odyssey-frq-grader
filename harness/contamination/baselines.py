#!/usr/bin/env python3
"""Guessing baselines for PROBE 2, computed from the corpus's own label distribution.
This is an ORACLE baseline: it is allowed to know the distribution, which makes it
a deliberately strong bar for the cold-recall probe to beat."""
import json, collections, itertools
key ={r["essay_id"]:r for r in map(json.loads,open("/tmp/contam-probe/data/key.jsonl"))}
meta={r["essay_id"]:r for r in map(json.loads,open("/tmp/contam-probe/data/meta.jsonl"))}
ids=list(key)
n=len(ids)
cA=collections.Counter(key[e]["row_a"] for e in ids)
cB=collections.Counter(key[e]["row_b"] for e in ids)
cC=collections.Counter(key[e]["row_c"] for e in ids)
print("label marginals  A:",dict(sorted(cA.items())),
      " B:",dict(sorted(cB.items()))," C:",dict(sorted(cC.items())),f" n={n}")
mA=cA.most_common(1)[0][0]; mB=cB.most_common(1)[0][0]; mC=cC.most_common(1)[0][0]
print(f"modal guess = {mA}-{mB}-{mC}")

def ev(f,label):
    eA=sum(1 for e in ids if f(e)[0]==key[e]["row_a"])/n
    eB=sum(1 for e in ids if f(e)[1]==key[e]["row_b"])/n
    eC=sum(1 for e in ids if f(e)[2]==key[e]["row_c"])/n
    tr=sum(1 for e in ids if tuple(f(e))==(key[e]["row_a"],key[e]["row_b"],key[e]["row_c"]))/n
    maeB=sum(abs(f(e)[1]-key[e]["row_b"]) for e in ids)/n
    tot=sum(1 for e in ids if sum(f(e))==key[e]["total"])/n
    maeT=sum(abs(sum(f(e))-key[e]["total"]) for e in ids)/n
    print(f"  {label:38s} A={eA:.3f} B={eB:.3f} C={eC:.3f} triple={tr:.3f} "
          f"total_exact={tot:.3f} rowB_MAE={maeB:.3f} total_MAE={maeT:.3f}")
    return tr,eB,maeT

print("\nBASELINES (oracle on this corpus's own distribution):")
ev(lambda e:(mA,mB,mC), f"modal constant {mA}-{mB}-{mC}")
# best constant triple by brute force
best=None
for a,b,c in itertools.product([0,1],range(5),[0,1]):
    tr=sum(1 for e in ids if (a,b,c)==(key[e]["row_a"],key[e]["row_b"],key[e]["row_c"]))/n
    if best is None or tr>best[0]: best=(tr,(a,b,c))
print(f"  best-possible CONSTANT triple = {best[1]} at triple={best[0]:.3f}")
ev(lambda e:best[1], f"best constant {best[1]}")
# per-year modal (even more oracular)
ymode={}
for y in ("2023","2024","2025"):
    sub=[e for e in ids if meta[e]["year"]==y]
    ymode[y]=(collections.Counter(key[e]["row_a"] for e in sub).most_common(1)[0][0],
              collections.Counter(key[e]["row_b"] for e in sub).most_common(1)[0][0],
              collections.Counter(key[e]["row_c"] for e in sub).most_common(1)[0][0])
print("  per-year modes:",ymode)
ev(lambda e:ymode[meta[e]["year"]], "per-year modal (max oracle)")
# sample-letter heuristic: released samples are usually ordered A>B>C in quality
print("\n  sample-letter heuristic (A/B/C ordering is public convention, needs no memorization):")
for mapping in [ {"A":(1,4,1),"B":(1,3,0),"C":(1,2,0)}, {"A":(1,4,0),"B":(1,3,0),"C":(1,2,0)},
                 {"A":(1,4,1),"B":(1,3,0),"C":(1,1,0)} ]:
    ev(lambda e,m=mapping:m[e[-1]], f"letter-map {mapping['A']}/{mapping['B']}/{mapping['C']}")

print("\nREFERENCE - Arms phase, WITH full rubric:")
llm={r["essay_id"]:(r["pred_a"],r["pred_b"],r["pred_c"]) for r in
     map(json.loads,open("/tmp/aplang-bakeoff-run/predictions.jsonl"))}
jev={r["essay_id"]:(r["pred_a"],r["pred_b"],r["pred_c"]) for r in
     json.load(open("/tmp/jev-arm/jev_results.json"))["rows_variant_A"]}
for nm,p in (("LLM arm (opus, rubric, 5-call panel)",llm),("Jev arm (rubric)",jev)):
    ev(lambda e,p=p:p[e], nm)
