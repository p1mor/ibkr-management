# IBKR Management

Foundation repository to capture, validate, persist, and observe IBKR market data with a simple and educational architecture.

## Current Scope
- Phase A (active): market data ingestion + basic visualization.
- Active contributors: Camilo (owner), Jaime (contributor).
- Current implementation focus: reliability and operational clarity.
- No real-order execution by default.

## API Scope (Important)
This repository uses **TWS / IB Gateway Socket API (`ibapi`)** via `EWrapper` / `EClient` callbacks.

### API Family Matrix
| API family | Status | Typical usage | Transport | Endpoint / port |
|---|---|---|---|---|
| TWS / IB Gateway Socket API (`ibapi`) | Active in this repo | Local event-driven market data and trading | TCP socket | IB Gateway: `4002` paper / `4001` live. TWS: `7497` paper / `7496` live |
| Client Portal API v1 | Not used in this phase | Local REST/WebSocket behind Client Portal Gateway | HTTPS local | `https://localhost:5000/v1/api` |
| Trading Web API | Not used in this phase | Cloud REST with OAuth2 | HTTPS internet | `https://api.ibkr.com/v1/api` |

## Quickstart
### 1. Prerequisites
- Python 3.9+ (recommended 3.11)
- IBKR account with market data permissions
- IB Gateway installed and logged in

### 2. Configure IB Gateway API
In IB Gateway:
- `File -> Global Configuration -> API -> Settings`
- Enable: `Enable ActiveX and Socket Clients`
- Trusted IP includes `127.0.0.1`
- Socket port (IB Gateway):
  - Paper: `4002`
  - Live: `4001`

### 3. Setup Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure `.env`
```bash
cp .env.example .env
```

Minimum config:
```bash
IBKR_HOST=127.0.0.1
IBKR_PORT=4002
IBKR_CLIENT_ID=1
IBKR_SYMBOL=ES
IBKR_EXCHANGE=CME
IBKR_CONTRACT_MONTH=202603
```

### 5. Validate setup
```bash
python verify_setup.py
```

### 6. Run capture + dashboard
Terminal 1:
```bash
python examples/basic_connection.py
```

Terminal 2:
```bash
streamlit run examples/dashboard_app/app.py
```

## Runtime Expectations
- If connection fails (e.g., wrong port), logs show error `502` and no ticks.
- If connection is OK but market is closed (weekends/off-session), there may be no ticks.
- Dashboard reads `ib_gateway_audit.log` and can show alerts even without ticks.

## Repository Structure
```text
ibkr-management/
├── AGENTS.md
├── README.md
├── START_HERE.md
├── .env.example
├── config/
├── core/
├── storage/
├── utils/
├── examples/
│   ├── basic_connection.py
│   └── dashboard_app/
│       ├── app.py
│       ├── app_config.py
│       ├── parsers.py
│       ├── metrics.py
│       └── ui.py
├── docs/
│   ├── architecture/overview.md
│   └── playbooks/agentic-repo-bootstrap.md
└── specs/
```

## Documentation Map
- `README.md`: canonical technical documentation (this file).
- `START_HERE.md`: shortest onboarding path.
- `AGENTS.md`: team rules, commands, and safety boundaries.
- `docs/architecture/overview.md`: current architecture snapshot.
- `specs/`: scope and acceptance criteria by feature.

## Troubleshooting (Common)
1. `Couldn't connect to TWS` / error `502`
- Verify IB Gateway is running and logged in.
- Verify port matches Gateway settings (`4002` paper, `4001` live).
- Verify API socket clients are enabled.

2. Connected but no ticks
- Check market session (weekend/off-hours can produce no ticks).
- Check market data subscription permissions.
- Check contract month (`IBKR_CONTRACT_MONTH`) is valid.

3. `No security definition has been found`
- Update `IBKR_CONTRACT_MONTH` to active contract.
- Confirm symbol/exchange pair is valid.

4. Dashboard appears empty
- Confirm `examples/basic_connection.py` is writing to `ib_gateway_audit.log`.
- Check dashboard `run_info` and alerts.

## Useful Commands
```bash
python verify_setup.py
python -m compileall config core storage utils examples verify_setup.py
python -m unittest discover -s tests -p "test_*.py"
```

## Official References
- IBKR Campus - TWS API docs (primary for this repo):
  - https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/
- IBKR Campus - Web API docs:
  - https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-doc/
- Trading Web API OpenAPI:
  - https://api.ibkr.com/gw/api/v3/api-docs
- Client Portal API v1:
  - https://www.interactivebrokers.eu/campus/ibkr-api-page/cpapi-v1/
- TWS API static docs (secondary legacy reference):
  - https://interactivebrokers.github.io/tws-api/

## Disclaimer
Educational/research use only. Futures trading involves substantial risk.
