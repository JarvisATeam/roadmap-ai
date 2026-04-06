#!/usr/bin/env python3
import json
import os
import hashlib
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOOK_KEY = os.getenv("SYMBIOSIS_HOOK_KEY", "")
PANEL_DIR = Path(os.getenv("SYMBIOSIS_PANEL_DIR", "/Users/christerolsen/roadmap-ai/panel_output"))
EVENTS_FILE = PANEL_DIR / "symbiosis_events.jsonl"
STATUS_FILE = PANEL_DIR / "symbiosis_status.json"
PORT = int(os.getenv("SYMBIOSIS_HOOK_PORT", "9191"))

PANEL_DIR.mkdir(parents=True, exist_ok=True)

def _utc():
    return datetime.now(timezone.utc).isoformat()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send(self, code: int, payload: dict):
        raw = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path != "/health":
            self._send(404, {"ok": False})
            return
        self._send(200, {"ok": True, "service": "symbiosis-hook", "port": PORT})

    def do_POST(self):
        if self.path != "/hooks/symbiosis":
            self._send(404, {"ok": False})
            return
        if HOOK_KEY and self.headers.get("X-Symbiosis-Key", "") != HOOK_KEY:
            self._send(401, {"ok": False, "error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode() or "{}")
        except:
            self._send(400, {"ok": False})
            return

        event = {
            "event_id": hashlib.sha256(json.dumps({"ts": _utc(), "kind": data.get("kind", "")}, sort_keys=True).encode()).hexdigest()[:16],
            "ts": _utc(),
            "kind": data.get("kind", "unknown"),
            "payload": data.get("payload", {}),
        }

        with EVENTS_FILE.open("a") as f:
            f.write(json.dumps(event) + "\n")

        STATUS_FILE.write_text(json.dumps({"ok": True, "last_event": event["event_id"], "ts": event["ts"]}, indent=2))
        self._send(200, {"ok": True, "event_id": event["event_id"]})

if __name__ == "__main__":
    print(f"Starting hook server on port {PORT}")
    print(f"Events: {EVENTS_FILE}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
