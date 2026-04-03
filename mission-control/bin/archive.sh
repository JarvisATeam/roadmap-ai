#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ACTIVE_DIR="$ROOT/.ai/missions/active"
ARCHIVE_DIR="$ROOT/.ai/missions/archive"

usage() {
  cat <<USAGE
Mission lifecycle management.

Usage:
  mc archive <mission-file>
  mc restore <mission-file>
  mc list archived
 
Examples:
  mc archive 001-my-feature.md
  mc restore 001-my-feature.md
  mc list archived
USAGE
}

cmd_archive() {
  local file="$1"
  local src="$ACTIVE_DIR/$file"
  local dst="$ARCHIVE_DIR/$file"
  if [ ! -f "$src" ]; then
    local base=$(basename "$file")
    if [ -f "$ACTIVE_DIR/$base" ]; then
      src="$ACTIVE_DIR/$base"
      dst="$ARCHIVE_DIR/$base"
    else
      echo "Error: Mission not found in active: $file" >&2
      ls "$ACTIVE_DIR" 2>/dev/null | head -10 >&2
      exit 1
    fi
  fi
  mkdir -p "$ARCHIVE_DIR"
  cp "$src" "$dst" && rm "$src"
  sed -i '' 's/Status:** active/Status:** archived/' "$dst" 2>/dev/null || true
  echo "✅ Archived: $(basename "$dst")"
}

cmd_restore() {
  local file="$1"
  local src="$ARCHIVE_DIR/$file"
  local dst="$ACTIVE_DIR/$file"
  if [ ! -f "$src" ]; then
    local base=$(basename "$file")
    if [ -f "$ARCHIVE_DIR/$base" ]; then
      src="$ARCHIVE_DIR/$base"
      dst="$ACTIVE_DIR/$base"
    else
      echo "Error: Mission not found in archive: $file" >&2
      ls "$ARCHIVE_DIR" 2>/dev/null | head -10 >&2
      exit 1
    fi
  fi
  mkdir -p "$ACTIVE_DIR"
  cp "$src" "$dst" && rm "$src"
  sed -i '' 's/Status:** archived/Status:** active/' "$dst" 2>/dev/null || true
  echo "✅ Restored: $(basename "$dst")"
}

cmd_list() {
  echo "=== ARCHIVED MISSIONS ==="
  local count=0
  for f in "$ARCHIVE_DIR"/*.md; do
    [ -f "$f" ] || continue
    echo "  $(basename "$f")"
    count=$((count+1))
  done
  [ $count -eq 0 ] && echo "  (none)"
  echo "Total: $count archived"
}

case "$1" in
  archive)
    shift
    [ $# -ge 1 ] || { echo "Missing mission file" >&2; exit 1; }
    cmd_archive "$1"
    ;;
  restore)
    shift
    [ $# -ge 1 ] || { echo "Missing mission file" >&2; exit 1; }
    cmd_restore "$1"
    ;;
  list)
    shift
    if [ "${1:-}" = archived ]; then
      cmd_list
    else
      echo "Unknown list type; use 'mc list archived'" >&2
      exit 1
    fi
    ;;
  *)
    usage
    exit 1
    ;;
esac
