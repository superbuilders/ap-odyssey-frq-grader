"""Deep pool of variant-B noul reads. Collect once, evaluate any composition offline.

One Jev call returns EVERY noul in the question set, so N independent calls per
essay give N independent draws of the whole gate vector. Any composition rule
can then be scored at any k with zero further calls, exactly as pool.py did for
the variant-A score.

    python3 -I integer_compose_pool.py <qset> <n_reads> <out.json>
"""
import importlib.util, json, os, sys, time, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import jev, vault
from build_state import build
import questions as Q

WORKERS = 16


def _qset(name):
    """variant_b, or a builder named questions() in one of my proposal files."""
    if name == "variant_b":
        return Q.variant_b
    spec = importlib.util.spec_from_file_location("qmod", name)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.questions


def collect(build_q, essays, n_reads):
    prepared = {r["essay_id"]: (r, *build(r)[:2]) for r in essays}
    pool = {e: [] for e in prepared}
    nseg = {e: len(prepared[e][2]) for e in prepared}
    errors = []
    t0 = time.time()

    def one(eid):
        rec, state, segs = prepared[eid]
        qs = build_q(rec, segs)
        a = jev.ask(state, qs)["answers"]
        missing = set(qs) - set(a)
        if missing:
            raise RuntimeError("missing %s" % sorted(missing)[:3])
        out = {k: float(v["noul"]) for k, v in a.items() if v["type"] == "noul"}
        out.update({"#" + k: float(v["score"]) for k, v in a.items() if v["type"] == "score"})
        return eid, out

    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(one, e) for e in prepared for _ in range(n_reads)]
        for f in cf.as_completed(futs):
            try:
                eid, g = f.result()
            except Exception as exc:
                errors.append(repr(exc)[:200])
                continue
            pool[eid].append(g)

    short = {e: len(v) for e, v in pool.items() if len(v) < n_reads}
    print("pool: %d essays x %d reads, %d errors, %d short, %.0fs, %s"
          % (len(pool), n_reads, len(errors), len(short), time.time() - t0, jev.stats()))
    if errors:
        print("  first error:", errors[0])
    meta = {e: {"n_seg": nseg[e], "frq_type": prepared[e][0]["frq_type"],
                "cited": len(prepared[e][0].get("cited_sources") or [])} for e in prepared}
    return pool, meta


if __name__ == "__main__":
    qname = sys.argv[1]
    n = int(sys.argv[2])
    out = sys.argv[3]
    essays = vault.working_set()
    if len(sys.argv) > 4:
        essays = essays[:int(sys.argv[4])]
    pool, meta = collect(_qset(qname), essays, n)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"qset": qname, "n_reads": n, "pool": pool, "meta": meta}, open(out, "w"))
    print("wrote", out)
