#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES_DIR="$ROOT/templates"
MISSIONS_DIR="$ROOT/.ai/missions/active"

usage() {
  cat <<USAGE
Create a new mission from template.

Usage:
  mc new <type> <name>
  mc new feature my-feature
  mc new bugfix login-error
  mc new research caching-strategy

Types:
  feature   New feature development
  bugfix    Bug fix or issue resolution
  research  Investigation or learning task
USAGE
}

if [ $# -lt 2 ]; then
  usage
  exit 1
fi

TYPE="$1"
shift
NAME="$*"

case "$TYPE" in
  feature|bugfix|research)
    TEMPLATE="$TEMPLATES_DIR/${TYPE}.md"
    ;;
  *)
    echo "Error: Unknown type '$TYPE'" >&2
    echo "Valid types: feature, bugfix, research" >&2
    exit 1
    ;;
esac

if [ ! -f "$TEMPLATE" ]; then
  echo "Error: Template not found: $TEMPLATE" >&2
  exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_PREFIX=$(date +"%Y%m%d")
SLUG=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
ID="${DATE_PREFIX}-${SLUG}"

mkdir -p "$MISSIONS_DIR"
NEXT_NUM=$(ls "$MISSIONS_DIR" 2>/dev/null | wc -l | tr -d ' ')
SEQ=$(printf "%03d" $((NEXT_NUM + 1)))
FILENAME="${SEQ}-${SLUG}.md"
FILEPATH="$MISSIONS_DIR/$FILENAME"

if [ -f "$FILEPATH" ]; then
  echo "Error: Mission already exists: $FILEPATH" >&2
  exit 1
fi

TITLE="$NAME"
sed -e "s/{title}/$TITLE/g" \
    -e "s/{id}/$ID/g" \
    -e "s/{created_at}/$TIMESTAMP/g" \
    "$TEMPLATE" > "$FILEPATH"

echo "✅ Created mission: $FILEPATH"
echo "Type: $TYPE"
echo "Name: $NAME"
echo "ID: $ID"
echo
