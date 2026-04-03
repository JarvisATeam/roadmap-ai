# Roadmap-AI — Dokumentasjonspakke
Oppdatert: 2026-04-03  
Sist bekreftet HEAD i økten: `43ea18f`  
Miljø: MAC

## Status
- **P0 Live-Proof:** 80% — lokal verifikasjon grønn, live-dispatch venter cowork-endpoint + token
- **P1 Mission-Control:** 100%
- **P2 Roadmap-AI Core:** 100%
- **P3 Dispatch V2 Hardening:** 100%
- **P4 Dashboard UI:** ikke verifisert startet
- **P5 Agent-orkestrering:** planlagt
- **P6 Integrasjoner:** planlagt

## Denne pakken inneholder
- `docs/01_SYSTEM_OVERVIEW.md` — arkitektur, prinsipper, dataflyt, faser P0–P6
- `docs/02_ROADMAP_CLI.md` — kommandoer, JSON-envelope, short IDs, ORION, deadlines
- `docs/03_DISPATCH.md` — dispatch-runner, idempotens, feilkontrakter, timeout, wake/sleep
- `docs/04_MISSION_CONTROL.md` — `mc`-kommandoer, drift, snapshots, logs, handover, CI
- `docs/05_DASHBOARD_UI.md` — P4-paneler, datakontrakter, fallback, refresh-strategi
- `docs/06_AGENT_ORCHESTRATION.md` — P5-roller, verb ownership, eskalering
- `docs/07_INTEGRATIONS.md` — bygget vs planlagte integrasjoner, brukerflyt, krav
- `docs/08_OPERATIONS.md` — installasjon, daglig drift, Git Proof Pack, fail-closed
- `docs/09_ROADMAP_NEXT.md` — anbefalt rekkefølge, milepæler, avhengigheter

## Canon vs plan
I denne dokumentasjonen er hver seksjon merket som:
- **VERIFISERT** = eksplisitt bygget eller bekreftet i økten
- **PLANLAGT** = ønsket eller neste fase, ikke verifisert levert
- **BLOKKERT** = kjent avhengighet mangler

## Viktige paths
- `~/roadmap-ai/roadmap/`
- `~/roadmap-ai/scripts/`
- `~/roadmap-ai/panel_output/`
- `~/roadmap-ai/mission-control/`
- `~/roadmap-ai/mission-control/HANDOFF.md`
- `~/roadmap-ai/mission-control/.ai/memory/decisions.jsonl`

## Kort anbefaling videre
1. Bygg P4-paneler i rekkefølgen Smart Next → Risk Summary → Progress → Decisions → Forecast
2. Lukk siste P0 live-gap når cowork-endpoint er klart
3. Definer P5 agent-kontrakter før integrasjoner
4. Kjør P6 i rekkefølgen PR-lane → Remote Health → Incident→Blockers → Revenue → Sync → Event-bus
