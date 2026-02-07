# Spec 002 - Dashboard App Foundation

## Goal
Create a first modular Streamlit dashboard app for log-based observability,
keeping the UX simple while improving robustness and operational clarity.

## In scope
- New app package under `examples/dashboard_app/`
- Modular split: config, parsers, metrics, ui, app entrypoint
- Robust tick parsing for optional/empty `Exchange` values
- Basic run-info panel (parse ratio + session/window visibility)
- Configurable chart/window/panel selection from sidebar
- Minimal docs updates for new path/architecture

## Out of scope
- Database or websocket backend
- Major migration away from log-driven observability
- Advanced charting libraries or custom front-end framework
- Multi-user authentication or role model

## Acceptance criteria
- `streamlit run examples/dashboard_app/app.py` runs with current dependencies
- Tick parser handles logs where `Exchange:` can be empty
- Dashboard exposes run info, stats, charts, alerts, and raw log as selectable panels

## Follow-up candidates
- Session segmentation with explicit run IDs in logging
- Incremental file tailing/cache to reduce re-parse cost
- Optional direct read from parquet for chart panels
