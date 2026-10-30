"""Grade all 54 essays with Jev, variants A and B. Reads ONLY blind/essays.jsonl."""
import json, sys, threading, concurrent.futures as cf
sys.path.insert(0, "/tmp/jev-arm")
import jev
RESULTS_PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/jev-arm/results_raw.json"
from build_state import build
from questions import variant_a, variant_b

BLIND = "/tmp/jev-arm/blind/essays.jsonl"
ALLOWED = {"essay_id","essay_text","prompt_text","stimulus_text","frq_type","source_titles",
           "word_count","cited_sources","year","set","question"}
T = 0.5
NEAR = 0.09
_lk = threading.Lock(); near_a = []; near_b = []

def load():
    rs = [json.loads(l) for l in open(BLIND, encoding="utf-8")]
    for r in rs:                                   # blindness assertion
        assert set(r) == ALLOWED, "blind file leaked fields: %s" % (set(r) - ALLOWED)
    return rs

def _n(ans, k):
    return float(ans[k]["noul"])

def compose_b(rec, segs, ans):
    """Variant B: the level is computed HERE in Python from single-fact nouls."""
    syn = rec["frq_type"] == "synthesis"; rhet = rec["frq_type"] == "rhetorical_analysis"
    K = len(segs)
    g = {k: _n(ans, k) for k in ans if ans[k]["type"] == "noul"}
    used = []
    def nb(k):
        used.append((k, g[k])); return g[k]
    restates = nb("b_restates"); specific = nb("b_specific")
    multiclaims = nb("b_multiclaims")
    uniform = g["b_uniform"]            # recorded, NOT a gate (degenerate universal)
    allc = g.get("b_allclaims", -1.0)
    lor = nb("b_lor"); mech = nb("b_mech")
    sev = [nb("seg%d_ev" % i) for i in range(1, K + 1)]
    sex = [nb("seg%d_expl" % i) for i in range(1, K + 1)]
    srh = [nb("seg%d_rhet" % i) for i in range(1, K + 1)] if rhet else []
    idx_ev = [i for i in range(K) if sev[i] > T]
    n_ev = len(idx_ev); n_expl = sum(1 for i in idx_ev if sex[i] > T)
    n_rhet = sum(1 for v in srh if v > T)
    cited = len(rec.get("cited_sources") or [])
    ev_ge2 = (cited >= 2) if syn else (n_ev >= 1)          # STATED FACT / code count
    ev_ge3 = (cited >= 3) if syn else (n_ev >= 1)
    if restates > T or not ev_ge2:          lvl = 0
    elif n_expl == 0:                        lvl = 1
    elif not (lor > T):                      lvl = 2
    elif not ev_ge3:                         lvl = 2
    elif not (specific > T and multiclaims > T): lvl = 2
    else:
        # EVERY universal quantifier is computed HERE, in Python, from per-segment
        # existential nouls. No universally-quantified question gates anything:
        # Jev answers "uniformly"/"all"/"consistently" false on 54/54 essays regardless
        # of quality (b_uniform, b_allclaims: sd<0.10, 0/54 true) -- see detail.
        consistently = n_ev >= 2 and n_expl == n_ev      # rubric: "Consistently explains..."
        lvl = 4 if (consistently and not (mech > T)) else 3
    if rhet:
        if n_rhet == 0:   lvl = min(lvl, 2)
        elif n_rhet < 2:  lvl = min(lvl, 3)
    # continuous signal: expected level from the same gates, unthresholded
    p1 = (1 - restates) * (1.0 if ev_ge2 else 0.0)
    p2 = p1 * (max(sex) if sex else 0.0)
    p3 = p2 * lor * (1.0 if ev_ge3 else 0.0) * specific * multiclaims
    if rhet: p3 *= (max(srh) if srh else 0.0)
    cons = min([sex[i] for i in idx_ev]) if n_ev >= 2 else 0.0
    p4 = p3 * cons * (1 - mech)
    if rhet: p4 *= (sorted(srh, reverse=True)[1] if len(srh) > 1 else 0.0)
    raw = p1 + p2 + p3 + p4
    diag = dict(n_seg=K, n_ev=n_ev, n_expl=n_expl, n_rhet=n_rhet, cited=cited,
                ev_cov=round(n_ev / max(K, 1), 3), expl_rat=round(n_expl / max(n_ev, 1), 3),
                restates=restates, specific=specific, uniform=uniform,
                multiclaims=multiclaims, lor=lor, mech=mech,
                seg_ev=sev, seg_expl=sex, seg_rhet=srh)
    return lvl, raw, used, diag

def grade(rec):
    state, segs, tier = build(rec)
    out = {"essay_id": rec["essay_id"], "frq_type": rec["frq_type"], "tier": tier, "n_seg": len(segs)}
    # ---- variant A ----
    qa = variant_a(rec, segs)
    ra = jev.ask(state, qa)["answers"]
    missing = set(qa) - set(ra)
    assert not missing, "variant A missing answers %s for %s" % (missing, rec["essay_id"])
    a_th = float(ra["a_thesis"]["noul"]); a_sc = float(ra["b_level"]["score"]); a_so = float(ra["c_soph"]["noul"])
    out["A"] = {"pred_a": int(a_th > T), "raw_a": a_th,
                "pred_b": int(round(a_sc)), "raw_b": a_sc,
                "pred_c": int(a_so > 0.65), "pred_c_50": int(a_so > T), "raw_c": a_so,
                "probs_b": ra["b_level"].get("probabilities", {})}
    with _lk:
        for k, v in [("a_thesis", a_th), ("c_soph", a_so)]:
            if abs(v - T) < NEAR: near_a.append((rec["essay_id"], k, v))
        if abs(v - 0.65) < NEAR: near_a.append((rec["essay_id"], "c_soph@0.65", a_so))
        if abs((a_sc % 1.0) - 0.5) < NEAR: near_a.append((rec["essay_id"], "b_level", a_sc))
    # ---- variant B ----
    qb = variant_b(rec, segs)
    rb = jev.ask(state, qb)["answers"]
    missing = set(qb) - set(rb)
    assert not missing, "variant B missing answers %s for %s" % (missing, rec["essay_id"])
    b_th = float(rb["a_thesis"]["noul"]); b_so = float(rb["c_soph"]["noul"])
    lvl, raw, used, diag = compose_b(rec, segs, rb)
    out["B"] = {"pred_a": int(b_th > T), "raw_a": b_th, "pred_b": lvl, "raw_b": raw,
                "pred_c": int(b_so > 0.65), "pred_c_50": int(b_so > T), "raw_c": b_so, "diag": diag}
    with _lk:
        for k, v in used + [("a_thesis", b_th), ("c_soph", b_so)]:
            if abs(v - T) < NEAR: near_b.append((rec["essay_id"], k, v))
        if abs(b_so - 0.65) < NEAR: near_b.append((rec["essay_id"], "c_soph@0.65", b_so))
    return out

def main():
    rs = load()
    res = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(grade, r): r["essay_id"] for r in rs}
        for f in cf.as_completed(futs):
            eid = futs[f]
            try:
                res[eid] = f.result()
            except Exception as e:
                print("FAIL", eid, repr(e)[:300], file=sys.stderr)
    order = [r["essay_id"] for r in rs]
    with open(RESULTS_PATH, "w") as f:
        json.dump({"results": [res[e] for e in order if e in res],
                   "near_cut_A": near_a, "near_cut_B": near_b,
                   "jev_stats": jev.stats()}, f, indent=1)
    print("graded", len(res), "/", len(rs), jev.stats())

if __name__ == "__main__":
    main()
