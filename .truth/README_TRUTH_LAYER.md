# README_TRUTH_LAYER

## Formål
Dette er den autoritative sannhetskilden for GinieSystem / Roadmap-AI-operasjonen.

## Repo-eier
- `~/roadmap-ai`

## Truth-root
- `~/roadmap-ai/.truth/`

## Leserekkefølge
1. `OWNER.txt`
2. `TRUTH_SOURCE.md`
3. `DEPLOY_MAP.md`
4. `AUTH_PROOF.md`
5. `SECRETS_INDEX.md`
6. `COST_BASELINE.md`
7. `NODE_ROLE_MAP.md`
8. `OFFER_AI_OPS_SNAPSHOT_48H.md`
9. `inventory/latest/RUN_SUMMARY.txt`
10. `inventory/latest/inventory.json`

## Gates
Ingen status, roadmap eller fremdriftsrapport uten:
- Git Proof Pack
- runtime-proof
- endpoint-proof
- auth-proof der auth finnes

## Klassifisering
Alt skal merkes som:
- VERIFISERT
- UKJENT
- MÅ INVENTERES

## Verifisert nå
- Git-eier: `~/roadmap-ai`
- Truth-layer commit: `9705c17`
- Aktiv cockpit-subtree: `~/roadmap-ai/total_missioncontrol`
- Sidecar subtree: `~/roadmap-ai/mission-control`
- Jetson runtime: `/home/aimigo/mission-control/total-missioncontrol`
- Beskyttet API: `127.0.0.1:8098`
- Auth-header: `x-api-key`
- Auth-variabel: `LEVIATHAN_API_KEY`

## Neste standardløp
1. Kjør inventar
2. Oppdater truth-filer
3. Stage kun `.truth/`
4. Commit/push
5. Ny Git Proof Pack
6. Først deretter roadmap eller ny byggesløyfe

## Forbud
- Ingen `git add .`
- Ingen destruktiv ryddejobb uten backup + eksplisitt `JA`
- Ingen statusrapport uten Git Proof Pack
