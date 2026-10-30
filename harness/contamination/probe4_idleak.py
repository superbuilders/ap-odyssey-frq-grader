#!/usr/bin/env python3
"""PROBE 4 - the essay_id rank leak.
Released CB samples are ordered A>B>C by total score in all 6 question-sets, and
essay_id embeds the letter. The arms graded from a projection that CONTAINED essay_id.
Re-grade a stratified subsample under two conditions, everything else identical:
  cond=id_present  -> the record shows essay_id exactly as the arms saw it
  cond=id_hashed   -> essay_id replaced by an opaque hash, nothing else changed
Reads ONLY blind.jsonl + the verbatim rubric files. Labels joined in a later step."""
import json, re, sys, hashlib, collections
sys.path.insert(0, "/tmp/contam-probe/scripts")
import tfy
from concurrent.futures import ThreadPoolExecutor

blind = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/blind.jsonl"))}
meta  = {r["essay_id"]: r for r in map(json.loads, open("/tmp/contam-probe/data/meta.jsonl"))}

_rub = {}
def rubric(year, st, q):
    """verbatim Row A/B/C scoring criteria for one question, sliced out of the rubric file"""
    k = (year, st)
    if k not in _rub:
        _rub[k] = open("/tmp/aplang-bakeoff/%s/rubric-set%d.md" % (year, st)).read()
    txt = _rub[k]
    lines = txt.split("\n")
    hdr = re.compile(r"^## Question " + str(q) + r"\b")
    nxt = re.compile(r"^## Question " + str(q + 1) + r"\b")
    start = next(i for i, L in enumerate(lines) if hdr.match(L))
    rest = [i for i, L in enumerate(lines) if i > start and nxt.match(L)]
    end = rest[0] if rest else len(lines)
    return "\n".join(lines[start:end]).strip()

# stratified: 3 years x 3 frq_types x 2 letters, letters balanced 6 A / 6 B / 6 C
LETTER_CYCLE = {("2023",1):"AB", ("2023",2):"BC", ("2023",3):"CA",
                ("2024",1):"BC", ("2024",2):"CA", ("2024",3):"AB",
                ("2025",1):"CA", ("2025",2):"AB", ("2025",3):"BC"}
PICK = []
for (y, q), letters in LETTER_CYCLE.items():
    for L in letters:
        PICK.append("%s-s1-q%d-%s" % (y, q, L))
assert len(PICK) == 18, len(PICK)
assert collections.Counter(p[-1] for p in PICK) == {"A":6,"B":6,"C":6}, collections.Counter(p[-1] for p in PICK)

def opaque(eid):
    return "ESSAY-" + hashlib.sha256(("saltv1|" + eid).encode()).hexdigest()[:12].upper()

def build(eid, cond):
    r = blind[eid]; m = meta[eid]
    shown = eid if cond == "id_present" else opaque(eid)
    rec = {"essay_id": shown, "frq_type": r["frq_type"], "word_count": r["word_count"],
           "cited_sources": r.get("cited_sources") or [], "source_titles": r.get("source_titles") or []}
    p = ["You are an AP English Language and Composition reader. Score the student response "
         "below against the official College Board scoring guidelines, which are reproduced "
         "verbatim.\n",
         "=== OFFICIAL SCORING GUIDELINES (verbatim) ===\n" + rubric(m["year"], m["set"], m["question"]),
         "\n=== PROMPT GIVEN TO THE STUDENT ===\n" + (r.get("prompt_text") or "").strip()]
    stim = (r.get("stimulus_text") or "").strip()
    if stim:
        p.append("\n=== %s ===\n%s" % ("PROVIDED SOURCE PACKET" if r["frq_type"] == "synthesis"
                 else "PASSAGE THE STUDENT ANALYZED", stim[:11000]))
    p.append("\n=== RESPONSE RECORD ===\n" + json.dumps(rec, indent=1))
    p.append("\n=== STUDENT RESPONSE ===\n" + r["essay_text"].strip())
    p.append('\nScore it. Answer with ONLY a JSON object, no other text:\n'
             '{"row_a": <0 or 1>, "row_b": <0-4>, "row_c": <0 or 1>}')
    return "\n".join(p)

def jparse(s):
    m = re.search(r"\{[^{}]*\}", s, re.S)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None

def run(job):
    eid, cond, model = job
    out = tfy.call(model, build(eid, cond), max_tokens=1500)
    return {"essay_id": eid, "cond": cond, "model": model.split("/")[-1],
            "shown_id": eid if cond == "id_present" else opaque(eid),
            "year": meta[eid]["year"], "frq_type": blind[eid]["frq_type"],
            "letter": eid[-1], "raw": out, "parsed": jparse(out)}

jobs = [(e, c, m) for m in tfy.MODELS for c in ("id_present", "id_hashed") for e in PICK]
print("probe4: %d calls (%d essays x 2 conditions x 2 models)" % (len(jobs), len(PICK)), file=sys.stderr)
with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(run, jobs))
with open("/tmp/contam-probe/out/probe4_raw.jsonl", "w") as f:
    for r in res: f.write(json.dumps(r) + "\n")
print("done", len(res), tfy.stats(), file=sys.stderr)
