"""
live_dashboard.py - Dashboard interactivo para logs de IBKR

Visualiza en tiempo real los ticks y eventos generados por:
    python examples/basic_connection.py

Uso:
    streamlit run examples/live_dashboard.py
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


DEFAULT_LOG_FILE = Path("ib_gateway_audit.log")

TICK_PATTERN = re.compile(
    r"(?P<local_time>\d{2}:\d{2}:\d{2}).*Tick #\s*(?P<tick_id>\d+)\s*\|"
    r"\s*(?P<event_time>\d{2}:\d{2}:\d{2})\s*\|\s*Precio:\s*(?P<price>\d+(?:\.\d+)?)\s*\|"
    r"\s*Cantidad:\s*(?P<size>\d+(?:\.\d+)?)\s*\|\s*Exchange:\s*(?P<exchange>\S+)"
)

SPREAD_PATTERN = re.compile(
    r"MID PRICE:\s*(?P<mid>\d+(?:\.\d+)?)\s*\|\s*SPREAD:\s*(?P<spread>\d+(?:\.\d+)?)\s*puntos"
)

ALERT_PATTERN = re.compile(
    r"(?P<local_time>\d{2}:\d{2}:\d{2}).*\[(?P<level>WARNING|ERROR)\s*]\s*(?P<message>.*)"
)


def _time_to_seconds(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M:%S")
    return parsed.hour * 3600 + parsed.minute * 60 + parsed.second


def _read_log_lines(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return log_path.read_text(encoding="utf-8", errors="ignore").splitlines()


def _parse_ticks(lines: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for line in lines:
        match = TICK_PATTERN.search(line)
        if not match:
            continue
        rows.append(
            {
                "local_time": match.group("local_time"),
                "event_time": match.group("event_time"),
                "tick_id": int(match.group("tick_id")),
                "price": float(match.group("price")),
                "size": float(match.group("size")),
                "exchange": match.group("exchange"),
                "local_seconds": _time_to_seconds(match.group("local_time")),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=["local_time", "event_time", "tick_id", "price", "size", "exchange", "local_seconds"]
        )
    return pd.DataFrame(rows)


def _parse_spreads(lines: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for line in lines:
        match = SPREAD_PATTERN.search(line)
        if not match:
            continue
        rows.append(
            {
                "mid_price": float(match.group("mid")),
                "spread_points": float(match.group("spread")),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["mid_price", "spread_points"])
    return pd.DataFrame(rows)


def _count_log_levels(lines: list[str]) -> dict[str, int]:
    return {
        "error_count": sum("[ERROR" in line for line in lines),
        "warning_count": sum("[WARNING" in line for line in lines),
        "info_count": sum("[INFO" in line for line in lines),
    }


def _extract_alerts(lines: list[str], limit: int = 50) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for line in lines:
        match = ALERT_PATTERN.search(line)
        if not match:
            continue
        rows.append(
            {
                "Hora": match.group("local_time"),
                "Nivel": match.group("level"),
                "Mensaje": match.group("message"),
            }
        )

    if not rows:
        return pd.DataFrame(columns=["Hora", "Nivel", "Mensaje"])
    return pd.DataFrame(rows).tail(limit)


def _spread_quality(spread_points: float | None) -> str:
    if spread_points is None:
        return "Sin dato"
    if spread_points <= 0.50:
        return "Estrecho (mejor)"
    if spread_points <= 2.0:
        return "Normal"
    return "Amplio (cuidado)"


def main() -> None:
    st.set_page_config(page_title="IBKR Log Dashboard", layout="wide")
    st.title("IBKR Log Dashboard")
    st.caption("Panel simple para leer en vivo precio, actividad y riesgo basico")

    with st.sidebar:
        st.header("Controles")
        log_file = st.text_input("Archivo de log", value=str(DEFAULT_LOG_FILE))
        max_chart_points = st.slider("Ticks en grafica", min_value=100, max_value=3000, value=500, step=100)
        tail_lines = st.slider("Lineas de log", min_value=20, max_value=400, value=120, step=20)
        show_raw_log = st.toggle("Mostrar log crudo", value=False)
        auto_refresh = st.toggle("Auto refresh", value=True)
        refresh_seconds = st.slider("Refrescar cada (s)", min_value=1, max_value=15, value=2)
        refresh_now = st.button("Refrescar ahora")

    log_path = Path(log_file)
    lines = _read_log_lines(log_path)
    ticks_df = _parse_ticks(lines)
    spread_df = _parse_spreads(lines)
    levels = _count_log_levels(lines)

    if not lines:
        st.warning(f"No se encontro log en: {log_path.resolve()}")
        st.code("python examples/basic_connection.py")
        st.stop()

    with st.expander("Como leer este panel (modo simple)", expanded=True):
        st.markdown(
            "- `Precio` y `Cambio ventana`: dicen si el mercado sube o baja en el tramo reciente.\n"
            "- `Ticks/min`: actividad del mercado (mas alto = mas movimiento).\n"
            "- `Spread`: costo aproximado de entrar/salir rapido (mas bajo = mejor).\n"
            "- `Estado`: `En vivo` significa que siguen entrando ticks."
        )

    if ticks_df.empty:
        st.warning("No hay ticks parseables aun. Espera unos segundos.")
        if show_raw_log:
            st.subheader("Log reciente")
            tail_content = "\n".join(lines[-tail_lines:])
            st.code(tail_content if tail_content else "Log vacio", language="text")
        st.stop()

    chart_ticks = ticks_df.tail(max_chart_points).copy()
    chart_ticks["price_ma20"] = chart_ticks["price"].rolling(20, min_periods=1).mean()

    last_price = chart_ticks["price"].iloc[-1]
    first_price = chart_ticks["price"].iloc[0]
    price_delta = last_price - first_price
    price_delta_pct = (price_delta / first_price) * 100 if first_price else 0.0
    last_size = chart_ticks["size"].iloc[-1]
    total_ticks = int(ticks_df["tick_id"].iloc[-1])

    last_spread = spread_df["spread_points"].iloc[-1] if not spread_df.empty else None
    spread_quality = _spread_quality(last_spread)

    now = datetime.now()
    now_seconds = now.hour * 3600 + now.minute * 60 + now.second
    last_tick_seconds = int(chart_ticks["local_seconds"].iloc[-1])
    seconds_since_last_tick = now_seconds - last_tick_seconds
    if seconds_since_last_tick < 0:
        seconds_since_last_tick += 24 * 3600

    if seconds_since_last_tick <= 5:
        feed_state = "En vivo"
    elif seconds_since_last_tick <= 20:
        feed_state = "Lento"
    else:
        feed_state = "Pausado"

    ticks_last_min = int((ticks_df["local_seconds"] >= max(0, last_tick_seconds - 60)).sum())
    alerts_df = _extract_alerts(lines)
    alert_count = len(alerts_df)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Estado", feed_state, delta=f"{seconds_since_last_tick}s sin tick")
    m2.metric("Ticks totales", f"{total_ticks:,}")
    m3.metric("Ticks/min", f"{ticks_last_min}")
    m4.metric("Precio", f"{last_price:.2f}", delta=f"{price_delta:+.2f}")
    m5.metric("Cambio ventana", f"{price_delta_pct:+.3f}%")
    m6.metric("Spread", f"{last_spread:.2f}" if last_spread is not None else "-", delta=spread_quality)

    if levels["error_count"] > 0:
        st.error(f"Se detectaron {levels['error_count']} errores en el log.")
    elif levels["warning_count"] > 0:
        st.warning(f"Se detectaron {levels['warning_count']} warnings en el log.")
    else:
        st.success("Sin errores ni warnings en el log actual.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Precio en tiempo real")
        price_chart = chart_ticks.set_index("tick_id")[["price", "price_ma20"]]
        st.line_chart(price_chart, use_container_width=True)
        st.caption("`price_ma20` suaviza ruido para leer tendencia corta.")

    with c2:
        st.subheader("Actividad por segundo")
        activity = (
            chart_ticks.groupby("local_time", as_index=False)
            .size()
            .rename(columns={"size": "ticks"})
            .tail(120)
            .set_index("local_time")
        )
        st.bar_chart(activity["ticks"], use_container_width=True)
        st.caption("Cuantos ticks llegan por segundo (pulso del mercado).")

    if not spread_df.empty:
        st.subheader("Spread (puntos)")
        st.line_chart(spread_df.tail(max_chart_points)["spread_points"], use_container_width=True)

    t1, t2 = st.columns(2)
    with t1:
        st.subheader("Ultimos ticks")
        display_ticks = chart_ticks.tail(25).sort_values("tick_id", ascending=False).copy()
        display_ticks = display_ticks[["tick_id", "event_time", "price", "size", "exchange"]]
        display_ticks.columns = ["Tick", "Hora", "Precio", "Cantidad", "Exchange"]
        st.dataframe(display_ticks, use_container_width=True, hide_index=True)
    with t2:
        st.subheader("Alertas recientes")
        if alerts_df.empty:
            st.info("Sin warnings/errors recientes.")
        else:
            st.dataframe(alerts_df.sort_values("Hora", ascending=False), use_container_width=True, hide_index=True)

    if show_raw_log:
        st.subheader("Log reciente (crudo)")
        tail_content = "\n".join(lines[-tail_lines:])
        st.code(tail_content if tail_content else "Log vacio", language="text")

    if refresh_now:
        st.rerun()

    if auto_refresh:
        st.caption(f"Auto refresh activo cada {refresh_seconds} segundos")
        time.sleep(refresh_seconds)
        st.rerun()
    else:
        st.caption("Auto refresh desactivado")


if __name__ == "__main__":
    main()
