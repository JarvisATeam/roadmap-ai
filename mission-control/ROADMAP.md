# ROADMAP - Mission Control

Roadmap for menneske+AI-samarbeid.
CLI: ~/roadmap-ai/venv/bin/roadmap

## CLI-kommandoer

    roadmap create "Navn" - Opprett ny mission
    roadmap milestone <id> "Navn" - Legg til milepael
    roadmap step <id> "Beskrivelse" - Legg til steg
    roadmap done <id> - Marker som ferdig
    roadmap status - Vis status
    roadmap open - Kontekst-gjenoppretting

## AKTIV BACKLOG

### KRITISK
- [ ] Fiks preflight.sh: venv + roadmap CLI paths
- [ ] Bygg dashboard.sh entry point
- [ ] Bygg mc hovedkommando

### VIKTIG
- [ ] Integrer .ai/memory i handover-flow
- [ ] Dokumenter projects.json struktur

### NICE-TO-HAVE
- [ ] Automatisk git proof for handover
- [ ] Window memory backup rutine

## BESLUTNINGER
- #5: Roadmap CLI path er ~/roadmap-ai/venv/bin/roadmap
- #6: Scripts bruker full path, ikke PATH-avhengighet

## RELATERTE PROSJEKTER
- GinieSystem: ~/GinieSystem
- RoadmapAI: ~/roadmap-ai (venv)
- AImigoBot: aimigo@100.97.199.60:~/AImigoBot

Sist oppdatert: 2026-04-01 av menneske+AI
