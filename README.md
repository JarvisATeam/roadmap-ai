# roadmap.ai

**"Never lose the thread again."**

A continuity engine that remembers your goal, tracks progress, detects drift, and always knows what's next.

## Core Differentiator

Not "AI with memory" — **continuity as primary design objective**.

- ✅ Thread recovery: 30-second re-entry brief
- ✅ Plan-diff tracking: planned vs. actual
- ✅ Decision trail: why choices were made
- ✅ Explainable AI: every recommendation has source + confidence

## What It IS

- Continuity engine maintaining project state across sessions
- Objects-first architecture (Mission → Milestone → Step → Decision)
- Build mode: for founders/developers/makers
- Signature feature: "Here's where you left off, here's what changed, here's what's next"

## What It's NOT

- ❌ Another chatbot with memory
- ❌ Generic task manager
- ❌ Standalone productivity tool
- ❌ Notion/Linear competitor

## Tech Stack

- **Language:** Python 3.11+
- **Storage:** SQLite (MVP) → PostgreSQL (production)
- **CLI:** Click
- **LLM:** OpenAI API (summarize/classify only - scoring is deterministic)
- **Architecture:** Objects first, AI on top

## Installation

    pip install -e .
    roadmap init

## Quick Start

    # Create a mission
    roadmap create "Launch SaaS MVP"
    
    # Add milestone
    roadmap milestone "Auth system complete" --success "Users can login/logout/reset password"
    
    # Check status
    roadmap status
    
    # Get re-entry brief
    roadmap open

## Signature Feature: Thread Recovery

    $ roadmap open
    
    ⚡ RE-ENTRY BRIEF (30 seconds)
    
    Last session: 2 days ago
    Status: Day 12 of 30-day build
    
    ✅ COMPLETED SINCE LAST:
      - Auth system deployed
      - 3/4 API endpoints live
    
    ⚠️ PLAN DRIFT DETECTED:
      - Skipped: Redis caching (deprioritized)
      - Added: Rate limiting (security requirement)
    
    🎯 TODAY'S FOCUS:
      - [ ] Final API endpoint (payments)
      - [ ] Integration tests
      - [ ] Deploy to staging
    
    🧠 KEY CONTEXT:
      - Decision 3 days ago: Chose Stripe over Lemon Squeezy (EU coverage)
      - Blocker: Stripe API key for prod missing
    
    Ready? (yes/review/roadmap)

## License

MIT
