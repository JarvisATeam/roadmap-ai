# Mission 001: Dashboard

## Status: active
## Prioritet: høy
## Startet: 2026-03-28

## Mål
Bygge `dashboard.sh` som aggregerer prosjektstatus fra Mission Control og roadmap-cli til én JSON (`.ai/dashboard.json`).

## Kontekst
- Preflight er på plass (7/7 pass).
- Vi mangler et enkelt overblikk over aktive missions og roadmap-status.
- Dashboard skal leses av både mennesker og AI som “langtidshukommelse”.

## Beslutninger tatt
- Output-fil: `.ai/dashboard.json` — dashboard_schema må forbli uendret.
- Datakilder: parse `.ai/missions/active/*.md` + `~/roadmap-ai/venv/bin/roadmap status`.
- Validering skjer i scriptet (minst strukturell).

## Akseptansekriterier
- [x] Leser metadata fra alle aktive mission-filer (navn, status, prioritet, fremdrift).
- [x] Parser `roadmap status` uten å kreve aktivert venv (bruker full path).
- [x] Skriver gyldig JSON til `.ai/dashboard.json`.
- [x] Verifiserer struktur mot `docs/dashboard_schema.json` (minst required keys).

## Filer involvert
- `scripts/dashboard.sh`
- `.ai/missions/active/001-dashboard.md`
- `.ai/dashboard.json`
- `docs/dashboard_schema.json`

## Relaterte lenker
- `~/roadmap-ai` repo (CLI-data)
- `~/mission-control/bin/preflight.sh`
