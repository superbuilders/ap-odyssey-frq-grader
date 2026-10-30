"""STEP 1 (blindness): project corpus to grader-legitimate fields only.
Writes blind/essays.jsonl (what the grader may read) and keys/labels.jsonl (answer key,
never opened by the grader). Run once; grader asserts the blind file's field set."""
import json, os

ALLOWED = ["essay_id", "essay_text", "prompt_text", "stimulus_text", "frq_type",
           "source_titles", "word_count", "cited_sources",
           # routing metadata: which verbatim rubric applies. Not a label.
           "year", "set", "question"]
KEYFIELDS = ["essay_id", "row_a", "row_b", "row_c", "total", "commentary", "sample_letter"]

def main():
    blind, keys = [], []
    for y in ["2023", "2024", "2025"]:
        for line in open(f"/tmp/aplang-bakeoff/{y}/corpus.jsonl", encoding="utf-8"):
            r = json.loads(line)
            blind.append({k: r[k] for k in ALLOWED})
            keys.append({k: r.get(k) for k in KEYFIELDS})
    with open("/tmp/jev-arm/blind/essays.jsonl", "w", encoding="utf-8") as f:
        for r in blind:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open("/tmp/jev-arm/keys/labels.jsonl", "w", encoding="utf-8") as f:
        for r in keys:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.chmod("/tmp/jev-arm/blind/essays.jsonl", 0o444)
    print("blind:", len(blind), "keys:", len(keys))
    print("blind fields:", sorted(blind[0].keys()))

main()
