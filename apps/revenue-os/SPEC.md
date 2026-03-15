# SPEC.md — Revenue OS

> Produktspesifikasjon for Revenue OS
> Versjon: v0.1.0-spec | Status: planning

## Hva er Revenue OS?

Revenue OS er et internt operasjonsdashboard for JarvisATeam som konsoliderer
inntektsdata fra Stripe, deployment-status fra Railway, og e-postmetrikker fra Resend
i et enkelt grensesnitt.

**Målgruppe:** Interne operatorer og founders som trenger sanntidsoversiktø over
business health uten å navigere mellom 5+ verktøy.

## Kjernefeatures

### 1. Stripe Revenue Dashboard
- **MRR (Monthly Recurring Revenue):** Beregnet fra aktive subscriptions
- **ARR:** MRR x 12
- **Churn rate:** Kansellerte subscriptions siste 30 dager
- **LTV:** Gjennomsnittlig kundelivstidsverdi
- **New MRR:** Nye subscriptions denne måneden
- **Expansion MRR:** Oppgraderinger
- **Contraction MRR:** Nedgraderinger
- **Net New MRR:** New + Expansion - Contraction - Churn

### 2. Kundeoversikt
- Liste over alle Stripe-kunder
- Subscription status (active/past_due/canceled)
- Betalingshistorikk
- Customer portal link

### 3. Railway Deployment Status
- Aktive deployments per service
- Siste deploy timestamp
- Build logs (siste 50 linjer)
- Health check status
- Ressursbruk (CPU/RAM)

### 4. Resend E-postmetrikker
- Sendte e-poster siste 30 dager
- Åpningsrate
- Klikkrate
- Bounce rate
- Unsubscribe rate

### 5. Webhook Event Log
- Real-time Stripe webhooks
- Event type, timestamp, payload
- Retry-status for feiledeevents

## Teknisk Stack

| Lag | Teknologi | Begrunnelse |
|-----|-----------|-------------|
| Framework | Next.js 14 (App Router) | Konsistent med FlowArk Solo |
| Styling | Tailwind CSS + shadcn/ui | Delt designsystem |
| Charts | Recharts / shadcn charts | Enkel integrasjon |
| Database | PostgreSQL (Railway) | Event storage |
| ORM | Prisma | Delt schema |
| Auth | NextAuth (admin only) | Intern tool |
| Stripe | stripe npm + webhooks | Core data source |
| Railway API | Railway GraphQL API | Deployment data |
| Resend | Resend API | Email metrics |
| Deploy | Railway | Co-lokalisert med data |

## Datamodell

```prisma
model StripeEvent {
  id          String   @id
  type        String
  data        Json
  processed   Boolean  @default(false)
  createdAt   DateTime @default(now())
}

model MRRSnapshot {
  id        String   @id @default(cuid())
  date      DateTime
  mrr       Float
  arr       Float
  customers Int
  churn     Float
  createdAt DateTime @default(now())
}

model DeploymentLog {
  id          String   @id @default(cuid())
  service     String
  environment String
  status      String
  deployedAt  DateTime
  commitSha   String?
  createdAt   DateTime @default(now())
}
```

## API Routes

```
GET  /api/stripe/metrics     — MRR, ARR, churn etc.
GET  /api/stripe/customers   — Kundliste
POST /api/stripe/webhook     — Stripe webhook handler
GET  /api/railway/status     — Deployment statuses
GET  /api/resend/metrics     — Email metrics
GET  /api/health             — Health check
```

## UI Sider

```
/                   — Overview dashboard (MRR, health summary)
/revenue            — Detaljert revenue metrics
/customers          — Kundliste og detaljer
/deployments        — Railway deployment status
/emails             — Resend metrics
/events             — Webhook event log
```

## Webhook-håndtering

Stripe webhooks som må håndteres:
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.created`
- `payment_intent.succeeded`

## Suksesskriterier

- [ ] MRR vises korrekt og matcher Stripe dashboard
- [ ] Webhooks behandles innen 2 sekunder
- [ ] Railway status oppdateres hvert 60. sekund
- [ ] Dashboard laster < 1 sekund (cached data)
- [ ] Ingen sensitive data eksponert i frontend

## Hva Revenue OS IKKE er

- Ikke en erstatning for Stripe Dashboard
- Ikke et CRM
- Ikke kundekommunikasjonsverktøy
- Ikke offentlig tilgjengelig
