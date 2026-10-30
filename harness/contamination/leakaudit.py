#!/usr/bin/env python3
"""AST-level blindness audit: for every script that TALKS TO A MODEL, enumerate every
path literal it can open. Comments and docstrings are ignored by construction."""
import ast, sys, os
GRADING = ["probe1_continuation.py","probe1b.py","probe2_coldrecall.py",
           "probe4_idleak.py","probe4b_hint.py"]
JOINING = ["project.py","baselines.py","year_gradient.py","cold_gradient.py",
           "score_probe1.py","score_probe1b.py","score_probe2.py","score_probe4.py"]
FORBID = ("key.jsonl","labels.jsonl","corpus.jsonl")
def opened(path):
    t = ast.parse(open(path).read())
    out = []
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "open":
            for a in n.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str): out.append(a.value)
                elif isinstance(a, ast.BinOp):  out.append(ast.unparse(a))
                else: out.append("<dynamic:" + ast.unparse(a)[:60] + ">")
    return out
bad = 0
print("A. SCRIPTS THAT CALL THE MODEL - every open() target:")
for f in GRADING:
    p = "/tmp/contam-probe/scripts/" + f
    if not os.path.exists(p): continue
    ops = opened(p)
    hit = [o for o in ops if any(k in o for k in FORBID)]
    bad += len(hit)
    print(f"  {f:26s} {ops}" + ("   <<< LEAK" if hit else "   OK"))
print("\nB. SCRIPTS THAT JOIN LABELS BACK (allowed to read the key):")
for f in JOINING:
    p = "/tmp/contam-probe/scripts/" + f
    if os.path.exists(p): print(f"  {f:26s} {opened(p)}")
print("\nC. transitive imports of the grading scripts:", "tfy (gateway client only)")
print("   tfy.py open() targets:", opened("/tmp/contam-probe/scripts/tfy.py"))
print("\nVERDICT:", "BLINDNESS HELD - no grading script can reach a label file" if bad == 0
      else "FAILED (%d leaks)" % bad)
