# GitHub Copilot repository instructions

Follow `AGENTS.md` at repository root as the primary project guidance.

Key expectations:
- Keep changes small and directly aligned to the current phase (foundation).
- Prefer simple, explicit Python code over framework-heavy patterns.
- Never introduce real-trading behavior by default.
- Use paper-trading-safe assumptions in examples and tests.

Before finishing a change:
- Run static checks and tests from `AGENTS.md`.
- Update `specs/` and docs when behavior changes.

