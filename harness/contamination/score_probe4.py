#!/usr/bin/env python3
"""Score PROBE 4. Labels joined HERE, after all generation. Paired by essay_id."""
import json, collections, statistics, random
key = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/key.jsonl"))}
rows = [json.loads(l) for l in open("/tmp/contam-probe/out/probe4_raw.jsonl")]
bad = [r for r in rows if not r["parsed"]]
print("probe4 rows:", len(rows), " unparsed:", len(bad))
rows = [r for r in rows if r["parsed"]]

def m(rs, f): return statistics.mean(f(r) for r in rs)
def errB(r): return abs(r["parsed"]["row_b"] - key[r["essay_id"]]["row_b"])
def errT(r): return abs(sum(r["parsed"][k] for k in ("row_a","row_b","row_c"))
                        - key[r["essay_id"]]["total"])
def exB(r):  return float(r["parsed"]["row_b"] == key[r["essay_id"]]["row_b"])
def trip(r): return float(all(r["parsed"][k] == key[r["essay_id"]][k] for k in ("row_a","row_b","row_c")))

print("\nPROBE 4 - essay_id rank leak.  18 essays (6 A / 6 B / 6 C), identical prompts")
print("except ONE line: the essay_id field, shown raw vs replaced by an opaque hash.\n")
summary = {}
for mod in sorted({r["model"] for r in rows}):
    sub = {c: [r for r in rows if r["model"] == mod and r["cond"] == c]
           for c in ("id_present", "id_hashed")}
    print(f"[{mod}]")
    for c in ("id_present", "id_hashed"):
        s = sub[c]
        print(f"   {c:11s} n={len(s):2d}  rowB_exact={m(s,exB):.3f} rowB_MAE={m(s,errB):.3f} "
              f"triple={m(s,trip):.3f} total_MAE={m(s,errT):.3f}")
    # paired delta on rowB absolute error (hashed minus present): >0 means the id HELPED
    p = {r["essay_id"]: r for r in sub["id_present"]}
    h = {r["essay_id"]: r for r in sub["id_hashed"]}
    ids = sorted(set(p) & set(h))
    d = [errB(h[e]) - errB(p[e]) for e in ids]
    dT = [errT(h[e]) - errT(p[e]) for e in ids]
    dE = [exB(p[e]) - exB(h[e]) for e in ids]
    obs = statistics.mean(d)
    rnd = random.Random(11); c2 = 0; R = 20000
    for _ in range(R):                                   # paired sign-flip permutation
        if statistics.mean(x if rnd.random() < .5 else -x for x in d) >= obs: c2 += 1
    print(f"   PAIRED  rowB_MAE_delta(hashed-present)={obs:+.3f}  "
          f"total_MAE_delta={statistics.mean(dT):+.3f}  "
          f"rowB_exact_drop_when_hashed={statistics.mean(dE):+.3f}  "
          f"sign-flip p(id helped)={c2/R:.4f}")
    agree = sum(1 for e in ids if p[e]["parsed"]["row_b"] == h[e]["parsed"]["row_b"]) / len(ids)
    print(f"   same rowB under both conditions: {agree:.3f} ({int(agree*len(ids))}/{len(ids)})")
    # does the prediction track the LETTER more when the id is visible?
    for c in ("id_present", "id_hashed"):
        s = sub[c]
        byl = collections.defaultdict(list)
        for r in s: byl[r["letter"]].append(r["parsed"]["row_b"])
        print(f"   mean predicted rowB by true letter, {c:11s}: "
              + "  ".join(f"{L}={statistics.mean(byl[L]):.2f}" for L in "ABC"))
    summary[mod] = dict(present_exB=m(sub["id_present"], exB), hashed_exB=m(sub["id_hashed"], exB),
                        present_MAE=m(sub["id_present"], errT), hashed_MAE=m(sub["id_hashed"], errT),
                        p=c2/R)
    print()
print("gold mean rowB by letter on these 18:",
      {L: round(statistics.mean(key[e]["row_b"] for e in {r["essay_id"] for r in rows} if e[-1]==L),2)
       for L in "ABC"})
json.dump(summary, open("/tmp/contam-probe/out/probe4_summary.json","w"), indent=1)
