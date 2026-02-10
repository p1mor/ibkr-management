from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


LOG_TS_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

SESSION_START_MARKERS = (
    "SimpleIBKRApp inicializada",
    "[DATA] Iniciando subscripcion a datos de mercado...",
    "[DATA] Iniciando subscripción a datos de mercado...",
)

TICK_PATTERN = re.compile(
    r"(?P<log_ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*Tick #\s*(?P<tick_id>\d+)\s*\|"
    r"\s*(?P<event_time>\d{2}:\d{2}:\d{2})\s*\|\s*Precio:\s*(?P<price>-?\d+(?:\.\d+)?)\s*\|"
    r"\s*Cantidad:\s*(?P<size>-?\d+(?:\.\d+)?)\s*\|\s*Exchange:\s*(?P<exchange>\S*)\s*$"
)

SPREAD_PATTERN = re.compile(
    r"(?P<log_ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*MID PRICE:\s*(?P<mid>-?\d+(?:\.\d+)?)"
    r"\s*\|\s*SPREAD:\s*(?P<spread>-?\d+(?:\.\d+)?)\s*puntos"
)

ALERT_PATTERN = re.compile(
    r"(?P<log_ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*\[(?P<level>WARNING|ERROR)\s*\]\s*(?P<message>.*)"
)


def _clock_to_seconds(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M:%S")
    return parsed.hour * 3600 + parsed.minute * 60 + parsed.second


def _parse_log_ts(value: str) -> datetime:
    return datetime.strptime(value, LOG_TS_FORMAT)


def read_log_lines(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return log_path.read_text(encoding="utf-8", errors="ignore").splitlines()


def select_latest_session_lines(lines: list[str]) -> tuple[list[str], int]:
    if not lines:
        return [], 0

    start_idx = 0
    for idx, line in enumerate(lines):
        if any(marker in line for marker in SESSION_START_MARKERS):
            start_idx = idx

    return lines[start_idx:], start_idx


def tail_line_window(lines: list[str], max_lines: int) -> list[str]:
    if max_lines <= 0:
        return lines
    return lines[-max_lines:]


def count_tick_lines(lines: list[str]) -> int:
    return sum("Tick #" in line for line in lines)


def parse_ticks(lines: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for line in lines:
        match = TICK_PATTERN.search(line)
        if not match:
            continue

        event_time = match.group("event_time")
        rows.append(
            {
                "log_ts": _parse_log_ts(match.group("log_ts")),
                "event_time": event_time,
                "tick_id": int(match.group("tick_id")),
                "price": float(match.group("price")),
                "size": float(match.group("size")),
                "exchange": match.group("exchange") or "-",
                "event_seconds": _clock_to_seconds(event_time),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=["log_ts", "event_time", "tick_id", "price", "size", "exchange", "event_seconds"]
        )

    return pd.DataFrame(rows).sort_values("tick_id").reset_index(drop=True)


def parse_spreads(lines: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for line in lines:
        match = SPREAD_PATTERN.search(line)
        if not match:
            continue

        rows.append(
            {
                "log_ts": _parse_log_ts(match.group("log_ts")),
                "mid_price": float(match.group("mid")),
                "spread_points": float(match.group("spread")),
            }
        )

    if not rows:
        return pd.DataFrame(columns=["log_ts", "mid_price", "spread_points"])

    return pd.DataFrame(rows).reset_index(drop=True)


def count_log_levels(lines: list[str]) -> dict[str, int]:
    return {
        "error_count": sum("[ERROR" in line for line in lines),
        "warning_count": sum("[WARNING" in line for line in lines),
        "info_count": sum("[INFO" in line for line in lines),
    }


def extract_alerts(lines: list[str], limit: int = 60) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for line in lines:
        match = ALERT_PATTERN.search(line)
        if not match:
            continue

        rows.append(
            {
                "Timestamp": match.group("log_ts"),
                "Nivel": match.group("level"),
                "Mensaje": match.group("message").strip(),
            }
        )

    if not rows:
        return pd.DataFrame(columns=["Timestamp", "Nivel", "Mensaje"])

    return pd.DataFrame(rows).tail(limit).reset_index(drop=True)
