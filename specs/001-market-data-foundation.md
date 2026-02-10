# Spec 001 - Market Data Foundation

## Goal
Stabilize the base project structure and workflows so future features
(LLM support, agentic flows, strategy logic) can be added safely.

## In scope
- Canonical agent/project guidance file (`AGENTS.md`)
- Tool-specific shims (`.github/copilot-instructions.md`, `CLAUDE.md`)
- Baseline architecture documentation (`docs/architecture/overview.md`)
- Minimal project tooling baseline (`pyproject.toml`)
- Minimal smoke tests (`tests/`)
- Minimal CI validation (`.github/workflows/ci.yml`)

## Out of scope
- New trading strategies
- Live order execution workflows
- Major runtime refactors
- Database/web backend introduction

## Acceptance criteria
- A new contributor can discover rules and architecture in under 5 minutes.
- Static checks and tests run locally with one command each.
- CI validates syntax + smoke tests on push/PR.
- No secrets or live-trading defaults are introduced.

## Follow-up candidates
- Spec 002: connection/reconnection hardening
- Spec 003: data processor alignment with writer/validator APIs
- Spec 004: structured metrics and runtime health endpoints

