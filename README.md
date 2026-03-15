# roadmap-ai

> **State-to-action engine + AI-powered roadmap builder**
> Versjon: v0.1.0-spec | Status: building

---

## Hva dette er

To produkter. Én visjon. Bygget for en spesifikk profil:

| App | Formål | Bruker |
|-----|--------|--------|
| **FlowArk Solo** | Personlig state-to-action motor | Deg selv |
| **Roadmap Operator** | B2B kaos-til-roadmap konverter | Solo founders, kleine team |

---

## Filtré

```
roadmap-ai/
├── README.md                    ← denne filen
├── ROADMAP.md                   ← 90-dagers masterplan
├── PROFILE.md                   ← operativ personlighetsprofil
│
├── docs/
│   ├── flow_formula.md          ← flow-tilstand definert
│   ├── frustration_formula.md   ← tapspunkter kartlagt
│   └── biometric_model.md       ← hvilke målinger som styrer handling
│
├── apps/
│   ├── flowark-solo/
│   │   ├── SPEC.md              ← produktbrief (fail-closed)
│   │   ├── SCREENS.md           ← skjermbilder + flows
│   │   ├── DATA_MODEL.md        ← datamodell
│   │   ├── BUILD_PLAN.md        ← 30-dagers byggeplan
│   │   └── NOT_IN_V1.md         ← eksplisitt eksklusjonslist
│   │
│   └── roadmap-operator/
│       ├── SPEC.md              ← produktbrief + ICP
│       ├── SCREENS.md           ← skjermbilder + flows
│       ├── DATA_MODEL.md        ← datamodell
│       ├── BUILD_PLAN.md        ← 30-dagers byggeplan
│       ├── ICP.md               ← ideal customer profile
│       └── NOT_IN_V1.md         ← eksplisitt eksklusjonslist
│
├── system/
│   ├── daily_loop.md            ← morgen/midt/kveld rutine
│   ├── work_layers.md           ← capture / active / parkering
│   ├── decision_rules.md        ← biologisk beslutningsprotokoll
│   └── project_template.md      ← 5-felts prosjektmal
│
└── tasks/
    ├── phase1_stabilize.md      ← fase 1: stabiliser operativ state
    ├── phase2_flowark.md        ← fase 2: bygg FlowArk Solo MVP
    └── phase3_productize.md     ← fase 3: produktiser til Roadmap Operator
```

---

## Kjerneprinsipper

### 1. Én aktiv build path per prosjekt
Ingen prosjekter får ha 12 ideer og 7 underspor åpne samtidig.

### 2. State bestemmer modus
```
søvn god + energi høy  → Deep Build
søvn ok + energi middels → Light Ops
søvn dårlig / irritert   → Admin / Recover
```

### 3. Flow-formelen
```
Flow = høy mening + tydelig neste steg + biologisk stabilitet + lav friksjon
```

### 4. Frustrasjon-formelen
```
Frustrasjon = lav mening + åpen loop + sult/ustabil energi + treghet rundt deg
```

---

## Kjappe lenker

- [90-dagers plan](./ROADMAP.md)
- [Din operative profil](./PROFILE.md)
- [FlowArk Solo — produktspec](./apps/flowark-solo/SPEC.md)
- [Roadmap Operator — produktspec](./apps/roadmap-operator/SPEC.md)
- [Daglig loop](./system/daily_loop.md)
- [Fase 1 tasks](./tasks/phase1_stabilize.md)

---

## Hard beslutning

| Valg | Beslutning |
|------|------------|
| Biometrikk | Oura / enkel wearable, IKKE full stack |
| Personlig app | FlowArk Solo |
| Kommersiell app | Roadmap Operator |
| Primærfokus | state → next action → proof of progress |
| Unngå | Tre parallelle appspor |
