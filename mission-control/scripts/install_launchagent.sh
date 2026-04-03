#!/usr/bin/env bash
# install_launchagent.sh — install/update LaunchAgent for roadmap-ai standup
set -euo pipefail

PLIST_NAME="com.roadmap-ai.morning-standup"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PROJECT_DIR="${ROADMAP_AI_DIR:-$HOME/roadmap-ai}"
LOG_FILE="$HOME/dispatch.log"
ERR_FILE="$HOME/dispatch_error.log"
COMMAND="cd ${PROJECT_DIR} && source venv/bin/activate && ./scripts/dispatch_runner.sh standup"
COMMAND_XML=${COMMAND//&/&amp;}

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

launchctl bootout gui/$(id -u) "$PLIST_PATH" >/dev/null 2>&1 || true
mkdir -p "$(dirname "$PLIST_PATH")"

cat >"$PLIST_PATH" <<EOF_INNER
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>${COMMAND_XML}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>${LOG_FILE}</string>
    <key>StandardErrorPath</key>
    <string>${ERR_FILE}</string>
</dict>
</plist>
EOF_INNER

plutil -lint "$PLIST_PATH" >/dev/null
launchctl bootstrap gui/$(id -u) "$PLIST_PATH"

echo "✅ LaunchAgent installed: $PLIST_NAME"
echo "   Schedule: 08:00 daily"
echo "   Logs: $LOG_FILE"
echo "   Test: launchctl kickstart gui/$(id -u)/$PLIST_NAME"
