# 04 — Mission-Control

## Status
**VERIFISERT**

## Kjerne
Mission-Control er operatørlaget rundt Roadmap-AI.

## Viktige kommandoer
```bash
mc status
mc status --json
mc doctor
mc doctor --json
mc watch [--interval N]
mc snapshot [--export FILE] [--import FILE] [--compare A B]
mc logs [dispatch|errors] [--tail]
mc new feature "<navn>"
mc new bugfix "<navn>"
mc new research "<navn>"
mc archive <mission>
mc restore <mission>
mc list archived
mc prompt <mode>
mc selftest
mc init
mc bootstrap
mc handover
mc handover --export handover.txt
mc handover --commit
```

## Hva de brukes til
- `status`: rask helsesjekk
- `doctor`: dypere diagnostikk
- `watch`: live terminal-dashboard
- `snapshot`: eksport/import/compare
- `logs`: feilsøk og observasjon
- `new`: strukturert oppstart av missions
- `archive/restore`: mission lifecycle
- `handover`: sesjonsoverføring

## LaunchAgent
**VERIFISERT** installert  
Status i økten: installert, men ikke nødvendigvis loaded hele tiden.

## GitHub Actions CI
**VERIFISERT**
- workflow finnes
- selftest/doctor/snapshot-type kjøringer er del av designet
- remote grønn status må fortsatt sjekkes per reell run

## Operatørflyt
### Start dag
```bash
mc status
mc doctor --json
mc handover
```

### Under arbeid
```bash
mc watch
mc logs --tail
```

### Før closeout
```bash
mc handover --commit
git status -sb
```

## Anbefalt bruk
- bruk `mc handover` ved hver større milepæl
- bruk `mc watch` for å holde øye med status uten å åpne flere verktøy
- bruk `mc snapshot` før større endringer
