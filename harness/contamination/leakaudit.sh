set -e
echo "=== 1. grading-side files must contain NO label token ==="
for f in data/blind.jsonl out/probe1b_raw.jsonl out/probe2_raw.jsonl out/probe4_raw.jsonl; do
  n=$(grep -c -E '"(row_a|row_b|row_c|total|commentary|sample_letter)"' "$f" 2>/dev/null || true)
  echo "  $f : label-token lines = ${n:-0}  (blind.jsonl must be 0; probe out files carry the MODEL'S OWN guesses only)"
done
echo
echo "=== 2. which scripts open the answer key ==="
grep -ln "key.jsonl\|corpus.jsonl" scripts/*.py | sed 's/^/  /'
echo
echo "=== 3. which of those are GRADING scripts (must be none) ==="
for f in scripts/probe1_continuation.py scripts/probe1b.py scripts/probe2_coldrecall.py scripts/probe4_idleak.py scripts/probe4b_hint.py; do
  if grep -q "key.jsonl" "$f"; then echo "  LEAK: $f"; else echo "  clean: $f"; fi
done
