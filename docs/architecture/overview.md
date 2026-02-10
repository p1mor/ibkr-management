# Architecture Overview

## Scope
This repository currently implements a local foundation for market-data ingestion
from Interactive Brokers (IBKR), with validation, storage, and basic observability.

API scope for current implementation:
- Active: TWS/IB Gateway Socket API (`ibapi`).
- Not in current scope: Client Portal API v1 and Trading Web API.
- Reference: `README.md` section `API Scope (Important)`.

## Collaboration model
- Repository owner: Camilo.
- Primary contributor: Jaime.
- Day-to-day work should land on feature branches and only merge stable increments to `main`.
- Current experiments can use Jaime's account/data, but core design should stay user-agnostic.

## Product intent (phased)
1. Initial: data capture + dashboard visibility.
2. Next: analysis tools and interpretable buy/sell signal research.
3. Later: automation framework for controlled order execution.

The repository should evolve incrementally without front-loading heavy infrastructure.

## Runtime flow
1. IB Gateway/TWS publishes market data.
2. `examples/basic_connection.py` receives callbacks from `ibapi`.
3. `src/ibkr_management/core/orderbook.py` maintains in-memory depth state.
4. `src/ibkr_management/core/validators.py` applies quality checks.
5. `src/ibkr_management/storage/parquet_writer.py` buffers and flushes records to Parquet.
6. `examples/dashboard_app/app.py` reads log output for real-time monitoring.

## Modules
- Entry-point convention:
  - executable flows live in `examples/` and `scripts/`
  - canonical code lives under `src/ibkr_management/`
- `src/ibkr_management/config/`
  - `settings.py`: env-driven configuration and helper paths
  - `contracts.py`: IBKR contract construction helpers
- `src/ibkr_management/core/`
  - `connection.py`: connection skeleton
  - `orderbook.py`: order book representation and metrics
  - `validators.py`: validation bitmask logic
  - `data_processor.py`: minimal coordinator for orderbook + validation + persistence
- `src/ibkr_management/storage/`
  - `parquet_writer.py`: thread-safe buffered Parquet persistence
- `src/ibkr_management/utils/`
  - `logging_config.py`: rotating logs and logger helpers
- `examples/`
  - `basic_connection.py`: runnable ingestion example
  - `dashboard_app/app.py`: modular streamlit dashboard for interpretation

## Design principles (current stage)
- Start simple, with explicit code paths.
- Keep operational safety high (paper-trading-first).
- Defer complexity until there is a validated need.
- Prefer incremental evolution through specs in `specs/`.

## Architectural reference (not a hard dependency)
NautilusTrader is used as a best-practice reference for:
- event-driven flow organization
- clear data/execution boundaries
- broker adapter separation

Relevant documentation:
- https://nautilustrader.io/docs/latest/concepts/overview/
- https://nautilustrader.io/docs/latest/integrations/ib/
