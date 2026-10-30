"""Vault read #2: does question-side relocation transfer, or reverse like gap-aware?

Candidate frozen as disjoint-levels v9, decoded with the SHIPPED thresholds at
k=9. Nothing is refitted here.
"""
import importlib.util, json, os, statistics, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import jev, vault, thresholds as TH
import questions as Q
from build_state import build
import concurrent.futures as cf

K, R = 9, 10
CAND = os.path.join(HERE, "proposals", "disjoint-levels-v9.py")


def load(path):
    spec = importlib.util.spec_from_file_location("cand", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(essays, qfn, label):
    prep = {r["essay_id"]: (r, *build(r)[:2]) for r in essays}
    sig = {e: [] for e in prep}
    errs = 0

    def unit(eid, _i):
        rec, state, segs = prep[eid]
        qs = qfn(rec, segs)
        vals = [float(jev.ask(state, qs)["answers"]["b_level"]["score"]) for _ in range(K)]
        return eid, statistics.fmean(vals)

    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        futs = [ex.submit(unit, e, i) for e in prep for i in range(R)]
        for f in cf.as_completed(futs):
            try:
                eid, s = f.result()
            except Exception:
                errs += 1
                continue
            sig[eid].append(s)
    print("  %-10s %d calls, %d errors" % (label, len(prep) * R * K, errs))
    return sig


def score(sig, gold):
    per, modes = {}, {}
    for e, runs in sig.items():
        lv = [TH.decode(s, TH.SHIPPED) for s in runs]
        n = len(lv)
        per[e] = 1.0 - sum(c * (c - 1) / 2 for c in Counter(lv).values()) / (n * (n - 1) / 2)
        modes[e] = Counter(lv).most_common(1)[0][0]
    ids = [e for e in modes if e in gold]
    acc = sum(1 for e in ids if modes[e] == gold[e])
    c4 = [e for e in ids if gold[e] == 4]
    return (sum(per.values()) / len(per), sum(1 for v in per.values() if v > 0),
            acc, sum(1 for e in c4 if modes[e] == 4), len(c4), dict(sorted(Counter(modes.values()).items())))


sealed = vault.open_vault("read 2: does disjoint-levels v9 question-side relocation transfer?", confirm=True)
print("vault opened. reads now %d/%d, %d essays\n" % (vault.reads_spent(), vault.READ_BUDGET, len(sealed)))

gold = {}
for l in open("/tmp/jev-arm/keys/labels.jsonl", encoding="utf-8"):
    r = json.loads(l)
    gold[r["essay_id"]] = r["row_b"]

cand = load(CAND)
ctl = run(sealed, Q.variant_a, "control")
v9 = run(sealed, cand.questions, "v9")

print("\n%-10s %9s %10s %9s %7s  %s" % ("arm", "flip", "unstable", "acc", "CB4", "marginal"))
rc = score(ctl, gold)
rv = score(v9, gold)
for nm, r in (("control", rc), ("v9", rv)):
    print("%-10s %9.4f %7d/18 %6d/18 %4d/%d  %s" % (nm, r[0], r[1], r[2], r[3], r[4], r[5]))

print("\n--- against pre-registration 2 ---")
print("1. v9 flip < control flip      : %.4f vs %.4f -> %s"
      % (rv[0], rc[0], "PASS" if rv[0] < rc[0] else "FAIL"))
print("2. v9 accuracy within 3        : %d vs %d (%+d) -> %s"
      % (rv[2], rc[2], rv[2] - rc[2], "PASS" if abs(rv[2] - rc[2]) <= 3 else "FAIL"))
print("3. v9 CB4 within 2             : %d vs %d (%+d) -> %s"
      % (rv[3], rc[3], rv[3] - rc[3], "PASS" if abs(rv[3] - rc[3]) <= 2 else "FAIL"))
json.dump({"control": rc[:5], "v9": rv[:5]}, open("/tmp/jev-reliability/verdict2.json", "w"), indent=1)
