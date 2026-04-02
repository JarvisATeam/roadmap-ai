#!/usr/bin/env bash
set -euo pipefail
echo "🧪 Running export tests..."
PASS=0; FAIL=0

for fmt in markdown json csv; do
  if bash "scripts/export_${fmt}.sh"; then
    echo "  ✅ export_${fmt}.sh"
    PASS=$((PASS+1))
  else
    echo "  ❌ export_${fmt}.sh"
    FAIL=$((FAIL+1))
  fi
done

for f in exports/plan.md exports/plan.json exports/plan.csv; do
  if [ -s "$f" ]; then
    echo "  ✅ $f exists ($(wc -c < "$f") bytes)"
    PASS=$((PASS+1))
  else
    echo "  ❌ $f missing or empty"
    FAIL=$((FAIL+1))
  fi
done

if python3 -c "import json; json.load(open(\"exports/plan.json\"))"; then
  echo "  ✅ plan.json is valid JSON"
  PASS=$((PASS+1))
else
  echo "  ❌ plan.json is invalid JSON"
  FAIL=$((FAIL+1))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && echo "🟢 ALL EXPORT TESTS GREEN" || echo "🔴 FAILURES DETECTED"
exit "$FAIL"
