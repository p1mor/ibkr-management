# AGENTS.md - ibkr-management

## Mission
Build a reliable and educational IBKR market-data foundation:
- connect to IB Gateway/TWS
- capture tick and depth data
- validate and persist records
- provide simple real-time observability

## Team model
- Owner/maintainer: Camilo (repository owner).
- Active contributor: Jaime.
- Default collaboration mode: work on feature branches, keep `main` stable.
- Current operating account/data is usually Jaime's IBKR account for experimentation.
- Target architecture must remain account-agnostic for future multi-user support.

## Current phase
Foundation only. Prioritize data capture, quality, and operational stability.

## Product trajectory
1. Phase A: market data ingestion and visualization.
2. Phase B: analysis tooling and signal interpretation.
3. Phase C: controlled automation framework for buy/sell execution.

Keep each phase minimal before moving to the next one.

## Source of truth
- Architecture: `docs/architecture/overview.md`
- API scope and official IBKR sources: `README.md` (section `API Scope (Important)`)
- Active specs: `specs/`
- Runtime config: `.env`

If docs and code differ, code is the current behavior and docs must be updated.

## Repository map
- `src/ibkr_management/`: canonical library code (`config`, `core`, `storage`, `utils`)
- `examples/`: runnable demos (`basic_connection.py`, `dashboard_app/app.py`)
- `scripts/`: operational helpers (`verify_setup.py` implementation + future utilities)
- `tests/`: smoke and unit checks
- `specs/`: feature-level implementation specs

Entry-point rule:
- Runnable scripts belong in `examples/` or `scripts/`.
- Canonical imports should target `ibkr_management.*` from `src/`.

## Development rules
- Keep changes minimal, testable, and reversible.
- Preserve educational clarity in examples.
- Prefer small modules over large abstractions.
- Do not add complex infra before it is needed.
- Design new components with clean boundaries so a future multi-user module can plug in.

## Safety boundaries
- Never commit API keys, passwords, or account identifiers.
- Never run code that places real orders by default.
- Use paper trading for development and tests.
- Ask first before changing risk-related behavior or execution semantics.
- Treat account-specific data as sensitive even in experimental workflows.

## Commands
- Setup env: `python3 -m venv venv && source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Verify setup: `python scripts/verify_setup.py`
- Run capture example: `python examples/basic_connection.py`
- Run dashboard: `streamlit run examples/dashboard_app/app.py`
- Static checks: `python -m compileall src examples scripts tests`
- Tests: `python -m unittest discover -s tests -p "test_*.py"`

## Contribution workflow
1. Create or update a spec in `specs/` for non-trivial changes.
2. Implement the smallest useful increment.
3. Run static checks and tests.
4. Update docs affected by behavior changes.

## External reference (architecture)
NautilusTrader is a reference for design ideas, not a dependency mandate:
- Event-driven design and backtest/live parity principles.
- Ports/adapters style for broker integrations.
- Clear separation of data, execution, and instrument responsibilities.

Reference docs:
- https://nautilustrader.io/docs/latest/concepts/overview/
- https://nautilustrader.io/docs/latest/integrations/ib/
