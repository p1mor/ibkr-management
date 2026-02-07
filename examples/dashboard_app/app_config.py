from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_LOG_FILE = Path("ib_gateway_audit.log")

WINDOW_LABELS = {
    "5m": "Ultimos 5 minutos",
    "30m": "Ultimos 30 minutos",
    "2h": "Ultimas 2 horas",
    "all": "Todo (lineas parseadas)",
}

WINDOW_SECONDS = {
    "5m": 5 * 60,
    "30m": 30 * 60,
    "2h": 2 * 60 * 60,
    "all": None,
}

PANEL_LABELS = {
    "run_info": "Run info",
    "stats": "Estado y metricas",
    "price": "Precio",
    "activity": "Actividad",
    "spread": "Spread",
    "tables": "Ultimos ticks",
    "alerts": "Alertas",
    "raw_log": "Log crudo",
}


@dataclass(frozen=True)
class DashboardDefaults:
    parse_line_window: int = 8_000
    max_chart_points: int = 800
    raw_log_lines: int = 150
    refresh_seconds: int = 2
    alert_limit: int = 60
    stale_live_seconds: int = 5
    stale_slow_seconds: int = 20
    panel_selection: tuple[str, ...] = (
        "run_info",
        "stats",
        "price",
        "activity",
        "spread",
        "tables",
        "alerts",
    )


def get_window_seconds(window_key: str) -> int | None:
    return WINDOW_SECONDS.get(window_key)
