# AUTH_PROOF

Sist oppdatert: 2026-04-08T20:01:39.384956

## Verifisert auth-proof
- Host: `aimigo`
- API-flate: `http://127.0.0.1:8098/health`
- Header: `x-api-key`
- Variabelnavn: `LEVIATHAN_API_KEY`
- Kildepath: `/home/aimigo/AImigoBot/.env`
- HTTP: `200`
- Content-Type: `application/json`

## Body-head
- `{"status":"ok","G0_env":true,"reason":"OPENAI_API_KEY satt"}`

## Konklusjon
- `8098` er beskyttet API/gate
- korrekt auth-mønster er `x-api-key: $LEVIATHAN_API_KEY`
- `8080` er presentasjonslag/dashboard, ikke autoritativ JSON-API

## Neste tiltak
1. Oppdater `DEPLOY_MAP.md` med auth-linje
2. Lag `COST_BASELINE.md`
3. Lag `NODE_ROLE_MAP.md`
4. Planlegg secrets-rydding uten destruktiv handling før eksplisitt `JA`
