#!/usr/bin/env python3
"""Year gradient: join each arm's predictions to the key AFTER grading, per year."""
import json, collections, math, random

key  = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/key.jsonl"))}
meta = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/meta.jsonl"))}

def load_llm():
    out={}
    for r in map(json.loads, open("/tmp/aplang-bakeoff-run/predictions.jsonl")):
        out[r["essay_id"]]={"a":r["pred_a"],"b":r["pred_b"],"c":r["pred_c"]}
    return out

def load_jev():
    d=json.load(open("/tmp/jev-arm/jev_results.json"))
    return {r["essay_id"]:{"a":r["pred_a"],"b":r["pred_b"],"c":r["pred_c"]}
            for r in d["rows_variant_A"]}

def qwk(g,p,lo,hi):
    n=len(g); k=hi-lo+1
    if n==0: return float('nan')
    O=[[0]*k for _ in range(k)]
    for a,b in zip(g,p): O[a-lo][b-lo]+=1
    gh=collections.Counter(g); ph=collections.Counter(p)
    num=den=0.0
    for i in range(k):
        for j in range(k):
            w=((i-j)**2)/((k-1)**2) if k>1 else 0
            E=gh.get(i+lo,0)*ph.get(j+lo,0)/n
            num+=w*O[i][j]; den+=w*E
    return 1-num/den if den>0 else float('nan')

def report(name, preds):
    print(f"\n===== {name} =====")
    byyear=collections.defaultdict(list)
    for eid,p in preds.items():
        g=key[eid]; y=meta[eid]["year"]
        byyear[y].append((g,p))
    allrows=[]
    for y in sorted(byyear):
        rows=byyear[y]; allrows+=rows
        n=len(rows)
        exB=sum(1 for g,p in rows if g["row_b"]==p["b"])/n
        exC=sum(1 for g,p in rows if g["row_c"]==p["c"])/n
        exA=sum(1 for g,p in rows if g["row_a"]==p["a"])/n
        trip=sum(1 for g,p in rows if g["row_a"]==p["a"] and g["row_b"]==p["b"] and g["row_c"]==p["c"])/n
        gt=[g["total"] for g,p in rows]; pt=[p["a"]+p["b"]+p["c"] for g,p in rows]
        exT=sum(1 for a,b in zip(gt,pt) if a==b)/n
        maeT=sum(abs(a-b) for a,b in zip(gt,pt))/n
        maeB=sum(abs(g["row_b"]-p["b"]) for g,p in rows)/n
        qT=qwk(gt,pt,0,6); qB=qwk([g["row_b"] for g,p in rows],[p["b"] for g,p in rows],0,4)
        print(f" {y} n={n}  rowB_exact={exB:.3f} rowB_MAE={maeB:.3f}  rowC_exact={exC:.3f}  "
              f"triple={trip:.3f}  total_exact={exT:.3f} total_MAE={maeT:.3f}  "
              f"qwkTotal={qT:.3f} qwkB={qB:.3f}")
    n=len(allrows)
    gt=[g["total"] for g,p in allrows]; pt=[p["a"]+p["b"]+p["c"] for g,p in allrows]
    print(f" ALL n={n}  rowB_exact={sum(1 for g,p in allrows if g['row_b']==p['b'])/n:.3f}"
          f"  total_MAE={sum(abs(a-b) for a,b in zip(gt,pt))/n:.3f}"
          f"  qwkTotal={qwk(gt,pt,0,6):.3f}")
    return byyear

llm=load_llm(); jev=load_jev()
print("ids match:", set(llm)==set(jev)==set(key))
report("LLM ARM (claude-opus-4-8 panel)", llm)
report("JEV ARM (jev-1.14.0 variant_A)", jev)

# Old(2023+2024) vs New(2025) contrast + permutation test on rowB MAE
def oldnew(preds,name):
    old=[(key[e],p) for e,p in preds.items() if meta[e]["year"] in ("2023","2024")]
    new=[(key[e],p) for e,p in preds.items() if meta[e]["year"]=="2025"]
    def mB(rows): return sum(abs(g["row_b"]-p["b"]) for g,p in rows)/len(rows)
    def eB(rows): return sum(1 for g,p in rows if g["row_b"]==p["b"])/len(rows)
    def mT(rows):
        return sum(abs(g["total"]-(p["a"]+p["b"]+p["c"])) for g,p in rows)/len(rows)
    print(f"\n-- {name}: OLD(23+24,n={len(old)}) vs NEW(25,n={len(new)})")
    print(f"   rowB MAE  old={mB(old):.3f} new={mB(new):.3f}  delta={mB(new)-mB(old):+.3f}")
    print(f"   rowB exact old={eB(old):.3f} new={eB(new):.3f}  delta={eB(new)-eB(old):+.3f}")
    print(f"   total MAE old={mT(old):.3f} new={mT(new):.3f}  delta={mT(new)-mT(old):+.3f}")
    # permutation test on total-MAE gap
    obs=mT(new)-mT(old); pool=old+new; rnd=random.Random(7); cnt=0; R=20000
    for _ in range(R):
        s=pool[:]; rnd.shuffle(s)
        if mT(s[len(old):])-mT(s[:len(old):]) >= obs: cnt+=1
    print(f"   perm p(one-sided, new worse than old, totalMAE) = {cnt/R:.4f}")
    return obs

oldnew(llm,"LLM"); oldnew(jev,"JEV")

# Gold-score distribution per year (confound check)
print("\n-- gold label distribution per year (confound check)")
for y in ("2023","2024","2025"):
    ids=[e for e in key if meta[e]["year"]==y]
    print(f"  {y} rowB={dict(sorted(collections.Counter(key[e]['row_b'] for e in ids).items()))} "
          f"rowC={dict(sorted(collections.Counter(key[e]['row_c'] for e in ids).items()))} "
          f"meanTotal={sum(key[e]['total'] for e in ids)/len(ids):.2f}")
