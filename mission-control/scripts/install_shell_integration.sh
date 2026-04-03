#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SHELL_NAME="$(basename "${SHELL:-}")"
ZSHRC="$HOME/.zshrc"
BASHRC="$HOME/.bashrc"
PROFILE_SNIPPET_BEGIN="# >>> mission-control >>>"
PROFILE_SNIPPET_END="# <<< mission-control <<<"

snippet() {
  cat <<SNIP
$PROFILE_SNIPPET_BEGIN
export MISSION_CONTROL_ROOT="$ROOT"
alias mc="$ROOT/bin/mc.sh"
[ -f "$ROOT/completions/mc.bash" ] && source "$ROOT/completions/mc.bash"
[ -f "$ROOT/completions/mc.zsh" ] && source "$ROOT/completions/mc.zsh"
$PROFILE_SNIPPET_END
SNIP
}

install_into_file() {
  local rcfile="$1"
  if ! touch "$rcfile" >/dev/null 2>&1; then
    echo "[shell] cannot modify $rcfile (permission denied)"
    return 1
  fi
  if grep -q "$PROFILE_SNIPPET_BEGIN" "$rcfile" 2>/dev/null; then
    echo "[shell] snippet already present in $rcfile"
  else
    {
      echo
      snippet
      echo
    } >> "$rcfile"
    echo "[shell] installed snippet into $rcfile"
  fi
}

echo "[shell] root: $ROOT"
echo "[shell] detected shell: ${SHELL_NAME:-unknown}"

case "${SHELL_NAME:-}" in
  zsh)
    install_into_file "$ZSHRC" || true
    ;;
  bash)
    install_into_file "$BASHRC" || true
    ;;
  *)
    echo "[shell] unknown shell; attempting both .zshrc and .bashrc"
    install_into_file "$ZSHRC" || true
    install_into_file "$BASHRC" || true
    ;;
esac

echo
echo "[shell] done"
echo "[shell] if snippet was not installed, manually add the following to your shell rc file:"
snippet
