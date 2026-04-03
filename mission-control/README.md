# Mission Control

Mission Control is a local operator toolkit for running a structured AI-assisted workflow with:

- bootstrap installation
- versioned git hooks
- prompt helpers with clipboard copy
- environment diagnostics
- LaunchAgent automation on macOS
- setup and build workflow documentation



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

## Quick start

```bash
cd ~/mission-control
./scripts/bootstrap_mission_control.sh
./bin/doctor.sh
./bin/prompt.sh build
```

## Main commands

### Bootstrap setup

```bash
./scripts/bootstrap_mission_control.sh
```

Useful flags:

```
./scripts/bootstrap_mission_control.sh --dry-run --skip-launchagent
./scripts/bootstrap_mission_control.sh --skip-hooks
```



### Status

```bash
./bin/mc.sh status
```

### Init

```bash
./bin/mc.sh init
```

### Shell completions

Bash:

```bash
source ./completions/mc.bash
```

Zsh:

```bash
source ./completions/mc.zsh
```

### Doctor

```bash
./bin/doctor.sh
./bin/mc.sh doctor
```

### Prompt helper

```bash
./bin/prompt.sh list
./bin/prompt.sh build
./bin/prompt.sh plan
./bin/prompt.sh dream
./bin/prompt.sh security
```

### Self-test

```bash
./scripts/selftest_mission_control.sh
```

## Documentation

- `docs/SETUP.md` — install and verification flow
- `docs/SYSTEM_PROMPT_BUILD.md` — build workflow prompt
- `docs/EXPORT_STATUS.md` — export audit
- `HANDOFF.md` — ongoing project handoff notes

## Repo capabilities

- `bin/mc.sh` — main entry point
- `bin/doctor.sh` — environment diagnostics
- `bin/prompt.sh` — prompt output + clipboard copy
- `.githooks/pre-commit` — versioned local git hook
- `scripts/install_launchagent.sh` — morning standup scheduler
- `scripts/bootstrap_mission_control.sh` — local setup bootstrap

## Recommended workflow

```bash
./scripts/bootstrap_mission_control.sh
./bin/doctor.sh
./bin/mc.sh
./bin/prompt.sh build
```

Then:
1. paste the prompt into Claude
2. build one verified block at a time
3. commit small, validated units

### Snapshot Export/Import

```bash
./bin/mc.sh snapshot --export snapshot.txt
./bin/mc.sh snapshot --import snapshot.txt
```

Use --export to write the current snapshot to a file (for sharing/archiving) and --import to re-display a stored snapshot later.

### Log viewer

```bash
./bin/mc.sh logs
./bin/mc.sh logs dispatch --lines 20
./bin/mc.sh logs errors --tail
```

Quickly inspect mission-control logs (mc.log) or dispatch logs, with optional tail/line limits.

### Snapshot Compare

```bash
./bin/mc.sh snapshot --compare before.txt after.txt
./bin/mc.sh snapshot --diff before.txt after.txt
```

Shows unified diffs between two snapshot files to highlight what changed.

### Watch mode

```bash
./bin/mc.sh watch
./bin/mc.sh watch --interval 10
```

Live auto-refresh dashboard showing status, logs, missions, and git state.


### Archive/Restore

```bash
mc archive 001-my-feature.md
mc list archived
mc restore 001-my-feature.md
```

Manage mission lifecycle by archiving completed or paused missions.

### Continuous Integration

```bash
name: Mission Control CI
file: .github/workflows/mission-control.yml
```

Every push and pull request runs the workflow to keep `mc` healthy:

1. `./scripts/bootstrap_mission_control.sh --skip-launchagent`
2. `./scripts/selftest_mission_control.sh`
3. `./bin/mc.sh doctor --json`
4. `./bin/mc.sh snapshot --export ci-snapshot.txt` (uploaded as an artifact)

Use the artifact to review the latest mission snapshot directly from CI logs.
