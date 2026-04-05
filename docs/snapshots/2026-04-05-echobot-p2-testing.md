# Snapshot: ECHOBOT P2 - Testing & Hardening

**Dato:** 2026-04-05  
**Milepæl:** Testing & Hardening P2

---

## Hva som ble gjort

- Satt opp Jest test-infrastruktur
  - `jest.config.js` med Next.js integration
  - `jest.setup.js` med jsdom environment

- Unit-tester for `mapper.ts` (11 tester)
  - `leadToMissionPayload` konvertering
  - `createSyncPreview`
  - Badge mapping (sentiment, truth, send status)

- Unit-tester for `policy.ts` (20 tester)
  - `DEFAULT_POLICY` validering
  - `canApprove` med alle edge cases
  - `canSync` fail-closed tester
  - `shouldShowInReviewQueue` logikk
  - `getRiskLevel` kalkulasjoner

- API route tester (struktur, error handling)
  - `/api/echobot/stats`
  - `/api/echobot/review`
  - `/api/echobot/sync`
  - `/api/echobot/webhook/{reply,stripe,unsubscribe}`

---

## Test Resultater

```
Test Suites: 2 passed, 2 total
Tests:       51 passed, 51 total
```

---

## Git Proof Pack

repo-root: /Users/christerolsen/roadmap-ai
branch: main
head: b6ceabe
upstream: origin/main
ahead/behind: 0/0

---

## Verifiserte Fail-Closed Prinsipper

| Regel | Test | Status |
|-------|------|--------|
| canSync krever positivt signal | ✅ Blokkerer neutral/negative | PASS |
| canSync blokkerer opted out | ✅ Selv med positiv sentiment | PASS |
| canSync blokkerer FAILED truth | ✅ Selv med positiv sentiment | PASS |
| canApprove blokkerer SENT | ✅ Ikke godkjenn sendt | PASS |
| canApprove blokkerer opted out | ✅ Ikke godkjenn opt-out | PASS |
| canApprove blokkerer FAILED | ✅ Ikke godkjenn failed | PASS |

---

## Nye filer

- `apps/roadmap-operator/__tests__/lib/mapper.test.ts`
- `apps/roadmap-operator/__tests__/lib/policy.test.ts`
- `apps/roadmap-operator/__tests__/app/api/echobot/stats.test.ts`
- `apps/roadmap-operator/__tests__/app/api/echobot/review.test.ts`
- `apps/roadmap-operator/__tests__/app/api/echobot/sync.test.ts`
- `apps/roadmap-operator/__tests__/app/api/echobot/webhook/reply.test.ts`
- `apps/roadmap-operator/__tests__/app/api/echobot/webhook/stripe.test.ts`
- `apps/roadmap-operator/__tests__/app/api/echobot/webhook/unsubscribe.test.ts`
- `apps/roadmap-operator/jest.config.js`
- `apps/roadmap-operator/jest.setup.js`

---

## Neste blokk (P3)

Faktisk mission sync:
- Koble til Roadmap missions service
- Implementere POST /missions
- Verifisere fail-closed regler i praksis

---

## Blokkere/risiko

- Ingen kjente blokkere
- API-tester trenger mer oppsett (Request/Response polyfill)
- Mission sync krever database/integrasjon med eksisterende Roadmap service
