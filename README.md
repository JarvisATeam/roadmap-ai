# ROADMAP-AI

Dette repoet er **source of truth**.  
Før du gjør noe som helst: verifiser faktisk repo-state.

## Repo
- Path: `~/roadmap-ai`
- Remote: `git@github.com:JarvisATeam/roadmap-ai.git`
- Branch: `main`

## Første kommando
Kjør alltid dette først:

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

## Les dette deretter

Når repo-state er verifisert, les:

* `docs/AI_OPERATOR_ROOT_PROMPT.md`

## Arbeidsregler

* Én blokk om gangen
* Verifiser etter hver blokk
* Fail-closed
* Ingen status uten Git Proof Pack
* Commit per logisk enhet
* Push etter grønn gate
* Snapshot ved milepæl

## Nåværende status

Lande og merget:

* Workspace foundation
* ECHOBOT P1: Python service ingress + contracts
* ECHOBOT P2: TypeScript adapters + internal routes
* ECHOBOT P3: webhook routes + mission sync

## Prinsipp

Ikke stol på gamle handovers eller gamle prompts.
Bruk repoet som sannhet.
