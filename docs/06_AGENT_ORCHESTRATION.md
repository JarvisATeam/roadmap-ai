# 06 — Agent-orkestrering (P5)

## Status
**PLANLAGT**

## Mål
Gi klare roller, ansvar og eskalering for hvert agent-lag.

## Foreslåtte roller
### Dispatch
- eier verb execution
- eier idempotens, timeout, error contracts

### Codex
- eier kodeleveranser
- eier patch/implementasjon innenfor ASK-rammer

### ClaudeBot
- eier briefing, docs, synthesis, postmortem

### AImigo
- eier cron/ops/deploy/validation/artifact-flyt der det er hensiktsmessig

## Verb ownership
Hver verb eller oppgavetype skal ha én tydelig eier.
Ingen overlapping uten eksplisitt regel.

## Eskaleringsregler
- ukjent tilstand → human review
- destruktive endringer → human only
- docs/status/handover → auto/pre-approved etter policy
- runtime state skal ikke bli canon ved et uhell

## Lanes
- Codex lane: implementasjon og kodeendringer
- ClaudeBot lane: oppsummering, docs, analyse
- AImigo lane: operasjonell kjøring, repeterbar drift
- Dispatch lane: selve verb execution

## Dokumenter som bør bygges
- `docs/AGENT_CONTRACTS.md`
- verb ownership-matrise
- escalation policy
- approval policy
