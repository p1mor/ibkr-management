# CLAUDE.md - project memory shim

Use `AGENTS.md` as the canonical instruction file for this repository.

## Local priorities
- Maintain a minimal and scalable base architecture.
- Keep data-capture code robust and easy to reason about.
- Avoid broad refactors without an explicit spec in `specs/`.

## Guardrails
- Do not add live-trading execution logic as default behavior.
- Do not commit secrets or environment-specific credentials.
- Ask before changing risk assumptions or execution paths.

## Validation
- `python -m compileall config core storage utils examples verify_setup.py`
- `python -m unittest discover -s tests -p "test_*.py"`

