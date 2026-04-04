#!/usr/bin/env python3
"""
Remote Health Monitor — Monitor Tailscale nodes
Usage: python scripts/remote_health_monitor.py
"""
import subprocess
import json
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "panel_output" / "remote_health.json"

# Nodes to monitor
NODES = [
    {"name": "aimigo", "ip": "100.97.199.60", "description": "Jetson - AImigo"},
    {"name": "macbook-pro-3", "ip": "100.80.160.91", "description": "MacBook Pro 3"},
]

def check_ping(ip, timeout=2):
    """Ping a node and return latency in ms"""
    try:
        start = time.time()
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout * 1000), ip],
            capture_output=True,
            timeout=timeout + 1
        )
        elapsed = (time.time() - start) * 1000
        
        if result.returncode == 0:
            # Parse actual ping time from output
            output = result.stdout.decode()
            if "time=" in output:
                ping_time = output.split("time=")[1].split()[0]
                return {"reachable": True, "latency_ms": float(ping_time)}
        
        return {"reachable": True, "latency_ms": elapsed}
    except:
        return {"reachable": False, "latency_ms": None}

def check_ssh(ip, port=22, timeout=2):
    """Check if SSH port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    node_status = []
    
    for node in NODES:
        ping_result = check_ping(node["ip"])
        ssh_open = check_ssh(node["ip"]) if ping_result["reachable"] else False
        
        status = "online" if ping_result["reachable"] else "offline"
        if ping_result["reachable"] and not ssh_open:
            status = "degraded"
        
        node_status.append({
            "name": node["name"],
            "ip": node["ip"],
            "description": node["description"],
            "status": status,
            "reachable": ping_result["reachable"],
            "latency_ms": ping_result["latency_ms"],
            "ssh_available": ssh_open,
            "last_check": datetime.now(timezone.utc).isoformat()
        })
    
    # Calculate summary
    online = sum(1 for n in node_status if n["status"] == "online")
    degraded = sum(1 for n in node_status if n["status"] == "degraded")
    offline = sum(1 for n in node_status if n["status"] == "offline")
    
    output = {
        "roadmap_version": "0.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": "remote-health-monitor",
        "data": {
            "nodes": node_status,
            "summary": {
                "total": len(NODES),
                "online": online,
                "degraded": degraded,
                "offline": offline
            }
        },
        "metadata": {
            "status": "success",
            "monitored_nodes": len(NODES)
        }
    }
    
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2))
    
    print(f"✅ Monitored {len(NODES)} nodes")
    print(f"   Online: {online} | Degraded: {degraded} | Offline: {offline}")
    print(f"   Output: {OUTPUT}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
