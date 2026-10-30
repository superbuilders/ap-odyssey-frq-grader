#!/usr/bin/env python3
"""SEPARATE STEP: join the answer key back onto the blind predictions and report.

Runs only after grading is finished. The grader process never imported this file
and never read labels.jsonl.
"""
import json, pathlib, re, statistics


LEVEL = re.compile(r"(\d)[- ]point level|scores? at (?:the )?(\d)|earns? (?:only )?(\d) of (?:the )?4|(\d) of 4 points", re.I)
def named_level(p):
    """Diagnostic only. Pull the Row B level the model states in prose, if any."""
    for c in p.get("criteria_results", []):
        if c["id"] == "row_b_evidence_commentary":
            m = LEVEL.search(c.get("feedback", "") or "")
            if m:
                return int(next(g for g in m.groups() if g))
    return None

D = pathlib.Path("/Users/jackjiang-work/Documents/GitHub/APPLAT/_bakeoff_baconwrite/data")
preds = {r["essay_id"]: r for r in json.loads((D / "raw-grades.json").read_text())}
labels = {json.loads(l)["essay_id"]: json.loads(l) for l in (D / "labels.jsonl").read_text().splitlines() if l.strip()}

rows, lat, tin, tout = [], [], [], []
for eid in sorted(labels):
    p, g = preds.get(eid), labels[eid]
    if not p or not p.get("ok"):
        rows.append({"essay_id": eid, "ok": False, "why": (p or {}).get("why", "not run"), **{f"gold_{k}": g[k] for k in ("row_a","row_b","row_c","total")}})
        continue
    lat.append(p["latencyMs"]);  tin.append(p["tokensIn"] or 0); tout.append(p["tokensOut"] or 0)
    rows.append({"essay_id": eid, "ok": True,
                 "pred_a": p["row_a"], "pred_b": p["row_b"], "pred_c": p["row_c"], "pred_total": p["total"],
                 "gold_a": g["row_a"], "gold_b": g["row_b"], "gold_c": g["row_c"], "gold_total": g["total"],
                 "latency_ms": p["latencyMs"], "tokens_in": p["tokensIn"], "tokens_out": p["tokensOut"],
                 # Diagnostic ONLY, never used as a prediction: the level the model
                 # names in its own Row B prose, which the binary schema discards.
                 "row_b_level_named_in_prose": named_level(p)})

def qwk(a, b, lo, hi):
    n = hi - lo + 1
    O = [[0]*n for _ in range(n)]
    for x, y in zip(a, b): O[x-lo][y-lo] += 1
    ha = [a.count(v+lo) for v in range(n)]; hb = [b.count(v+lo) for v in range(n)]
    N = len(a); num = den = 0.0
    for i in range(n):
        for j in range(n):
            w = ((i-j)**2)/((n-1)**2)
            num += w*O[i][j]; den += w*ha[i]*hb[j]/N
    return 1 - num/den if den else 0.0

ok = [r for r in rows if r["ok"]]
rep = {"graded": len(ok), "failed": len(rows)-len(ok)}
for key, lo, hi in (("a",0,1), ("b",0,4), ("c",0,1), ("total",0,6)):
    pr = [r[f"pred_{key}"] for r in ok]; go = [r[f"gold_{key}"] for r in ok]
    rep[f"row_{key}"] = {
        "exact": round(sum(p==g for p,g in zip(pr,go))/len(ok), 4),
        "adjacent": round(sum(abs(p-g)<=1 for p,g in zip(pr,go))/len(ok), 4),
        "mae": round(statistics.fmean(abs(p-g) for p,g in zip(pr,go)), 3),
        "bias_pred_minus_gold": round(statistics.fmean(p-g for p,g in zip(pr,go)), 3),
        "qwk": round(qwk(pr,go,lo,hi), 4),
        "pred_dist": {v: pr.count(v) for v in sorted(set(pr))},
        "gold_dist": {v: go.count(v) for v in sorted(set(go))},
    }
rep["latency_p50_ms"] = round(statistics.median(lat), 1) if lat else 0
rep["latency_p95_ms"] = round(sorted(lat)[max(0,int(len(lat)*0.95)-1)], 1) if lat else 0
rep["tokens_in_total"] = sum(tin); rep["tokens_out_total"] = sum(tout)
# claude-sonnet-4-6 list price: $3 / Mtok in, $15 / Mtok out.
rep["cost_usd"] = round(sum(tin)/1e6*3 + sum(tout)/1e6*15, 4)
(D / "results.json").write_text(json.dumps({"summary": rep, "rows": rows}, indent=1))
print(json.dumps(rep, indent=1))
