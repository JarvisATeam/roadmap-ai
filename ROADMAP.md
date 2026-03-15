# ROADMAP.md — 90-dagers masterplan

> **Versjon:** v0.1 | **Oppdatert:** 2026-03-15
> **Prinsipp:** Færre spor. Hardere prioritering. Biologisk styrt.

---

## Oversikt

| Fase | Periode | Mål | Status |
|------|---------|------|--------|
| **Fase 1** | Dag 1–30 | Stabiliser operativ state | 🟡 Aktiv |
| **Fase 2** | Dag 31–60 | Bygg FlowArk Solo MVP | ⏳ Venter |
| **Fase 3** | Dag 61–90 | Produktiser til Roadmap Operator | ⏳ Venter |

---

## Fase 1 — Stabiliser operativ state (Dag 1–30)

### Mål
Redusere frustrasjon. Øke flyt. Minimum viable self-regulation.

### Kjerneoppgaver

#### Biologisk baseline
- [ ] Lås søvntid: seng 23:00, opp 07:00
- [ ] Måltidsrytme: frokost 08:00, lunsj 13:00, middag 19:00
- [ ] Unngå viktige beslutninger når du er sulten/søvnløs
- [ ] Velg wearable (Oura anbefales), ikke full biometrisk stack

#### Daglig loop (se `system/daily_loop.md`)
- [ ] Innfør morgenrutine (3 min)
- [ ] Innfør midt-på-dag-sjekk (1 min)
- [ ] Innfør kveldsavslutning (3 min)

#### Arbeidsstruktur
- [ ] Én innboks for alt (capture)
- [ ] Maks 3 aktive spor
- [ ] Alt annet i parkering
- [ ] Bruk 5-felts prosjektmal (se `system/project_template.md`)

#### Separasjon av moduser
- [ ] Egne tidsvinduer for Deep Build vs. Admin/Møter
- [ ] Ikke bland dypt bygg og sosiale oppgaver i samme blokk

### Output / bevis
- Daglig loop er gjennomført 20+ av 30 dager
- Maks 3 åpne spor til enhver tid
- Søvn og måltidsrytme er stabil

---

## Fase 2 — Bygg FlowArk Solo MVP (Dag 31–60)

### Mål
En personlig "state-to-action motor" som beskytter mot dine faktiske tapspunkter.

### Kjerneoppgaver

#### Uke 1 (dag 31–37)
- [ ] Sett opp prosjektstruktur (se `apps/flowark-solo/BUILD_PLAN.md`)
- [ ] Bygg state input screen
- [ ] Bygg modus-velger (Deep Build / Light Ops / Admin / Recover)
- [ ] Lokal datalagring

#### Uke 2 (dag 38–44)
- [ ] Bygg "Next Action"-kort
- [ ] Bygg frustrasjonslogg
- [ ] Koble state til anbefalte moduser

#### Uke 3 (dag 45–51)
- [ ] Bygg kveldsshutdown-flyt
- [ ] Parkering / sidequest-stopper
- [ ] Test på deg selv daglig

#### Uke 4 (dag 52–60)
- [ ] Refinement basert på daglig bruk
- [ ] Dokumenter hva som faktisk hjelper
- [ ] Beslutning: fortsette eller pivotere før fase 3

### Output / bevis
- App kjører lokalt
- Daglig bruk > 20 dager
- Frustrasjonslogg har minst 15 entries
- State → action kobling dokumentert

---

## Fase 3 — Produktiser til Roadmap Operator (Dag 61–90)

### Mål
Ta FlowArk-logikken, bredd den ut til B2B-produkt, test på 5 brukere.

### Kjerneoppgaver

#### Uke 1 (dag 61–67)
- [ ] Definer ICP (se `apps/roadmap-operator/ICP.md`)
- [ ] Bygg "lim inn kaos"-input
- [ ] AI-konvertering til roadmap-struktur
- [ ] MVP-skjerm: mål / arbeidsstrøm / blokkere / neste steg

#### Uke 2 (dag 68–74)
- [ ] Bygg 7-dagers plan-generator
- [ ] Statusmarkering (✅ / 🟡 / 🔴)
- [ ] Eksport til Markdown

#### Uke 3 (dag 75–81)
- [ ] Friksjonsvarsler (for mange spor, mangler neste steg)
- [ ] Test med 3 brukere
- [ ] Dokumenter feedback

#### Uke 4 (dag 82–90)
- [ ] Refinement basert på brukerfeedback
- [ ] Prisingstest: hva betaler de faktisk for?
- [ ] Beslutning: klar for beta-lansering?

### Output / bevis
- 5 brukere har testet
- Minst 2 har betalt / villet betalt
- Funksjonene som gir verdi er identifisert

---

## Hva som IKKE er i denne planen

- ArchModeler (for tung som første kommersielle spor)
- Full biometrisk stack (vent til state er stabil)
- Gamification, sosial feed, masse dashboards
- Tre parallelle appspor
- "Bedre disiplin" som løsning

---

## Ukentlig review-sjékkliste

```
[ ] Hva ble faktisk gjort denne uken?
[ ] Hva er de 3 viktigste oppgavene neste uke?
[ ] Hvilke spor må parkeres?
[ ] Er state (søvn, energi, måltid) stabil?
[ ] Trengs justeringer i daglig loop?
```
