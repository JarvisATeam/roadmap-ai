#!/usr/bin/env python3
"""
GINIE CLOSEOUT AGENT v1.0
Autonomt closeout-system: skanner mapper, prosesser og filer.
Ingen git nødvendig. Ingen manuelle sjekklister.
Output: strukturert rapport + handlingsplan per vindu.
"""
import os, sys, subprocess, json, hashlib, shutil
from pathlib import Path
from datetime import datetime

NOW    = datetime.now().strftime("%Y-%m-%d %H:%M")
BASE   = Path.home() / ".ginie" / "closeout"
LOG    = BASE / f"closeout_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
BASE.mkdir(parents=True, exist_ok=True)

ROED="\033[91m"; GROE="\033[92m"; GULL="\033[93m"; BLAA="\033[94m"
BOLD="\033[1m"; RESET="\033[0m"

# Filtyper som er verdifulle og MÅ bevares
BEVAR_EXT = {
    ".py",".js",".ts",".jsx",".tsx",".sh",".env",".json",
    ".yaml",".yml",".toml",".md",".sql",".tf",".go",".rs"
}
# Filtyper som er søppel
SOPP_EXT = {
    ".DS_Store",".pyc",".log",".tmp",".cache",".swp",
    ".egg-info",".dist-info"
}
SOPP_DIRS = {
    "__pycache__","node_modules",".git",".venv","venv",
    "dist","build",".next",".cache"
}

def kjor(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except:
        return ""

def scan_procs():
    """Finn alle relevante prosesser med mappeinfo"""
    out = kjor("ps aux")
    procs = []
    for linje in out.splitlines()[1:]:
        deler = linje.split(None, 10)
        if len(deler) < 11: continue
        cmd = deler[10]
        # Filtrer ut systemprocs
        if any(x in cmd for x in ["/System/","/usr/sbin/","launchd","WindowServer","Dock"]):
            continue
        if any(x in cmd for x in ["python","node","npm","ssh","stripe","tail","watch"]):
            procs.append({"pid":deler[1],"cmd":cmd.strip(),"cpu":deler[2],"mem":deler[3]})
    return procs

def scan_mappe(sti: Path, dybde=0, max_dybde=3):
    """Rekursiv mappeskanning — returnerer verdivurdering"""
    if dybde > max_dybde: return {"verdi":0,"filer":[],"subdir":[]}
    if not sti.exists() or sti.name in SOPP_DIRS: return {"verdi":0,"filer":[],"subdir":[]}

    verdifiler = []
    sopp = []
    sub = []

    try:
        for item in sti.iterdir():
            if item.is_symlink(): continue
            if item.is_dir():
                if item.name not in SOPP_DIRS:
                    sub.append(scan_mappe(item, dybde+1, max_dybde))
            elif item.is_file():
                ext = item.suffix.lower()
                if ext in BEVAR_EXT:
                    try:
                        st = item.stat()
                        verdifiler.append({
                            "fil": str(item),
                            "størrelse": st.st_size,
                            "endret": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                        })
                    except: pass
                elif ext in SOPP_EXT or item.name.startswith("."):
                    sopp.append(str(item))
    except PermissionError:
        pass

    verdi = len(verdifiler) * 10 + sum(s.get("verdi",0) for s in sub)
    return {"sti":str(sti),"verdi":verdi,"verdifiler":verdifiler,"sopp":sopp,"subdir":sub}

def klasifiser_proc(cmd):
    """Klasifiser prosess og finn tilhørende mappe"""
    info = {"type":"ukjent","mappe":None,"handling":None}
    if "ssh" in cmd:
        info["type"] = "SSH-tilkobling"
        info["handling"] = "exit → bekreft supervisord kjører"
    elif "npm" in cmd or "node" in cmd:
        deler = cmd.split()
        for d in deler:
            p = Path(d)
            if p.exists() and p.is_dir(): info["mappe"] = str(p); break
        info["type"] = "Node.js prosess"
        info["handling"] = "Ctrl+C → git-sjekk → lukk"
    elif "python" in cmd:
        deler = cmd.split()
        for d in deler:
            p = Path(d)
            if p.exists() and p.suffix == ".py": info["mappe"] = str(p.parent); break
        info["type"] = "Python prosess"
        info["handling"] = "Ctrl+C → sjekk output"
    elif "stripe" in cmd:
        info["type"] = "Stripe webhook tunnel"
        info["handling"] = "pkill -f 'stripe listen'"
    elif "tail" in cmd or "watch" in cmd:
        info["type"] = "Log-watcher"
        info["handling"] = "Ctrl+C — stateless, trygt"
    return info

def vurder_mappe_handling(scan):
    """Bestem hva som skal gjøres med en mappe basert på skanning"""
    if not scan or scan.get("verdi",0) == 0:
        return "SLETT/IGNORER — ingen verdifulle filer"
    filer = scan.get("verdifiler",[])
    if not filer:
        return "TRYGT Å LUKKE — ingen kode funnet"
    nyeste = sorted(filer, key=lambda x: x.get("endret",""), reverse=True)
    siste = nyeste[0] if nyeste else None
    if siste:
        return f"BEVAR — {len(filer)} verdifulle filer. Siste endret: {siste['endret']} ({Path(siste['fil']).name})"
    return f"BEVAR — {len(filer)} verdifulle filer"

def main():
    mapper_å_scanne = [
        Path.home() / "GinieMobile",
        Path.home() / "GinieSystem",
        Path.home() / "roadmap_ai",
        Path.home() / "mission-control",
        Path.home() / "revenue_os",
        Path.home() / "kadens",
        Path.home() / "AImigoBot",
    ]

    print(f"\n{BOLD}GINIE CLOSEOUT AGENT  |  {NOW}{RESET}")
    print("═"*80)

    procs = scan_procs()
    rapport = {"ts": NOW, "prosesser": [], "mapper": []}

    # --- PROSESSER ---
    print(f"\n{BOLD}► AKTIVE PROSESSER{RESET}")
    for p in procs:
        info = klasifiser_proc(p["cmd"])
        farge = GULL if info["type"] in ["Log-watcher"] else ROED
        kort = p["cmd"][:60]
        print(f"  {farge}[{info['type']}]{RESET} {kort}")
        print(f"    → {GROE}{info['handling']}{RESET}")
        if info.get("mappe"):
            scan = scan_mappe(Path(info["mappe"]))
            vurd = vurder_mappe_handling(scan)
            print(f"    📁 {info['mappe']} — {BLAA}{vurd}{RESET}")
        rapport["prosesser"].append({**p, **info})

    # --- MAPPER ---
    print(f"\n{BOLD}► MAPPESKANNING{RESET}")
    for sti in mapper_å_scanne:
        if not sti.exists():
            print(f"  {GULL}⊘ {sti} — finnes ikke{RESET}")
            continue
        scan = scan_mappe(sti)
        vurd = vurder_mappe_handling(scan)
        farge = GROE if "BEVAR" in vurd else GULL
        print(f"\n  {farge}📁 {sti.name}{RESET}")
        print(f"    Status: {vurd}")
        filer = scan.get("verdifiler",[])[:3]
        for f in filer:
            print(f"    • {Path(f['fil']).name:<30} {f['endret']}")
        rapport["mapper"].append({"sti":str(sti),"vurdering":vurd,"antall_filer":len(scan.get("verdifiler",[]))})

    # --- HANDLINGSPLAN ---
    print(f"\n{BOLD}► HANDLINGSPLAN (kopier og kjør){RESET}")
    print("─"*80)
    print(f"  {ROED}pkill -f 'stripe listen'{RESET}   # stripe webhook")
    print(f"  {ROED}pkill -f 'npm run dev'{RESET}      # npm dev server")
    print(f"  {ROED}pkill -f 'watch -n 2 ls'{RESET}   # outbox watcher")
    print(f"\n  Gjenværende etter closeout: 1 terminal + remote log (AIM-LOG-01)")

    LOG.write_text(json.dumps(rapport, indent=2, ensure_ascii=False))
    print(f"\n  Rapport lagret: {LOG}")
    print(f"\n{BOLD}Neste:{RESET} python3 ~/mission-control/closeout_agent.py\n")

if __name__ == "__main__":
    main()
