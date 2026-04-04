#!/usr/bin/env python3
"""
ECHOBOT v3.0 — Asymmetrisk Verdimotor
Produksjonsklar. MAC/JETSON-kompatibel.
Christer Osen / GinieSystem — April 2026

Bruk:
  python echobot_v3.py --mode hunt --input leads.csv --leads 50
  python echobot_v3.py --mode review
  python echobot_v3.py --mode send
  uvicorn echobot_v3:webhook_app --host 0.0.0.0 --port 8000
  python echobot_v3.py --mode stats
"""

import asyncio
import argparse
import json
import logging
import os
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

import aiohttp
import stripe
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY        = os.environ.get("OPENAI_API_KEY", "")
FIRECRAWL_API_KEY     = os.environ.get("FIRECRAWL_API_KEY", "")
APOLLO_API_KEY        = os.environ.get("APOLLO_API_KEY", "")
GRAYHAT_API_KEY       = os.environ.get("GRAYHAT_API_KEY", "")
STRIPE_SECRET_KEY     = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
SENDGRID_API_KEY      = os.environ.get("SENDGRID_API_KEY", "")
FROM_EMAIL            = os.environ.get("FROM_EMAIL", "you@yourdomain.com")
N8N_ONBOARDING_URL    = os.environ.get("N8N_ONBOARDING_WEBHOOK_URL", "")

DB_PATH            = Path("echobot.db")
MODEL_TRIAGE       = "gpt-4.1-nano"
MODEL_CHECKER      = "gpt-4.1"
MODEL_HYPOTHESIS   = "gpt-4.1-nano"
SEMAPHORE_TRIAGE   = 20
SEMAPHORE_CHECKER  = 5
MAX_COHORT_SIZE    = 50
INVOICE_AMOUNT_USD = 800

stripe.api_key = STRIPE_SECRET_KEY
client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("echobot")

# ─── DATAMODELL ───────────────────────────────────────────────────────────────
@dataclass
class Lead:
    domain: str
    company_name: str = ""
    contact_email: str = ""
    contact_name: str = ""
    tech_stack_raw: str = ""
    apollo_data: str = ""
    s3_buckets_found: str = ""
    hypothesis: str = ""
    evidence_url: str = ""
    confidence_score: float = 0.0
    hook_type: str = ""
    compressed_timeline: str = ""
    draft_subject: str = ""
    draft_body: str = ""
    truth_status: str = "PENDING"
    send_status: str = "QUEUE"
    followup_day: int = 0
    reply_sentiment: str = ""
    stripe_invoice_url: str = ""
    legal_basis: str = "legitimate_interest"
    data_retention_days: int = 90
    opted_out: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

# ─── DATABASE ─────────────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS leads (
        domain TEXT PRIMARY KEY, data JSON NOT NULL, updated_at TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS processed_events (
        event_id TEXT PRIMARY KEY, processed_at TEXT)""")
    con.commit()
    con.close()

def save_lead(lead: Lead):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT OR REPLACE INTO leads (domain, data, updated_at) VALUES (?, ?, ?)",
        (lead.domain, json.dumps(asdict(lead)), datetime.utcnow().isoformat())
    )
    con.commit()
    con.close()

def load_leads(send_status: str = None) -> list:
    con = sqlite3.connect(DB_PATH)
    if send_status:
        rows = con.execute(
            "SELECT data FROM leads WHERE json_extract(data, '$.send_status') = ?",
            (send_status,)
        ).fetchall()
    else:
        rows = con.execute("SELECT data FROM leads").fetchall()
    con.close()
    return [Lead(**json.loads(r[0])) for r in rows]

def event_processed(event_id: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    r = con.execute("SELECT 1 FROM processed_events WHERE event_id = ?", (event_id,)).fetchone()
    con.close()
    return r is not None

def mark_event_processed(event_id: str):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT OR IGNORE INTO processed_events (event_id, processed_at) VALUES (?, ?)",
        (event_id, datetime.utcnow().isoformat())
    )
    con.commit()
    con.close()

# ─── KOMPONENT 1: ENRICHMENT ──────────────────────────────────────────────────
async def fetch_http_headers(session: aiohttp.ClientSession, domain: str) -> dict:
    """Passiv OSINT — kun hoder serveren frivillig returnerer."""
    found = {}
    try:
        async with session.get(
            f"https://{domain}",
            timeout=aiohttp.ClientTimeout(total=8),
            allow_redirects=True
        ) as r:
            for key in [
                "x-powered-by", "server", "x-aspnet-version",
                "x-amz-bucket-region", "x-amz-request-id",
                "x-generator", "x-drupal-cache", "x-wp-total",
                "x-runtime", "x-rack-cache", "via"
            ]:
                val = r.headers.get(key)
                if val:
                    found[key] = val
    except Exception as e:
        log.debug(f"Header fetch {domain}: {e}")
    return found

async def apollo_lookup(session: aiohttp.ClientSession, domain: str) -> dict:
    """Apollo.io Organization API — firmografi og tech stack."""
    if not APOLLO_API_KEY:
        return {}
    try:
        async with session.post(
            "https://api.apollo.io/v1/organizations/enrich",
            json={"domain": domain},
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "X-Api-Key": APOLLO_API_KEY
            },
            timeout=aiohttp.ClientTimeout(total=15)
        ) as r:
            if r.status == 200:
                data = await r.json()
                org = data.get("organization", {})
                return {
                    "name": org.get("name"),
                    "industry": org.get("industry"),
                    "employee_count": org.get("estimated_num_employees"),
                    "funding_stage": org.get("latest_funding_stage"),
                    "technologies": org.get("technology_names", []),
                    "founded_year": org.get("founded_year")
                }
    except Exception as e:
        log.debug(f"Apollo {domain}: {e}")
    return {}

async def grayhat_s3_lookup(session: aiohttp.ClientSession, domain: str) -> list:
    """
    Grayhat Warfare API — ferdigindekserte åpne S3-buckets.
    LEGAL: Kontrollerer kun eksistens. Lister/laster aldri ned innhold.
    """
    if not GRAYHAT_API_KEY:
        return []
    company = domain.replace(".", "").replace("-", "")[:20]
    try:
        async with session.get(
            "https://buckets.grayhatwarfare.com/api/v2/buckets",
            params={"keywords": company, "limit": 5},
            headers={"Authorization": f"Bearer {GRAYHAT_API_KEY}"},
            timeout=aiohttp.ClientTimeout(total=15)
        ) as r:
            if r.status == 200:
                data = await r.json()
                return [b.get("bucket", "") for b in data.get("buckets", [])]
    except Exception as e:
        log.debug(f"Grayhat {domain}: {e}")
    return []

async def firecrawl_extract(session: aiohttp.ClientSession, domain: str) -> dict:
    """Firecrawl JSON extraction — 5 credits/side. Hobby $16/mnd = 600 sider."""
    if not FIRECRAWL_API_KEY:
        return {}
    try:
        async with session.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={
                "url": f"https://{domain}",
                "formats": ["extract"],
                "extract": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "tech_stack": {"type": "array", "items": {"type": "string"}},
                            "recent_news": {"type": "string"},
                            "api_endpoints": {"type": "array", "items": {"type": "string"}},
                            "job_postings_hint": {"type": "string"}
                        }
                    }
                }
            },
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as r:
            if r.status == 200:
                d = await r.json()
                return d.get("data", {}).get("extract", {})
    except Exception as e:
        log.debug(f"Firecrawl {domain}: {e}")
    return {}

# ─── KOMPONENT 2: TWO-LAYER TRUTH-CHECKER ─────────────────────────────────────
HYPOTHESIS_SYSTEM = (
    "Du er en teknisk analytiker. Analyser rådata og identifiser EN spesifikk "
    "teknisk sarbarhet eller teknisk gjeld. "
    "Returner KUN gyldig JSON: "
    "{\"hypothesis\": string, \"evidence_url\": string, "
    "\"confidence_score\": float 0.0-1.0, "
    "\"hook_type\": \"tech_debt\"|\"security\"|\"api_deprecation\"|\"s3_exposure\"}. "
    "Krav: confidence >= 0.7. Ellers sett confidence_score=0.0 og hypothesis=\"\"."
)

CHECKER_SYSTEM = (
    "Du er en kynisk faktasjekker og B2B-copywriter. "
    "REGLER: "
    "1. FAILED hvis noen del av hypotesen IKKE er eksplisitt bevist av kildedataene. "
    "2. Ingen antagelser. Ingen hallusinasjon. "
    "3. Hvis PASSED: skriv e-post under 75 ord med timeline-hook (f.eks. '14 dager vs 6 maneder'). "
    "4. CTA: lav friksjon (f.eks. 'Verdt en 15-minutters prat?'). "
    "5. Emne: under 7 ord. "
    "Returner KUN JSON: "
    "{\"status\": \"PASSED\"|\"FAILED\", \"hook_type\": string, "
    "\"evidence_url\": string, \"compressed_timeline\": string, "
    "\"draft_subject\": string, \"draft_body\": string}"
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=15),
    retry=retry_if_exception_type(Exception)
)
async def generate_hypothesis(raw: dict, domain: str, sem: asyncio.Semaphore) -> dict:
    async with sem:
        resp = await client.chat.completions.create(
            model=MODEL_HYPOTHESIS,
            messages=[
                {"role": "system", "content": HYPOTHESIS_SYSTEM},
                {"role": "user", "content": f"Domene: {domain}\nRadata: {json.dumps(raw)[:3000]}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=300
        )
    try:
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {"hypothesis": "", "evidence_url": "", "confidence_score": 0.0, "hook_type": ""}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=15),
    retry=retry_if_exception_type(Exception)
)
async def truth_check_and_draft(lead: Lead, raw: dict, sem: asyncio.Semaphore) -> dict:
    user = (
        f"Hypotese: {lead.hypothesis}\n"
        f"Hook: {lead.hook_type}\n"
        f"Bevis-URL: {lead.evidence_url}\n"
        f"S3-buckets: {lead.s3_buckets_found}\n"
        f"Apollo: {lead.apollo_data}\n"
        f"Radata: {json.dumps(raw)[:4000]}"
    )
    async with sem:
        resp = await client.chat.completions.create(
            model=MODEL_CHECKER,
            messages=[
                {"role": "system", "content": CHECKER_SYSTEM},
                {"role": "user", "content": user}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
    try:
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {
            "status": "FAILED", "hook_type": "", "evidence_url": "",
            "compressed_timeline": "", "draft_subject": "", "draft_body": ""
        }

async def process_lead(domain, email, name, company, session, sem_t, sem_c) -> Lead:
    lead = Lead(domain=domain, contact_email=email, contact_name=name, company_name=company)

    headers_data, fc_data, apollo_data, s3_data = await asyncio.gather(
        fetch_http_headers(session, domain),
        firecrawl_extract(session, domain),
        apollo_lookup(session, domain),
        grayhat_s3_lookup(session, domain)
    )
    raw = {**headers_data, **fc_data}
    lead.tech_stack_raw   = json.dumps(raw)
    lead.apollo_data      = json.dumps(apollo_data)
    lead.s3_buckets_found = json.dumps(s3_data) if s3_data else ""

    if apollo_data.get("technologies"):
        raw["apollo_tech"] = apollo_data["technologies"]
    if s3_data:
        raw["s3_buckets"] = s3_data

    hyp = await generate_hypothesis(raw, domain, sem_t)
    lead.hypothesis       = hyp.get("hypothesis", "")
    lead.evidence_url     = hyp.get("evidence_url", "")
    lead.confidence_score = hyp.get("confidence_score", 0.0)
    lead.hook_type        = hyp.get("hook_type", "")

    if lead.confidence_score < 0.7 or not lead.hypothesis:
        lead.truth_status = "FAILED"
        log.info(f"FORKASTET (confidence {lead.confidence_score:.2f}): {domain}")
        save_lead(lead)
        return lead

    result = await truth_check_and_draft(lead, raw, sem_c)
    lead.truth_status        = result.get("status", "FAILED")
    lead.hook_type           = result.get("hook_type", lead.hook_type)
    lead.evidence_url        = result.get("evidence_url", lead.evidence_url)
    lead.compressed_timeline = result.get("compressed_timeline", "")
    lead.draft_subject       = result.get("draft_subject", "")
    lead.draft_body          = result.get("draft_body", "")

    if lead.truth_status == "PASSED":
        lead.send_status = "QUEUE"
        log.info(f"GODKJENT: {domain} | {lead.hook_type} | {lead.compressed_timeline}")
    else:
        log.info(f"FORKASTET (truth-check): {domain}")

    save_lead(lead)
    return lead

async def hunt_mode(input_csv: str, max_leads: int):
    import csv
    rows = []
    with open(input_csv, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if i >= max_leads:
                break
            rows.append(row)

    sem_t = asyncio.Semaphore(SEMAPHORE_TRIAGE)
    sem_c = asyncio.Semaphore(SEMAPHORE_CHECKER)
    conn  = aiohttp.TCPConnector(limit=40, ssl=False)

    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [
            process_lead(
                r.get("domain", "").strip(), r.get("email", "").strip(),
                r.get("name", "").strip(), r.get("company", "").strip(),
                session, sem_t, sem_c
            ) for r in rows if r.get("domain")
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    passed = [r for r in results if isinstance(r, Lead) and r.truth_status == "PASSED"]
    log.info(
        f"\n=== HUNT FERDIG === Godkjent: {len(passed)}/{len(results)} "
        f"({len(passed)/max(len(results),1)*100:.1f}%)"
    )
    for l in passed:
        print(f"\n{'='*60}")
        print(f"Domene:  {l.domain}  ({l.company_name})")
        print(f"Hook:    {l.hook_type} | {l.compressed_timeline}")
        print(f"Emne:    {l.draft_subject}")
        print(f"\n{l.draft_body}")
        print(f"\nBevis: {l.evidence_url}")

# ─── KOMPONENT 3: 3-7-7 KADENS ────────────────────────────────────────────────
FOLLOWUP_TEMPLATES = {
    3: (
        "Oppfolging — {company_name}",
        "Hei {first_name},\n\n"
        "Fant forresten at {hypothesis_short}.\n\n"
        "Nytt datapunkt — kan spare dere {compressed_timeline}.\n\n"
        "Fortsatt verdt en prat?\n\n{sender_name}"
    ),
    10: (
        "ROI-perspektiv — {company_name}",
        "Hei {first_name},\n\n"
        "Vinkler det annerledes: bedrifter i {industry} med lignende stack "
        "ser typisk raskere deployments etter denne type utbedring.\n\n"
        "Hva blokkerer dere mest akkurat na?\n\n{sender_name}"
    ),
    17: (
        "Avslutter — {company_name}",
        "Hei {first_name},\n\n"
        "Sitter pa analysen om {hook_type} hos dere hvis det noen gang blir relevant.\n\n"
        "Ingen rush — bare si fra.\n\n{sender_name}"
    )
}

def get_followup_draft(lead: Lead, day: int, sender_name: str = "Christer") -> tuple:
    template = FOLLOWUP_TEMPLATES.get(day)
    if not template:
        return "", ""
    subject_tpl, body_tpl = template
    industry = "din bransje"
    try:
        apollo = json.loads(lead.apollo_data or "{}")
        industry = apollo.get("industry") or "din bransje"
    except Exception:
        pass

    first_name = lead.contact_name.split()[0] if lead.contact_name else "Hei"
    subject = subject_tpl.format(company_name=lead.company_name)
    body = body_tpl.format(
        first_name=first_name,
        company_name=lead.company_name,
        compressed_timeline=lead.compressed_timeline or "tid",
        hypothesis_short=lead.hypothesis[:80] if lead.hypothesis else "det tekniske funnet",
        hook_type=lead.hook_type or "teknisk gjeld",
        industry=industry,
        sender_name=sender_name
    )
    return subject, body

# ─── REVIEW ───────────────────────────────────────────────────────────────────
def review_mode():
    leads = [l for l in load_leads("QUEUE") if l.truth_status == "PASSED" and not l.opted_out]
    if not leads:
        print("Ingen leads i ko.")
        return
    print(f"\n{len(leads)} leads klare for review. (~{len(leads)*2} min)")

    for lead in leads:
        print(f"\n{'='*60}")
        print(f"Domene:  {lead.domain}  ({lead.company_name})")
        print(f"Kontakt: {lead.contact_name} <{lead.contact_email}>")
        print(f"Hook:    {lead.hook_type} | {lead.compressed_timeline}")
        print(f"Conf:    {lead.confidence_score:.2f}")
        print(f"\nEmne:    {lead.draft_subject}")
        print(f"\n{lead.draft_body}")
        print(f"\nBevis:   {lead.evidence_url}")
        if lead.s3_buckets_found and lead.s3_buckets_found not in ("[]", ""):
            print(f"S3:      {lead.s3_buckets_found}")

        c = input("\n[g]odkjenn / [a]vvis / [e]diter / [s]kip: ").strip().lower()
        if c == "g":
            lead.send_status = "APPROVED"
            save_lead(lead)
            print("Godkjent")
        elif c == "a":
            lead.send_status = "REJECTED"
            save_lead(lead)
            print("Avvist")
        elif c == "e":
            new_s = input("Nytt emne (enter=behold): ").strip()
            if new_s:
                lead.draft_subject = new_s
            new_b = input("Ny krop (enter=behold): ").strip()
            if new_b:
                lead.draft_body = new_b
            lead.send_status = "APPROVED"
            save_lead(lead)
            print("Redigert og godkjent")
        else:
            print("Hoppet over")

# ─── SEND ─────────────────────────────────────────────────────────────────────
async def send_email(session: aiohttp.ClientSession,
                     to_email: str, to_name: str,
                     subject: str, body: str) -> bool:
    if not SENDGRID_API_KEY:
        log.info(f"[DRY RUN] -> {to_email} | {subject}")
        return True
    unsub_domain = FROM_EMAIL.split("@")[-1]
    try:
        async with session.post(
            "https://api.sendgrid.com/v3/mail/send",
            json={
                "personalizations": [{"to": [{"email": to_email, "name": to_name}]}],
                "from": {"email": FROM_EMAIL},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
                "headers": {
                    "List-Unsubscribe": f"<mailto:unsubscribe@{unsub_domain}?subject=unsubscribe>",
                    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"
                }
            },
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=15)
        ) as r:
            return r.status == 202
    except Exception as e:
        log.error(f"SendGrid: {e}")
        return False

async def send_mode():
    leads = [l for l in load_leads("APPROVED") if not l.opted_out]
    if not leads:
        print("Ingen godkjente leads.")
        return
    cohort = leads[:MAX_COHORT_SIZE]
    log.info(f"Sender {len(cohort)} e-poster...")
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_email(session, l.contact_email, l.contact_name, l.draft_subject, l.draft_body)
            for l in cohort if l.contact_email
        ]
        results = await asyncio.gather(*tasks)
    sent = sum(1 for r in results if r)
    log.info(f"Sendt: {sent}/{len(cohort)}")
    for lead, ok in zip(cohort, results):
        if ok:
            lead.send_status = "SENT"
            save_lead(lead)

# ─── WEBHOOK APP ──────────────────────────────────────────────────────────────
webhook_app = FastAPI(title="ECHOBOT v3.0")

async def classify_sentiment(text: str) -> str:
    if not client:
        return "Ukjent"
    resp = await client.chat.completions.create(
        model=MODEL_TRIAGE,
        messages=[
            {"role": "system", "content": (
                "Du er et internt klassifiseringsverkty for kalde e-post-svar. "
                "Returner KUN en av tre strenger: "
                "'Interessert', 'Ikke Interessert', eller 'Fravarsmeling'."
            )},
            {"role": "user", "content": text[:1000]}
        ],
        max_tokens=10
    )
    return resp.choices[0].message.content.strip()

def create_stripe_invoice(email: str, name: str, company: str, service_desc: str) -> str:
    """
    Stripe onboarding. Flyt: customer.created -> invoice.finalized -> invoice.paid
    Returnerer hosted_invoice_url.
    """
    customer = stripe.Customer.create(
        email=email, name=name,
        metadata={"company": company, "source": "echobot_v3"}
    )
    invoice = stripe.Invoice.create(
        customer=customer.id,
        collection_method="send_invoice",
        days_until_due=7,
        auto_advance=False
    )
    stripe.InvoiceItem.create(
        customer=customer.id,
        invoice=invoice.id,
        description=service_desc,
        unit_amount=INVOICE_AMOUNT_USD * 100,
        currency="usd",
        quantity=1
    )
    finalized = stripe.Invoice.finalize_invoice(invoice.id)
    return finalized.hosted_invoice_url or ""

@webhook_app.post("/webhook/reply")
async def handle_reply(request: Request):
    """Svar-klassifisering + Stripe auto-onboarding."""
    body = await request.json()
    domain     = body.get("domain", "")
    reply_text = body.get("reply_text", "")
    from_email = body.get("from_email", "")

    if not reply_text:
        return {"status": "ignored"}

    opt_out_words = ["unsubscribe", "fjern meg", "stopp", "avmeld", "remove me"]
    if any(w in reply_text.lower() for w in opt_out_words):
        leads = [l for l in load_leads() if l.domain == domain]
        for lead in leads:
            lead.opted_out = True
            lead.reply_sentiment = "Opted-out"
            save_lead(lead)
        log.info(f"OPT-OUT: {domain}")
        return {"status": "opted_out"}

    sentiment = await classify_sentiment(reply_text)
    log.info(f"Svar fra {domain}: {sentiment}")

    leads = [l for l in load_leads() if l.domain == domain]
    if leads:
        lead = leads[0]
        lead.reply_sentiment = sentiment
        if sentiment == "Interessert" and STRIPE_SECRET_KEY:
            try:
                url = create_stripe_invoice(
                    email=from_email or lead.contact_email,
                    name=lead.contact_name,
                    company=lead.company_name,
                    service_desc=f"Teknisk utbedring - {lead.company_name} ({lead.compressed_timeline})"
                )
                lead.stripe_invoice_url = url
                log.info(f"STRIPE FAKTURA: {domain} -> {url}")
            except Exception as e:
                log.error(f"Stripe: {e}")
        save_lead(lead)

    return {"status": "ok", "sentiment": sentiment}

@webhook_app.post("/webhook/stripe")
async def handle_stripe(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Idempotent Stripe webhook.
    Lytter pa invoice.paid -> trigger n8n onboarding.
    Bruker invoice.paid (ikke payment_succeeded) for full dekning.
    """
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event_processed(event["id"]):
        return {"status": "already_processed"}

    if event["type"] == "invoice.paid":
        obj = event["data"]["object"]
        log.info(f"BETALT: {obj.get('customer_email')} - ${obj.get('amount_paid', 0)/100:.2f}")
        if N8N_ONBOARDING_URL:
            async with aiohttp.ClientSession() as s:
                await s.post(N8N_ONBOARDING_URL, json={
                    "customer_email": obj.get("customer_email"),
                    "customer_name":  obj.get("customer_name"),
                    "amount_paid":    obj.get("amount_paid", 0) / 100,
                    "invoice_id":     obj.get("id"),
                    "trigger":        "invoice.paid",
                    "ts":             datetime.utcnow().isoformat()
                })

    mark_event_processed(event["id"])
    return {"status": "ok"}

@webhook_app.post("/webhook/unsubscribe")
async def handle_unsubscribe(request: Request):
    """RFC 8058 ett-klikks avmelding."""
    body = await request.json()
    email = body.get("email", "")
    leads = [l for l in load_leads() if l.contact_email == email]
    for lead in leads:
        lead.opted_out = True
        save_lead(lead)
    log.info(f"RFC 8058 opt-out: {email}")
    return {"status": "unsubscribed"}

@webhook_app.get("/health")
async def health():
    total = len(load_leads())
    return {
        "status": "ok", "version": "3.0",
        "ts": datetime.utcnow().isoformat(),
        "leads_total": total,
        "leads_sent": len(load_leads("SENT")),
        "leads_queue": len(load_leads("QUEUE"))
    }

# ─── STATS ────────────────────────────────────────────────────────────────────
def stats_mode():
    all_leads = load_leads()
    if not all_leads:
        print("Database tom. Kjor --mode hunt forst.")
        return
    by_status = {}
    for l in all_leads:
        by_status[l.send_status] = by_status.get(l.send_status, 0) + 1
    by_truth = {}
    for l in all_leads:
        by_truth[l.truth_status] = by_truth.get(l.truth_status, 0) + 1
    by_sentiment = {}
    for l in all_leads:
        if l.reply_sentiment:
            by_sentiment[l.reply_sentiment] = by_sentiment.get(l.reply_sentiment, 0) + 1
    sent = by_status.get("SENT", 0)
    interested = by_sentiment.get("Interessert", 0)
    opted_out = sum(1 for l in all_leads if l.opted_out)
    print(f"\n{'='*50}")
    print(f"ECHOBOT v3.0 - STATISTIKK")
    print(f"{'='*50}")
    print(f"Totalt leads:   {len(all_leads)}")
    print(f"Truth-check:    {by_truth}")
    print(f"Send-status:    {by_status}")
    print(f"Svar-sentiment: {by_sentiment}")
    if sent > 0:
        print(f"Reply-rate:     {sum(by_sentiment.values())/sent*100:.1f}%")
        print(f"Positiv-rate:   {interested/sent*100:.1f}%")
    print(f"Opt-outs:       {opted_out} ({opted_out/max(sent,1)*100:.2f}%)")
    print(f"{'='*50}")

# ─── EKSEMPEL CSV ─────────────────────────────────────────────────────────────
EXAMPLE_CSV = "domain,email,name,company\nexample-startup.io,cto@example-startup.io,Jane Smith,Example Startup\n"

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    init_db()
    parser = argparse.ArgumentParser(description="ECHOBOT v3.0")
    parser.add_argument("--mode", choices=["hunt", "review", "send", "server", "stats"], required=True)
    parser.add_argument("--leads", type=int, default=50)
    parser.add_argument("--input", type=str, default="leads.csv")
    args = parser.parse_args()

    if args.mode == "hunt":
        if not os.path.exists(args.input):
            with open(args.input, "w") as f:
                f.write(EXAMPLE_CSV)
            print(f"Opprettet eksempel {args.input}. Rediger og kjor igjen.")
            return
        asyncio.run(hunt_mode(args.input, args.leads))
    elif args.mode == "review":
        review_mode()
    elif args.mode == "send":
        asyncio.run(send_mode())
    elif args.mode == "server":
        uvicorn.run(webhook_app, host="0.0.0.0", port=8000, log_level="info")
    elif args.mode == "stats":
        stats_mode()

if __name__ == "__main__":
    main()
