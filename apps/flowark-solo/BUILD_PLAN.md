# BUILD_PLAN.md — FlowArk Solo

> 30-dagers byggeplan for FlowArk Solo v1.0
> Merk: Dette er en fail-closed produktivitetsapp — alle features må håndhève systemet

## Teknisk stack

| Lag | Teknologi |
|-----|-----------|
| Frontend | Next.js 14 (App Router) |
| Styling | Tailwind CSS + shadcn/ui |
| Database | PostgreSQL (Railway) |
| ORM | Prisma v5 |
| Auth | NextAuth v5 |
| Email | Resend |
| Deploy | Railway |
| Monorepo | Turborepo |

## Filstruktur

```
apps/flowark-solo/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── login/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── page.tsx           # Dagens blokker
│   │   │   ├── frustrasjon/page.tsx
│   │   │   ├── statistikk/page.tsx
│   │   │   └── innstillinger/page.tsx
│   │   ├── api/
│   │   │   ├── auth/[...nextauth]/route.ts
│   │   │   ├── blocks/route.ts
│   │   │   ├── frustration/route.ts
│   │   │   ├── consequence/route.ts
│   │   │   └── health/route.ts
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── DayBlock/
│   │   │   ├── DayBlock.tsx
│   │   │   ├── BlockLock.tsx
│   │   │   └── index.ts
│   │   ├── FrustrationLog/
│   │   │   ├── FrustrationLog.tsx
│   │   │   ├── FrustrationForm.tsx
│   │   │   ├── FrustrationHistory.tsx
│   │   │   └── index.ts
│   │   ├── StreakTracker/
│   │   │   ├── StreakCounter.tsx
│   │   │   ├── HeatmapCalendar.tsx
│   │   │   └── index.ts
│   │   └── ui/                # shadcn komponenter
│   ├── lib/
│   │   ├── consequence-engine.ts
│   │   ├── streak-calculator.ts
│   │   ├── auth.ts
│   │   └── prisma.ts
│   └── types/
│       └── index.ts
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── public/
├── Dockerfile
├── railway.json
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Uke 1: Foundation (Dager 1-7)

### Dag 1-2: Setup og infrastruktur
- [ ] TASK-001: Next.js app scaffold
- [ ] TASK-008: Railway deploy config
- [ ] Sett opp PostgreSQL på Railway
- [ ] Koble domene

### Dag 3-4: Database og auth
- [ ] TASK-002: Prisma schema
- [ ] TASK-007: NextAuth oppsett
- [ ] Magic link login fungerer
- [ ] Database migrering kjører på Railway

### Dag 5-7: Core UI
- [ ] TASK-003: DayBlock UI
- [ ] Dashboard layout
- [ ] Navigasjon mellom sider

## Uke 2: Features (Dager 8-14)

### Dag 8-10: Frustrasjonslogg
- [ ] TASK-004: FrustrationLog component
- [ ] API routes for CRUD
- [ ] Historikk-visning

### Dag 11-14: Konsekvensmotor
- [ ] TASK-005: ConsequenceEngine
- [ ] TASK-006: Streak tracker
- [ ] Cron job for evaluering
- [ ] Notifikasjoner via Resend

## Uke 3: Polish (Dager 15-21)

### Dag 15-17: Analytics
- [ ] 90-dagers heatmap
- [ ] Tap-point analyse
- [ ] Ukentlig rapport (email)

### Dag 18-21: UX-forbedringer
- [ ] Mobile-first responsivt design
- [ ] Merkøl-tilstand og onboarding
- [ ] Error states og edge cases

## Uke 4: Launch (Dager 22-30)

### Dag 22-25: Testing
- [ ] E2E tester med Playwright
- [ ] Load testing
- [ ] Security audit

### Dag 26-28: Beta
- [ ] 5 beta-brukere invitert
- [ ] Feedback innsamlet
- [ ] Kritiske bugs fikset

### Dag 29-30: Launch
- [ ] Product Hunt post
- [ ] Landing page live
- [ ] Stripe payments aktivert

## Suksesskriterier v1.0

- [ ] 20+ aktive brukere
- [ ] Frustrasjonslogg: 15+ entries per bruker
- [ ] Streak: minst 1 bruker med 30-dagers streak
- [ ] Railway uptime: 99.5%+
- [ ] P50 responsetid < 200ms
