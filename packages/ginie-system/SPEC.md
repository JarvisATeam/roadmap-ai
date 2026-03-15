# GinieSystem v1.1.1 — Endelig Fail-Closed Spesifikasjon

> Implementeringskontrakt for run-wrapper + FlowArk Operational Dome
> **Dette dokumentet er SANNHETSKILDEN.**
> Ingen kode skrives som ikke har rot her.

## Hierarki

1. Denne spec (uforanderlig etter godkjenning)
2. `contracts.py` generert FRA denne spec
3. Implementasjonskode validert MOT denne spec
4. Akseptansetester definert I denne spec

---

# DEL A: SHELL-WRAPPER GinieSystem run-kontrakt

## A.1 Grunnregler

```yaml
shell: bash -lc (ikke-interaktiv, ingen PTY)
execution: subprocess.Popen (streaming, egen prosessgruppe)
state: tilstands-løs per kall (state injiseres, aldri arves)
async: ikke støttet i v1
nohup/disown/coproc: DENY
```

## A.2 Låste Datakontrakter

### A.2.1 PolicyContext
```python
class PolicyContext(BaseModel):
    """Eksplisitt godkjenningskontekst for alle guarded operasjoner."""
    git_proofpack_approved: bool = False
    allow_guarded_write: bool = False
    approval_token: Optional[str] = Field(default=None, pattern=r"^(GPP|WRITE|ADMIN)-\d{8}-\d{3}$")
```

### A.2.2 SessionState
```python
class SessionState(BaseModel):
    session_id: str = Field(pattern=r"^GS-SESSION-\d{8}-\d{3}$")
    workspace_root: str  # Absolutt path
    cwd: str
    env: dict[str, str]
    allowed_env_keys: list[str] = ["PYTHON_UNBUFFERED", "NO_COLOR", "CI", "TERM", "VIRTUAL_ENV", "NODE_ENV"]
    max_output_bytes: int = Field(default=40960, ge=1024, le=1048576)
    timeout_seconds: int = Field(default=60, ge=5, le=600)
    history: list[HistoryEntry] = Field(max_length=50)
    loop_score: int = Field(default=0, ge=0)
```

### A.2.3 CommandResponse
```python
class CommandResponse(BaseModel):
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    cwd: str
    duration_ms: int
    timed_out: bool = False
    truncated: bool = False
    truncation_notice: str = ""
    warnings: list[str] = Field(default_factory=list)
    guardrail_events: list[str] = Field(default_factory=list)
    state_delta: StateDelta = Field(default_factory=StateDelta)
```

### A.2.4 Reserverte Exit-Koder
- **22:** Unsupported syntax
- **77:** Blocked by guard
- **89:** Loop breaker
- **124:** Timeout

## A.3 Command Guard

### A.3.1 cd Eksakt Regel
- KUN `cd PATH` støttet
- PATH must resolve innenfor `workspace_root` via `realpath`
- Alle andre former → exit 22
- Path utenfor workspace → exit 77

### A.3.2 export Eksakt Regel
- KUN `export KEY=VALUE` med ren alfanumerisk value
- KEY må finnes i `allowed_env_keys`
- Ingen quotes, spaces, shell-metategn
- PATH, HOME, USER, SHELL, LD_PRELOAD → DENY

### A.3.3 Fire-Nivås Command Guard
1. **ALLOW_READ:** ls, cat, grep, find, etc.
2. **ALLOW_WORKSPACE_WRITE:** mkdir, touch, python, npm, etc.
3. **GUARDED_WRITE:** rm, mv (krever `allow_guarded_write=true` + `approval_token`)
4. **DENY:** sudo, curl, wget, docker, ssh, kill

### A.3.4 Git Subpolicy
- **READONLY:** status, diff, log, branch
- **GUARDED_WRITE:** add, commit, push (krever `git_proofpack_approved=true`)

## A.4 Shell Harness

### A.4.1 CWD State Marker
Wrapper garanterer CWD-markør:
```bash
{user_command}; EXIT_CODE=$?; printf '___GINIE_STATE_CWD:%s' "$(pwd)"; exit $EXIT_CODE
```

### A.4.2 Popen Execution
- Egen prosessgruppe (`os.setsid`)
- Streaming med `read1()` chunks
- Binary detection (`\x00`) → exit 77
- Timeout → SIGKILL prosessgruppe

### A.4.3 Head+Tail Streaming Buffer
- **Asymmetrisk 30/70:** HEAD (30%) + TAIL (70%)
- TAIL roterer som ringbuffer
- Truncation notice med byte counts

## A.5 Output Processor
- ANSI strip
- CWD marker ekstraksjon (siste forekomst)
- Silent Success: "Command executed successfully with exit code 0."

## A.6 Loop Detector
- **Decay-modell:** +3 for gjentakelse, -2 for progresjon
- **Break threshold:** score ≥ 5
- **Sammenligning:** normalized command + stderr hash + filesystem fingerprint

## A.7 Filesystem Fingerprint
- SHA-256 av toppnivå dir-innhold (navn, type, size, mtime)

## A.8 Akseptansetestmatrise: 23 tester
- A1-A7: State control (cd valid, export, blocked commands)
- B8-B14: Data flow (ANSI strip, truncation, marker)
- C15-C23: Security (binary block, timeout, loop breaker, interpreter escape)

---

# DEL B: FLOWARK OPERATIONAL DOME

## B.1 Systemets Grunnlov

**Formål:** Gjøre deg farligere på dine sterke sider mens det automatisk beskytter svakhetene.

**5-Lags System:**
1. **Biologisk Foundation:** State Engine
2. **Anti-Spredning:** 3-Lags Arbeidssystem
3. **Beslutningsport:** State-to-Action Firewall
4. **Frustrasjons-Firewall:** Anti-Waste Engine
5. **Produkt-Wrapper:** FlowArk Solo + Roadmap.ai

## B.2 Lag 1: Biologisk Foundation

```python
class BioState(BaseModel):
    energy: EnergyLevel  # HIGH/MEDIUM/LOW
    sleep_score: int  # 0-100
    hrv_score: Optional[int]  # Oura API
    hunger_signal: bool
    hours_since_meal: float
    frustration_active: bool

def compute_mode(bio: BioState) -> WorkMode:
    # RECOVER: HRV < 40 OR biologisk frustrasjon
    # ADMIN: Lav energi OR sulten OR dårlig søvn
    # LIGHT_OPS: Middels energi
    # DEEP_BUILD: Alt er godt
```

### Morgen-Loop (3 min, ikke-forhandlingsbar)
- Input: energi, søvn, sult
- Output: `recommended_mode`, 3 `daily_actions`

### Midt-på-dagen Interrupt (1 min, hver 90 min)
- Biological fix: mat, luft, pause
- Cognitive clarify: nextstep OR park

### Shutdown-Loop (3 min, ikke-forhandlingsbar)
- **Loop detection:** 80%+ likhet med gårsdagens output → krever refleksjon

## B.3 Lag 2: Anti-Spredning

```python
class WorkSystem(BaseModel):
    capture_inbox: list[str] = Field(max_length=20)  # Maks 5 min opphold
    active_items: list[ActiveItem] = Field(max_length=3)  # HARD LIMIT
    parking: dict[str, list[str]] = {"later": [], "blocked": [], "maybe": []}
```

### Daglig Minimum-Kontrakt
- **Minimum 3 konkrete handlinger per dag**
- Typer: `codex`, `ssh/aimigo`, `manual`

## B.4 Lag 3: Beslutningsport

```python
class DecisionGate:
    STRATEGIC_DECISIONS = frozenset(["new_app_idea", "architecture_change", "pivot"])
    
    @staticmethod
    def validate(decision_type: str, bio: BioState) -> tuple[DecisionResult, str]:
        # Biologisk veto: sulten/lav energi → DEFER
        # Mode veto: ADMIN kan ikke ta arkitekturbeslutninger
```

## B.5 Lag 4: Frustrasjons-Firewall

5 typer:
1. **BIOLOGICAL:** Spis → force RECOVER mode
2. **SLOWNESS:** Finn minste handling OR delegér
3. **UNCLEAR:** Split oppgave OR park
4. **MEANINGLESS:** Bevis verdi OR park umiddelbart
5. **SOCIAL:** Async first, batch, delegér

## B.6 Lag 5: Produkt-Wrapper

### B.6.1 FlowArk Solo
5 skjermer:
1. **Morgen-Input:** Bio state + daily contract
2. **Dashboard:** Mode badge + primary action + secondary list
3. **Frustrasjon-Triage:** Modal med auto-response
4. **Shutdown:** Actual output + next step + loop detection
5. **Parkering:** Ukentlig review (fredager)

### B.6.2 Roadmap.ai
Kommersiell engine:
- Input: tekst/møtenotater/strategidocs
- Output: Work streams (maks 3), blockers, friction warnings
- Sync til FlowArk: topp 3 goals → active items

## B.7 Daglig Operativ Protokoll

```
0900: Morgen-Loop → mode + 3 handlinger
0930-1200: Deep Build / Light Ops
1200-1300: Mat + luft (ingen skjerm)
1300-1600: Handling 2 og 3
1600-1700: Admin (email, Slack, triage)
1700: Shutdown-Loop → logg output + next step
1800+: Recovery (ingen arbeid)
```

## B.9 Teknisk Stack

| Lag | Teknologi |
|-----|-----------|
| Frontend | Next.js 14 + shadcn/ui |
| Backend | Python 3.11 + FastAPI |
| Database | PostgreSQL (Neon) |
| AI/NLP | OpenAI GPT-4o + Claude fallback |
| Auth | Clerk |
| Hosting | Vercel + Railway |

## B.10 30-Dagers Byggeplan

**Uke 1 (Dag 1-7):** FlowArk Foundation
- contracts.py + SQLite schema
- Morgen-Input API + UI
- Dashboard med mode badge

**Uke 2 (Dag 8-14):** FlowArk Komplett
- Shutdown + loop detection
- Frustrasjon-Triage
- Parkering UI

**Uke 3 (Dag 15-21):** GinieSystem Shell Wrapper
- command_guard.py (23 akseptansetester)
- shell_harness.py (Popen + streaming)
- output_processor.py + loop_detector.py

**Uke 4 (Dag 22-30):** Roadmap.ai + Deploy
- Roadmap input processing
- FlowArk ↔ Roadmap.ai sync
- Deploy til Vercel + Railway

## B.11 Forretningsmodell Roadmap.ai

| Tier | Pris | Features |
|------|------|----------|
| Free | $0 | 5 roadmaps/måned, markdown export |
| Pro | $29/måned | Unlimited, Notion sync |
| Team | $99/måned | 5 brukere, API |

**Success Metrics:** 50 signups + 5 paying pro + 1 team

---

## Neste Handling: Akkurat Nå

1. Commit denne spec-en til `packages/ginie-system/SPEC.md`
2. Opprett stub-filer for Codex-implementering:
   - `contracts.py`
   - `command_guard.py`
   - `shell_harness.py`
   - `output_processor.py`
   - `loop_detector.py`
   - `session_store.py`
3. Oppdater `CODEX_TASKS.md` med TASK-013 til TASK-020
