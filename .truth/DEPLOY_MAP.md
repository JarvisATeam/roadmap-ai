# DEPLOY_MAP

## Repo-eier
- `~/roadmap-ai`

## Autoritativ sannhetskilde
- `~/roadmap-ai/.truth/`

## MAC source trees
- Aktiv cockpit-subtree:
  - `~/roadmap-ai/total_missioncontrol`
- Sidecar/control-room subtree:
  - `~/roadmap-ai/mission-control`

## Jetson runtime trees
- Runtime deploy:
  - `/home/aimigo/mission-control/total-missioncontrol`
- Mission-control base:
  - `/home/aimigo/mission-control`
- AImigoBot:
  - `/home/aimigo/AImigoBot`

## Verifiserte porter / flater
- `127.0.0.1:8080/health`
  - Resultat: `HTTP 200`
  - Type: `text/html`
  - Tolkning: dashboard/web-lag
- `127.0.0.1:8080/api/v2/system/snapshot`
  - Resultat: `HTTP 200`
  - Type: `text/html`
  - Tolkning: route/front proxy returnerer HTML, ikke JSON
- `127.0.0.1:8080/api/v2/skills/unified`
  - Resultat: `HTTP 200`
  - Type: `text/html`
  - Tolkning: route/front proxy returnerer HTML, ikke JSON
- `127.0.0.1:8098/health`
  - Resultat: `HTTP 401`
  - Tolkning: beskyttet API/gate
- `127.0.0.1:8098/docs`
  - Resultat: `HTTP 401`
  - Tolkning: samme beskyttede API-flate

## Verifiserte runtime-signaler
- Jetson host: `aimigo`
- `AImigoBot` path finnes
- `mission-control` path finnes
- `total-missioncontrol` path finnes
- `app/api.py` finnes
- `uvicorn app.api:app` er observert på port `8098`
- `observer/daemon.py --verify` er observert
- docker-proxy på `8222` er observert

## Verifisert auth
- `127.0.0.1:8098/health`
  - Resultat: `HTTP 200`
  - Header: `x-api-key`
  - Variabelnavn: `LEVIATHAN_API_KEY`
  - Kildepath: `/home/aimigo/AImigoBot/.env`
  - Type: `application/json`

## Foreløpig konklusjon
- Port `8080` er presentasjonslag/dashboard
- Port `8098` er faktisk API, men auth-beskyttet
- Neste nødvendige proof er auth-metadatakartlegging, ikke mer endpoint-gjetting

## Neste filer
- `SECRETS_INDEX.md`
- `COST_BASELINE.md`
- `OFFER_AI_OPS_SNAPSHOT_48H.md`
- `NODE_ROLE_MAP.md`
