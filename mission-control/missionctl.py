#!/usr/bin/env python3
import json, os, sys, subprocess, signal
from pathlib import Path
from datetime import datetime, date

BASE     = Path.home() / ".ginie" / "mission-control"
REG      = BASE / "registry.json"
SESS_DIR = BASE / "sessions"
MD_OUT   = BASE / "MISSION_CONTROL.md"
TODAY    = date.today().isoformat()
NOW      = datetime.now().strftime("%Y-%m-%d %H:%M")

DEFAULT_REGISTRY = [
    {"id":"AIM-LOG-01","title":"[AIMIGO][WATCH][prod] worker.log","type":"watcher","project":"AImigo",
     "repo_path":"aimigo@100.97.199.60:~/AImigoBot","state":"running","criticality":"critical",
     "safe_to_close":"no","why_open":"Livefeed av worker. Stopp = blind flekk i prod.",
     "start_cmd":"ssh aimigo@100.97.199.60 'tail -f ~/AImigoBot/logs/worker.log'",
     "stop_cmd":"","restore_group":"aimigo-prod","owner":"remote-node",
     "dependencies":["Tailscale","SSH","AImigo VPS"],"cost":"VPS ~€5/mo",
     "session_end_rule":"La stå – kjøres remote uansett","notes":""},
    {"id":"AIM-WATCH-02","title":"[AIMIGO][WATCH][prod] outbox watcher","type":"watcher","project":"AImigo",
     "repo_path":"aimigo@100.97.199.60:~/AImigoBot/data/outbox","state":"running","criticality":"important",
     "safe_to_close":"yes","why_open":"Sjekker outbox-prosessering.",
     "start_cmd":"ssh aimigo@100.97.199.60 'watch -n 2 ls -lnt ~/AImigoBot/data/outbox/ | head -10'",
     "stop_cmd":"Ctrl+C","restore_group":"aimigo-prod","owner":"remote-node",
     "dependencies":["Tailscale","SSH"],"cost":"Gratis",
     "session_end_rule":"Lukk etter outbox bekreftet tom","notes":""},
    {"id":"AIM-SSH-03","title":"[AIMIGO][SSH][node] aimigo@100.97.199.60","type":"ssh","project":"AImigo",
     "repo_path":"aimigo@100.97.199.60:~","state":"running","criticality":"critical",
     "safe_to_close":"after-closeout","why_open":"Direkte node-tilgang for admin.",
     "start_cmd":"ssh aimigo@100.97.199.60","stop_cmd":"exit",
     "restore_group":"aimigo-prod","owner":"remote-node",
     "dependencies":["Tailscale","SSH key"],"cost":"Gratis",
     "session_end_rule":"exit + bekreft prosess er i supervisor","notes":""},
    {"id":"REV-HOOK-01","title":"[REVENUE_OS][HOOK][local] stripe webhook relay","type":"tunnel","project":"revenue_os",
     "repo_path":"~/GinieSystem/revenue_os","state":"running","criticality":"important",
     "safe_to_close":"after-closeout","why_open":"Videresender Stripe-events til localhost:3000.",
     "start_cmd":"stripe listen --forward-to localhost:3000/v1/billing/webhook",
     "stop_cmd":"pkill -f 'stripe listen'","restore_group":"revenue-os-dev","owner":"lokal",
     "dependencies":["Stripe CLI","Stripe konto","npm dev"],"cost":"Stripe: betalt/tx",
     "session_end_rule":"Stopp når webhook-test ferdig","notes":"Stopp FØR prod-deploy"},
    {"id":"REV-DEV-02","title":"[REVENUE_OS][DEV][local] npm dev :3000","type":"dev-server","project":"revenue_os",
     "repo_path":"~/GinieSystem/revenue_os","state":"running","criticality":"important",
     "safe_to_close":"after-closeout","why_open":"Lokal dev-server for Revenue OS.",
     "start_cmd":"cd ~/GinieSystem/revenue_os && npm run dev","stop_cmd":"Ctrl+C",
     "restore_group":"revenue-os-dev","owner":"lokal",
     "dependencies":["Node.js","npm","Railway CLI"],"cost":"Railway ~$5/mo",
     "session_end_rule":"Stopp etter git closeout","notes":""},
    {"id":"REV-CODEX-03","title":"[REVENUE_OS][ONESHOT][local] codex auth task","type":"one-shot","project":"revenue_os",
     "repo_path":"~/GinieSystem/revenue_os","state":"unknown","criticality":"optional",
     "safe_to_close":"yes","why_open":"Kjørte codex tasks/01_auth.md – sannsynlig ferdig.",
     "start_cmd":"codex 'Les tasks/01_auth.md og implementer'","stop_cmd":"",
     "restore_group":"revenue-os-dev","owner":"lokal",
     "dependencies":["Codex CLI","OpenAI konto"],"cost":"OpenAI: betalt/token",
     "session_end_rule":"Lukk etter resultat er committet","notes":"Sjekk: git diff HEAD --stat"},
    {"id":"RA-REPORT-01","title":"[ROADMAP_AI][REPORT][local] start.sh --report","type":"one-shot","project":"roadmap_ai",
     "repo_path":"~/roadmap_ai","state":"unknown","criticality":"optional",
     "safe_to_close":"yes","why_open":"Genererte rapport. Ferdig hvis prosess ikke kjører.",
     "start_cmd":"cd ~/roadmap_ai && ./start.sh --report","stop_cmd":"",
     "restore_group":"roadmap-ai","owner":"lokal",
     "dependencies":["Node.js","Notion API"],"cost":"Gratis",
     "session_end_rule":"Lukk etter: ls -lnt ~/roadmap_ai/reports/ | head -3","notes":""},
    {"id":"GM-WORK-01","title":"[GINIEMOBILE][WORK][local] shell","type":"workspace","project":"GinieMobile",
     "repo_path":"~/GinieMobile","state":"unknown","criticality":"optional",
     "safe_to_close":"after-closeout","why_open":"Arbeidsskall for GinieMobile.",
     "start_cmd":"cd ~/GinieMobile && zsh","stop_cmd":"exit",
     "restore_group":"ginie-mobile","owner":"lokal",
     "dependencies":["Git","Xcode/Node"],"cost":"Gratis",
     "session_end_rule":"git status + commit før lukk","notes":""},
    {"id":"SYS-KADENS-01","title":"[GINIEOS][SERVICE][local] kadens","type":"service","project":"GINIE_OS",
     "repo_path":"~/kadens","state":"unknown","criticality":"important",
     "safe_to_close":"yes","why_open":"Kadens nervesystem – stateless, alltid trygt å lukke.",
     "start_cmd":"python3 ~/kadens/kadens.py status","stop_cmd":"",
     "restore_group":"ginie-os","owner":"lokal",
     "dependencies":["Python 3","Notion API","Git"],"cost":"Gratis",
     "session_end_rule":"Stateless – ingen stopp nødvendig","notes":""},
]

ROED="\033[91m"; GROE="\033[92m"; GULL="\033[93m"; BLAA="\033[94m"
RESET="\033[0m"; BOLD="\033[1m"

def last_reg():
    BASE.mkdir(parents=True, exist_ok=True)
    SESS_DIR.mkdir(exist_ok=True)
    if REG.exists():
        data = json.loads(REG.read_text())
        # Sikkerhet: alltid list av dict
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            return data
    REG.write_text(json.dumps(DEFAULT_REGISTRY, indent=2, ensure_ascii=False))
    return DEFAULT_REGISTRY

def lagre(data):
    REG.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def scan_procs():
    try:
        r = subprocess.run(["ps","aux"], capture_output=True, text=True)
        return {p.split(None,10)[1]: p.split(None,10)[10]
                for p in r.stdout.splitlines()[1:]
                if len(p.split(None,10)) > 10}
    except Exception:
        return {}

def er_live(cmd, procs):
    if not cmd: return False
    nøkkel = cmd.split()[0].split("/")[-1]
    return any(nøkkel in v for v in procs.values())

def safe_ikon(s):
    return {"yes":"✅ TRYGT","no":"🔴 IKKE LUK",
            "after-closeout":"⚠️  CLOSEOUT"}.get(s, "❓ UKJENT")

def status():
    data = last_reg()
    procs = scan_procs()
    print(f"\n{BOLD}GINIE MISSION CONTROL  |  {NOW}{RESET}")
    print("═"*100)
    print(BOLD + f"{'ID':<16} {'TITTEL':<42} {'TYPE':<12} {'PROSJEKT':<14} {'LUKK?':<16} {'KRITISK'}" + RESET)
    print("─"*100)
    for w in data:
        if not isinstance(w, dict): continue
        live  = er_live(w.get("start_cmd",""), procs)
        safe  = w.get("safe_to_close","unknown")
        crit  = w.get("criticality","unknown")
        farge = (GROE if safe=="yes" or w.get("state")=="done"
                 else ROED if crit=="critical" or safe=="no"
                 else GULL)
        rad = (f"{w['id']:<16} {w.get('title','')[:40]:<42} "
               f"{w.get('type',''):<12} {w.get('project',''):<14} "
               f"{safe_ikon(safe):<16} {crit}")
        print(farge + rad + RESET)
    print(f"\n  🟢=trygt  ⚠️=lukk etter closeout  🔴=ikke lukk")
    print(f"  python3 missionctl.py restore <ID>  — vis startkommando\n")

def scan_cmd():
    data = last_reg()
    procs = scan_procs()
    n = 0
    for w in data:
        if not isinstance(w, dict): continue
        live = er_live(w.get("start_cmd",""), procs)
        if live and w.get("state") != "running":
            w["state"] = "running"; n += 1
        elif not live and w.get("state") == "running":
            w["state"] = "unknown"; n += 1
    lagre(data)
    sess = SESS_DIR / f"{TODAY}.json"
    sess.write_text(json.dumps({"ts":NOW,"windows":data}, indent=2, ensure_ascii=False))
    print(f"Scan OK. {n} oppdatert. Snapshot: {sess}")

def closeout():
    data = last_reg()
    procs = scan_procs()
    print(f"\n{BOLD}⚠️  CLOSEOUT GUIDE  |  {NOW}{RESET}\n")
    for kategori, label, farge in [
        ("no",            "🔴 IKKE LUKK:", ROED),
        ("after-closeout","⚠️  LUKK ETTER DISSE STEGENE:", GULL),
        ("yes",           "✅ TRYGT Å LUKKE:", GROE),
        ("unknown",       "❓ UKJENT — sjekk:", BLAA),
    ]:
        vinduene = [w for w in data if isinstance(w,dict) and w.get("safe_to_close")==kategori]
        if not vinduene: continue
        print(farge+BOLD+label+RESET)
        for w in vinduene:
            live = er_live(w.get("start_cmd",""), procs)
            print(f"  {farge}{w['id']:<16}{RESET} {w.get('title','')[:55]}")
            print(f"             {'● LIVE' if live else '○ ukjent'}  |  {w.get('session_end_rule','--')}")
            if w.get("stop_cmd"):
                print(f"             Stopp: {w['stop_cmd']}")
            print()

def restore(wid):
    data = last_reg()
    w = next((x for x in data if isinstance(x,dict) and x.get("id")==wid), None)
    if not w:
        print(f"ID {wid} ikke funnet. Kjør: python3 missionctl.py status"); return
    print(f"\n{BOLD}RESTORE: {w['id']} — {w.get('title','')}{RESET}")
    print(f"  Prosjekt:    {w.get('project','')}")
    print(f"  Type:        {w.get('type','')}")
    print(f"\n  {BOLD}Start:{RESET} {GROE}{w.get('start_cmd','')}{RESET}")
    if w.get("stop_cmd"):
        print(f"  {BOLD}Stopp:{RESET} {ROED}{w.get('stop_cmd','')}{RESET}")
    print(f"  Deps:  {', '.join(w.get('dependencies',[]))}")
    print(f"  Kost:  {w.get('cost','')}\n")

def update(wid):
    data = last_reg()
    w = next((x for x in data if isinstance(x,dict) and x.get("id")==wid), None)
    if not w:
        print(f"ID {wid} ikke funnet."); return
    for f in ["state","criticality","safe_to_close","notes","session_end_rule"]:
        print(f"  {f} [{w.get(f,'')}]: ", end="", flush=True)
        try:
            val = input().strip()
        except EOFError:
            val = ""
        if val: w[f] = val
    lagre(data)
    print("Oppdatert.")

def sync():
    data = last_reg()
    linjer = [
        f"# GINIE MISSION CONTROL\n_Oppdatert: {NOW}_\n\n",
        "## Vinduer\n\n",
        "| ID | Tittel | Type | Prosjekt | Lukk? | Kritisk | Avh. | Kost |\n",
        "|---|---|---|---|---|---|---|---|\n",
    ]
    for w in data:
        if not isinstance(w,dict): continue
        si = {"yes":"✅","no":"🔴","after-closeout":"⚠️","unknown":"❓"}.get(w.get("safe_to_close","unknown"),"❓")
        deps = ", ".join(w.get("dependencies",[]))
        linjer.append(f"| {w['id']} | {w.get('title','')[:44]} | {w.get('type','')} | "
                      f"{w.get('project','')} | {si} | {w.get('criticality','')} | {deps} | {w.get('cost','')} |\n")
    linjer += ["\n## Restore-kommandoer\n\n```bash\n"]
    for w in data:
        if isinstance(w,dict):
            linjer.append(f"# {w['id']}\n{w.get('start_cmd','')}\n\n")
    linjer.append("```\n")
    MD_OUT.write_text("".join(linjer), encoding="utf-8")
    print(f"MISSION_CONTROL.md: {MD_OUT}")

def cron():
    linje = f"0 3 * * * python3 {Path.home()}/mission-control/missionctl.py sync >> {BASE}/sync.log 2>&1"
    try:
        r = subprocess.run(["crontab","-l"], capture_output=True, text=True)
        eks = r.stdout if r.returncode==0 else ""
        if "missionctl.py sync" in eks:
            print("Cron allerede aktiv."); return
        subprocess.run(["crontab","-"], input=eks.rstrip()+"\n"+linje+"\n", text=True)
        print(f"Daglig cron satt (03:00):\n  {linje}")
    except Exception as e:
        print(f"Cron feilet: {e}\nLegg til manuelt:\n  {linje}")

def main():
    args = sys.argv[1:]
    if not args or args[0]=="status":        status()
    elif args[0]=="scan":                     scan_cmd()
    elif args[0]=="closeout":                 closeout()
    elif args[0]=="restore" and len(args)>1:  restore(args[1])
    elif args[0]=="update"  and len(args)>1:  update(args[1])
    elif args[0]=="sync":                     sync()
    elif args[0]=="cron":                     cron()
    else: print("Kommandoer: status | scan | closeout | restore <ID> | update <ID> | sync | cron")

if __name__=="__main__":
    main()
