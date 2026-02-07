# IBKR Management

<p align="left">
  <img src="https://img.shields.io/badge/Phase-A%20Foundation-0ea5e9?style=for-the-badge" alt="Phase A Foundation" />
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/IBKR-Socket%20API-2563eb?style=for-the-badge" alt="IBKR Socket API" />
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit Dashboard" />
  <img src="https://img.shields.io/badge/Tests-unittest-22c55e?style=for-the-badge" alt="unittest" />
  <img src="https://img.shields.io/github/last-commit/p1mor/ibkr-management?style=for-the-badge&logo=github" alt="Last Commit" />
</p>

Educational foundation to capture, validate, persist, and observe IBKR market data with a clear and minimal architecture.

<a id="overview"></a>
## 🚀 Overview
- Current phase: **Phase A** (market data ingestion + basic visualization).
- Active API in this repo: **TWS / IB Gateway Socket API (`ibapi`)**.
- Goal: prioritize data quality and operational stability before adding execution automation.
- Real-order execution is not part of the default workflow.

## 🧭 Table of Contents
- [🚀 Overview](#overview)
- [⚡ Quick Start](#quick-start)
- [🔌 API Scope](#api-scope)
- [🧱 How Phase A Works](#how-phase-a-works)
- [🗂️ Repository Layout](#repository-layout)
- [🛠️ Development Commands](#development-commands)
- [🩺 Troubleshooting](#troubleshooting)
- [📚 Documentation and References](#documentation-and-references)
- [⚠️ Safety Notice](#safety-notice)

<a id="quick-start"></a>
## ⚡ Quick Start
<details open>
<summary><strong>1) Prerequisites</strong></summary>

- Python `3.9+` (recommended `3.11`)
- IBKR account with market data permissions
- IB Gateway installed on desktop

</details>

<details open>
<summary><strong>2) Configure IB Gateway (required)</strong></summary>

In IB Gateway Desktop:
- `File -> Global Configuration -> API -> Settings`
- Enable `Enable ActiveX and Socket Clients`
- Add `127.0.0.1` to trusted IPs
- Keep Gateway open and logged in while scripts are running
- Use correct port:
  - Paper: `4002`
  - Live: `4001`

</details>

<details open>
<summary><strong>3) Setup and run</strong></summary>

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/verify_setup.py
```

Minimum `.env`:
```bash
IBKR_HOST=127.0.0.1
IBKR_PORT=4002
IBKR_CLIENT_ID=1
IBKR_SYMBOL=ES
IBKR_EXCHANGE=CME
IBKR_CONTRACT_MONTH=202603
```

Run capture and dashboard in separate terminals:

```bash
# Terminal 1
python examples/basic_connection.py

# Terminal 2
streamlit run examples/dashboard_app/app.py
```

</details>

<a id="api-scope"></a>
## 🔌 API Scope
This repository is aligned to **Socket API (`ibapi`)** and not to Web API flows in Phase A.

| API family | Status in this repo | Transport | Endpoint / Port |
|---|---|---|---|
| TWS / IB Gateway Socket API (`ibapi`) | Active | TCP socket | IB Gateway `4002` paper / `4001` live, TWS `7497` paper / `7496` live |
| Client Portal API v1 | Not used in Phase A | HTTPS local | `https://localhost:5000/v1/api` |
| Trading Web API | Not used in Phase A | HTTPS internet | `https://api.ibkr.com/v1/api` |

<a id="how-phase-a-works"></a>
## 🧱 How Phase A Works
1. `examples/basic_connection.py` opens socket session with IB Gateway/TWS.
2. `src/ibkr_management/core/` processes and validates tick/depth events.
3. `src/ibkr_management/storage/parquet_writer.py` persists normalized data.
4. `examples/dashboard_app/app.py` provides real-time observability from generated logs.

Runtime expectations:
- If port/session is wrong, connection errors such as `502` appear.
- If Gateway closes or logs out, data flow stops.
- If market is closed (for example weekend), connection may be healthy but no ticks arrive.
- Dashboard can still show run status/alerts from `ib_gateway_audit.log`.

<a id="repository-layout"></a>
## 🗂️ Repository Layout
```text
ibkr-management/
├── README.md
├── AGENTS.md
├── .env.example
├── src/
│   └── ibkr_management/
│       ├── config/
│       ├── core/
│       ├── storage/
│       └── utils/
├── scripts/
│   └── verify_setup.py
├── examples/
│   ├── basic_connection.py
│   └── dashboard_app/
├── docs/
│   ├── architecture/overview.md
│   └── playbooks/agentic-repo-bootstrap.md
└── specs/
```

Conventions:
- `src/ibkr_management/`: canonical importable code.
- `examples/` and `scripts/`: executable entrypoints.
- Keep business logic in `src/`; keep entrypoints thin.

<a id="development-commands"></a>
## 🛠️ Development Commands
```bash
python scripts/verify_setup.py
python -m compileall src examples scripts tests
python -m unittest discover -s tests -p "test_*.py"
```

<a id="troubleshooting"></a>
## 🩺 Troubleshooting
<details>
<summary><strong>Connection error (e.g., "Couldn't connect to TWS", code 502)</strong></summary>

- Verify IB Gateway is running and logged in
- Verify `IBKR_PORT` matches mode (`4002` paper, `4001` live)
- Verify socket clients are enabled in Gateway API settings

</details>

<details>
<summary><strong>Connected but no market data ticks</strong></summary>

- Check if market is open (weekends/off-hours produce no ticks)
- Check market data subscription permissions
- Validate `IBKR_CONTRACT_MONTH`

</details>

<details>
<summary><strong>"No security definition has been found"</strong></summary>

- Update `IBKR_CONTRACT_MONTH` to active contract
- Confirm symbol and exchange are valid

</details>

<details>
<summary><strong>Dashboard appears empty</strong></summary>

- Confirm `examples/basic_connection.py` is generating `ib_gateway_audit.log`
- Check dashboard run status and alert panels

</details>

<a id="documentation-and-references"></a>
## 📚 Documentation and References
Internal docs:
- `README.md`: canonical setup and operational runbook
- `AGENTS.md`: team workflow, safety boundaries, and contribution rules
- `docs/architecture/overview.md`: architecture snapshot
- `specs/`: feature scope and acceptance criteria

Official references:
- IBKR Campus - TWS API docs:
  - https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/
- IBKR Campus - Web API docs:
  - https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-doc/
- Trading Web API OpenAPI:
  - https://api.ibkr.com/gw/api/v3/api-docs
- Client Portal API v1:
  - https://www.interactivebrokers.eu/campus/ibkr-api-page/cpapi-v1/
- TWS API static docs (legacy secondary reference):
  - https://interactivebrokers.github.io/tws-api/

<a id="safety-notice"></a>
## ⚠️ Safety Notice
Educational and research use only. Futures trading involves substantial risk.
