#!/bin/bash
# Export panels to local panel_output directory
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${ROOT_DIR}/panel_output"

cd "$ROOT_DIR"

printf "\n📊 Exporting panel data to %s\n\n" "$OUTPUT_DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    printf "❌ venv not found. Run 'python -m venv venv && source venv/bin/activate && pip install -e .'\n"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

printf "🎯 Exporting smart next...\n"
roadmap smart next --json > "$OUTPUT_DIR/smart_next.json"

printf "⚠️  Exporting risks...\n"
roadmap risks --json > "$OUTPUT_DIR/risks.json"

printf "📈 Exporting status...\n"
roadmap status --json > "$OUTPUT_DIR/status.json"

printf "📝 Exporting decisions...\n"
roadmap list-decisions --limit 10 --json > "$OUTPUT_DIR/decisions.json"

printf "📊 Exporting daily report...\n"
roadmap report --daily --json > "$OUTPUT_DIR/daily_report.json"

printf "\n✅ Export complete!\n\n"
printf "📁 Generated files:\n"
ls -lh "$OUTPUT_DIR"

printf "\n🧪 Validating exports...\n"
roadmap validate-all "$OUTPUT_DIR"

printf "\n✨ All panels exported and validated.\n"
printf "📖 Next steps:\n"
printf "   - View JSON: cat %s/smart_next.json | jq\n" "$OUTPUT_DIR"
printf "   - Copy to dashboard data directory if needed\n"
printf "   - Set up cron: %s/scripts/setup_cron_local.sh\n\n" "$ROOT_DIR"
