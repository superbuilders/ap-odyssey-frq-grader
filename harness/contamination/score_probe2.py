#!/usr/bin/env python3
"""Score PROBE 2 (cold recall). Joins labels back HERE, after generation."""
import json, collections, statistics, random
key  = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/key.jsonl"))}
meta = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/meta.jsonl"))}
rows = [json.loads(l) for l in open("/tmp/contam-probe/out/probe2_raw.jsonl")]

sc = [r for r in rows if r["probe"] == "score" and r["parsed"]]
idp = [r for r in rows if r["probe"] == "ident" and r["parsed"]]
print("parsed score rows:", len(sc), "/", sum(1 for r in rows if r["probe"] == "score"),
      "  ident rows:", len(idp), "/", sum(1 for r in rows if r["probe"] == "ident"))

def ev(rows, label):
    n = len(rows)
    if not n: return
    g = lambda r: key[r["essay_id"]]
    p = lambda r, k: r["parsed"].get(k)
    eA = sum(1 for r in rows if p(r,"row_a") == g(r)["row_a"]) / n
    eB = sum(1 for r in rows if p(r,"row_b") == g(r)["row_b"]) / n
    eC = sum(1 for r in rows if p(r,"row_c") == g(r)["row_c"]) / n
    tr = sum(1 for r in rows if (p(r,"row_a"),p(r,"row_b"),p(r,"row_c")) ==
             (g(r)["row_a"],g(r)["row_b"],g(r)["row_c"])) / n
    tot = sum(1 for r in rows
              if None not in (p(r,"row_a"),p(r,"row_b"),p(r,"row_c"))
              and p(r,"row_a")+p(r,"row_b")+p(r,"row_c") == g(r)["total"]) / n
    mB = statistics.mean(abs(p(r,"row_b") - g(r)["row_b"]) for r in rows
                         if isinstance(p(r,"row_b"), int))
    mT = statistics.mean(abs(p(r,"row_a")+p(r,"row_b")+p(r,"row_c") - g(r)["total"])
                         for r in rows if None not in (p(r,"row_a"),p(r,"row_b"),p(r,"row_c")))
    print(f"  {label:32s} n={n:3d}  A={eA:.3f} B={eB:.3f} C={eC:.3f}  triple={tr:.3f} "
          f"total_exact={tot:.3f}  rowB_MAE={mB:.3f} total_MAE={mT:.3f}")
    return dict(n=n, B=eB, triple=tr, total_exact=tot, rowB_MAE=mB, total_MAE=mT)

print("\nPROBE 2 - COLD SCORE RECALL (no rubric, no criteria given)")
print("  BAR TO BEAT: oracle modal constant 1-3-0 -> B=0.315 triple=0.222 rowB_MAE=0.833")
print("  STRONGER BAR: letter-map (ordering is public convention) -> B=0.722 triple=0.593 rowB_MAE=0.278")
res = {}
for m in sorted({r["model"] for r in sc}):
    sub = [r for r in sc if r["model"] == m]
    res[m] = ev(sub, m)
    for y in ("2023","2024","2025"):
        ev([r for r in sub if r["year"] == y], f"    {m} {y}")

print("\n  self-reported recall flag:")
for m in sorted({r["model"] for r in sc}):
    c = collections.Counter(str(r["parsed"].get("recalled")).lower() for r in sc if r["model"] == m)
    print(f"    {m:18s} {dict(c)}")

print("\nPROBE 2b - DOCUMENT IDENTIFICATION (year / set / question / sample letter)")
for m in sorted({r["model"] for r in idp}):
    sub = [r for r in idp if r["model"] == m]
    n = len(sub)
    ey = sum(1 for r in sub if str(r["parsed"].get("year")) == meta[r["essay_id"]]["year"]) / n
    es = sum(1 for r in sub if r["parsed"].get("set") == meta[r["essay_id"]]["set"]) / n
    eq = sum(1 for r in sub if r["parsed"].get("question") == meta[r["essay_id"]]["question"]) / n
    el = sum(1 for r in sub if str(r["parsed"].get("letter")).upper() == r["essay_id"][-1]) / n
    rec = collections.Counter(str(r["parsed"].get("recognized")).lower() for r in sub)
    print(f"  {m:18s} n={n}  year={ey:.3f} (chance~.33 over 3 yrs) set={es:.3f} (chance .50) "
          f"q={eq:.3f} (chance .33) letter={el:.3f} (chance .33)  recognized={dict(rec)}")
