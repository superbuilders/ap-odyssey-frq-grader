"""One confirmatory read of the sealed 18. Spends a vault read. Do not iterate after this.

Thresholds are frozen at the values derived from the 36 working essays. They are
NOT refitted here; refitting on the holdout is the whole thing the vault exists
to prevent.
"""
import json, os, statistics, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import measure, metric, vault, thresholds as TH

FROZEN_GAP = (1.905, 2.41, 2.8359)
SHIPPED = TH.SHIPPED

sealed = vault.open_vault("final verdict: gap-aware vs shipped quantile thresholds", confirm=True)
print("vault opened. reads now %d/%d, %d essays\n" % (vault.reads_spent(), vault.READ_BUDGET, len(sealed)))

res = measure.measure("A1", 10, essays=sealed)
sig = res["signals"]
print("jev: %d calls, %d errors, %.0fs\n" % (res["jev"]["calls"], res["errors"], res["elapsed_s"]))

keys = {}
for l in open("/tmp/jev-arm/keys/labels.jsonl", encoding="utf-8"):
    r = json.loads(l)
    keys[r["essay_id"]] = r["row_b"]
ids = sorted(sig)
gold = {e: keys[e] for e in ids}
cb4 = [e for e in ids if gold[e] == 4]

print("sealed 2025, n=%d, gold Row B marginal: %s" % (len(ids), dict(sorted(Counter(gold.values()).items()))))
print("measured SD on sealed set: %.4f\n" % statistics.median(res["signal_sd"].values()))

print("%-14s %-26s %8s %9s %8s %7s" % ("thresholds", "marginal", "flip", "unstable", "acc", "CB4"))
out = {}
for name, cuts in [("round()", (1.5, 2.5, 3.5)), ("shipped", SHIPPED), ("gap-aware", FROZEN_GAP)]:
    r = TH.evaluate(sig, cuts)
    acc = sum(1 for e in ids if r["modes"][e] == gold[e])
    hit4 = sum(1 for e in cb4 if r["modes"][e] == 4)
    out[name] = (r["flip_rate"], r["unstable"], acc, hit4)
    print("%-14s %-26s %8.4f %6d/%-2d %6d/%-2d %4d/%d"
          % (name, str(r["marginal"]), r["flip_rate"], r["unstable"], len(ids), acc, len(ids), hit4, len(cb4)))

print("\n--- against the pre-registered predictions ---")
gf, gu, ga, g4 = out["gap-aware"]
sf, su, sa, s4 = out["shipped"]
print("1. gap flip < 0.06 and shipped flip > 0.10 : gap %.4f, shipped %.4f -> %s"
      % (gf, sf, "PASS" if (gf < 0.06 and sf > 0.10) else "FAIL"))
print("2. gap accuracy within 2 of shipped        : %d vs %d (delta %+d) -> %s"
      % (ga, sa, ga - sa, "PASS" if abs(ga - sa) <= 2 else "FAIL"))
print("3. gap CB4 recall >= shipped - 1           : %d vs %d -> %s"
      % (g4, s4, "PASS" if g4 >= s4 - 1 else "FAIL"))
json.dump({"frozen_cuts": FROZEN_GAP, "results": out, "n": len(ids)},
          open("/tmp/jev-reliability/verdict.json", "w"), indent=1)
