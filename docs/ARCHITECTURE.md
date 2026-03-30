# Technical Architecture

## Core Principle

**Objects first, not chat first.** AI works on top of structured state.

## Data Model

    Mission          – Overall goal
    ├── Milestone    – Major sub-goal with success criteria
    │   ├── Step     – Concrete action with status
    │   └── Blocker  – What's stopping progress
    ├── Thread       – Continuous work session
    ├── Decision     – Choice + reason + who + when
    ├── Artifact     – Document/file/link/code/result
    ├── CheckIn      – Status update from user
    └── Recovery     – 30-second context for re-entry

## Plan-Diff: The Invisible Superpower

Between sessions, log:
- What was planned
- What actually happened
- The delta between them
- Hypothesis for why (from user input + patterns)

This reproduces PM retrospective thinking — without user attending a retrospective.

## LLM Usage Rule

    LLM  → language, synthesis, pattern recognition
    Code → scoring, logic, deterministic decisions

Never let AI alone decide what's most important. Let it suggest, let code score, let user confirm/deny. This makes system **explainable**.

## Stack Decisions

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | Python 3.11+ | Fast iteration, rich ecosystem |
| Storage | SQLite → PostgreSQL | Portable MVP → scalable production |
| CLI | Click | Standard, well-documented |
| LLM | OpenAI API | Extract/summarize/classify only |
| Scoring | Deterministic code | Must be traceable |

## GitHub Actions Parallel

roadmap.ai applies same lessons as GitHub's 2026 security roadmap:

| GitHub Problem | roadmap.ai Parallel |
|----------------|---------------------|
| Mutable tags → non-deterministic runs | Mutable plans → non-reproducible decisions |
| Over-shared secrets | Over-shared context without structure |
| No observability on triggers | No traceability on why decision made |
| Solution: lock files + scoped secrets | Solution: Decision objects + scoped context + plan-diff |

Every step in plan should have: hash, source, reason — so nothing "just changes".

## Confidence Scoring

Every AI recommendation includes:
- **Score** (0-100)
- **Source** (what data informed this)
- **Confidence level** (high/medium/low)
- **What changed** (since last version)

This separates "fancy chatbot" from "decision tool".
