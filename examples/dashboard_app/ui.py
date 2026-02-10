from __future__ import annotations

import pandas as pd
import streamlit as st


def render_guide() -> None:
    with st.expander("Como leer este panel (modo simple)", expanded=True):
        st.markdown(
            "- `Precio` y `Cambio ventana`: resumen de direccion reciente.\n"
            "- `Ticks/min`: intensidad de actividad del mercado.\n"
            "- `Spread`: costo aproximado de entrar/salir rapido.\n"
            "- `Estado`: `En vivo` cuando siguen llegando ticks."
        )


def render_run_info(run_info: dict[str, str]) -> None:
    st.subheader("Run info")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tamano log", run_info["Tamano log"])
    c2.metric("Lineas sesion", run_info["Lineas sesion"])
    c3.metric("Parse ratio", run_info["Parse ratio"])
    c4.metric("Ultimo tick", run_info["Ultimo tick"])

    st.dataframe(
        pd.DataFrame([run_info]).T.rename(columns={0: "Valor"}),
        width="stretch",
    )


def render_summary_metrics(summary: dict[str, str | int | float | None]) -> None:
    if not summary:
        return

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Estado", str(summary["feed_state"]), delta=f"{summary['seconds_since_last_tick']}s sin tick")
    m2.metric("Ticks totales", f"{int(summary['total_ticks']):,}")
    m3.metric("Ticks/min", f"{int(summary['ticks_last_min'])}")
    m4.metric("Precio", f"{float(summary['last_price']):.2f}", delta=f"{float(summary['price_delta']):+.2f}")
    m5.metric("Cambio ventana", f"{float(summary['price_delta_pct']):+.3f}%")

    last_spread = summary["last_spread"]
    spread_value = "-" if last_spread is None else f"{float(last_spread):.2f}"
    m6.metric("Spread", spread_value, delta=str(summary["spread_quality"]))


def render_health_status(levels: dict[str, int]) -> None:
    if levels["error_count"] > 0:
        st.error(f"Se detectaron {levels['error_count']} errores en la sesion.")
    elif levels["warning_count"] > 0:
        st.warning(f"Se detectaron {levels['warning_count']} warnings en la sesion.")
    else:
        st.success("Sin errores ni warnings en la sesion actual.")


def render_price_chart(chart_ticks: pd.DataFrame) -> None:
    st.subheader("Precio en tiempo real")
    if chart_ticks.empty:
        st.info("Sin datos para grafica de precio.")
        return

    price_chart = chart_ticks.set_index("tick_id")[["price", "price_ma20"]]
    st.line_chart(price_chart, width="stretch")
    st.caption("`price_ma20` suaviza ruido para leer tendencia corta.")


def render_activity_chart(chart_ticks: pd.DataFrame) -> None:
    st.subheader("Actividad por segundo")
    if chart_ticks.empty:
        st.info("Sin datos para grafica de actividad.")
        return

    activity = (
        chart_ticks.assign(second=chart_ticks["log_ts"].dt.floor("s"))
        .groupby("second", as_index=False)
        .size()
        .rename(columns={"size": "ticks"})
        .tail(120)
        .set_index("second")
    )
    st.bar_chart(activity["ticks"], width="stretch")
    st.caption("Cuantos ticks llegan por segundo (pulso del mercado).")


def render_spread_chart(spread_df: pd.DataFrame, max_chart_points: int) -> None:
    st.subheader("Spread (puntos)")
    if spread_df.empty:
        st.info("No hay eventos de spread en la ventana seleccionada.")
        return

    spread_chart = spread_df.tail(max_chart_points).set_index("log_ts")[["spread_points"]]
    st.line_chart(spread_chart, width="stretch")


def render_tick_table(chart_ticks: pd.DataFrame) -> None:
    st.subheader("Ultimos ticks")
    if chart_ticks.empty:
        st.info("Sin ticks para mostrar.")
        return

    display_ticks = chart_ticks.tail(25).sort_values("tick_id", ascending=False).copy()
    display_ticks = display_ticks[["tick_id", "event_time", "price", "size", "exchange"]]
    display_ticks.columns = ["Tick", "Hora", "Precio", "Cantidad", "Exchange"]
    st.dataframe(display_ticks, width="stretch", hide_index=True)


def render_alert_table(alerts_df: pd.DataFrame) -> None:
    st.subheader("Alertas recientes")
    if alerts_df.empty:
        st.info("Sin warnings/errors recientes.")
        return

    st.dataframe(alerts_df.sort_values("Timestamp", ascending=False), width="stretch", hide_index=True)


def render_raw_log(lines: list[str], tail_lines: int) -> None:
    st.subheader("Log reciente (crudo)")
    tail_content = "\n".join(lines[-tail_lines:])
    st.code(tail_content if tail_content else "Log vacio", language="text")
