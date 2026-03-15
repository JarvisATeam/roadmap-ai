# FlowArk Solo — Produktspec (fail-closed)

> **Type:** Personlig app | **Bruker:** Kun deg selv | **Versjon:** MVP v1
> **Prinsipp:** Gjør én ting ekstremt bra. Ingen padding.

---

## Hva det er

En personlig **state-to-action motor**.
Ikke en produktivitetsapp. Ikke en habit tracker. Ikke en journal.

Den gjør bare dette:
1. Registrerer din biologiske/operative state
2. Anbefaler riktig arbeidsmodus
3. Viser kun nærmeste neste steg
4. Logger frustrasjoner og energilekkasjer
5. Stopper sidequests og åpne looper

---

## ICP (Ideal Customer Profile)

**Bruker:** Deg selv
- Høy-åpenhet bygger
- Høy drive, lav frykt
- Sterk på mønstergjenkjenning og visjon
- Svak på lineaer sekvensering og fokuskontroll
- Tapes av: friksjon, treghet, meningsløse oppgaver, åpne looper

---

## Kjernefunksjoner MVP

### 1. State Input (morgen)
```
Søvnkvalitet:    [ ] Dårlig  [ ] OK  [ ] God
Energi:          [ ] Lav     [ ] Middels  [ ] Høy
Stress/HRV:      [ ] Høy    [ ] Middels  [ ] Lav
Sult/Stabilitet: [ ] Ustabil [ ] Nesten ok [ ] Stabil
Fokus:           [ ] Spredt  [ ] Middels   [ ] Skarp
```

### 2. Modusvalg (auto-anbefalt basert på state)
| State | Anbefalt modus |
|-------|----------------|
| Søvn god + energi høy + fokus skarp | **Deep Build** |
| Søvn ok + energi middels | **Light Ops** |
| Sult / ustabil energi | **Admin** |
| Søvn dårlig / stresset | **Recover** |

### 3. Next Action-kort
- Viser KUN én oppgave om gangen
- Hentet fra "Active"-laget
- Ingen backlog i synsfeltet
- Klar-knapp → logger og laster neste

### 4. Frustrasjonslogg
Når du trykker "Frustrert":  
Velg årsak:
- [ ] Treghet / venting
- [ ] Uklarhet (vet ikke hva neste steg er)
- [ ] Meningsløs oppgave
- [ ] Folk / sosial friksjon
- [ ] Biologisk (sulten, trett, uro)
- [ ] Sidequest / distraksjons-pull

### 5. Kveld Shutdown
```
Hva ble faktisk gjort:  [fritekst]
Neste steg i morgen:    [fritekst]
Hva parkeres:           [fritekst]
State ved avslutning:   høy / ok / lav
```

---

## Skjermflyt

```
[Morgen Check-in]
    ↓
[State vurdert] → [Modus anbefalt]
    ↓
[Next Action Kort]
    ↓
[Klar / Frustrert / Parker]
    ↓
[Ny handling eller Shutdown]
    ↓
[Kveld Shutdown]
```

---

## Datamodell (kort)

```typescript
type DailyState = {
  date: string
  sleep: 'bad' | 'ok' | 'good'
  energy: 'low' | 'mid' | 'high'
  stress: 'high' | 'mid' | 'low'
  hunger: 'unstable' | 'ok' | 'stable'
  focus: 'scattered' | 'mid' | 'sharp'
  recommendedMode: 'deep_build' | 'light_ops' | 'admin' | 'recover'
}

type Action = {
  id: string
  title: string
  project: string
  status: 'active' | 'done' | 'parked'
  createdAt: string
  completedAt?: string
}

type FrustrationEntry = {
  id: string
  timestamp: string
  cause: 'friction' | 'unclear' | 'meaningless' | 'social' | 'biological' | 'sidequest'
  note?: string
}

type ShutdownEntry = {
  date: string
  accomplished: string
  nextStep: string
  parked: string
  endState: 'high' | 'ok' | 'low'
}
```

---

## Hva som IKKE er i v1

- Gamification / streaks
- Sosial feed eller deling
- Komplekse dashboards
- AI-analyse av data
- Integrering med kalender / Notion / Slack
- Push-varsler
- Biometrisk auto-import (manuell input først)
- Abonnement / betaling
- Flerbruker

---

## 30-dagers byggeplan

Se `BUILD_PLAN.md` i samme mappe.

---

## Suksesskriterier

- Brukt daglig i 20+ av 30 dager
- Frustrasjonslogg har 15+ entries (data om tapspunkter)
- State → modus-kobling føles riktig 80%+ av gangene
- En "kjedelig mellomdag" håndtert bedre enn uten appen
