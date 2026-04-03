#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "[install] root: $ROOT"
echo "[install] running bootstrap"
"$ROOT/scripts/bootstrap_mission_control.sh" "$@"

echo
echo "[install] running self-test"
"$ROOT/scripts/selftest_mission_control.sh"

echo
echo "[install] next steps:"
echo "  1. Optional shell integration:"
echo "     $ROOT/scripts/install_shell_integration.sh"
echo "  2. Run doctor:"
echo "     $ROOT/bin/mc.sh doctor"
echo "  3. Show status:"
echo "     $ROOT/bin/mc.sh status"
