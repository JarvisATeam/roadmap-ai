# COST_BASELINE

Sist oppdatert: 2026-04-08T20:04:18.562520

## Formål
Etablere én operativ kost-baseline for GinieSystem slik at videre valg styres av:
- lav friksjon
- høy ROI
- første krone raskest mulig

## Verifiserte engangskostnader
- Jetson Orin Nano Super Developer Kit
  - status: kjøpt
  - ca pris: 3 601 NOK inkl. mva
  - rolle: edge-compute-node for lokal LLM / RAG / agent-routing

- TP-Link SG108S 8-port gigabit switch
  - status: kjøpt
  - pris: UKJENT
  - rolle: kablet nodenett

- Logik CAT6 Ethernet-kabel 5m
  - status: kjøpt
  - pris: UKJENT
  - rolle: stabil intern nettverkstilkobling

## Verifiserte program-/tjenestespor fra repo/env metadata
- Stripe-relaterte variabler observert
- Railway-relaterte variabler observert
- Resend-relaterte variabler observert
- SendGrid-relaterte variabler observert
- OpenAI-relaterte variabler observert
- Gemini-relaterte variabler observert
- Perplexity-relaterte variabler observert
- Telegram bot-relaterte variabler observert
- Tailscale-relaterte variabler observert
- Leviathan gate / API key-relaterte variabler observert

## Faste kostkategorier
### 1. Hosting / compute
- Railway
- eventuelle VPS-er
- eventuell Replit / andre build-miljø
- lokal strøm til Jetson / Mac-noder

### 2. AI / API
- OpenAI
- Gemini
- Perplexity
- eventuelle andre modell-APIer

### 3. E-post / kommunikasjon
- Resend
- SendGrid
- Telegram bot-drift

### 4. Betaling / kommersiell stack
- Stripe
- eventuelle andre betalingsleverandører

### 5. Nettverk / drift
- Tailscale
- domener / DNS
- backup / lagring

## Foreløpig operativ vurdering
- største risiko nå er ikke rå kostnad, men uklarhet
- største gevinst nå er å synliggjøre hvilke kostnader som faktisk er aktive
- målet er å kutte alt som ikke støtter:
  1. truth layer
  2. runtime
  3. første krone

## Uavklarte felt som må fylles
- faktisk månedskost for OpenAI
- faktisk månedskost for Gemini
- faktisk månedskost for Railway
- faktisk månedskost for domener / DNS
- faktisk månedskost for Tailscale hvis betalt plan brukes
- faktisk månedskost for e-postleverandører
- faktisk strøm-/driftskost for Jetson og øvrige noder
- faktisk kost / verdi av backup-Mac-er

## Beslutningsregel
Behold kun kostnader som støtter minst én av:
- sannhetskilde / kontroll
- leveringsevne / runtime
- salgbart produkt
- direkte inntekt eller kritisk distribusjon

## Neste tiltak
1. Lag `NODE_ROLE_MAP.md`
2. Lag `OFFER_AI_OPS_SNAPSHOT_48H.md`
3. Stage kun `.truth/`
4. Deretter separat ryddeplan for secrets-sprawl og backup-env-filer
