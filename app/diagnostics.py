"""
diagnostics.py - Timer de rendimiento + panel debug.

Cadena de dependencias: independiente (solo usa streamlit + pandas)
"""

import time
from contextlib import contextmanager

import streamlit as st
import pandas as pd


# --- Estado para logs de rendimiento ---
def _init_perf_state():
    if "_perf_logs" not in st.session_state:
        st.session_state["_perf_logs"] = []
    if "_perf_on" not in st.session_state:
        st.session_state["_perf_on"] = False


@contextmanager
def perf_timer(etiqueta: str):
    """Context manager para medir tiempos. Úsalo alrededor de bloques pesados."""
    _init_perf_state()
    t0 = time.perf_counter()
    try:
        yield
    finally:
        t1 = time.perf_counter()
        if st.session_state.get("_perf_on", False):
            st.session_state["_perf_logs"].append((etiqueta, t1 - t0))


def df_stats(df: pd.DataFrame) -> dict:
    if df is None:
        return {"filas": 0, "columnas": 0, "mem_mb": 0.0}
    try:
        mem = df.memory_usage(deep=True).sum() / 1e6
    except Exception:
        mem = 0.0
    return {"filas": len(df), "columnas": len(df.columns), "mem_mb": mem}


def render_diagnostics_sidebar():
    """Panel de control en sidebar: toggle de perf, limpiar caché, borrar logs."""
    _init_perf_state()
    with st.sidebar:
        with st.expander("🧪 Diagnóstico & rendimiento", expanded=False):
            st.session_state["_perf_on"] = st.toggle(
                "Activar logging de rendimiento",
                value=st.session_state["_perf_on"],
            )
            if st.button("🧹 Limpiar caché de datos"):
                st.cache_data.clear()
                st.success("Caché de datos limpiada.")
            if st.button("🗑️ Borrar logs de rendimiento"):
                st.session_state["_perf_logs"].clear()
                st.success("Logs de rendimiento borrados.")


def render_diagnostics_summary(dataframes_dict: dict[str, pd.DataFrame]):
    """Resumen técnico de dataframes + logs de rendimiento."""
    _init_perf_state()

    with st.expander("📊 Resumen técnico de dataframes (filtrados por Clave Q)"):
        resumen = []
        for nombre, df in dataframes_dict.items():
            info = df_stats(df)
            resumen.append((nombre, info["filas"], info["columnas"], round(info["mem_mb"], 3)))

        df_resumen = pd.DataFrame(
            resumen,
            columns=["DataFrame", "Filas", "Columnas", "Memoria (MB)"],
        )
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)

    if st.session_state["_perf_logs"]:
        with st.expander("⏱️ Logs de rendimiento (secciones instrumentadas)"):
            df_logs = pd.DataFrame(
                st.session_state["_perf_logs"], columns=["Sección", "Segundos"]
            )
            df_logs["Segundos"] = df_logs["Segundos"].map(lambda x: round(x, 4))
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            st.caption(
                "Sugerencia: rodea bloques costosos con `with perf_timer('nombre_de_bloque'):` para registrarlos aquí."
            )
