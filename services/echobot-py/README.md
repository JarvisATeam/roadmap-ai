# ECHOBOT v3.0 — Asymmetrisk Verdimotor
**Produksjonsklar. Merget + korrigert. MAC/JETSON-kompatibel.**
**Christer Osen / GinieSystem — April 2026**

---

## Installasjon

```bash
pip install -r requirements.txt
```

## Miljøvariabler (.env)

```bash
# Påkrevd
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Valgfritt (berikelse)
FIRECRAWL_API_KEY=fc-...        # Hobby $16/mnd (600 sider) — eller selvhost
APOLLO_API_KEY=...              # Firmografi og tech stack
GRAYHAT_API_KEY=...             # S3 OSINT (kun eksistens-sjekk)

# Valgfritt (utsendelse)
SENDGRID_API_KEY=SG...          # Uten: dry-run modus
FROM_EMAIL=you@yourdomain.com
N8N_ONBOARDING_WEBHOOK_URL=https://...  # n8n/Zapier leveranse ved invoice.paid
```

## leads.csv format

```
domain,email,name,company
example-startup.io,cto@example-startup.io,Jane Smith,Example Startup
```

## Bruk

```bash
# Steg 1: Berik leads og generer utkast
python echobot_v3.py --mode hunt --input leads.csv --leads 50

# Steg 2: Manuell godkjenning (~2 min/lead)
python echobot_v3.py --mode review

# Steg 3: Send godkjente e-poster (maks 50/kohort)
python echobot_v3.py --mode send

# Steg 4: Start webhook-server
uvicorn echobot_v3:webhook_app --host 0.0.0.0 --port 8000

# Statistikk
python echobot_v3.py --mode stats
```

## Arkitektur

```
leads.csv
    │
    ▼
[Komponent 1] Parallell Enrichment (3 lag)
  ├── HTTP-hode-inspeksjon (legal OSINT)
  ├── Firecrawl JSON extraction (valgfritt)
  ├── Apollo.io firmografi (valgfritt)
  └── Grayhat Warfare S3 OSINT (kun eksistens)
    │
    ▼
[Komponent 2] Two-Layer Truth-Checker
  ├── Lag 1: GPT-4.1 nano — Hypotesegenerering
  │         Confidence-filter: < 0.7 → FORKASTET
  └── Lag 2: GPT-4.1 — Kynisk redaktør (structured JSON)
             status == "FAILED" → FORKASTET
    │
    ▼
[Manuell Review] Godkjenn / Avvis / Editer
    │
    ▼
[Komponent 3] 3-7-7 Kadens
  ├── Dag 0:  Timeline-hook (< 75 ord, 1 CTA)
  ├── Dag 3:  Verditillegg (nytt datapunkt)
  ├── Dag 10: Vinkelskifte (ROI/sosialt bevis)
  └── Dag 17: Fratredelsesmelding
    │
    ▼
[Komponent 4] Webhook + Stripe
  ├── /webhook/reply   → sentiment → Stripe invoice (ved "Interessert")
  ├── /webhook/stripe  → invoice.paid → n8n onboarding (idempotent)
  └── /webhook/unsubscribe → RFC 8058 opt-out
```

## Token-økonomi ($50 budsjett)

| Lag | Modell | Volum | Kostnad |
|-----|--------|-------|---------|
| Enrichment parsing | GPT-4.1 nano (cached) | ~2000 leads | ~$4–6 |
| Hypotesegenerering | GPT-4.1 nano | ~2000 leads | ~$5–8 |
| Truth-checker + utkast | GPT-4.1 | ~200 leads | ~$20–25 |
| Reserve / killswitch | — | — | ~$10 |

## Modeller og priser (april 2026)

| Modell | Input | Cached input | Output |
|--------|-------|--------------|--------|
| GPT-4.1 nano | $0.10/1M | $0.025/1M | $0.40/1M |
| GPT-4.1 | $2.00/1M | $0.50/1M | $8.00/1M |
| GPT-4o-mini | $0.15/1M | $0.075/1M | $0.60/1M |

## Stopp-regler (GDPR + leveringsdyktighet)

- Spam-klagerate: siktemål < 0.05% (Google-grense: 0.10%)
- Bounce-rate: < 2.0% (over 8% → full pause)
- Kohort: aldri > 50 per utsendelse
- Opt-out: propageres umiddelbart til DB
- Stripe: idempotent event_id-deduplication
- S3 OSINT: kun eksistens-sjekk, aldri list/download

## Webhook-endepunkter

| Endepunkt | Metode | Formål |
|-----------|--------|--------|
| /webhook/reply | POST | Svar-klassifisering + Stripe onboarding |
| /webhook/stripe | POST | Betaling mottatt → n8n leveranse |
| /webhook/unsubscribe | POST | RFC 8058 opt-out |
| /health | GET | Systemstatus + statistikk |

## Stripe Webhook Setup

```bash
# Installer Stripe CLI
brew install stripe/stripe-cli/stripe

# Lokal testing
stripe listen --forward-to localhost:8000/webhook/stripe

# Produksjon: registrer i Stripe Dashboard
# Events å lytte på: invoice.paid, customer.created
```
