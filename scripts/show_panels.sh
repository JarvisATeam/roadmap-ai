#!/usr/bin/env bash
# show_panels.sh — Pretty terminal view of all Roadmap-AI panels
# Stdlib only. No external deps.

PANEL_DIR="${ROADMAP_AI_DIR:-$HOME/roadmap-ai}/panel_output"
INDENT="  "

# Colors
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    NC='\033[0m'
    BOLD='\033[1m'
else
    GREEN='' YELLOW='' RED='' BLUE='' CYAN='' NC='' BOLD=''
fi

check() {
    [ -f "$PANEL_DIR/$1" ]
}

jq_extract() {
    # Extract single value from JSON using stdlib sed + grep (no jq dependency)
    local file="$1"
    local key="$2"
    grep -o "\"${key}\"[[:space:]]*:[[:space:]]*[^,}]*" "$file" 2>/dev/null \
        | head -1 \
        | sed 's/.*:[[:space:]]*//' \
        | tr -d '"' \
        | tr -d "'"
}

jq_array() {
    local file="$1"
    local key="$2"
    local count
    count=$(grep -o "\"${key}\"" "$file" 2>/dev/null | wc -l | tr -d ' ')
    echo "$count"
}

echo ""
echo -e "${BOLD}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║    ROADMAP-AI — Panel Overview          ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════╝${NC}"
echo ""
echo "  Generated: $(date +%Y-%m-%d\ %H:%M)"
echo ""

# ── Smart Next ────────────────────────────────────────
echo -e "${CYAN}▸ SMART NEXT${NC}"
echo -e "${INDENT}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check "smart_next.json"; then
    task_name=$(jq_extract "$PANEL_DIR/smart_next.json" "task_name")
    task_id=$(jq_extract "$PANEL_DIR/smart_next.json" "task_id")
    mission_id=$(jq_extract "$PANEL_DIR/smart_next.json" "mission_id")
    score=$(jq_extract "$PANEL_DIR/smart_next.json" "score")

    if [ -n "$task_name" ]; then
        echo -e "${GREEN}${INDENT}✓ Top task: ${BOLD}${task_name}${NC}"
        [ -n "$task_id" ] && echo -e "${INDENT}  ID:    ${task_id}"
        [ -n "$mission_id" ] && echo -e "${INDENT}  Mission: ${mission_id}"
        [ -n "$score" ] && echo -e "${INDENT}  Score: ${score}"
    else
        echo -e "${YELLOW}${INDENT}○ No recommendations${NC}"
    fi
else
    echo -e "${RED}${INDENT}✗ smart_next.json missing — run standup${NC}"
fi
echo ""

# ── Risks ─────────────────────────────────────────────
echo -e "${CYAN}▸ RISKS${NC}"
echo -e "${INDENT}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check "risks.json"; then
    warnings=$(grep -c '"severity"' "$PANEL_DIR/risks.json" 2>/dev/null || echo 0)
    blocked=$(jq_extract "$PANEL_DIR/risks.json" "blocked_tasks")
    overdue=$(jq_extract "$PANEL_DIR/risks.json" "overdue_tasks")

    if [ "$warnings" -gt 0 ] 2>/dev/null; then
        echo -e "${YELLOW}${INDENT}⚠  ${warnings} warnings${NC}"
    else
        echo -e "${GREEN}${INDENT}✓ No warnings${NC}"
    fi

    if [ -n "$blocked" ] && [ "$blocked" -gt 0 ] 2>/dev/null; then
        echo -e "${RED}${INDENT}✗ ${blocked} blocked tasks${NC}"
    else
        echo -e "${GREEN}${INDENT}✓ No blocked tasks${NC}"
    fi

    if [ -n "$overdue" ] && [ "$overdue" -gt 0 ] 2>/dev/null; then
        echo -e "${RED}${INDENT}✗ ${overdue} overdue tasks${NC}"
    else
        echo -e "${GREEN}${INDENT}✓ No overdue tasks${NC}"
    fi
else
    echo -e "${RED}${INDENT}✗ risks.json missing — run standup${NC}"
fi
echo ""

# ── Decisions ─────────────────────────────────────────
echo -e "${CYAN}▸ DECISIONS${NC}"
echo -e "${INDENT}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check "decisions.json"; then
    count=$(jq_array "$PANEL_DIR/decisions.json" "decision_id")
    if [ -n "$count" ] && [ "$count" -gt 0 ] 2>/dev/null; then
        echo -e "${GREEN}${INDENT}✓ ${count} decisions logged${NC}"
        latest=$(grep '"text"' "$PANEL_DIR/decisions.json" 2>/dev/null | head -1 | \
                 sed 's/.*"text"[[:space:]]*:[[:space:]]*//' | tr -d '",')
        [ -n "$latest" ] && echo -e "${INDENT}  Latest: ${latest:0:60}…"
    else
        echo -e "${YELLOW}${INDENT}○ No decisions yet${NC}"
    fi
else
    echo -e "${RED}${INDENT}✗ decisions.json missing${NC}"
fi
echo ""

# ── Status ────────────────────────────────────────────
echo -e "${CYAN}▸ STATUS${NC}"
echo -e "${INDENT}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check "status.json"; then
    missions=$(jq_extract "$PANEL_DIR/status.json" "missions_count")
    tasks=$(jq_extract "$PANEL_DIR/status.json" "tasks_count")
    blocked=$(jq_extract "$PANEL_DIR/status.json" "blocked_count")

    echo -e "${INDENT}Missions: ${missions:-0}"
    echo -e "${INDENT}Tasks:    ${tasks:-0}"
    echo -e "${INDENT}Blocked:  ${blocked:-0}"
else
    echo -e "${RED}${INDENT}✗ status.json missing — run export-panels${NC}"
fi
echo ""

# ── Daily Report ─────────────────────────────────────
echo -e "${CYAN}▸ DAILY REPORT${NC}"
echo -e "${INDENT}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check "daily_report.json"; then
    completed=$(jq_extract "$PANEL_DIR/daily_report.json" "completed")
    remaining=$(jq_extract "$PANEL_DIR/daily_report.json" "remaining")
    energy=$(jq_extract "$PANEL_DIR/daily_report.json" "energy_level")

    [ -n "$completed" ] && echo -e "${GREEN}${INDENT}✓ ${completed} completed${NC}"
    [ -n "$remaining" ] && echo -e "${INDENT}  → ${remaining} remaining"
    [ -n "$energy" ] && echo -e "${INDENT}  Energy: ${energy}"
else
    echo -e "${YELLOW}${INDENT}○ Daily report not generated${NC}"
fi
echo ""

# ── Footer ────────────────────────────────────────────
echo -e "${BOLD}────────────────────────────────────────${NC}"
echo -e "  ${BOLD}Commands:${NC}"
echo -e "    ${INDENT}standup       ${BLUE}→${NC} morning briefing"
echo -e "    ${INDENT}export-panels ${BLUE}→${NC} all 5 panels"
echo -e "    ${INDENT}closeout      ${BLUE}→${NC} end-of-day + commit"
echo -e "    ${INDENT}show_panels   ${BLUE}→${NC} this view"
echo ""
