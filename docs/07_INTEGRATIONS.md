# 07 — Integrasjoner

## Statusoversikt

### Bygget
#### GitHub Actions CI
**VERIFISERT**
- workflow finnes
- brukes for kvalitetssikring rundt Mission-Control / selftest-lag

#### LaunchAgent
**VERIFISERT**
- macOS scheduler/installasjon er del av systemet

#### Shell integration + completions
**VERIFISERT**
- `mc`-flyten er gjort brukbar i shell

### Delvis bygget
#### Live dispatch mot cowork-endpoint
**BLOKKERT**
- lokal side grønn
- remote endpoint + token mangler

---

## Planlagte integrasjoner

### 1. GitHub PR-lane
**PLANLAGT**
Formål:
- knytte PR-flyt til roadmap og review

Brukerinstruksjon:
1. definér workflow for PR events
2. map PR → mission/step eller review-state
3. kjør test gates
4. oppdater status tilbake til roadmap

Krav:
- stabil GitHub Actions base
- klar mapping mellom branch/PR og mission

### 2. Stripe/Vipps Revenue Bridge
**PLANLAGT**
Formål:
- mate ekte revenue-signaler inn i forecast/ORION

Brukerinstruksjon:
1. velg kilde: Stripe, Vipps eller begge
2. definer webhook eller polling-jobb
3. normaliser revenue event-format
4. koble til missions/steps eller aggregert forecast

Krav:
- PR-lane og Remote Health bør være på plass først
- secrets håndteres utenfor repo

### 3. Sentry Incident → Blockers
**PLANLAGT**
Formål:
- gjøre incidenter til blockers eller steps

Brukerinstruksjon:
1. ta inn Sentry webhook
2. map severity → priority/blocker
3. opprett eller oppdater mission/step
4. eksponer i Risk Summary-panel

Krav:
- roadmap blocker-flyt må være definert der dette skal lande

### 4. Linear/Jira Sync
**PLANLAGT**
Formål:
- synk mellom ekstern prosjektstyring og roadmap

Brukerinstruksjon:
1. definer én source of truth per felt
2. map status-felter
3. unngå loop-skriving
4. logg konflikt ved mismatch

Krav:
- agent ownership må være på plass først

### 5. n8n Event-bus
**PLANLAGT**
Formål:
- eventdrevet automasjon mellom systemer

Brukerinstruksjon:
1. eksponer sikre webhooks
2. send normaliserte events
3. logg alle incoming/outgoing events
4. route til Dispatch eller roadmap-lag

Krav:
- tydelig event schema
- auth/OPSEC policy

### 6. Tailscale / Remote Health Bridge
**PLANLAGT**
Formål:
- fjernhelse og distribuert observasjon

Brukerinstruksjon:
1. eksponer health-endepunkter internt
2. bruk Tailscale for sikker reachability
3. aggreger health til panel_output eller mc status
4. vis remote health i dashboard / watch

Krav:
- bør komme tidlig i P6
- egnet før revenue bridge

---

## Prioritert rekkefølge
1. GitHub PR-lane
2. Tailscale / Remote Health
3. Sentry → Blockers
4. Stripe/Vipps Revenue Bridge
5. Linear/Jira Sync
6. n8n Event-bus
