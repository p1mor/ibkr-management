from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def spread_quality(spread_points: float | None) -> str:
    if spread_points is None:
        return "Sin dato"
    if spread_points <= 0.50:
        return "Estrecho"
    if spread_points <= 2.0:
        return "Normal"
    return "Amplio"


def feed_state(seconds_since_last_tick: int, live_limit: int, slow_limit: int) -> str:
    if seconds_since_last_tick <= live_limit:
        return "En vivo"
    if seconds_since_last_tick <= slow_limit:
        return "Lento"
    return "Pausado"


def filter_by_window(df: pd.DataFrame, window_seconds: int | None, ts_col: str = "log_ts") -> pd.DataFrame:
    if df.empty or window_seconds is None:
        return df

    end_ts = df[ts_col].max()
    start_ts = end_ts - pd.Timedelta(seconds=window_seconds)
    return df[df[ts_col] >= start_ts].reset_index(drop=True)


def build_market_summary(
    ticks_df: pd.DataFrame,
    spread_df: pd.DataFrame,
    total_ticks: int,
    live_limit: int,
    slow_limit: int,
) -> dict[str, str | int | float | None]:
    if ticks_df.empty:
        return {}

    first_price = float(ticks_df["price"].iloc[0])
    last_price = float(ticks_df["price"].iloc[-1])
    price_delta = last_price - first_price
    price_delta_pct = (price_delta / first_price) * 100 if first_price else 0.0

    latest_tick_ts = ticks_df["log_ts"].iloc[-1]
    if isinstance(latest_tick_ts, pd.Timestamp):
        latest_tick_dt = latest_tick_ts.to_pydatetime()
    else:
        latest_tick_dt = latest_tick_ts

    seconds_since_last_tick = max(0, int((datetime.now() - latest_tick_dt).total_seconds()))

    one_minute_window = latest_tick_ts - pd.Timedelta(minutes=1)
    ticks_last_min = int((ticks_df["log_ts"] >= one_minute_window).sum())

    last_spread = float(spread_df["spread_points"].iloc[-1]) if not spread_df.empty else None

    return {
        "feed_state": feed_state(seconds_since_last_tick, live_limit=live_limit, slow_limit=slow_limit),
        "seconds_since_last_tick": seconds_since_last_tick,
        "total_ticks": total_ticks,
        "ticks_last_min": ticks_last_min,
        "last_price": last_price,
        "price_delta": price_delta,
        "price_delta_pct": price_delta_pct,
        "last_spread": last_spread,
        "spread_quality": spread_quality(last_spread),
        "last_tick_ts": latest_tick_dt,
    }


def build_run_info(
    log_path: Path,
    all_lines_count: int,
    session_lines_count: int,
    parse_lines_count: int,
    tick_lines_count: int,
    parsed_ticks_count: int,
    latest_tick_ts: datetime | None,
) -> dict[str, str]:
    file_size_kb = 0.0
    if log_path.exists():
        file_size_kb = log_path.stat().st_size / 1024.0

    parse_ratio = 0.0
    if tick_lines_count > 0:
        parse_ratio = (parsed_ticks_count / tick_lines_count) * 100

    return {
        "Archivo": str(log_path),
        "Tamano log": f"{file_size_kb:,.1f} KB",
        "Lineas totales": f"{all_lines_count:,}",
        "Lineas sesion": f"{session_lines_count:,}",
        "Lineas parseadas": f"{parse_lines_count:,}",
        "Ticks en ventana": f"{tick_lines_count:,}",
        "Ticks parseados": f"{parsed_ticks_count:,}",
        "Parse ratio": f"{parse_ratio:.1f}%",
        "Ultimo tick": latest_tick_ts.strftime("%Y-%m-%d %H:%M:%S") if latest_tick_ts else "-",
    }
