"""STEP 3 (join): attach the answer key to the blind predictions and report."""
import json, collections, statistics, sys

res = json.load(open("/tmp/jev-arm/results_run3.json"))
keys = {r["essay_id"]: r for r in (json.loads(l) for l in open("/tmp/jev-arm/keys/labels.jsonl"))}
R = res["results"]

def report(v, cfield="pred_c"):
    ok_a = ok_b = ok_c = ok_all = 0; off = collections.Counter(); conf = collections.Counter()
    for r in R:
        k = keys[r["essay_id"]]; p = r[v]
        a = p["pred_a"] == k["row_a"]; b = p["pred_b"] == k["row_b"]; c = p[cfield] == k["row_c"]
        ok_a += a; ok_b += b; ok_c += c; ok_all += (a and b and c)
        off[p["pred_b"] - k["row_b"]] += 1
        conf[(k["row_b"], p["pred_b"])] += 1
    n = len(R)
    return dict(n=n, rowA=ok_a, rowB=ok_b, rowC=ok_c, exact_triple=ok_all,
                rowB_within1=sum(c for d, c in off.items() if abs(d) <= 1),
                b_offsets=dict(sorted(off.items())), conf=conf)

def pr(name, d):
    print(f"\n### {name}  (n={d['n']})")
    print(f"  Row A exact: {d['rowA']}/{d['n']}   Row B exact: {d['rowB']}/{d['n']}  "
          f"(within 1: {d['rowB_within1']}/{d['n']})   Row C exact: {d['rowC']}/{d['n']}")
    print(f"  all-three-rows exact: {d['exact_triple']}/{d['n']}")
    print(f"  Row B pred-minus-truth offsets: {d['b_offsets']}")
    print("  Row B confusion (truth -> pred):")
    for t in sorted(set(k[0] for k in d['conf'])):
        row = {p: c for (tt, p), c in d['conf'].items() if tt == t}
        print(f"    CB {t}: " + "  ".join(f"pred{p}={c}" for p, c in sorted(row.items())))

for v in ["A", "B"]:
    pr("VARIANT " + v + "  (Row C cut 0.65)", report(v))
    d50 = report(v, "pred_c_50"); print(f"  [Row C at cut 0.50 instead: {d50['rowC']}/{d50['n']}, "
                                        f"triple {d50['exact_triple']}/{d50['n']}]")

print("\n### Row B exact agreement by question type")
for v in ["A", "B"]:
    by = collections.defaultdict(lambda: [0, 0])
    for r in R:
        k = keys[r["essay_id"]]; by[r["frq_type"]][1] += 1
        by[r["frq_type"]][0] += (r[v]["pred_b"] == k["row_b"])
    print(" ", v, {t: f"{a}/{b}" for t, (a, b) in sorted(by.items())})

print("\n### Row B exact agreement by CB level")
for v in ["A", "B"]:
    by = collections.defaultdict(lambda: [0, 0])
    for r in R:
        k = keys[r["essay_id"]]; by[k["row_b"]][1] += 1; by[k["row_b"]][0] += (r[v]["pred_b"] == k["row_b"])
    print(" ", v, {t: f"{a}/{b}" for t, (a, b) in sorted(by.items())})

print("\n### held-out check (2023+2024 only, 36 essays; the 2025 12 were the prior dev set)")
H = [r for r in R if not r["essay_id"].startswith("2025")]
for v in ["A", "B"]:
    a = sum(1 for r in H if r[v]["pred_b"] == keys[r["essay_id"]]["row_b"])
    c = sum(1 for r in H if r[v]["pred_c"] == keys[r["essay_id"]]["row_c"])
    t = sum(1 for r in H if r[v]["pred_b"] == keys[r["essay_id"]]["row_b"]
            and r[v]["pred_c"] == keys[r["essay_id"]]["row_c"] and r[v]["pred_a"] == keys[r["essay_id"]]["row_a"])
    print(f"  {v}: RowB {a}/36  RowC {c}/36  triple {t}/36")

print("\n### 3-vs-4 discriminator separation (variant B 'consistently' rule)")
for lab, pick in [("CB-4 essays", 4), ("CB-3 essays", 3)]:
    vals = [r["B"]["diag"]["n_expl"] / max(r["B"]["diag"]["n_ev"], 1) for r in R if keys[r["essay_id"]]["row_b"] == pick]
    evs = [r["B"]["diag"]["n_ev"] for r in R if keys[r["essay_id"]]["row_b"] == pick]
    print(f"  {lab}: n={len(vals)} mean explain-ratio={statistics.mean(vals):.3f} mean n_ev={statistics.mean(evs):.2f}")
print("  variant A mean raw score on CB-4:",
      round(statistics.mean([r["A"]["raw_b"] for r in R if keys[r["essay_id"]]["row_b"] == 4]), 3),
      " on CB-3:", round(statistics.mean([r["A"]["raw_b"] for r in R if keys[r["essay_id"]]["row_b"] == 3]), 3))
print("  variant A max raw score anywhere:", round(max(r["A"]["raw_b"] for r in R), 3),
      " variant B max raw:", round(max(r["B"]["raw_b"] for r in R), 3))
print("  variant A emitted a 4 on:", sum(1 for r in R if r["A"]["pred_b"] == 4), "essays;",
      "variant B emitted a 4 on:", sum(1 for r in R if r["B"]["pred_b"] == 4), "essays")

print("\n### near-cut calls (|noul-0.5| < 0.09, or score frac within 0.09 of .5)")
print("  variant A:", len(res["near_cut_A"]), "of", 54 * 3, "decision calls")
print("  variant B:", len(res["near_cut_B"]), "of", sum(len(r["B"]["diag"]["seg_ev"]) * (3 if r["frq_type"]=="rhetorical_analysis" else 2) + 7 for r in R), "decision calls")
print("  jev:", res["jev_stats"])
