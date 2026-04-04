# 11 — Recent State Sync (2026-04-04)

Dette dokumentet er autoritativ status-sync for endringer som kom **etter** `005d136` og fram til verifisert HEAD `d3faad5`.

## Verifisert baseline

- Dato: 2026-04-04
- HEAD: `d3faad5`
- Forrige produksjons-closeout: `005d136`
- Status: P0–P6 levert, men ikke uten operasjonelle avvik

## Hva som faktisk ble gjort nylig

Siden `005d136` kom disse nye filene inn:

- `QUICKSTART.md`
- `scripts/demo_walkthrough.sh`
- `scripts/open_dashboards.sh`
- `scripts/quickstart.sh`
- `scripts/r.sh`

I tillegg ble `scripts/r.sh` rettet i `d3faad5` slik at `add-step` bruker korrekt syntaks:

```bash
roadmap add-step "$mission" "$desc" [--due YYYY-MM-DD]
```

Dette er verifisert i commit `d3faad5`.

## Oppdatert operativ sannhet

### Faser
- **P0 Dispatch V1 / live:** lokal verifisering grønn, live cowork fortsatt blokkert
- **P1 Mission Control:** grønn
- **P2 Roadmap Core:** grønn
- **P3 Dispatch V2:** grønn
- **P4 Dashboard UI:** grønn
- **P5 Agent Orchestration:** grønn
- **P6 Integrasjoner:** grønn

### Dashboard-paneler (9)
- `dashboard/smart_next.html`
- `dashboard/risk_summary.html`
- `dashboard/progress.html`
- `dashboard/decisions.html`
- `dashboard/forecast.html`
- `dashboard/orchestration.html`
- `dashboard/pr_lane.html`
- `dashboard/remote_health.html`
- `dashboard/revenue.html`

Viktig:
- risikopanelet heter `risk_summary.html`, ikke `risks.html`

### Nye operatørscripts

#### `scripts/r.sh`
Status: **verifisert med nylig syntaksfix**

Brukes til:
- start / quick refresh
- smart-next
- dashboards
- mission control status/watch
- demo
- add mission
- add step
- mark done

#### `scripts/open_dashboards.sh`
Status: **verifisert som eksisterende launcher**

Dette scriptet:
- går til repo-root
- starter `python3 -m http.server 8000` ved behov
- åpner riktige dashboard-paneler
- bruker `risk_summary.html`
- inkluderer også P6-panelene `pr_lane`, `remote_health`, `revenue`

#### `scripts/demo_walkthrough.sh`
Status: **nylig lagt til**

#### `scripts/quickstart.sh`
Status: **delvis riktig, men ikke helt lukket**

Kjent avvik:
- scriptet kaller `python scripts/orchestration_status.sh`
- men `scripts/orchestration_status.sh` er et Bash-script

Korrekt kall skal være en av disse:

```bash
./scripts/orchestration_status.sh
# eller
bash scripts/orchestration_status.sh
```

## Kjente reelle avvik per 2026-04-04

### 1. Quickstart er ikke 100% riktig
Årsak:
- feil kall til orchestration-status

Konsekvens:
- `scripts/quickstart.sh` bør ikke regnes som helt grønt før dette er rettet

### 2. Credential-oppsett er ikke helt lukket
`scripts/setup_credentials.sh` instruerer brukeren til å source:

```bash
source ~/roadmap-ai/.credentials/load_credentials.sh
```

Men denne loader-fila er ikke verifisert som tilstede i repoet i denne økten.

Konsekvens:
- credential warning-problemet er plausibelt ekte
- auth-flyten bør regnes som delvis lukket, ikke helt ferdig

### 3. Webserver-problemet er ikke bevist som kodefeil
`open_dashboards.sh` ser korrekt ut i repoet.
Derfor skal “Not Found” foreløpig tolkes som:
- gammel bakgrunnsserver
- feil katalog ved manuell kjøring
- feil runtime-state

Ikke som bekreftet repo-bug før det er bevist med ny proof.

## Hva eldre handover/guide-tekst skal overstyres med

### Overstyr disse påstandene

#### Gammel påstand:
`quickstart.sh` = ✅ fungerer

#### Ny sannhet:
`quickstart.sh` = 🟡 nesten ferdig, men må få korrekt Bash-kall til orchestration-status

---

#### Gammel påstand:
credential auto-load er ferdig

#### Ny sannhet:
auto-load er ikke fullt bevist ferdig før loader-fila finnes eller referansen fjernes

---

#### Gammel påstand:
webserver-problem er nødvendigvis kodeproblem

#### Ny sannhet:
webserver-problem er foreløpig et runtime-problem, ikke bevist repo-feil

## Riktig next action

Neste riktige ASK er:

```text
ASK-P6-OPS-FIX-001 — Lukk operasjonelle avvik etter P6. Bytt scripts/quickstart.sh fra 'python scripts/orchestration_status.sh' til korrekt Bash-kall. Enten opprett .credentials/load_credentials.sh som matcher setup_credentials.sh, eller fjern referansen og bruk én konsistent credential-strategi. Verifiser r.sh, quickstart.sh og open_dashboards.sh. Commit + push + Git Proof Pack når grønt.
```

## Hvorfor dette dokumentet finnes

GitHub-connectoren i denne økten lot meg opprette nye filer, men ikke overskrive eksisterende filer direkte. Derfor brukes denne filen som ny SSOT for de siste endringene etter `005d136`.
