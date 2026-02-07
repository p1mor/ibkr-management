# Start Here

Use this sequence:

1. `README.md` (quickstart + API scope + troubleshooting)
2. `docs/architecture/overview.md` (current architecture)
3. `AGENTS.md` (team/process rules)

## Fast Path
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Keep IB Gateway Desktop open/logged in (Paper uses port 4002)
python scripts/verify_setup.py
python examples/basic_connection.py
```

In another terminal:
```bash
streamlit run examples/dashboard_app/app.py
```

## Critical Reminder
This repository uses **Socket API (`ibapi`)** with IB Gateway/TWS, not Web API.

IB Gateway ports:
- Paper: `4002`
- Live: `4001`
