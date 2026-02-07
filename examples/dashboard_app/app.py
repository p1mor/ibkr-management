"""Streamlit dashboard for IBKR log observability."""

from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

try:
    from .app_config import (
        DEFAULT_LOG_FILE,
        PANEL_LABELS,
        WINDOW_LABELS,
        DashboardDefaults,
        get_window_seconds,
    )
    from .metrics import build_market_summary, build_run_info, filter_by_window
    from .parsers import (
        count_log_levels,
        count_tick_lines,
        extract_alerts,
        parse_spreads,
        parse_ticks,
        read_log_lines,
        select_latest_session_lines,
        tail_line_window,
    )
    from .ui import (
        render_activity_chart,
        render_alert_table,
        render_guide,
        render_health_status,
        render_price_chart,
        render_raw_log,
        render_run_info,
        render_spread_chart,
        render_summary_metrics,
        render_tick_table,
    )
except ImportError:
    from app_config import (
        DEFAULT_LOG_FILE,
        PANEL_LABELS,
        WINDOW_LABELS,
        DashboardDefaults,
        get_window_seconds,
    )
    from metrics import build_market_summary, build_run_info, filter_by_window
    from parsers import (
        count_log_levels,
        count_tick_lines,
        extract_alerts,
        parse_spreads,
        parse_ticks,
        read_log_lines,
        select_latest_session_lines,
        tail_line_window,
    )
    from ui import (
        render_activity_chart,
        render_alert_table,
        render_guide,
        render_health_status,
        render_price_chart,
        render_raw_log,
        render_run_info,
        render_spread_chart,
        render_summary_metrics,
        render_tick_table,
    )


def _apply_refresh(auto_refresh: bool, refresh_seconds: int, refresh_now: bool) -> None:
    if refresh_now:
        st.rerun()

    if auto_refresh:
        st.caption(f"Auto refresh activo cada {refresh_seconds} segundos")
        time.sleep(refresh_seconds)
        st.rerun()

    st.caption("Auto refresh desactivado")


def main() -> None:
    st.set_page_config(page_title="IBKR Log Dashboard", layout="wide")
    st.title("IBKR Log Dashboard")
    st.caption("Panel basico y funcional para monitoreo de ticks, spread y alertas")

    defaults = DashboardDefaults()

    with st.sidebar:
        st.header("Controles")

        log_file = st.text_input("Archivo de log", value=str(DEFAULT_LOG_FILE))
        parse_line_window = st.slider(
            "Lineas a parsear",
            min_value=500,
            max_value=50_000,
            value=defaults.parse_line_window,
            step=500,
        )
        max_chart_points = st.slider(
            "Puntos max por grafica",
            min_value=100,
            max_value=5_000,
            value=defaults.max_chart_points,
            step=100,
        )

        window_key = st.selectbox(
            "Ventana de analisis",
            options=list(WINDOW_LABELS.keys()),
            format_func=lambda key: WINDOW_LABELS[key],
            index=1,
        )

        selected_panels = st.multiselect(
            "Paneles activos",
            options=list(PANEL_LABELS.keys()),
            default=list(defaults.panel_selection),
            format_func=lambda key: PANEL_LABELS[key],
        )

        raw_log_lines = st.slider(
            "Lineas en log crudo",
            min_value=20,
            max_value=600,
            value=defaults.raw_log_lines,
            step=20,
        )
        alert_limit = st.slider(
            "Alertas maximas",
            min_value=10,
            max_value=200,
            value=defaults.alert_limit,
            step=10,
        )

        auto_refresh = st.toggle("Auto refresh", value=True)
        refresh_seconds = st.slider(
            "Refrescar cada (s)",
            min_value=1,
            max_value=15,
            value=defaults.refresh_seconds,
        )
        refresh_now = st.button("Refrescar ahora")

    log_path = Path(log_file)
    all_lines = read_log_lines(log_path)

    if not all_lines:
        st.warning(f"No se encontro log en: {log_path.resolve()}")
        st.code("python examples/basic_connection.py")
        _apply_refresh(auto_refresh=auto_refresh, refresh_seconds=refresh_seconds, refresh_now=refresh_now)
        return

    session_lines, _session_start_idx = select_latest_session_lines(all_lines)
    parse_lines = tail_line_window(session_lines, parse_line_window)

    ticks_df = parse_ticks(parse_lines)
    spread_df = parse_spreads(parse_lines)
    alerts_df = extract_alerts(session_lines, limit=alert_limit)
    level_counts = count_log_levels(session_lines)

    window_seconds = get_window_seconds(window_key)
    ticks_window_df = filter_by_window(ticks_df, window_seconds)
    spread_window_df = filter_by_window(spread_df, window_seconds)

    if ticks_window_df.empty and not ticks_df.empty:
        ticks_window_df = ticks_df

    if spread_window_df.empty and not spread_df.empty:
        spread_window_df = spread_df

    latest_tick_ts = None
    if not ticks_df.empty:
        latest_ts = ticks_df["log_ts"].iloc[-1]
        latest_tick_ts = latest_ts.to_pydatetime() if hasattr(latest_ts, "to_pydatetime") else latest_ts

    run_info = build_run_info(
        log_path=log_path,
        all_lines_count=len(all_lines),
        session_lines_count=len(session_lines),
        parse_lines_count=len(parse_lines),
        tick_lines_count=count_tick_lines(parse_lines),
        parsed_ticks_count=len(ticks_df),
        latest_tick_ts=latest_tick_ts,
    )

    render_guide()

    if "run_info" in selected_panels:
        render_run_info(run_info)

    if ticks_window_df.empty:
        st.warning("No hay ticks parseables en la ventana seleccionada. Revisa run info y formato del log.")
        if not alerts_df.empty:
            latest_alert = alerts_df.iloc[-1]
            st.error(f"Ultima alerta ({latest_alert['Nivel']}): {latest_alert['Mensaje']}")
        if "alerts" in selected_panels:
            render_alert_table(alerts_df)
        if "raw_log" in selected_panels:
            render_raw_log(session_lines, raw_log_lines)
        _apply_refresh(auto_refresh=auto_refresh, refresh_seconds=refresh_seconds, refresh_now=refresh_now)
        return

    total_ticks = int(ticks_df["tick_id"].iloc[-1]) if not ticks_df.empty else 0
    summary = build_market_summary(
        ticks_df=ticks_window_df,
        spread_df=spread_window_df,
        total_ticks=total_ticks,
        live_limit=defaults.stale_live_seconds,
        slow_limit=defaults.stale_slow_seconds,
    )

    if "stats" in selected_panels:
        render_summary_metrics(summary)
        render_health_status(level_counts)

    chart_ticks = ticks_window_df.tail(max_chart_points).copy()
    chart_ticks["price_ma20"] = chart_ticks["price"].rolling(20, min_periods=1).mean()

    if "price" in selected_panels and "activity" in selected_panels:
        c1, c2 = st.columns(2)
        with c1:
            render_price_chart(chart_ticks)
        with c2:
            render_activity_chart(chart_ticks)
    elif "price" in selected_panels:
        render_price_chart(chart_ticks)
    elif "activity" in selected_panels:
        render_activity_chart(chart_ticks)

    if "spread" in selected_panels:
        render_spread_chart(spread_window_df, max_chart_points=max_chart_points)

    if "tables" in selected_panels:
        render_tick_table(chart_ticks)

    if "alerts" in selected_panels:
        render_alert_table(alerts_df)

    if "raw_log" in selected_panels:
        render_raw_log(session_lines, raw_log_lines)

    _apply_refresh(auto_refresh=auto_refresh, refresh_seconds=refresh_seconds, refresh_now=refresh_now)


if __name__ == "__main__":
    main()
