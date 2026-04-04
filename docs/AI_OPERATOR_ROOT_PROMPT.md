# AI OPERATOR ROOT PROMPT — ROADMAP-AI

Du overtar et pågående prosjekt.  
Du skal jobbe kun ut fra **verifisert repo-state**, ikke gamle antakelser.

## 1. Repo
- Path: `~/roadmap-ai`
- Remote: `git@github.com:JarvisATeam/roadmap-ai.git`
- Branch: `main`

## 2. Første regel
Før du vurderer status, roadmap eller ny kode:
1. Kjør Git Proof Pack
2. Verifiser relevante filer
3. Les dokumentasjon
4. Identifiser aktiv fase
5. Først da foreslå eller gjør endringer

## 3. Git Proof Pack minimum
Må alltid inkludere:
- repo-root
- aktiv branch
- HEAD commit
- `git status -sb`
- upstream
- ahead/behind
- diff
- unpushed commits
- stash

Hvis dette ikke kan verifiseres:
- stopp
- ikke gi statusrapport
- ikke gi roadmap som om du vet tilstanden

## 4. Arbeidsmodus
- Én blokk om gangen
- Verifiser etter hver blokk
- Fail-closed
- Ikke dump store flertrinnsblokker uten grunn
- Ikke anta at tidligere handover fortsatt er riktig
- Beskytt golden path
- Endre minst mulig for å få mest mulig effekt

## 5. Git-regler
- Commit per logisk enhet
- Push etter grønn gate
- Ny Git Proof Pack etter push
- Snapshot ved milepæl
- Ingen prosjektstatus uten bevis

## 6. Nåværende bekreftede milepæler
Følgende er landet på `main`:

### Workspace foundation
Repoet er løftet fra spec-first til byggbart workspace.

### ECHOBOT P1 — Service ingress
- `services/echobot-py/`
- Python Echobot execution engine er inne
- contracts er etablert/oppdatert i `packages/operator-contracts/src/`

### ECHOBOT P2 — Adaptere og interne routes
- `apps/roadmap-operator/lib/echobot/`
- interne routes for `stats`, `review`, `sync`

### ECHOBOT P3 — Webhooks og mission sync
- webhook-routes for `reply`, `stripe`, `unsubscribe`
- positivt signal kan gi mission-sync result
- fail-closed gates gjelder

## 7. Arkitektur som gjelder
- `roadmap-ai` = source of truth
- `echobot` = Python execution engine
- TypeScript = contracts + adapters + routes + UI
- Ingen separat Echobot-app
- Ingen full rewrite uten eksplisitt grunn
- UI bygges oppå eksisterende contracts/routing

## 8. Relevante paths
- `services/echobot-py/`
- `apps/roadmap-operator/lib/echobot/`
- `apps/roadmap-operator/app/api/echobot/`
- `packages/operator-contracts/src/`
- `docs/ECHOBOT_OPERATOR_SPEC.md`

## 9. Snapshot-regel
Ved hver milepæl:
- lag fil under `docs/snapshots/`
- navn: `YYYY-MM-DD-<milestone>.md`

Snapshot skal inneholde:
- hva som ble gjort
- hva som er verifisert
- hva som gjenstår
- neste blokk
- Git Proof Pack
- relevante paths
- blokkere/risiko

## 10. Definition of done
Ingen fase er ferdig før:
- relevante gates er grønne
- git er rent eller pushet
- proof pack er oppdatert
- snapshot er skrevet
- neste blokk er tydelig

## 11. Leserekkefølge etter proof
1. `README.md`
2. `docs/AI_OPERATOR_ROOT_PROMPT.md`
3. `docs/ECHOBOT_OPERATOR_SPEC.md`
4. relevante filer i `services/echobot-py/`, `apps/roadmap-operator/lib/echobot/`, `apps/roadmap-operator/app/api/echobot/`, `packages/operator-contracts/src/`

## 12. Praktisk oppstartssekvens
Kjør først:

```bash
cd ~/roadmap-ai && {
  echo "=== ROOT ==="
  pwd
  echo
  echo "=== HEAD ==="
  git log --oneline -1
  echo
  echo "=== STATUS ==="
  git status -sb
  echo
  echo "=== UPSTREAM ==="
  git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "no-upstream"
  echo
  echo "=== AHEAD/BEHIND ==="
  git rev-list --left-right --count @{u}...HEAD 2>/dev/null || echo "n/a"
  echo
  echo "=== STASH ==="
  git stash list | tail -n 5 || true
  echo
  echo "=== ROOT FILES ==="
  ls -1
}
```

Deretter: verifiser aktiv fase, les docs, foreslå neste blokk.

## 13. Neste naturlige spor
- Operator UI / review surface
- videre mission/proof arbeidsflate
- hardening/test av webhook/sync

## 14. Forbudte feil
- Ikke bruk gamle branch-navn (repo er `main`)
- Ikke bruk gamle repo-paths
- Ikke anta at gammel prompt er riktigere enn repoet
- Ikke presenter roadmap uten proof
- Ikke bygg UI før contracts/routes er riktige
- Ikke rewrit nåværende modell uten grunn
