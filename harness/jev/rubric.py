"""Extract verbatim College Board rubric cell text from fixed-width rubric markdown.
Handles both the 2025 heading style and the 2023/2024 page-heading style."""
import re, json, sys, functools

BASE = "/tmp/aplang-bakeoff"

@functools.lru_cache(maxsize=None)
def _blocks(path):
    txt = open(path, encoding="utf-8").read()
    qsplits = [(m.group(1), m.start()) for m in re.finditer(r"^## Question (\d)", txt, re.M)]
    qsplits.append((None, len(txt)))
    out = {}
    for i in range(len(qsplits) - 1):
        q = int(qsplits[i][0]); a, b = qsplits[i][1], qsplits[i + 1][1]
        span = txt[a:b]
        for m in re.finditer(r"```text\n(.*?)\n```", span, re.S):
            body = m.group(1)
            if "Scoring Criteria" not in body:
                continue
            row = None
            for r in "ABC":
                if re.search(rf"^\s*Row {r}\s", body, re.M):
                    row = r; break
            if row and (q, row) not in out:
                out[(q, row)] = body
    return out

def _col_offsets(block, n):
    for line in block.split("\n"):
        if "0 points" not in line:
            continue
        labels = ["0 points"] + [f"{i} point" + ("s" if i > 1 else "") for i in range(1, n)]
        offs, pos, ok = [], 0, True
        for lab in labels:
            i = line.find(lab, pos)
            if i < 0:
                ok = False; break
            offs.append(i); pos = i + len(lab)
        if ok and len(offs) == n:
            return offs, line
    raise ValueError("no header row found")

def _slice(lines, offs):
    n = len(offs); cols = [[] for _ in range(n)]
    for line in lines:
        for i in range(n):
            a = offs[i]; b = offs[i + 1] if i + 1 < n else len(line) + 1000
            piece = line[a:b].strip()
            if piece:
                cols[i].append(piece)
    return [" ".join(c) for c in cols]

@functools.lru_cache(maxsize=None)
def cell(year, sset, q, row):
    path = f"{BASE}/{year}/rubric-set{sset}.md"
    blk = _blocks(path)[(q, row)]
    n = 5 if row == "B" else 2
    offs, hdr = _col_offsets(blk, n)
    lines = blk.split("\n")
    hi = lines.index(hdr)
    di = next((i for i, l in enumerate(lines) if "Decision Rules and Scoring Notes" in l), len(lines))
    ai = next((i for i, l in enumerate(lines) if "Additional Notes:" in l), len(lines))
    crit = _slice(lines[hi + 1:di], offs)
    notes = _slice(lines[di + 1:ai], offs)
    extra = "\n".join(l.strip() for l in lines[ai:] if l.strip())
    return {"criteria": tuple(crit), "notes": tuple(notes), "additional": extra}

if __name__ == "__main__":
    y, s, q, r = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    c = cell(y, s, q, r)
    print(json.dumps({k: (list(v) if isinstance(v, tuple) else v) for k, v in c.items()}, indent=2))
