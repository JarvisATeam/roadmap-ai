# 02 — Roadmap CLI

## Status
**VERIFISERT**

## Hovedformål
Roadmap CLI håndterer missions og steps, scorer arbeid, og eksponerer både menneskelesbar og maskinlesbar output.

## Kommandoer
```bash
roadmap add-mission "<navn>" [--type feature|bugfix|research]
roadmap add-step "<beskrivelse>" --mission <id|prefiks> [--due YYYY-MM-DD]
roadmap list-missions
roadmap list-steps [--mission <id|prefiks>] [--json]
roadmap decide <id|prefiks>
roadmap value <id|prefiks>
roadmap forecast <id|prefiks>
```

## Short IDs
- Prefix matching er støttet
- Ambiguitet skal gi feil
- Ukjent ID skal gi feil
- Bruk dette i daglig drift for kortere operatørflyt

## JSON-envelope
Alle JSON-kommandoer skal bruke:
```json
{
  "roadmap_version": "x.y.z",
  "timestamp": "ISO-8601",
  "command": "roadmap list-steps",
  "data": {},
  "metadata": {}
}
```

## ORION-scoring
**VERIFISERT**
Scoring bygger på en kombinasjon av urgency, verdi og andre faktorer.

### Deadline-vekter
- overdue = 2.0x
- mindre enn 3 dager = 1.5x
- mindre enn 7 dager = 1.2x
- ingen deadline = 0.8x

## Operatørinstruksjoner
1. Opprett mission
2. Legg til steps
3. Sett `--due` der det er reell deadline
4. Bruk short ID i daglig bruk
5. Bruk JSON-output som input til videre lag, ikke skjermtekst

## Eksempler
```bash
roadmap add-mission "Vipps bridge" --type feature
roadmap add-step "Lag webhook-kontrakt" --mission VIP-1 --due 2026-04-10
roadmap list-steps --mission VIP-1 --json
roadmap forecast VIP-1
```

## Regler
- Ikke hardkod UI-data oppå roadmap-output
- Ikke omgå JSON-envelope-kontrakten
- Ikke kall noe grønt uten Git Proof Pack
