#!/usr/bin/env python3
"""Score PROBE 1. Metrics, all on lowercased word tokens of the TRUE TAIL vs GENERATION:
  LCCR  = longest common CONTIGUOUS token run / len(true_tail)   <- memorization signal
  C8    = 8-gram containment: |8-grams(gen) & 8-grams(tail)| / |8-grams(gen)|
  LCS   = longest common subsequence / len(true_tail)            <- order-aware similarity
  JACC  = unigram Jaccard                                        <- TOPICALITY, not memory
Reads only probe1b_raw.jsonl (no labels anywhere)."""
import json, re, collections, statistics

W = re.compile(r"[a-z0-9']+")
def toks(s): return W.findall(s.lower())

def lccr(a, b):
    """longest common contiguous run, O(n*m) DP over rolling rows"""
    if not a or not b: return 0
    prev = [0]*(len(b)+1); best = 0
    for i in range(1, len(a)+1):
        cur = [0]*(len(b)+1); ai = a[i-1]
        for j in range(1, len(b)+1):
            if ai == b[j-1]:
                v = prev[j-1] + 1; cur[j] = v
                if v > best: best = v
        prev = cur
    return best

def lcs(a, b):
    if not a or not b: return 0
    prev = [0]*(len(b)+1)
    for i in range(1, len(a)+1):
        cur = [0]*(len(b)+1); ai = a[i-1]
        for j in range(1, len(b)+1):
            cur[j] = prev[j-1]+1 if ai == b[j-1] else max(prev[j], cur[j-1])
        prev = cur
    return prev[-1]

def ngrams(t, n): return {tuple(t[i:i+n]) for i in range(len(t)-n+1)}

rows = [json.loads(l) for l in open("/tmp/contam-probe/out/probe1b_raw.jsonl")]
out = []
for r in rows:
    if r["gen"].startswith("__ERROR__"):
        print("ERR", r["id"], r["model"]); continue
    T, G = toks(r["true_tail"]), toks(r["gen"])
    # cap DP cost: compare generation against the true tail, both truncated to 900 tokens
    Tc, Gc = T[:900], G[:900]
    g8, t8 = ngrams(G, 8), ngrams(T, 8)
    rec = dict(id=r["id"], kind=r["kind"], year=r["year"], frq=r["frq"], model=r["model"],
               tail_tok=len(T), gen_tok=len(G),
               LCCR=lccr(Tc, Gc)/max(1, len(Tc)),
               lccr_tokens=lccr(Tc, Gc),
               C8=(len(g8 & t8)/len(g8)) if g8 else 0.0,
               LCS=lcs(Tc, Gc)/max(1, len(Tc)),
               JACC=len(set(T) & set(G))/max(1, len(set(T) | set(G))))
    out.append(rec)
json.dump(out, open("/tmp/contam-probe/out/probe1b_scored.json", "w"), indent=1)

def agg(sel, label):
    s = [r for r in out if sel(r)]
    if not s: return
    f = lambda k: statistics.mean(r[k] for r in s)
    mx = lambda k: max(r[k] for r in s)
    print(f"  {label:34s} n={len(s):2d}  LCCR={f('LCCR'):.4f} (max {mx('LCCR'):.4f}, "
          f"longest run {max(r['lccr_tokens'] for r in s):3d} tok)  C8={f('C8'):.4f} "
          f"(max {mx('C8'):.4f})  LCS={f('LCS'):.3f}  JACC={f('JACC'):.3f}")

print("PROBE 1b - FINISH-THE-ESSAY continuation (non-refusal framing)")
for m in sorted({r["model"] for r in out}):
    print(f"\n[{m}]")
    agg(lambda r, m=m: r["model"] == m and r["kind"] == "control", "CONTROL (unseen, mine)")
    agg(lambda r, m=m: r["model"] == m and r["kind"] == "real", "REAL released samples")
    for y in ("2023", "2024", "2025"):
        agg(lambda r, m=m, y=y: r["model"] == m and r["year"] == y, f"  real {y}")

print("\nPER-ITEM (sorted by longest verbatim run):")
for r in sorted(out, key=lambda r: -r["lccr_tokens"])[:12]:
    print(f"  {r['id']:16s} {r['model']:16s} {r['kind']:7s} longest_run={r['lccr_tokens']:3d} "
          f"LCCR={r['LCCR']:.4f} C8={r['C8']:.4f} LCS={r['LCS']:.3f}")
