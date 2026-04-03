# HANDOFF - Mission Control

## SISTE SESJON
- Dato: 2026-04-01
- Type: SETUP + MEMORY LAYER

## FULLFORT
- .ai/memory/ opprettet (context.md, decisions.jsonl, mistakes.md)
- .ai/missions/ med aktiv mission 001-dashboard
- .ai/dashboard.json generert
- ROADMAP.md opprettet
- bin/preflight.sh: 7/7 pass
- scripts/dashboard.sh bygget
- Roadmap CLI path funnet og dokumentert
- Claude-promptbibliotek + `bin/prompt.sh` aliaser
- Fase 1.1 wrappers: `scripts/export_markdown/json/csv.sh` + `scripts/test_exports.sh`

## HVORDAN LESE REPOET
- Mission Control er cockpit + hukommelse for RoadmapAI
- `bin/mc.sh` kjører standardløpet: preflight → dashboard → roadmap-status → Git proof + prompt-anbefaling
- `.ai/` er lokal sannhet (context, decisions, mistakes, aktiv mission, schema, snapshot)
- `docs/` er prosesskontrakter (workflow, systemprompt, dashboard-schema)
- `missionctl.py` er bro/orkestrator
- Roadmap-listen kommer fra `~/roadmap-ai` via CLI – rydde duplikater der, ikke her

## NESTE JOBB
- Integrer .ai/dashboard.json i handoff-rutinen
- Rydd opp duplikat smoke test missions i roadmap DB
- Legg `exports/` scripts i pre-commit hook (`scripts/test_exports.sh`)
- Fase 1.2: implementer `roadmap-ai` CLI-kommandoer (`add-task`, `complete`, `next`, `validate`, …)

## PROMPT-BIBLIOTEK
- `claude-prompts/` inneholder auto, plan, dream og security prompts fra Claude Code-repoet
- Bruk `bin/prompt.sh list` for oversikt
- Eksempler:
  - `./bin/prompt.sh build` → Auto Mode systemprompt
  - `./bin/prompt.sh architect` → Plan/architect prompt
  - `./bin/prompt.sh memory` → KAIROS memory consolidation
  - `./bin/prompt.sh guard` → Security monitor del 1 (`security2` for del 2)

## ROADMAP CLI
- Path: ~/roadmap-ai/venv/bin/roadmap
- Kommandoer: create, milestone, step, done, status, open
- DB: allerede initialisert med missions
- Eksport-audit (2026-04-01): `pytest -k export` grønn, wrappers og `scripts/test_exports.sh` lagt til — se `docs/EXPORT_STATUS.md`. Pre-commit hook pending.

## KONTEKST FOR NESTE SESJON
Start ny chat med:
  Les ~/mission-control/HANDOFF.md og fortsett.
  Kjor bin/preflight.sh og sjekk status.

## HANDOVER UPDATE — 2026-04-02T20:22:35Z

- roadmap-ai Phase 3.0 (Dashboard Integration) ✅ KOMPLETT
- Git: master @ 6349e3b, 47 tests passing
- Alle known limitations løst (auto-deploy, auto-refresh, validation)
- Deployment scripts klar: deploy_to_roadmapai.sh, export_panels_local.sh
- JSON validation: `roadmap validate` og `roadmap validate-all`
- Docs komplett: DASHBOARD.md, README.md, ROADMAP.md
- System prompt oppdatert til BUILD-modus med auto-clipboard workflow

## HANDOVER UPDATE — 2026-04-02T21:25:00Z

- roadmap-ai Phase 3.0 (Dashboard Integration) ✅ KOMPLETT
- Git: master @ 6349e3b, 47 tests passing
- Alle known limitations løst (auto-deploy, auto-refresh, validation)
- Deployment scripts klar: deploy_to_roadmapai.sh, export_panels_local.sh
- JSON validation: `roadmap validate` og `roadmap validate-all`
- Docs komplett: DASHBOARD.md, README.md, ROADMAP.md
- System prompt oppdatert til BUILD-modus med auto-clipboard workflow

## HANDOVER UPDATE — 2026-04-03T00:02:49Z

- SYSTEM_PROMPT_BUILD.md rewritten via Python (heredoc-safe, ~100 lines)
- Backup preserved as SYSTEM_PROMPT_BUILD.md.bak
- Build workflow standardized: roadmap-first, clipboard-tee, fail-closed
- Next NTA: ASK-RA-BLOCKERS-001 — verify LaunchAgent for morning standup

## HANDOVER UPDATE — 2026-04-03T00:03:58Z

- SYSTEM_PROMPT_BUILD.md oppdatert med trygg BUILD-modus
- Arbeidsflyt standardisert til én blokk av gangen med verifisering
- Heredoc/quote-feil unngås ved å bruke trygg skriveflyt
- Neste iterasjon: LaunchAgent + git status verifisering
