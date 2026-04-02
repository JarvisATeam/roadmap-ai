#!/bin/bash
# Auto-deployment script for ~/roadmapai integration with graceful fallback
set -e

ROADMAPAI_DIR="${ROADMAPAI_DIR:-$HOME/roadmapai}"
ROADMAP_AI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

printf "\n🚀 Deploying roadmap-ai panels to %s\n\n" "$ROADMAPAI_DIR"

copy_with_fallback() {
    local src="$1"
    local dest="$2"
    local label="$3"

    if cp "$src" "$dest" 2>/dev/null; then
        printf "✅ %s deployed to %s\n" "$label" "$dest"
        return 0
    else
        printf "⚠️  %s deployment failed (permission denied)\n" "$label"
        printf "    Manual copy required: cp %s %s\n" "$src" "$dest"
        return 1
    fi
}

mkdir -p "$ROADMAPAI_DIR/bin" 2>/dev/null || true
mkdir -p "$ROADMAPAI_DIR/config" 2>/dev/null || true
mkdir -p "$ROADMAPAI_DIR/data/roadmap" 2>/dev/null || true

if copy_with_fallback \
    "$ROADMAP_AI_DIR/scripts/roadmap_panels.sh" \
    "$ROADMAPAI_DIR/bin/roadmap_panels.sh" \
    "Wrapper script"; then
    chmod +x "$ROADMAPAI_DIR/bin/roadmap_panels.sh" 2>/dev/null || true
fi

copy_with_fallback \
    "$ROADMAP_AI_DIR/scripts/roadmap_panels.json" \
    "$ROADMAPAI_DIR/config/roadmap_panels.json" \
    "Panel config" || true

printf "\n🧪 Testing deployment...\n"

if [ -x "$ROADMAPAI_DIR/bin/roadmap_panels.sh" ]; then
    printf "✅ Wrapper script is executable\n"
    if cd "$ROADMAPAI_DIR" && bin/roadmap_panels.sh all 2>/dev/null; then
        printf "✅ Panel refresh succeeded\n"
        printf "\n📊 Generated panels:\n"
        ls -lh "$ROADMAPAI_DIR/data/roadmap" 2>/dev/null || printf "   No panel data yet\n"
    else
        printf "⚠️  Panel refresh failed - check logs above\n"
    fi
else
    printf "⚠️  Deployment incomplete - using local fallback\n"
    printf "   Run: %s/scripts/export_panels_local.sh\n" "$ROADMAP_AI_DIR"
fi

printf "\n✨ Deployment script complete.\n"
printf "📖 Next steps:\n"
printf "   1. Verify: ls -lh %s/data/roadmap/\n" "$ROADMAPAI_DIR"
printf "   2. Setup cron: %s/scripts/setup_cron.sh\n" "$ROADMAP_AI_DIR"
printf "   3. Test refresh: cd %s && bin/roadmap_panels.sh all\n\n" "$ROADMAPAI_DIR"
