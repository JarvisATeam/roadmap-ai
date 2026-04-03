#!/usr/bin/env bash
# Idempotency helper for dispatch_runner.sh
# Provides deterministic keys, persistence, and replay detection.

IDEMPOTENCY_DIR="${OUTPUT_DIR:-.}"
IDEMPOTENCY_LOG="${IDEMPOTENCY_DIR}/dispatch_idempotency.jsonl"

# Generate deterministic key using verb + args + date bucket to avoid unbounded growth.
idem_generate_key() {
    local verb="$1"
    local args="${2:-}"
    local bucket
    bucket=$(date -u +"%Y-%m-%d")
    local raw hash
    raw=$(printf "%s%s%s" "$verb" "$args" "$bucket")
    hash=$(printf "%s" "$raw" | shasum -a 256 | awk '{print $1}' | cut -c1-24)
    echo "${verb}:${bucket}:${hash}"
}

idem_log_exists() {
    local key="$1"
    [[ -f "$IDEMPOTENCY_LOG" ]] && grep -q "\"key\":\"${key}\"" "$IDEMPOTENCY_LOG"
}

idem_log_entry() {
    local key="$1"
    [[ -f "$IDEMPOTENCY_LOG" ]] && grep "\"key\":\"${key}\"" "$IDEMPOTENCY_LOG" | tail -1
}

idem_append_record() {
    local record="$1"
    mkdir -p "$IDEMPOTENCY_DIR"
    echo "$record" >> "$IDEMPOTENCY_LOG"
}

idem_record() {
    local key="$1"
    local verb="$2"
    local status="$3"
    local replay_count="$4"
    local first_seen="$5"
    local last_seen="$6"
    local is_replay="$7"
    python3 - "$key" "$verb" "$status" "$replay_count" "$first_seen" "$last_seen" "$is_replay" <<'PY'
import json, sys
key, verb, status, replay_count, first_seen, last_seen, is_replay = sys.argv[1:8]
record = {
    "key": key,
    "verb": verb,
    "status": status,
    "first_seen": first_seen,
    "last_seen": last_seen,
    "replay_count": int(replay_count),
    "is_replay": is_replay == "true",
}
json.dump(record, sys.stdout)
print()
PY
}

idem_guard() {
    local verb="$1"
    local args="${2:-}"
    local key
    key=$(idem_generate_key "$verb" "$args")
    if idem_log_exists "$key"; then
        local entry
        entry=$(idem_log_entry "$key")
        local prev_status
        prev_status=$(printf '%s' "$entry" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('status','unknown'))")
        local first_seen
        first_seen=$(printf '%s' "$entry" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('first_seen',''))")
        local replay_count
        replay_count=$(printf '%s' "$entry" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('replay_count',0))")
        local now
        now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        replay_count=$((replay_count + 1))
        if [[ "$prev_status" == "success" || "$prev_status" == "replayed" ]]; then
            echo "[IDEMPOTENCY] Replay detected for $verb (key=$key). Skipping execution." >&2
            local rec
            rec=$(idem_record "$key" "$verb" "replayed" "$replay_count" "$first_seen" "$now" true)
            idem_append_record "$rec"
            return 1
        fi
        echo "[IDEMPOTENCY] Previous $verb failed (status=$prev_status). Retrying." >&2
    fi
    echo "$key"
    return 0
}

idem_mark_success() {
    local key="$1"
    local verb="$2"
    local now
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local replay_count=0
    local first_seen="$now"
    local is_replay=false
    if idem_log_exists "$key"; then
        local entry
        entry=$(idem_log_entry "$key")
        first_seen=$(printf '%s' "$entry" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('first_seen',''))")
        replay_count=$(printf '%s' "$entry" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('replay_count',0))")
        replay_count=$((replay_count + 1))
        is_replay=true
    fi
    local rec
    rec=$(idem_record "$key" "$verb" "success" "$replay_count" "$first_seen" "$now" "$is_replay")
    idem_append_record "$rec"
}

idem_mark_failure() {
    local key="$1"
    local verb="$2"
    local now
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local replay_count=0
    local first_seen="$now"
    local is_replay=false
    if idem_log_exists "$key"; then
        local entry
        entry=$(idem_log_entry "$key")
        first_seen=$(printf '%s' "$entry" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('first_seen',''))")
        replay_count=$(printf '%s' "$entry" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('replay_count',0))")
        replay_count=$((replay_count + 1))
        is_replay=true
    fi
    local rec
    rec=$(idem_record "$key" "$verb" "failed" "$replay_count" "$first_seen" "$now" "$is_replay")
    idem_append_record "$rec"
}
