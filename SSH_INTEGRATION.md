# SSH-aimigo Integration Guide for roadmap.ai

## Oversikt

Dette dokumentet forklarer hvordan roadmap.ai brukes sammen med SSH-baserte AI-verktøy (som Codex CLI, Claude Code, eller andre AI-terminaler) for å bygge systemer effektivt og sikkert.

## Hva er SSH-aimigo?

SSH-aimigo refererer til AI-assistenter som kan:
- Kjøre kommandoer på remote servere via SSH
- Deploye kode automatisk
- Administrere infrastruktur
- Utføre oppgaver i terminal gjennom naturlig språk

Eksempler:
- Codex CLI (Claude Sonnet 4.5/4.6)
- Chaterm AI SSH Terminal
- Claude Code med SSH-tilgang
- MCP SSH-servere

## Hvordan roadmap.ai hjelper systembygging

### 1. Strukturert oppgaveliste (CODEX_TASKS.md)

roadmap.ai gir:
- **Atomiske oppgaver**: Hver task har én klar kommando
- **Estimater**: Tidsestimat per oppgave (2t, 3t, etc.)
- **Prioritering**: P0 (critical), P1 (high), P2 (medium)
- **Avhengigheter**: Task-002 avhenger av Task-001

Eksempel:
```bash
codex --model claude-sonnet-4-5 \
  "Scaffold Next.js 14 app in apps/flowark-solo with: 
   TypeScript strict, Tailwind CSS, shadcn/ui, Prisma ORM"
```

### 2. State-to-action mapping

roadmap.ai mapper biologisk state til riktig arbeidsmodus:

```
God søvn + høy energi → Deep Build (koding)
OK søvn + middels energi → Light Ops (admin, testing)
Dårlig søvn / irritert → Recover (dokumentasjon, review)
```

Dette sikrer at AI-oppgaver matches med din faktiske kapasitet.

### 3. Fail-closed filosofi

roadmap.ai krever:
- **Pre-execution research**: Terminal research før hver oppgave
- **Cost estimation**: Estimat token-bruk før kjøring
- **Explicit exclusion**: NOT_IN_V1.md lister hva som IKKE skal bygges

## SSH-aimigo workflow med roadmap.ai

### Setup

1. **Start SSH-agent med sikker nøkkel**:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
# Nøkkelen er nå tilgjengelig for AI uten å eksponere private key
```

2. **Velg oppgave fra CODEX_TASKS.md**:
```bash
# Se alle P0 oppgaver
grep -A 5 'Status: \[ \]' CODEX_TASKS.md | grep -B 3 'P0'
```

3. **Kjør via Codex CLI**:
```bash
codex --model claude-sonnet-4-6 \
  --task "TASK-001: Next.js App Setup" \
  --context "$(cat apps/flowark-solo/SPEC.md)"
```

### Eksempel-workflow

**Scenario**: Bygge FlowArk Solo MVP

**Steg 1: Research** (terminal)
```bash
# AI kjører først research
codex research "Next.js 14 app router best practices"
codex research "Prisma with Railway PostgreSQL setup"
```

**Steg 2: Execute** (fra CODEX_TASKS.md)
```bash
codex execute TASK-001  # Scaffold app
codex execute TASK-002  # Prisma schema
codex execute TASK-003  # DayBlock UI
```

**Steg 3: Deploy** (via Railway SSH)
```bash
ssh railway@app.railway.app deploy flowark-solo
```

**Steg 4: Verify**
```bash
curl https://flowark-solo.up.railway.app/api/health
```

## Integrasjon med GenieSystem v1.1.1

GenieSystem (packages/ginie-system) wrapper SSH-kommandoer:

```typescript
import { GenieSystem } from '@roadmap-ai/ginie-system';

const genie = new GenieSystem();
await genie.initialize();

// AI kjører kommando via SSH
const result = await genie.execute(
  'ssh user@server "cd /app && npm run build"'
);

console.log(result);
```

### ShellWrapper sikkerhetsfeatures

- **Command wrapping**: Alle kommandoer logges
- **Timeout protection**: Max 30s per kommando
- **Error handling**: Graceful failure
- **Audit trail**: Full kommandohistorikk

### FlowArkDome operational tracking

- **Operation queuing**: Flere SSH-tasks i kø
- **Status tracking**: pending → running → completed
- **Concurrent ops**: Max 5 samtidige operasjoner
- **Failure recovery**: Automatisk retry-logikk

## Sikkerhetsprinsipper

### 1. Aldri eksponere secrets

❌ **Feil**:
```bash
codex "deploy with password: mysecret123"
```

✅ **Riktig**:
```bash
# Bruk ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/deploy_key
codex "deploy via ssh"
```

### 2. Preview før execute

AI skal alltid vise kommandoen før kjøring:
```
[AI Preview]
Kommando: ssh deploy@prod "docker compose up -d"
Impact: Starter production deployment
Estimat: 45 sekunder

Bekreft? [y/N]
```

### 3. Audit trail

Alle SSH-kommandoer logges:
```bash
# GenieSystem logger automatisk
[2026-03-16 05:23:41] [ShellWrapper] Executing: ssh deploy@prod
[2026-03-16 05:23:45] [FlowArkDome] Operation op_1710563021_abc123 completed
```

## Praktiske brukseksempler

### Eksempel 1: Deploye til Railway

```bash
# 1. Hent deployment config fra roadmap
cat infra/railway/flowark-solo.json

# 2. AI scaffold Railway config hvis mangler
codex --task "TASK-008: Railway Deploy Config"

# 3. Deploy via Railway CLI (AI-kontrollert)
railway up --service flowark-solo

# 4. Verifiser deployment
railway logs --service flowark-solo --tail 50
```

### Eksempel 2: Codex kjører test-suite

```bash
# AI leser CODEX_TASKS.md
codex --read CODEX_TASKS.md

# Kjører alle P0 tasks sekvensielt
for task in TASK-001 TASK-002 TASK-007 TASK-008; do
  echo "=== $task ==="
  codex --model claude-sonnet-4-6 --task "$task"
done
```

### Eksempel 3: Remote debugging

```bash
# SSH inn til Railway med AI-assistanse
codex "SSH into Railway production, check logs for errors"

# AI kjører:
ssh railway@flowark-solo.railway.app
tail -f /var/log/app.log | grep ERROR
```

## Workflow-diagram

```
┌─────────────────┐
│  roadmap.ai     │
│  CODEX_TASKS.md │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Codex CLI      │
│  (AI terminal)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GenieSystem    │
│  ShellWrapper   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SSH Connection │
│  (Railway/VPS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deploy/Build   │
│  Production     │
└─────────────────┘
```

## Neste steg

1. **Installer Codex CLI**:
```bash
npm install -g @anthropic/codex-cli
```

2. **Konfigurer SSH-nøkler**:
```bash
ssh-keygen -t ed25519 -C "codex@roadmap-ai"
ssh-add ~/.ssh/id_ed25519
```

3. **Test GenieSystem**:
```bash
cd packages/ginie-system
npm install
npm run build
npm test
```

4. **Kjør første task**:
```bash
codex --task "TASK-001: Next.js App Setup"
```

## Ressurser

- [CODEX_TASKS.md](./CODEX_TASKS.md) - Alle byggoppgaver
- [ROADMAP.md](./ROADMAP.md) - 90-dagers masterplan
- [GenieSystem README](./packages/ginie-system/README.md) - Shell wrapper docs
- [Railway docs](https://docs.railway.app/) - Deployment platform

---

**Versjon**: 1.0.0  
**Oppdatert**: 2026-03-16  
**Forfatter**: JarvisATeam
