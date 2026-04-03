#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_DIR="$ROOT/.ai"
MISSIONS_DIR="$AI_DIR/missions"
OUTPUT="$AI_DIR/dashboard.json"
SCHEMA="$ROOT/docs/dashboard_schema.json"
ROADMAP_CLI="$HOME/roadmap-ai/venv/bin/roadmap"

if [[ ! -x "$ROADMAP_CLI" ]]; then
  echo "❌ Roadmap CLI ikke funnet på $ROADMAP_CLI" >&2
  exit 1
fi

export ROOT AI_DIR MISSIONS_DIR OUTPUT SCHEMA ROADMAP_CLI

python3 <<'PY'
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(os.environ["ROOT"])
ai_dir = pathlib.Path(os.environ["AI_DIR"])
missions_dir = pathlib.Path(os.environ["MISSIONS_DIR"])
output_path = pathlib.Path(os.environ["OUTPUT"])
schema_path = pathlib.Path(os.environ["SCHEMA"])
roadmap_cli = os.environ["ROADMAP_CLI"]

def parse_mission(md_path: pathlib.Path):
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    mission = {
        "file": str(md_path.relative_to(root)),
        "id": None,
        "name": None,
        "status": None,
        "priority": None,
        "started": None,
        "progress": {"done": 0, "total": 0},
        "acceptance": [],
        "files": []
    }
    title_match = re.match(r"#\s*Mission\s+(\d+):\s*(.+)", lines[0])
    if title_match:
        mission["id"] = title_match.group(1)
        mission["name"] = title_match.group(2).strip()
    for line in lines:
        lower = line.strip().lower()
        if lower.startswith("## status"):
            mission["status"] = line.split(":", 1)[1].strip().lower()
        elif lower.startswith("## prioritet"):
            mission["priority"] = line.split(":", 1)[1].strip().lower()
        elif lower.startswith("## startet"):
            mission["started"] = line.split(":", 1)[1].strip()
    mission["progress"]["done"] = len(re.findall(r"\[[xX]\]", text))
    mission["progress"]["total"] = len(re.findall(r"\[(?: |x|X)\]", text))

    # acceptance checklist
    in_acceptance = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## akseptansekriterier"):
            in_acceptance = True
            continue
        if in_acceptance and stripped.startswith("## "):
            break
        if in_acceptance and stripped.startswith(("-", "*")) and "[" in stripped:
            title = stripped.split("]", 1)[1].strip(" -")
            done = "[x" in stripped.lower()
            mission["acceptance"].append({"title": title, "done": done})

    # file references
    in_files = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## filer involvert"):
            in_files = True
            continue
        if in_files and stripped.startswith("## "):
            break
        if in_files and stripped.startswith("-"):
            mission["files"].append(stripped.lstrip("- ").strip())

    return mission

def parse_roadmap():
    try:
        proc = subprocess.run(
            [roadmap_cli, "status"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return {"entries": [], "raw": "", "exit_code": 127}

    entries = []
    current = None
    for line in proc.stdout.splitlines():
        if line.startswith("📋"):
            if current:
                entries.append(current)
            current = {"title": line.replace("📋", "").strip(), "details": []}
        elif current is not None and line.strip():
            current["details"].append(line.strip())
    if current:
        entries.append(current)

    return {
        "entries": entries,
        "raw": proc.stdout,
        "exit_code": proc.returncode,
    }

def repo_status(repo_path: pathlib.Path):
    if not repo_path.exists():
        return {"status": "missing", "head": None}
    try:
        rev = subprocess.check_output(
            ["git", "-C", str(repo_path), "rev-parse", "--short", "HEAD"],
            text=True,
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(repo_path), "status", "--short"],
            text=True,
        )
        return {"status": "dirty" if dirty.strip() else "clean", "head": rev}
    except subprocess.CalledProcessError:
        return {"status": "error", "head": None}

active_dir = missions_dir / "active"
missions = []
if active_dir.exists():
    for md in sorted(active_dir.glob("*.md")):
        missions.append(parse_mission(md))

checklist = [
    {"name": "Mission-Control docs exists", "ok": (root / "docs").exists()},
    {"name": "System Prompt loaded", "ok": (root / "docs" / "SYSTEM_PROMPT_BUILD.md").exists()},
    {"name": "Virtual Env active", "ok": pathlib.Path(os.environ["HOME"]).joinpath("roadmap-ai", "venv", "bin", "activate").exists()},
    {"name": "Git initialized", "ok": root.joinpath(".git").exists()},
]

codex_repo = repo_status(pathlib.Path(os.environ["HOME"]) / "roadmap-ai")

timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

dashboard = {
    "version": "0.1",
    "timestamp_utc": timestamp,
    "control_plane": {
        "system_prompt_active": True,
        "workflow_version": "v2.0",
        "clipboard_tool": "pbcopy"
    },
    "engines": {
        "claudobot": {"role": "Spec, Review, Test"},
        "codex": {
            "role": "Impl, Test, Commit",
            "repo_status": codex_repo["status"],
            "last_commit_sha": codex_repo["head"],
        },
        "ginie": {"role": "Orkestrering, Gatekeeper"}
    },
    "missions": missions,
    "roadmap": parse_roadmap(),
    "checklist": checklist,
}

schema_keys = {"version", "timestamp_utc", "control_plane", "engines", "missions", "checklist"}
missing = schema_keys - dashboard.keys()
if missing:
    raise SystemExit(f"Dashboard mangler nøkler: {missing}")

output_path.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Dashboard oppdatert: {output_path}")
PY
