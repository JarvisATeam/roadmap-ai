# NODE_ROLE_MAP

## Formål
Låse én tydelig rolle per node slik at riggen blir enklere å drifte, lettere å selge og mindre kaotisk.

## Node 1 — MAC hovedmaskin
- Rolle: control plane / build / truth layer / dokumentasjon / salg
- Primæroppgaver:
  - eie `~/roadmap-ai/.truth/`
  - bygge og oppdatere specs, prompts og dokumentasjon
  - Git Proof Pack og selektiv stage/commit
  - produktisering og kundeleveranser
- Skal ikke:
  - være uklar dump for alle runtime-prosesser

## Node 2 — Jetson (`aimigo`)
- Rolle: runtime / inference / agent execution / API-gate
- Primæroppgaver:
  - kjøre AImigoBot
  - kjøre beskyttet API på `8098`
  - observer/daemon og relaterte runtime-jobber
  - lokal edge-kjøring og agent-routing
- Verifisert:
  - `AImigoBot` finnes
  - `mission-control` finnes
  - `total-missioncontrol` finnes
  - `uvicorn app.api:app` observert
  - `8098/health` gir `HTTP 200` med `x-api-key` + `LEVIATHAN_API_KEY`

## Node 3 — Mac 2012 Ubuntu
- Rolle: backup worker / observability / OCR / ingest / batch jobs
- Primæroppgaver:
  - lange ikke-kritiske jobber
  - filskanning / OCR / import / backup-kjøring
  - sekundær runner for batch og test
- Skal ikke:
  - være primær AI-runtime eller kritisk auth-gate

## Node 4 — øvrige Mac-er
- Rolle: reservekapasitet / demo / staging / monitor
- Primæroppgaver:
  - staging
  - dashboard/demo
  - ekstra build-kapasitet
  - redundans ved feil på hoved-Mac

## Beslutningsregel
Hver node skal ha én hovedrolle.
Nye oppgaver skal legges der de gir:
1. mest inntekt
2. minst friksjon
3. minst risiko for golden path

## Foreløpig anbefalt arbeidsdeling
- MAC hovedmaskin:
  - truth, docs, git, salg, roadmap
- Jetson:
  - runtime, API, workers, orchestration
- Mac 2012 Ubuntu:
  - batch, OCR, observability, backup
- Øvrige Mac-er:
  - staging, demo, reserve

## Neste tiltak
1. Lag `OFFER_AI_OPS_SNAPSHOT_48H.md`
2. Stage kun `.truth/`
3. Deretter egen ryddeplan for secrets-sprawl
