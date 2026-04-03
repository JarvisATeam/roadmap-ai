# 03 — Dispatch

## Status
**VERIFISERT** for P0/P3 lokalt  
**BLOKKERT** for live cowork-kjøring

## Hovedkomponenter
- `scripts/dispatch_runner.sh`
- `scripts/idempotency.sh`
- `scripts/format_phone_summary.sh`
- `dispatch_ops.yaml`
- `DISPATCH_RULES.md`

## Verb-modell
Dispatch kjører verb som `health`, `standup`, `forecast`, `decide`, `export-panels`, `closeout`.

## Idempotens
**VERIFISERT**
- deterministisk `idempotency_key`
- replay-detection
- cached return ved replay
- audit-logg i `dispatch_idempotency.jsonl`

## Feilkontrakter
**VERIFISERT**
- `error.json` standard envelope
- `error_<verb>.json` per verb
- `error_history.jsonl` / tilsvarende historikklogg

Eksempelkontrakt:
```json
{
  "timestamp": "ISO-8601",
  "verb": "standup",
  "status": "error",
  "error_type": "timeout",
  "message": "Verb exceeded max_duration",
  "metadata": {
    "idempotency_key": "..."
  }
}
```

## Timeout enforcement
**VERIFISERT**
- hver verb har `max_duration`
- timeout skal være fail-closed
- timeout skal skrive standard error envelope

## Wake/sleep
**VERIFISERT**
- kjøring under `caffeinate`
- sleep/wake-håndtering lagt til for Mac
- må overvåkes i praksis videre ved live-bruk

## Telefonformat
**VERIFISERT**
- korte summaries
- mobilvennlig format
- egnet for rask konsumering i korte vinduer

## Operatørinstruksjoner
### Lokal verifikasjon
```bash
scripts/dispatch_runner.sh health
scripts/dispatch_runner.sh standup
```

### Ved feil
1. Les `error.json`
2. Sjekk per-verb error-fil
3. Sjekk om idempotency-key har replay
4. Bekreft timeout-regel i `dispatch_ops.yaml`

## Vei videre
- live proof mot cowork-endpoint
- remote observability
- koble output sikkert inn i P4-panelene
