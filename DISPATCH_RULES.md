# DISPATCH_RULES.md
# Guardrails for Claude Desktop when running via Dispatch/Cowork
# Version: 1.0
# Repo: ~/roadmap-ai

## Prinsipp
Dispatch er en fjernkontroll. Roadmap-AI er sannhetskilden.
Claude kjører kun forhåndsdefinerte operasjoner mot kjente filer.

---

## TILLATT

### Kommandoer
- Kjøre operasjoner definert i `dispatch_ops.yaml` — ingen andre
- Kalle `roadmap` CLI med flagg som er listet i ops-kontrakten
- Kjøre `scripts/dispatch_runner.sh` med gyldige verb

### Filer — lese
- Alt under `~/roadmap-ai/`
- `panel_output/*.json`
- `docs/*.md`
- `dispatch_ops.yaml`
- Denne filen (`DISPATCH_RULES.md`)

### Filer — skrive
- `panel_output/*.json` (kun output fra kjente kommandoer)
- `panel_output/*.md` (kun oppsummeringer)
- Git commits i `~/roadmap-ai` (kun via closeout-verb)

---

## IKKE TILLATT

### Kommandoer
- Vilkårlige shell-kommandoer utenfor ops-kontrakten
- `pip install`, `brew install`, eller annen pakkeinstallasjon
- `curl`, `wget`, eller nettverkskall til eksterne tjenester
- `rm -rf`, `chmod`, `chown` eller destruktive operasjoner
- Kjøring av scripts som ikke er listet i `dispatch_ops.yaml`

### Filer
- Skrive til mapper utenfor `~/roadmap-ai/`
- Endre `.py`-filer, `setup.py`, `requirements.txt`
- Endre `.git/config` eller remote-oppsett
- Lese/skrive `~/.ssh/`, `~/.env`, `~/.zshrc` eller lignende

### Apper
- Åpne nettleser
- Åpne e-postklient
- Åpne Slack, Notion, eller andre connectors
  (dette kan endres senere med eksplisitt per-app godkjenning)
- Starte bakgrunnsprosesser eller daemons

---

## VED FEIL

1. Skriv feilmelding til `panel_output/error.json`:
   ```json
   {
     "timestamp": "ISO-8601",
     "op": "verb som feilet",
     "step": "kommando som feilet",
     "error": "feilmelding",
     "exit_code": 1
   }
   ```
2. **Ikke** forsøk automatisk reparasjon
3. **Ikke** kjør alternative kommandoer
4. Meld tilbake i Dispatch-tråden med:
   - Hvilket verb som feilet
   - Hvilket steg som feilet
   - Feilmeldingen
   - Forslag til manuell handling (uten å utføre den)

---

## VED UKJENT FORESPØRSEL

Hvis bruker ber om noe som ikke matcher et verb i `dispatch_ops.yaml`:
1. Svar: "Denne operasjonen er ikke definert i ops-kontrakten."
2. List tilgjengelige verbs
3. **Ikke** forsøk å tolke forespørselen kreativt
4. **Ikke** kjør noe

---

## IDEMPOTENS-KRAV

Alle operasjoner skal tåle å kjøres to ganger på rad uten sideeffekter.
- `standup` overskriver panel_output-filer (OK)
- `closeout` committer kun hvis det er endringer (`git diff --quiet` sjekk)
- `decide` legger til ny beslutning (additiv — akseptabelt)
- `export-panels` overskriver (OK)
- `health` er read-only (OK)

---

## MAC SLEEP / APP LUKKES

Hvis Mac sovner eller Claude Desktop lukkes under en oppgave:
- Oppgaven stopper
- Ingen automatisk gjenopptakelse
- Bruker må sende samme verb på nytt fra Dispatch
- Fordi operasjonene er idempotente, er dette trygt

Anbefalt forebygging:
```bash
caffeinate -i -w $(pgrep -f "Claude Desktop") &
```

---

## VERSJONERING

Denne filen versjoneres i git sammen med `dispatch_ops.yaml`.
Endringer krever eksplisitt commit med melding:
`"update dispatch rules: <hva som endret seg>"`
