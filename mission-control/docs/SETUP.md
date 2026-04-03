# Mission Control Setup

Denne guiden setter opp `mission-control` lokalt med prompts, versioned git hooks og valgfri LaunchAgent på macOS.

## Forutsetninger

Minimum:
- `git`
- `python3`

For LaunchAgent på macOS:
- `launchctl`
- `plutil`

Anbefalt:
- `pbcopy`

## Repo-struktur

Viktige filer:
- `bin/mc.sh` — entry point / status
- `bin/prompt.sh` — skriv ut og kopier prompt til clipboard
- `scripts/bootstrap_mission_control.sh` — bootstrapper lokal setup
- `scripts/install_launchagent.sh` — installerer morning standup LaunchAgent
- `.githooks/pre-commit` — versioned git hook
- `docs/SYSTEM_PROMPT_BUILD.md` — build workflow prompt



### Shell integration

Install aliases and completions:

```bash
./scripts/install_shell_integration.sh
```

This adds:
- `mc` alias for `./bin/mc.sh`
- shell completion sourcing
- `MISSION_CONTROL_ROOT` export



### One-command install

```bash
./install.sh
```

This runs:
1. bootstrap
2. self-test
3. prints next steps

## Standard bootstrap

Kjør fra repo root:

```bash
cd ~/mission-control
./scripts/bootstrap_mission_control.sh
```

Dette gjør:
1. Oppretter nødvendige kataloger
2. Verifiserer nøkkelfiler
3. Setter `core.hooksPath` til `.githooks`
4. Kjører LaunchAgent-installer på macOS
5. Printer verifikasjonsoutput

## Dry run

For å se hva som ville skjedd uten å gjøre endringer:

```bash
cd ~/mission-control
./scripts/bootstrap_mission_control.sh --dry-run --skip-launchagent
```

## Nyttige flags

### Skip hooks

```bash
./scripts/bootstrap_mission_control.sh --skip-hooks
```

Brukes hvis du ikke vil konfigurere git hooks lokalt.

### Skip LaunchAgent

```bash
./scripts/bootstrap_mission_control.sh --skip-launchagent
```

Brukes hvis du ikke er på macOS eller ikke vil installere scheduler.

## Verifisering

### Verifiser hooks

```bash
git config core.hooksPath
ls -l .githooks/pre-commit
```

Forventet:
- `core.hooksPath` = `.githooks`
- `.githooks/pre-commit` er executable

### Verifiser prompt helper

```bash
./bin/prompt.sh build
pbpaste | head
```

Forventet:
- prompt skrives til terminal
- prompt kopieres til clipboard

### Verifiser LaunchAgent (macOS)

```bash
launchctl list | grep com.roadmap-ai.morning-standup
plutil -lint ~/Library/LaunchAgents/com.roadmap-ai.morning-standup.plist
```

Forventet:
- agent vises i `launchctl list`
- plist validerer som `OK`

### Manuell test av LaunchAgent

```bash
launchctl kickstart gui/$(id -u)/com.roadmap-ai.morning-standup
tail -n 50 ~/dispatch.log
tail -n 50 ~/dispatch_error.log
```

## Feilsøking

### `missing required command`
Installer manglende verktøy eller bruk passende skip-flag.

### `LaunchAgent installation is only supported on macOS`
Bruk:

```bash
./scripts/bootstrap_mission_control.sh --skip-launchagent
```

### Hook kjører ikke
Bekreft:

```bash
git config core.hooksPath
```

Hvis tom:
```bash
git config core.hooksPath .githooks
```

### Prompt kopieres ikke
Bekreft at `pbcopy` finnes:

```bash
command -v pbcopy
```

## Anbefalt arbeidsflyt

```bash
cd ~/mission-control
./scripts/bootstrap_mission_control.sh
./bin/mc.sh
./bin/prompt.sh build
```

Deretter:
- lim prompt inn i Claude
- jobb én blokk av gangen
- commit små, verifiserte enheter

## Snapshot Export/Import

```bash
./bin/mc.sh snapshot --export snapshot.txt
./bin/mc.sh snapshot --import snapshot.txt
```

Bruk --export for å lagre snapshot til fil, og --import for å vise den igjen senere.

## Log viewer

```bash
./bin/mc.sh logs
./bin/mc.sh logs dispatch --lines 50
./bin/mc.sh logs errors --tail
```

Bruk log viewer til å se mc.log, dispatch.log eller dispatch_error.log direkte fra CLI.

## Snapshot Compare

```bash
./bin/mc.sh snapshot --compare before.txt after.txt
```

Bruk dette for å se forskjeller mellom to tidligere snapshots (viser unified diff).

## Watch mode

```bash
./bin/mc.sh watch
./bin/mc.sh watch --interval 10
```

Gir live dashbord med status/logg/missions. Avslutt med Ctrl+C.


## Archive/Restore

```bash
mc archive <mission-file>
mc list archived
mc restore <mission-file>
```

Arkiver fullførte missions for å holde `.ai/missions/active/` ryddig.
