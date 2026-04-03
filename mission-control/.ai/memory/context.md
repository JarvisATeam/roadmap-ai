# Prosjektkontekst — Mission Control

## Hva er dette?
Meta-workflow for menneske+AI-samarbeid. Mission Control holder roadmap, minne og guardrails for alle tilknyttede repos (roadmap-ai, GinieSystem, osv.)

## Tech stack
- Bash + Python 3.11 (scripts)
- JSON + Markdown som autoritative datastrukturer
- macOS 15.x (pbcopy), git CLI

## Nåværende fokus
Mission 001: Bygge `dashboard.sh` som genererer `.ai/dashboard.json` fra missions + `roadmap status`.

## Arkitekturregler
- Ingen globale PATH-avhengigheter — bruk fullpath eller aktiver correct venv (`~/roadmap-ai/venv/bin/activate`)
- Alle scripts bruker `set -euo pipefail`
- Output skal valideres mot relevante schemaer før bruk
- Append-only for beslutnings- og feil-logg (`decisions.jsonl`, `mistakes.md`)

## Viktige lenker
- Roadmap CLI: `~/roadmap-ai/venv/bin/roadmap`
- Mission Control repo: `~/mission-control`
- GinieSystem repo: `~/GinieSystem`

## Ting å huske
- Valgt JSON fremfor YAML for config (#3)
- Dashboard-script skal *ikke* mutere schema-filer, kun skrive `.ai/dashboard.json`
- Preflight må passere før nye scripts kjøres

## Sist oppdatert
2026-04-01 — Oppdatert kontekst med aktiv mission + regler for dashboard-arbeid
