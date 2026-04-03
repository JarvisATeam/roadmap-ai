#!/usr/bin/env bash
# dispatch_runner.sh — Fail-closed Dispatch operator for Roadmap-AI
# Version: 1.0
# Stdlib only. No external dependencies.
# Usage: ./scripts/dispatch_runner.sh <verb> [params...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Config ──────────────────────────────────────────────
REPO_DIR="${ROADMAP_AI_DIR:-$HOME/roadmap-ai}"
VENV_DIR="${REPO_DIR}/venv"
OUTPUT_DIR="${REPO_DIR}/panel_output"
OPS_FILE="${REPO_DIR}/dispatch_ops.yaml"
RULES_FILE="${REPO_DIR}/DISPATCH_RULES.md"
MAX_DURATION="${DISPATCH_MAX_DURATION:-120}"
DATE_STR="$(date +%F)"
TIMESTAMP="$(date -u +%FT%TZ)"

source "${SCRIPT_DIR}/idempotency.sh"

# ── Colors (degrade gracefully if no tty) ───────────────
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' BLUE='' NC=''
fi

# ── Helpers ─────────────────────────────────────────────
log_ok()   { echo -e "${GREEN}[OK]${NC}    $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC}  $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_info() { echo -e "${BLUE}[INFO]${NC}  $1"; }

write_error_json() {
    local op="$1" step="$2" error_msg="$3" exit_code="${4:-1}"
    mkdir -p "$OUTPUT_DIR"
    cat > "${OUTPUT_DIR}/error.json" <<EOF_JSON
{
  "timestamp": "${TIMESTAMP}",
  "op": "${op}",
  "step": "${step}",
  "error": "${error_msg}",
  "exit_code": ${exit_code}
}
EOF_JSON
    log_fail "Error written to ${OUTPUT_DIR}/error.json"
}

usage() {
    echo ""
    echo "Usage: $0 <verb> [params...]"
    echo ""
    echo "Available verbs:"
    echo "  standup                  Morning briefing"
    echo "  forecast <mission_id>   Mission forecast"
    echo "  decide <text> [reason]  Log a decision"
    echo "  export-panels           Export all 5 panels"
    echo "  closeout                End-of-day + git commit"
    echo "  health                  System health check"
    echo ""
    exit 1
}

# ── Pre-flight checks ──────────────────────────────────
preflight() {
    local failed=0

    if [ ! -d "$REPO_DIR" ]; then
        log_fail "Repo not found: $REPO_DIR"
        failed=1
    fi

    if [ ! -d "$VENV_DIR" ]; then
        log_fail "Venv not found: $VENV_DIR"
        failed=1
    fi

    if [ ! -f "$OPS_FILE" ]; then
        log_warn "Ops file not found: $OPS_FILE (running without contract validation)"
    fi

    if [ ! -f "$RULES_FILE" ]; then
        log_warn "Rules file not found: $RULES_FILE"
    fi

    if [ $failed -ne 0 ]; then
        write_error_json "preflight" "check" "Required files/dirs missing" 2
        exit 2
    fi

    # Activate venv (activate scripts often rely on unset vars)
    # shellcheck disable=SC1091
    set +eu
    source "${VENV_DIR}/bin/activate"
    set -eu

    # Ensure output dir
    mkdir -p "$OUTPUT_DIR"

    log_ok "Pre-flight passed"
}

# ── Run a single roadmap command with timeout ───────────
run_step() {
    local op="$1"
    local cmd="$2"
    local output_file="${3:-}"
    local required="${4:-true}"
    local timeout_sec="${5:-$MAX_DURATION}"

    log_info "Running: $cmd"

    local tmp_out
    tmp_out=$(mktemp)
    local tmp_err
    tmp_err=$(mktemp)

    local exit_code=0

    if command -v timeout &>/dev/null; then
        timeout "$timeout_sec" bash -c "cd '$REPO_DIR' && $cmd" \
            >"$tmp_out" 2>"$tmp_err" || exit_code=$?
    elif command -v gtimeout &>/dev/null; then
        gtimeout "$timeout_sec" bash -c "cd '$REPO_DIR' && $cmd" \
            >"$tmp_out" 2>"$tmp_err" || exit_code=$?
    else
        # No timeout available — run without guard
        bash -c "cd '$REPO_DIR' && $cmd" \
            >"$tmp_out" 2>"$tmp_err" || exit_code=$?
    fi

    if [ $exit_code -ne 0 ]; then
        local err_msg
        err_msg=$(cat "$tmp_err" 2>/dev/null || echo "unknown error")
        if [ "$required" = "true" ]; then
            log_fail "Step failed (exit $exit_code): $cmd"
            log_fail "Error: $err_msg"
            write_error_json "$op" "$cmd" "$err_msg" "$exit_code"
            rm -f "$tmp_out" "$tmp_err"
            return 1
        else
            log_warn "Optional step failed (exit $exit_code): $cmd"
            rm -f "$tmp_out" "$tmp_err"
            return 0
        fi
    fi

    # Write output to file if specified
    if [ -n "$output_file" ]; then
        cp "$tmp_out" "${output_file}"
        log_ok "Output → ${output_file}"
    fi

    rm -f "$tmp_out" "$tmp_err"
    return 0
}

# ── Verb implementations ───────────────────────────────

do_standup() {
    log_info "═══ STANDUP — ${DATE_STR} ═══"

    run_step "standup" \
        "roadmap smart next --json" \
        "${OUTPUT_DIR}/smart_next.json" \
        "true" 90 || return 1

    run_step "standup" \
        "roadmap risks --json" \
        "${OUTPUT_DIR}/risks.json" \
        "true" 90 || return 1

    run_step "standup" \
        "roadmap list-decisions --json" \
        "${OUTPUT_DIR}/decisions.json" \
        "false" 60

    log_ok "Standup complete. Outputs in ${OUTPUT_DIR}/"

    echo ""
    echo "── Quick Summary ──"
    echo "Smart Next:"
    head -20 "${OUTPUT_DIR}/smart_next.json" 2>/dev/null || echo "  (no output)"
    echo ""
    echo "Top Risk:"
    head -10 "${OUTPUT_DIR}/risks.json" 2>/dev/null || echo "  (no output)"
    echo ""
}

do_forecast() {
    local mission_id="${1:-}"

    if [ -z "$mission_id" ]; then
        log_fail "forecast requires mission_id parameter"
        log_fail "Usage: $0 forecast M-xxxxxxxx"
        write_error_json "forecast" "param_check" "missing mission_id" 3
        return 1
    fi

    # Validate mission ID format
    if ! echo "$mission_id" | grep -qE '^M-[a-f0-9]{8}$'; then
        log_fail "Invalid mission_id format: $mission_id"
        log_fail "Expected: M-xxxxxxxx (8 hex chars)"
        write_error_json "forecast" "param_check" \
            "invalid mission_id format: $mission_id" 3
        return 1
    fi

    log_info "═══ FORECAST — ${mission_id} ═══"

    run_step "forecast" \
        "roadmap forecast ${mission_id} --json" \
        "${OUTPUT_DIR}/forecast.json" \
        "true" 60 || return 1

    log_ok "Forecast complete."
    cat "${OUTPUT_DIR}/forecast.json" 2>/dev/null
}

do_decide() {
    local decision_text="${1:-}"
    local rationale="${2:-}"

    if [ -z "$decision_text" ]; then
        log_fail "decide requires decision_text parameter"
        log_fail "Usage: $0 decide \"decision text\" [\"rationale\"]"
        write_error_json "decide" "param_check" "missing decision_text" 3
        return 1
    fi

    # Length check
    if [ ${#decision_text} -gt 500 ]; then
        log_fail "decision_text exceeds 500 chars"
        write_error_json "decide" "param_check" \
            "decision_text too long (${#decision_text} > 500)" 3
        return 1
    fi

    log_info "═══ DECIDE ═══"

    local cmd="roadmap decide \"${decision_text}\""
    if [ -n "$rationale" ]; then
        cmd="${cmd} --rationale \"${rationale}\""
    fi

    run_step "decide" "$cmd" "" "true" 30 || return 1

    # Capture latest decision
    run_step "decide" \
        "roadmap list-decisions --limit 1 --json" \
        "${OUTPUT_DIR}/decisions.json" \
        "false" 30

    log_ok "Decision logged."
}

do_export_panels() {
    log_info "═══ EXPORT ALL PANELS ═══"

    local failed=0

    run_step "export-panels" \
        "roadmap smart next --json" \
        "${OUTPUT_DIR}/smart_next.json" \
        "true" 120 || failed=1

    run_step "export-panels" \
        "roadmap risks --json" \
        "${OUTPUT_DIR}/risks.json" \
        "true" 120 || failed=1

    run_step "export-panels" \
        "roadmap status --json" \
        "${OUTPUT_DIR}/status.json" \
        "true" 120 || failed=1

    run_step "export-panels" \
        "roadmap list-decisions --json" \
        "${OUTPUT_DIR}/decisions.json" \
        "true" 120 || failed=1

    run_step "export-panels" \
        "roadmap report --daily --json" \
        "${OUTPUT_DIR}/daily_report.json" \
        "true" 120 || failed=1

    if [ $failed -ne 0 ]; then
        log_fail "Some panels failed to export"
        return 1
    fi

    log_ok "All 5 panels exported to ${OUTPUT_DIR}/"

    echo ""
    echo "── Panel Validation ──"
    for f in smart_next risks status decisions daily_report; do
        local path="${OUTPUT_DIR}/${f}.json"
        if [ -f "$path" ]; then
            local size
            size=$(wc -c < "$path" | tr -d ' ')
            if [ "$size" -gt 2 ]; then
                log_ok "${f}.json (${size} bytes)"
            else
                log_warn "${f}.json is empty or minimal"
            fi
        else
            log_fail "${f}.json missing"
        fi
    done
}

do_closeout() {
    log_info "═══ CLOSEOUT — ${DATE_STR} ═══"

    # Run export-panels first
    do_export_panels || return 1

    # Git commit (optional — won't fail the closeout)
    log_info "Attempting git commit..."

    cd "$REPO_DIR"

    if git diff --quiet panel_output/ 2>/dev/null && \
       git diff --cached --quiet panel_output/ 2>/dev/null; then
        log_info "No changes to commit in panel_output/"
    else
        run_step "closeout" \
            "git add panel_output/" \
            "" "false" 15

        run_step "closeout" \
            "git commit -m \"closeout ${DATE_STR}\"" \
            "" "false" 15
    fi

    log_ok "Closeout complete."
}

do_health() {
    log_info "═══ HEALTH CHECK ═══"

    local checks_passed=0
    local checks_total=0

    # Check 1: repo exists
    checks_total=$((checks_total + 1))
    if [ -d "$REPO_DIR" ]; then
        log_ok "Repo: $REPO_DIR"
        checks_passed=$((checks_passed + 1))
    else
        log_fail "Repo missing: $REPO_DIR"
    fi

    # Check 2: venv exists and activates
    checks_total=$((checks_total + 1))
    if [ -f "${VENV_DIR}/bin/activate" ]; then
        log_ok "Venv: $VENV_DIR"
        checks_passed=$((checks_passed + 1))
    else
        log_fail "Venv missing: $VENV_DIR"
    fi

    # Check 3: roadmap CLI responds
    checks_total=$((checks_total + 1))
    if roadmap status --help &>/dev/null || roadmap --help &>/dev/null; then
        log_ok "CLI: roadmap responsive"
        checks_passed=$((checks_passed + 1))
    else
        log_fail "CLI: roadmap not responding"
    fi

    # Check 4: output dir exists/writable
    checks_total=$((checks_total + 1))
    if [ -d "$OUTPUT_DIR" ] && [ -w "$OUTPUT_DIR" ]; then
        log_ok "Output dir: $OUTPUT_DIR (writable)"
        checks_passed=$((checks_passed + 1))
    else
        log_warn "Output dir: issues (creating...)"
        mkdir -p "$OUTPUT_DIR" && checks_passed=$((checks_passed + 1))
    fi

    # Check 5: git status clean-ish
    checks_total=$((checks_total + 1))
    cd "$REPO_DIR"
    local git_status
    git_status=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ "$git_status" -lt 10 ]; then
        log_ok "Git: ${git_status} uncommitted changes"
        checks_passed=$((checks_passed + 1))
    else
        log_warn "Git: ${git_status} uncommitted changes"
        checks_passed=$((checks_passed + 1))  # warn, don't fail
    fi

    # Check 6: can run status
    checks_total=$((checks_total + 1))
    if run_step "health" "roadmap status --json" \
        "${OUTPUT_DIR}/health_status.json" "true" 30; then
        checks_passed=$((checks_passed + 1))
    fi

    echo ""
    echo "── Health: ${checks_passed}/${checks_total} checks passed ──"

    if [ $checks_passed -eq $checks_total ]; then
        log_ok "System healthy"
        return 0
    elif [ $checks_passed -ge $((checks_total - 1)) ]; then
        log_warn "System mostly healthy"
        return 0
    else
        log_fail "System has issues"
        return 1
    fi
}

# ── Main dispatch ───────────────────────────────────────
main() {
    local verb="${1:-}"

    if [ -z "$verb" ]; then
        usage
    fi

    local raw_args="${*:2}"
    local idem_active=0
    local idem_key=""

    case "$verb" in
        standup|forecast|decide|export-panels|closeout)
            if ! idem_key=$(idem_guard "$verb" "$raw_args"); then
                log_info "Idempotent replay detected for $verb. Exiting without execution."
                exit 0
            fi
            idem_active=1
            trap 'idem_mark_failure "$idem_key" "$verb"' ERR
            ;;
        *)
            ;;
    esac

    # Shift past verb to get params
    shift

    # Pre-flight (validates repo, venv, dirs)
    preflight

    # Dispatch to verb
    case "$verb" in
        standup)
            do_standup "$@"
            ;;
        forecast)
            do_forecast "$@"
            ;;
        decide)
            do_decide "$@"
            ;;
        export-panels)
            do_export_panels "$@"
            ;;
        closeout)
            do_closeout "$@"
            ;;
        health)
            do_health "$@"
            ;;
        *)
            log_fail "Unknown verb: $verb"
            log_fail "This operation is not defined in the ops contract."
            echo ""
            usage
            ;;
    esac

    if [ $idem_active -eq 1 ]; then
        idem_mark_success "$idem_key" "$verb"
        trap - ERR
    fi
}

main "$@"
