"""Collect a deep pool of independent reads per essay, once.

Measuring k-read averaging by re-running the grader for every k wastes calls
and couples each k to its own run. Instead collect N independent reads per
essay and partition them offline: k=9 with R=10 is exactly 90 disjoint reads,
so no read is reused between runs and the flip rate is honest.

This is the whole reason a k-sweep costs nothing after the first 3240 calls.
"""
import json, os, sys, time, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "jev"))

import jev, vault
from build_state import build
from questions import variant_a

OUT = "/tmp/jev-reliability/pool.json"
WORKERS = 16


def collect(essays, n_reads):
    prepared = {r["essay_id"]: (r, *build(r)[:2]) for r in essays}
    pool = {e: [] for e in prepared}
    errors = []
    t0 = time.time()

    def one(eid):
        rec, state, segs = prepared[eid]
        qs = variant_a(rec, segs)
        return eid, float(jev.ask(state, qs)["answers"]["b_level"]["score"])

    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(one, e) for e in prepared for _ in range(n_reads)]
        for f in cf.as_completed(futs):
            try:
                eid, s = f.result()
            except Exception as exc:
                errors.append(repr(exc)[:160])
                continue
            pool[eid].append(s)

    short = {e: len(v) for e, v in pool.items() if len(v) < n_reads}
    print("pool: %d essays x %d reads, %d errors, %d short, %.0fs, %s"
          % (len(pool), n_reads, len(errors), len(short), time.time() - t0, jev.stats()))
    if errors:
        print("  first error:", errors[0])
    return pool


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    which = sys.argv[2] if len(sys.argv) > 2 else "working"
    essays = vault.working_set()
    pool = collect(essays, n)
    json.dump({"n_reads": n, "which": which, "pool": pool}, open(OUT, "w"))
    print("wrote", OUT)
