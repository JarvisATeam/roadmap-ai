# 01 — Systemoversikt

## 1. Mål
Roadmap-AI er et operatørsystem for planlegging, prioritering, kjøring, observasjon og handover. Systemet er bygget for korte arbeidsvinduer, høy verifiserbarhet og fail-closed drift.

## 2. Arkitektur
```text
Roadmap CLI
  ↓
Dispatch Runner / verb execution
  ↓
panel_output/*.json + error.json + logs
  ↓
Mission-Control (mc)
  ↓
Dashboard UI (P4)
  ↓
Agent-orkestrering (P5)
  ↓
Eksterne integrasjoner (P6)
```

## 3. Prinsipper
- **VERIFISERT:** Git-tracket kode og dokumentasjon er canon
- **VERIFISERT:** Git Proof Pack kreves før status/roadmap/progresjon
- **VERIFISERT:** fail-closed — ukjent tilstand skal ikke pyntes til grønn
- **VERIFISERT:** én logisk leveranse per commit
- **VERIFISERT:** data først, UI etterpå
- **PLANLAGT:** mer autonomi via agent-lag, men med eksplisitt eierskap og eskalering

## 4. Faser

### P0 — Live-Proof
**VERIFISERT DELVIS**
- lokal dispatch-runner verifisert
- `health` grønn
- `standup` genererer artifacts
- tag: `dispatch-v1.0-local-verified`

**BLOKKERT**
- live-dispatch mot cowork-endpoint
- token/remote oppsett

### P1 — Mission-Control
**VERIFISERT**
- operatør-CLI
- status, doctor, logs, watch, snapshots, templates, archive/restore
- installasjon og shell-integrasjon
- GitHub Actions workflow
- `mc handover`

### P2 — Roadmap Core
**VERIFISERT**
- short ID resolver
- deadline-aware urgency
- `list-steps --mission`
- standard JSON-envelope på alle kommandoer

### P3 — Dispatch V2
**VERIFISERT**
- idempotens
- standard `error.json`
- timeout enforcement
- wake/sleep-håndtering
- telefonformat

### P4 — Dashboard UI
**PLANLAGT**
- fem paneler
- kun lesing fra verifisert JSON
- graceful degradation
- timestamp/refresh

### P5 — Agent-orkestrering
**PLANLAGT**
- AImigo, Codex, ClaudeBot, Dispatch roller
- verb ownership
- lanes og eskalering

### P6 — Integrasjoner
**PLANLAGT**
- GitHub PR-lane
- Remote Health / Tailscale
- Sentry incidents → blockers
- Stripe/Vipps revenue bridge
- Linear/Jira sync
- n8n event-bus

## 5. Tekstlig sekvensdiagram

### Roadmap → Dispatch → Panel-output
```text
Operatør kjører roadmap/mc
  → roadmap vurderer mission/step
  → dispatch_runner utfører verb
  → resultat lagres i panel_output/*.json
  → mission-control viser status/logs/handover
  → dashboard leser JSON og renderer panel
```

### Feilflyt
```text
verb start
  → idempotency-check
  → timeout-guard
  → success => panel_output/logg oppdateres
  → failure => error_<verb>.json + error.json + historikk
```
