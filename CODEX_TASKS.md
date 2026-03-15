# CODEX_TASKS.md

> Oppgaveliste for Codex CLI (Claude Sonnet 4.5) — JarvisATeam roadmap-ai
> Oppdatert: 2024-01
> Status-format: [ ] Pending | [x] Done | [~] In Progress | [!] Blocked

---

## SPRINT 1: FlowArk Solo — Core Infrastructure

### TASK-001: Next.js App Setup
- **Status:** [ ]
- **Prioritet:** P0 – Critical
- **Estimat:** 2t
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Scaffold Next.js 14 app in apps/flowark-solo with: TypeScript strict, Tailwind CSS, shadcn/ui, Prisma ORM, NextAuth. Include app router, src/ structure, and Railway-ready Dockerfile."
  ```
- **Output:** `apps/flowark-solo/` med komplett Next.js 14 struktur
- **Akseptansekriterier:**
  - [ ] `next dev` starter uten feil
  - [ ] Tailwind + shadcn fungerer
  - [ ] Prisma client genereres
  - [ ] Dockerfile bygger

---

### TASK-002: Prisma Database Schema
- **Status:** [ ]
- **Prioritet:** P0 – Critical
- **Estimat:** 1.5t
- **Avhenger av:** TASK-001
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Create Prisma schema for FlowArk Solo with models: User, DayBlock (morning/afternoon/evening), FrustrationLog (text, tapPoint, severity 1-5), ConsequenceRule (if X missed Y times, then Z), HabitStreak. Add Railway PostgreSQL connection string support."
  ```
- **Output:** `packages/db/prisma/schema.prisma`
- **Akseptansekriterier:**
  - [ ] Alle modeller definert
  - [ ] Relations korrekte
  - [ ] `prisma generate` kjører
  - [ ] `prisma migrate dev` feiler ikke

---

### TASK-003: Dag-blokkerings UI
- **Status:** [ ]
- **Prioritet:** P0 – Critical
- **Estimat:** 3t
- **Avhenger av:** TASK-001, TASK-002
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Build the DayBlock UI for FlowArk Solo. Three time blocks: Morgen (06-12), Ettermiddag (12-17), Kveld (17-22). Each block has: task input, duration slider, completion checkbox, block-lock toggle (prevents editing after start). Use shadcn Card + Checkbox + Slider components. Dark theme."
  ```
- **Output:** `apps/flowark-solo/src/components/DayBlock/`
- **Akseptansekriterier:**
  - [ ] Alle tre blokker vises
  - [ ] Lock-mekanisme fungerer
  - [ ] Lagrer til Prisma
  - [ ] Responsivt design

---

### TASK-004: Frustrasjonslogg
- **Status:** [ ]
- **Prioritet:** P1 – High
- **Estimat:** 2t
- **Avhenger av:** TASK-001, TASK-002
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Build FrustrationLog component for FlowArk Solo. Features: free-text entry, tap-point selector (15 predefined categories), severity slider 1-5, timestamp auto-fill, 30-day history view with filter by severity/category. Must reach 15 entries to unlock weekly analysis."
  ```
- **Output:** `apps/flowark-solo/src/components/FrustrationLog/`
- **Akseptansekriterier:**
  - [ ] Ny logg kan opprettes
  - [ ] Historikk vises
  - [ ] Unlock-terskel fungerer
  - [ ] Filtering fungerer

---

### TASK-005: Konsekvensmotor
- **Status:** [ ]
- **Prioritet:** P1 – High
- **Estimat:** 3t
- **Avhenger av:** TASK-002, TASK-003
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Build ConsequenceEngine for FlowArk Solo. Rule-based system: if user misses block X times in Y days, trigger consequence Z. Consequences: lock non-essential features, require journaling before unlock, force review session. Rules stored in DB, evaluated via cron job (Vercel/Railway cron). Include rule builder UI."
  ```
- **Output:** `apps/flowark-solo/src/lib/consequence-engine.ts` + UI
- **Akseptansekriterier:**
  - [ ] Regler kan opprettes
  - [ ] Evaluering skjer automatisk
  - [ ] Konsekvenser aktiveres korrekt
  - [ ] Override krever passord/bekreftelse

---

### TASK-006: Streak-system
- **Status:** [ ]
- **Prioritet:** P1 – High
- **Estimat:** 1.5t
- **Avhenger av:** TASK-002, TASK-003
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Build HabitStreak tracker for FlowArk Solo. Track consecutive days of completing all blocks. Show streak counter, longest streak, 90-day calendar heatmap. Break streak if any block missed. Streak data drives consequence rules (TASK-005)."
  ```
- **Output:** `apps/flowark-solo/src/components/StreakTracker/`

---

## SPRINT 2: FlowArk Solo — Auth + Deploy

### TASK-007: NextAuth Setup
- **Status:** [ ]
- **Prioritet:** P0 – Critical
- **Estimat:** 1.5t
- **Avhenger av:** TASK-001
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Add NextAuth v5 to FlowArk Solo. Providers: Email (magic link via Resend), Google OAuth. Session strategy: database. Protect all routes except /login. Add middleware for auth checking."
  ```

---

### TASK-008: Railway Deploy Config
- **Status:** [ ]
- **Prioritet:** P0 – Critical
- **Estimat:** 1t
- **Avhenger av:** TASK-001
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Create Railway deployment config for FlowArk Solo: railway.json, Dockerfile, .env.example, nixpacks.toml. Include PostgreSQL service link, health check endpoint (/api/health), auto-migrate on deploy script."
  ```
- **Output:** `apps/flowark-solo/railway.json`, `Dockerfile`, `infra/railway/flowark-solo.json`

---

## SPRINT 3: Revenue OS

### TASK-009: Revenue OS Scaffold
- **Status:** [ ]
- **Prioritet:** P1 – High
- **Estimat:** 2t
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Scaffold Revenue OS Next.js 14 app in apps/revenue-os. Features: Stripe dashboard (MRR, churn, LTV), Railway deployment status panel, Resend email metrics. Use shadcn/ui charts, dark theme. Stripe webhook handler for real-time updates."
  ```

---

### TASK-010: Stripe Integration
- **Status:** [ ]
- **Prioritet:** P1 – High
- **Estimat:** 2.5t
- **Avhenger av:** TASK-009
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Implement full Stripe integration for Revenue OS: webhook handler for all subscription events, MRR calculation from active subscriptions, churn detection (subscription.deleted events), LTV calculation, customer portal link generation. Store events in PostgreSQL."
  ```

---

## SPRINT 4: Shared Packages

### TASK-011: UI Package
- **Status:** [ ]
- **Prioritet:** P2 – Medium
- **Estimat:** 2t
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Create packages/ui shared component library. Extract common components from FlowArk Solo and Revenue OS: Button, Card, Input, Modal, Toast, LoadingSpinner. Use shadcn/ui as base. Export as ESM package with TypeScript types."
  ```

---

### TASK-012: GitHub Actions CI/CD
- **Status:** [ ]
- **Prioritet:** P1 – High
- **Estimat:** 1.5t
- **Kommando:**
  ```bash
  codex --model claude-sonnet-4-5 \
    "Create GitHub Actions workflows: 1) ci.yml - lint, type-check, test on PR. 2) deploy-flowark.yml - deploy to Railway on push to main. 3) deploy-revenue-os.yml - deploy Revenue OS to Railway. Use RAILWAY_TOKEN secret."
  ```
- **Output:** `.github/workflows/`

---

## Kjelle-kommando (alt på en gang)

```bash
# Kjør alle P0 oppgaver sekvensielt
for task in TASK-001 TASK-002 TASK-003 TASK-007 TASK-008; do
  echo "=== $task ==="
  codex --model claude-sonnet-4-5 --task "$task"
done
```

## Status Dashboard

| Task | Tittel | Prioritet | Status | Est |
|------|--------|-----------|--------|-----|
| TASK-001 | Next.js Setup | P0 | [ ] | 2t |
| TASK-002 | Prisma Schema | P0 | [ ] | 1.5t |
| TASK-003 | DayBlock UI | P0 | [ ] | 3t |
| TASK-004 | Frustrasjonslogg | P1 | [ ] | 2t |
| TASK-005 | Konsekvensmotor | P1 | [ ] | 3t |
| TASK-006 | Streak System | P1 | [ ] | 1.5t |
| TASK-007 | NextAuth | P0 | [ ] | 1.5t |
| TASK-008 | Railway Deploy | P0 | [ ] | 1t |
| TASK-009 | Revenue OS | P1 | [ ] | 2t |
| TASK-010 | Stripe Integration | P1 | [ ] | 2.5t |
| TASK-011 | UI Package | P2 | [ ] | 2t |
| TASK-012 | CI/CD Workflows | P1 | [ ] | 1.5t |

**Total estimat:** ~23.5 timer
