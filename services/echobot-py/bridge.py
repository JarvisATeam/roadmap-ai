from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ECHOBOT = ROOT / "echobot_v3.py"

def run_mode(mode: str, extra: list[str] | None = None) -> dict:
    cmd = [sys.executable, str(ECHOBOT), "--mode", mode]
    if extra:
        cmd.extend(extra)
    res = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "ok": res.returncode == 0,
        "mode": mode,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "returncode": res.returncode,
    }

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stats"
    print(json.dumps(run_mode(mode), ensure_ascii=False))
