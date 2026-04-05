# ECHOBOT Operator Specification

Detaljert spesifikasjon for ECHOBOT operatørgrensesnitt og API.

---

## Oversikt

ECHOBOT v3.0 er en asymmetrisk verdiverktøy som konverterer ~50 USD i tokenkost til 800+ USD i leveranser. Systemet består av:

- **Python Service** (`services/echobot-py/`) - Execution engine
- **Next.js Operator** (`apps/roadmap-operator/`) - UI og API adapter
- **Shared Contracts** (`packages/operator-contracts/`) - TypeScript typer

---

## Datakontrakter

### EchobotLead

```typescript
interface EchobotLead {
  id?: string;
  domain: string;
  companyName: string;
  contactEmail: string;
  contactName?: string;
  hypothesis: string;
  hookType?: string;
  compressedTimeline?: string;
  draftSubject?: string;
  draftBody?: string;
  evidenceUrl?: string;
  confidenceScore: number;        // 0.0 - 1.0
  truthStatus: "PASSED" | "FAILED" | "PENDING";
  sendStatus: "QUEUE" | "APPROVED" | "REJECTED" | "SENT";
  replySentiment?: "positive" | "neutral" | "negative" | "unknown";
  stripeInvoiceUrl?: string;
  optedOut?: boolean;
  createdAt?: string;
}
```

### EchobotStats

```typescript
interface EchobotStats {
  total: number;
  leadsByStatus: Record<string, number>;
  leadsByTruth: Record<string, number>;
  sentiments: Record<string, number>;
  replyRate: number;              // 0.0 - 1.0
  positiveRate: number;           // 0.0 - 1.0
  queueSize: number;
}
```

### RoadmapMissionPayload

```typescript
interface RoadmapMissionPayload {
  missionTitle: string;
  origin: "echobot" | "manual" | "other";
  proofDefinition: {
    description: string;
    requiredArtifacts?: string[];
  };
  operatorNotes?: string;
  nextActions: string[];
  metadata?: Record<string, unknown>;
}
```

### RoadmapSyncResult

```typescript
interface RoadmapSyncResult {
  missionId: string;
  createdAt: string;
  status: "created" | "queued" | "skipped" | "blocked" | "already_processed";
}
```

---

## API Spesifikasjon

### GET /api/echobot/stats

Returnerer aggregert statistikk for Echobot leads.

**Response:** `EchobotStats`

```json
{
  "total": 150,
  "leadsByStatus": { "QUEUE": 50, "APPROVED": 30, "SENT": 70 },
  "leadsByTruth": { "PASSED": 120, "FAILED": 20, "PENDING": 10 },
  "sentiments": { "positive": 15, "neutral": 45, "negative": 10 },
  "replyRate": 0.47,
  "positiveRate": 0.21,
  "queueSize": 50
}
```

---

### GET /api/echobot/review

Returnerer leads som venter på gjennomgang.

**Response:** `EchobotLead[]`

Filtrerer leads hvor:
- `sendStatus === "QUEUE"` ELLER
- `truthStatus === "PENDING"` OG `sendStatus !== "SENT"`

---

### POST /api/echobot/review

Godkjenn eller avvis et lead.

**Request:**
```json
{
  "leadId": "lead-123",
  "action": "approve" | "reject",
  "notes": "Optional reviewer notes"
}
```

**Response:**
```json
{
  "success": true,
  "leadId": "lead-123",
  "action": "approve",
  "notes": "Optional reviewer notes"
}
```

**Validering:**
- Lead må eksistere
- Lead kan ikke allerede være `SENT`
- Lead kan ikke være `optedOut`
- Lead kan ikke ha `truthStatus === "FAILED"`

---

### GET /api/echobot/sync?leadId={id}&preview=true

Returnerer preview av hva som ville blitt synkronisert.

**Response:** `RoadmapSyncPreview`

```json
{
  "lead": { /* EchobotLead */ },
  "payload": {
    "missionTitle": "Echobot: Company Name",
    "origin": "echobot",
    "proofDefinition": {
      "description": "Lead hypothesis",
      "requiredArtifacts": ["evidence-url"]
    },
    "nextActions": [
      "Send personalized outreach email",
      "Schedule discovery call",
      "Capture proof of value delivery"
    ]
  }
}
```

---

### POST /api/echobot/sync

Synkroniserer lead til Roadmap mission.

**Request:**
```json
{
  "leadId": "lead-123",
  "operatorNotes": "Optional notes"
}
```

**Response:** `RoadmapSyncResult`

```json
{
  "missionId": "mission-456",
  "createdAt": "2026-04-05T12:00:00Z",
  "status": "created"
}
```

**Fail-closed regler:**
- Krever `replySentiment === "positive"` ELLER `stripeInvoiceUrl` satt
- Lead kan ikke være `optedOut`
- Lead kan ikke ha `truthStatus === "FAILED"`

---

### POST /api/echobot/webhook/reply

Mottar svar fra leads (SMS/email).

**Request:**
```json
{
  "leadId": "lead-123",
  "sentiment": "positive" | "neutral" | "negative",
  "replyText": "User reply content"
}
```

**Response:**
```json
{ "success": true, "processed": true }
```

---

### POST /api/echobot/webhook/stripe

Mottar Stripe betalingseventer.

**Request:** Stripe webhook payload

**Håndtering:**
- Deduplisering via `eventId`
- Kun `invoice.paid` prosesseres
- Lagrer `stripeInvoiceUrl` på lead
- Trigger n8n onboarding workflow

**Response:**
```json
{ "success": true, "processed": true }
```

---

### POST /api/echobot/webhook/unsubscribe

Mottar opt-out forespørsler.

**Request:**
```json
{
  "email": "user@example.com",
  "leadId": "lead-123",
  "reason": "Optional reason"
}
```

**Håndtering:**
- Setter `optedOut = true` på lead
- Logger reason hvis oppgitt

**Response:**
```json
{ "success": true, "optedOut": true }
```

---

## Forretningsregler (Policy)

### canApprove(lead)

Lead kan godkjennes hvis:
- `sendStatus !== "SENT"`
- `optedOut !== true`
- `truthStatus !== "FAILED"`
- `truthStatus` er `PASSED` eller `PENDING`

### canSync(lead)

Lead kan synkroniseres hvis:
- `replySentiment === "positive"` ELLER `stripeInvoiceUrl` er satt
- `optedOut !== true`
- `truthStatus !== "FAILED"`

### shouldShowInReviewQueue(lead)

Lead vises i review queue hvis:
- `sendStatus === "QUEUE"` ELLER
- `truthStatus === "PENDING"` OG `sendStatus !== "SENT"`

### getRiskLevel(lead)

Returnerer risikonivå:
- `"high"`: `truthStatus === "FAILED"` eller `optedOut` eller `confidenceScore < 0.5`
- `"medium"`: `confidenceScore < 0.7`
- `"low"`: Alt annet

---

## UI Komponenter

### StatsPanel

Viser 4 kort:
1. **Total Leads** - Antall leads totalt
2. **Reply Rate** - Prosentandel med svar
3. **Positive Rate** - Prosentandel positive svar
4. **Queue Size** - Antall leads i kø

### ReviewTable

Kolonner:
- Company (med opted out badge)
- Domain
- Truth Status (badge)
- Confidence (prosent)
- Send Status (badge)
- Reply Sentiment (badge)
- Actions (Approve/Reject/Sync knapper)

### SyncPreviewModal

Viser:
- Mission Title
- Proof Definition
- Next Actions liste
- Close knapp

---

## Badge Fargekoding

### Truth Status
- `PASSED` - Grønn
- `FAILED` - Rød
- `PENDING` - Gul

### Send Status
- `SENT` - Blå
- `APPROVED` - Grønn
- `REJECTED` - Rød
- `QUEUE` - Grå

### Sentiment
- `positive` - Grønn
- `negative` - Rød
- `neutral` - Grå
- `unknown` - Gul

---

## Fail-Closed Prinsipper

1. **Ingen auto-send** uten manuell approval
2. **Ingen sync** uten positivt signal (reply sentiment eller betaling)
3. **Ingen sync** hvis opted out
4. **Ingen sync** hvis truth check failed
5. **Stripe events dedupliseres** via `processed_events` tabell
6. **Opt-outs håndteres** i databasen og surfaces i UI

---

## Sikkerhet

- Webhook payload valideres alltid
- Stripe signatur verifiseres (TODO)
- API krever autentisering (TODO)
- Secrets lagres i miljøvariabler

---

## Observabilitet

### Logging
- Strukturert logging i Python og TypeScript
- Logg `replySentiment`, faktura-URL, unsubscribes

### Health Checks
- Python: `/health` returnerer systemstatus
- Next.js: Innebygd Next.js health check

### Metrics
- `leads_total`
- `leads_sent`
- `leads_queue`
- `reply_rate`
- `positive_rate`

---

## Testing

### Unit-tester (TODO)
- `mapper.ts` - Payload konvertering
- `policy.ts` - Signal-regler

### Integrasjonstester (TODO)
- API routes med mock data
- Webhook scenarioer (positiv/negativ/unsubscribe)
- Stripe webhook signering
- Idempotens (samme event skal avvises)

### E2E-tester (TODO)
- Full flyt: Lead → Review → Approve → Sync

---

## Deployment

### Next.js (Operator UI)
- **Plattform**: Vercel (anbefalt)
- **Build**: `npm run build`
- **Port**: 3001

### Python Service
- **Plattform**: Container/Cloud Run
- **Runtime**: Uvicorn
- **Port**: 8000

### Miljøvariabler
```bash
# Python
STRIPE_WEBHOOK_SECRET=
OPENAI_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=

# Next.js
NEXT_PUBLIC_API_URL=
ROADMAP_API_KEY=
```

---

## Veikart

### P5 - Testing & Hardening
- [ ] Unit-tester for mapper.ts
- [ ] Unit-tester for policy.ts
- [ ] API route tester
- [ ] Webhook integrasjonstester

### P6 - Faktisk Mission Sync
- [ ] Koble til Roadmap missions service
- [ ] Implementere POST /missions
- [ ] Verifisere fail-closed regler

### P7 - Deployment
- [ ] Vercel deployment
- [ ] Python container build
- [ ] Miljøvariabler konfigurasjon
- [ ] Overvåking og alerting

---

*Sist oppdatert: 2026-04-05*
*Versjon: 1.0*
