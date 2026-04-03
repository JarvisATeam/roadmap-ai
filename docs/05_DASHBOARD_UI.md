# 05 — Dashboard UI (P4)

## Status
**PLANLAGT**  
Viktig: P4 skal ikke regnes som levert før panelene er bygd mot ekte JSON i `panel_output/`.

## Panelrekkefølge
1. Smart Next
2. Risk Summary
3. Progress
4. Decisions
5. Forecast

## Felles krav
- les kun fra verifisert JSON i `panel_output/`
- ingen hardkodede demo-data
- graceful degradation ved manglende fil
- graceful degradation ved korrupt JSON
- vis `last-updated` timestamp
- commit per panel
- Git Proof Pack etter panel

## Datakilder
- `panel_output/smart_next.json`
- `panel_output/risks.json`
- `panel_output/status.json`
- `panel_output/decisions.json`
- `panel_output/forecast.json`

## UI-strategi
Enkel statisk frontend er nok i første omgang, så lenge den:
- leser JSON dynamisk
- ikke skjuler feil
- viser tom/fallback-state tydelig

## Fallback-design
Eksempel:
```text
Smart Next
Waiting for first dispatch run...
Last checked: 2026-04-03T16:00:00Z
Source: panel_output/smart_next.json
```

## Refresh-strategi
- polling eller reload-basert visning
- refresh-intervall må være tydelig
- timestamp skal alltid vises

## Data-contract policy
Før panelkode skrives:
1. `cat` eller valider JSON-filen
2. dokumenter forventet struktur
3. bygg renderer
4. bygg fallback
5. commit/push

## Viktig lærdom
Data bestemmer UI. Ikke motsatt.
