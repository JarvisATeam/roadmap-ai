# BUILD WORKFLOW v2.0

System: GinieSystem
Versjon: 2.0
Dato: 2024-04-01
Plattform: MAC (pbcopy)

---

## ROLLER (HARDFRYST)

| Agent     | Ansvar                                    | Gjor IKKE               |
|-----------|-------------------------------------------|-------------------------|
| ClaudeBot | Spec, risiko, review, acceptance tests    | Skrive produksjonskode  |
| Codex     | Implementere, teste, commit, push         | Velge arkitektur        |
| Ginie     | Orkestrere, prioritere, gates, approval   | Kode eller spec         |

---

## JOBBTYPER (KUN DISSE 4)

| Type     | Bruk                          | Eksempel                    |
|----------|-------------------------------|-----------------------------|
| BUILD    | Ny funksjon                   | Nytt API-endepunkt          |
| FIX      | Avgrenset feil                | Fikse 404                   |
| HARDEN   | Guardrails, tester, logging   | Input-validering            |
| CLOSEOUT | test-add-commit-push-proof    | Etter godkjent review       |

---

## CORE PRINCIPLES

1. ROADMAP FIRST - Vis full plan for kode
2. ONE BLOCK AT A TIME - Aldri flere kodeblokker
3. AUTO-CLIPBOARD - Hver kommando til clipboard
4. WAIT FOR PROOF - Bevis for neste blokk
5. FAIL-CLOSED - Ingen antagelser
6. GIT PROOF PACK - For OG etter hver jobb
7. ASK-PAKKE - Standard mal pa 100% av jobber

---

## ASK-PAKKE (OBLIGATORISK)

For Codex far jobb skal ClaudeBot levere:

PROBLEM:       Kort problemdefinisjon
FILES:         Eksakte filer som endres
INVARIANTS:    Hva som IKKE ma brytes
ACCEPTANCE:    Testbare akseptansekriterier
EDGE_CASES:    Kjente kanttilfeller
COMMIT:        Foreslatt commit-melding
CLOSEOUT:      Krav for closeout
REVIEW_CHECK:  Checkliste for diff-review

---

## WORKFLOW

### FASE 1: ROADMAP
Vis tabell med leveranser, tid, risiko, type.
Vent pa bekreftelse for du starter.

### FASE 2: INKREMENTELL BYGGING
1. Presenter EN kodeblokk
2. Inkluder verifikasjon
3. Auto-clipboard med pbcopy
4. Vent pa output fra operator

### FASE 3: VERIFIKASJONSLOOP
- Sjekk forventet output
- Bekreft: PHASE X CONFIRMED
- Ga til neste blokk
- ALDRI anta at det fungerte

---

## GIT PROOF PACK

Kjores FOR og ETTER hver jobb:

  echo "=== GIT PROOF PACK ==="
  echo "TIMESTAMP: $(date -u)"
  echo "BRANCH: $(git branch --show-current)"
  echo "COMMIT: $(git log --oneline -1)"
  git status --short
  git diff --stat
  echo "=== END PROOF ==="

---

## FEILHANDTERING (FAIL-CLOSED)

1. ACKNOWLEDGE - Siter eksakt feil
2. DIAGNOSE - Vis 1-2 diagnostiske kommandoer
3. FIX - Presenter korrigert blokk
4. VERIFY - Vent pa nytt output

Aldri:
- Lat som det fungerte
- Ignorer feilen
- Skyld pa operatoren
- Gjett uten data

Hvis tilstand er ukjent:
  Kjor diagnostikk for og fa fakta

---

## STORE FILER (over 200 linjer)

Bruk Python writer:
  python3 -c "
  content = '''innhold her'''
  with open('path', 'w') as f:
      f.write(content)
  print('OK')
  "

---

## COMMIT WORKFLOW

  cd ~/project
  git add .
  git status --short
  git diff --cached --stat
  git commit -m "type: beskrivelse"
  git log --oneline -3

---

## TESTING FORMAT

  TEST 1: Fil eksisterer
  test -f file.txt && echo PASS || echo FAIL

  TEST 2: Tjeneste kjorer
  pgrep -f service && echo PASS || echo FAIL

  TEST 3: Endepunkt svarer
  curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health

---

## DEPLOYMENT SUMMARY

  echo "=== DEPLOYMENT SUMMARY ==="
  echo "Filer opprettet: X"
  echo "Tjenester startet: Y"
  echo "Tester bestatt: Z"
  git log --oneline -5
  git status --short
  echo "BRANCH: $(git branch --show-current)"
  echo "HEAD: $(git log --oneline -1)"
  echo "=== END SUMMARY ==="

---

## KPI FOR HVER SESJON

- 100% av jobber bruker ASK-pakke
- Under 2 review-runder per ASK
- 0 path-improvisasjoner
- 100% Git Proof for og etter
- 100% closeout med test/add/commit/push/proof
- 0 blokker uten clipboard-verify

---

## ANTI-PATTERNS (ALDRI GJOR DETTE)

- Flere kodeblokker i en melding
- Kommandoer uten clipboard
- Neste fase uten bekreftelse
- Anta at filer eksisterer
- Falske AI-svar
- Kompleks regex uten testing
- Heredoc med unescaped variabler i literal-modus
- ClaudeBot skriver produksjonskode
- Codex velger arkitektur
- Jobb uten ASK-pakke
- Status uten Git Proof Pack

---

## VERSJON

v2.0 - 2024-04-01
Bygget inkrementelt med 3 blokker.
Verifisert etter hver blokk.

---

## TESTING FORMAT

  TEST 1: Fil eksisterer
  test -f file.txt && echo PASS || echo FAIL

  TEST 2: Tjeneste kjorer
  pgrep -f service && echo PASS || echo FAIL

  TEST 3: Endepunkt svarer
  curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health

---

## DEPLOYMENT SUMMARY

  echo "=== DEPLOYMENT SUMMARY ==="
  echo "Filer opprettet: X"
  echo "Tjenester startet: Y"
  echo "Tester bestatt: Z"
  git log --oneline -5
  git status --short
  echo "BRANCH: $(git branch --show-current)"
  echo "HEAD: $(git log --oneline -1)"
  echo "=== END SUMMARY ==="

---

## KPI FOR HVER SESJON

- 100% av jobber bruker ASK-pakke
- Under 2 review-runder per ASK
- 0 path-improvisasjoner
- 100% Git Proof for og etter
- 100% closeout med test/add/commit/push/proof
- 0 blokker uten clipboard-verify

---

## ANTI-PATTERNS (ALDRI GJOR DETTE)

- Flere kodeblokker i en melding
- Kommandoer uten clipboard
- Neste fase uten bekreftelse
- Anta at filer eksisterer
- Falske AI-svar
- Kompleks regex uten testing
- Heredoc med unescaped variabler i literal-modus
- ClaudeBot skriver produksjonskode
- Codex velger arkitektur
- Jobb uten ASK-pakke
- Status uten Git Proof Pack

---

## VERSJON

v2.0 - 2024-04-01
Bygget inkrementelt med 3 blokker.
Verifisert etter hver blokk.
