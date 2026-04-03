# 08 — Drift og operatørinstruksjoner

## Installasjon
```bash
git clone git@github.com:JarvisATeam/roadmap-ai.git ~/roadmap-ai
cd ~/roadmap-ai
scripts/bootstrap_mission_control.sh
mc init
```

## Daglig start
```bash
mc status
mc doctor
mc handover
```

## Under aktiv økt
```bash
mc watch
mc logs --tail
```

## Før commit/closeout
```bash
git status -sb
mc handover --commit
```

## Git Proof Pack
Minimum:
- repo-root
- branch
- HEAD
- `git status -sb`
- upstream
- ahead/behind
- diff
- unpushed commits
- stash

Eksempel:
```bash
bash -lc '
cd ~/roadmap-ai
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git log --oneline -1
git status -sb
git rev-parse --abbrev-ref --symbolic-full-name "@{u}" || true
git diff --stat || true
git diff --cached --stat || true
git stash list || true
'
```

## Fail-closed regler
- ingen statusrapport uten proof
- ingen “operativt” uten fersk verifikasjon
- ingen P5 før P4 grønn
- ingen revenue bridge før PR-lane + Remote Health
- ved ukjent state: stopp og dokumenter

## Terminalregler
- én oppgave om gangen
- ved heredoc/quote-problemer: stopp og lever ny hel blokk
- minimal innliming tilbake
- bruk korte, robuste kommandoer

## Operatørchecklist
### Start
- [ ] `mc status`
- [ ] `mc doctor`
- [ ] `mc handover`

### Under arbeid
- [ ] verifiser input-data
- [ ] én ASK om gangen
- [ ] commit per logisk enhet

### Slutt
- [ ] handover oppdatert
- [ ] commit + push
- [ ] Git Proof Pack
