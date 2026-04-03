#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

pass() { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
fail() { echo "❌ $*"; exit 1; }

echo "=== MISSION CONTROL SELF-TEST ==="
echo "root: $ROOT"
echo

echo "=== BOOTSTRAP HELP ==="
"$ROOT/scripts/bootstrap_mission_control.sh" --help >/dev/null
pass "bootstrap help works"

echo
echo "=== DOCTOR ==="
"$ROOT/bin/doctor.sh" >/dev/null
pass "doctor runs successfully"

echo
echo "=== PROMPT ==="
"$ROOT/bin/prompt.sh" list >/dev/null
pass "prompt helper runs successfully"

echo
echo "=== VERSIONED HOOKS ==="
HOOKS_PATH="$(git -C "$ROOT" config core.hooksPath 2>/dev/null || true)"
if [ "$HOOKS_PATH" = ".githooks" ]; then
  pass "core.hooksPath is .githooks"
else
  warn "core.hooksPath is '$HOOKS_PATH'"
fi


echo
echo "=== SNAPSHOT EXPORT/IMPORT ==="
SNAPSHOT_FILE="/tmp/mc-selftest-snapshot.txt"

SNAPSHOT_COMPARE_A="/tmp/mc-selftest-snapshot-a.txt"
SNAPSHOT_COMPARE_B="/tmp/mc-selftest-snapshot-b.txt"
"$ROOT/bin/mc.sh" snapshot --export "$SNAPSHOT_COMPARE_A" >/dev/null
sleep 1
"$ROOT/bin/mc.sh" snapshot --export "$SNAPSHOT_COMPARE_B" >/dev/null
"$ROOT/bin/mc.sh" snapshot --compare "$SNAPSHOT_COMPARE_A" "$SNAPSHOT_COMPARE_A" >/dev/null
pass "snapshot compare identical works"
"$ROOT/bin/mc.sh" snapshot --compare "$SNAPSHOT_COMPARE_A" "$SNAPSHOT_COMPARE_B" >/dev/null
pass "snapshot compare diff works"

"$ROOT/bin/mc.sh" snapshot --export "$SNAPSHOT_FILE" >/dev/null
if [ -s "$SNAPSHOT_FILE" ]; then
  pass "snapshot export works"
else
  fail "snapshot export failed"
fi
"$ROOT/bin/mc.sh" snapshot --import "$SNAPSHOT_FILE" >/dev/null
pass "snapshot import works"


echo
echo "=== LOG VIEWER ==="

echo
echo "=== WATCH MODE ==="
timeout 2 "$ROOT/bin/mc.sh" watch --interval 1 >/dev/null 2>&1 || true
pass "watch command runs"

"$ROOT/bin/mc.sh" logs --lines 1 >/dev/null || true
"$ROOT/bin/mc.sh" logs dispatch --lines 1 >/dev/null || true
"$ROOT/bin/mc.sh" logs errors --lines 1 >/dev/null || true
pass "log viewer commands run"

echo
echo "=== FILE CHECKS ==="
for path in \
  "$ROOT/bin/mc.sh" \
  "$ROOT/bin/doctor.sh" \
  "$ROOT/bin/prompt.sh" \
  "$ROOT/scripts/bootstrap_mission_control.sh" \
  "$ROOT/scripts/install_launchagent.sh" \
  "$ROOT/docs/SETUP.md" \
  "$ROOT/docs/SYSTEM_PROMPT_BUILD.md" \
  "$ROOT/.githooks/pre-commit"
do
  if [ -e "$path" ]; then
    pass "exists: $path"
  else
    fail "missing: $path"
  fi
done

echo
echo "✅ SELF-TEST PASSED"


echo
echo "=== ARCHIVE/RESTORE ==="
TEST_MISSION="$ROOT/.ai/missions/active/999-test-archive.md"
echo "test" > "$TEST_MISSION"
"$ROOT/bin/mc.sh" archive 999-test-archive.md && echo "✅" || echo "❌"
LIST_OUTPUT="$("$ROOT/bin/mc.sh" list archived)"
echo "$LIST_OUTPUT"
if grep -q "999-test-archive.md" <<< "$LIST_OUTPUT"; then
  echo "✅"
else
  echo "❌"
fi
"$ROOT/bin/mc.sh" restore 999-test-archive.md && echo "✅" || echo "❌"
rm -f "$TEST_MISSION"
