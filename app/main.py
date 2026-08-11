"""
main.py - Punto de entrada de la app Streamlit.

Orquesta sidebar, carga de datos, y delega a módulos:
  helpers, loaders, ui_components, tab_metas
"""

import io
from pathlib import Path

import streamlit as st
import pandas as pd
import html

from helpers import (
    _first_nonempty, _diff_html, _fmt_id_meta,
)
from loaders import (
    COLUMNAS_DATOS_GENERALES,
    cargar_hoja,
    cargar_proyecto_filtrado,
    cargar_beneficiarios_filtrado,
)
from ui_components import (
    inject_css, titulo_con_tooltip, resaltar_ortografia_html,
)
from tab_metas import render_tab_metas

# ========= Configuración inicial (debe ser la primera llamada a st.*) =========
st.set_page_config(layout="wide")
st.title("Revisión Programación SED")
inject_css()

# ========= SIDEBAR: CARGA Y FILTROS =========

_DEMO_DIR = Path(__file__).parent / "Demo_data"

with st.sidebar:
    # --- Botón Demo ---
    if st.session_state.get("demo_mode"):
        st.info("**Modo Demo activo**")
        if st.button("Salir de Demo"):
            st.session_state["demo_mode"] = False
            st.rerun()
    else:
        if st.button("Cargar datos Demo"):
            st.session_state["demo_mode"] = True
            st.rerun()

    with st.expander("📤 Cargar Detalle de Qs", expanded=not st.session_state.get("demo_mode")):
        archivo_antes = st.file_uploader("Archivo - Corte Antes", type=["xlsx"], key="archivo_antes")
        archivo_ahora = st.file_uploader("Archivo - Corte Ahora", type=["xlsx"], key="archivo_ahora")
    with st.expander("📥 Beneficiarios — Detalle de Qs 2", expanded=False):
        ben_antes_file = st.file_uploader(
            "Corte ANTES (Detalle de Qs 2)",
            type=["xlsx"], key="ben_antes_file",
        )
        ben_ahora_file = st.file_uploader(
            "Corte AHORA (Detalle de Qs 2)",
            type=["xlsx"], key="ben_ahora_file",
        )

# --- Inyectar archivos demo si el modo está activo ---
if st.session_state.get("demo_mode"):
    archivo_antes = io.BytesIO((_DEMO_DIR / "DetalleQ1_Antes_Demo.xlsx").read_bytes())
    archivo_ahora = io.BytesIO((_DEMO_DIR / "DetalleQ1_aHORA_Demo.xlsx").read_bytes())
    ben_antes_file = io.BytesIO((_DEMO_DIR / "DetalleQ2_Antes_Demo.xlsx").read_bytes())
    ben_ahora_file = io.BytesIO((_DEMO_DIR / "DetalleQ2_Ahora_Demo.xlsx").read_bytes())

with st.sidebar:
    st.markdown("### 🔑 Llave para comparar metas")
    llave_opcion = st.radio(
        "¿Tus reportes ya cuentan con claves estandarizadas de metas? Selecciona Clave de meta:",
        ["No, usar ID Meta", "Sí, usar Clave de Meta"],
        horizontal=True,
        key="llave_meta_opcion",
    )

# Variables de selección
eje_sel = ""
dep_sel = ""
clave_q = None
clave_q_display = ""
opciones_q = {}

if archivo_antes and archivo_ahora:
    datos_ahora_min = cargar_hoja(archivo_ahora, "Datos Generales", COLUMNAS_DATOS_GENERALES)

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔎 Filtrar proyectos")

        ejes_disponibles = sorted([e for e in datos_ahora_min["Eje"].dropna().unique().tolist() if str(e).strip() != ""])
        eje_sel = st.selectbox("Eje", [""] + ejes_disponibles, key="filtro_eje")

        if eje_sel:
            deps_filtradas = datos_ahora_min.loc[datos_ahora_min["Eje"] == eje_sel, "Dep Siglas"].dropna().unique().tolist()
        else:
            deps_filtradas = datos_ahora_min["Dep Siglas"].dropna().unique().tolist()
        deps_filtradas = sorted([d for d in deps_filtradas if str(d).strip() != ""])
        dep_sel = st.selectbox("Dependencia", [""] + deps_filtradas, key="filtro_dep")

        filtro_q_df = datos_ahora_min.copy()
        if eje_sel:
            filtro_q_df = filtro_q_df[filtro_q_df["Eje"] == eje_sel]
        if dep_sel:
            filtro_q_df = filtro_q_df[filtro_q_df["Dep Siglas"] == dep_sel]

        filtro_q_df = filtro_q_df[["Clave Q", "Nombre del Proyecto (Ejercicio Actual)"]].dropna()
        filtro_q_df["display"] = (
            filtro_q_df["Clave Q"].astype(str) + " — " +
            filtro_q_df["Nombre del Proyecto (Ejercicio Actual)"].astype(str)
        )
        filtro_q_df = filtro_q_df.sort_values("display")

        opciones_q = dict(zip(filtro_q_df["display"], filtro_q_df["Clave Q"]))
        clave_q_display = st.selectbox(
            "Clave Q",
            [""] + list(opciones_q.keys()),
            placeholder="Buscar por Clave Q o nombre...",
            key="filtro_q",
        )
        clave_q = opciones_q.get(clave_q_display)

    if not clave_q:
        st.warning("Selecciona una Clave Q específica en el panel lateral para ver los datos comparativos.")
        st.stop()

else:
    st.markdown("""
    ## 👋 Bienvenido a la app de Revisión de Programación SED

    Para comenzar, sigue estos pasos desde el panel lateral:

    1. 📂 **Carga los archivos** correspondientes a los cortes **Antes** y **Ahora** del reporte Detalle de Qs.
    2. 🧭 **Selecciona un Eje**.
    3. 🏛️ **Selecciona la Dependencia o Entidad**.
    4. 🔑 **Elige la Clave Q** del proyecto que deseas revisar.

    **¡Ahora incluye un comparativo para Beneficiarios 👥!** si lo necesitas solo carga los archivos adicionales 📑.

    Una vez cargados seleccionada una Clave Q, se mostrarán las distintas secciones comparativas para facilitar el análisis entre fechas de corte.
    """)
    st.stop()


# ========= CARGA + LIMPIEZA + FILTRO POR CLAVE Q (cacheado) =========

proy = cargar_proyecto_filtrado(archivo_antes, archivo_ahora, clave_q, llave_opcion)

META_COL = proy["META_COL"]

if not proy["meta_col_ok"]:
    st.error(f"No se encontró la columna **{META_COL}** en la hoja 'Sección de Metas-Cumplimiento'. "
             f"Cambia la opción de llave o revisa el archivo.")
    st.stop()

datos_ahora = proy["datos_ahora"]
datos_antes = proy["datos_antes"]
metas_ahora = proy["metas_ahora"]
metas_antes = proy["metas_antes"]
metas_crono_ahora = proy["crono_ahora"]
metas_crono_antes = proy["crono_antes"]
metas_partidas_ahora = proy["partidas_ahora"]
metas_partidas_antes = proy["partidas_antes"]
cumplimiento_ahora = proy["cumplimiento_ahora"]
cumplimiento_antes = proy["cumplimiento_antes"]
nombre_proyecto = proy["nombre_proyecto"]

# Beneficiarios
beneficiarios_df = cargar_beneficiarios_filtrado(ben_antes_file, ben_ahora_file, clave_q)


# ========= INFO DEL PROYECTO (MONTOS) =========

st.markdown(f"### Proyecto: {clave_q} — {nombre_proyecto}")

monto_total_antes = float(metas_antes["Monto Total"].sum()) if not metas_antes.empty else 0.0
monto_total_ahora = float(metas_ahora["Monto Total"].sum()) if not metas_ahora.empty else 0.0
diferencia_monto_total = monto_total_ahora - monto_total_antes

st.markdown("### 💰 Monto Modificado del Proyecto")
col_proy1, col_proy2 = st.columns(2)
col_proy1.metric("Monto Total (Antes)", f"${monto_total_antes:,.2f}")
col_proy2.metric(
    "Monto Total (Ahora)",
    f"${monto_total_ahora:,.2f}",
    delta=f"${diferencia_monto_total:,.2f}",
    delta_color="normal",
)

st.markdown("---")


# ========= PESTAÑAS =========

tabs = st.tabs(["📄 Datos Generales", "🎯 Metas", "👥 Beneficiarios"])

# ---------------------- TAB 1: DATOS GENERALES ----------------------
with tabs[0]:
    st.subheader("📄 Datos Generales")

    CAMPOS_TEXTO = [
        "Diagnóstico",
        "Objetivo General",
        "Descripción del Proyecto",
        "Descripción del Avance Actual",
        "Alcance Anual",
    ]

    _STY_ANTES = "border:1px solid #e5e7eb;padding:8px;word-break:break-word;background:#f9fafb"
    _STY_AHORA = "border:1px solid #e5e7eb;padding:8px;word-break:break-word"

    if datos_ahora.empty:
        st.warning("No se encontró información para esta Clave Q en el corte actual.")
    else:
        if datos_antes.empty:
            st.info("🆕 Este proyecto no existía en el corte anterior. Se muestra solo la versión actual.")

        fila_ahora = datos_ahora.iloc[0]
        fila_antes = datos_antes.iloc[0] if not datos_antes.empty else None

        # --- Resumen de cambios ---
        estados = {}
        for campo in CAMPOS_TEXTO:
            va = fila_antes.get(campo, "") if fila_antes is not None else ""
            vh = fila_ahora.get(campo, "")
            if fila_antes is None:
                estados[campo] = "nuevo"
            elif str(va) != str(vh):
                estados[campo] = "modificado"
            else:
                estados[campo] = "sin_cambios"

        n_mod = sum(1 for v in estados.values() if v == "modificado")
        n_eq = sum(1 for v in estados.values() if v == "sin_cambios")
        n_new = sum(1 for v in estados.values() if v == "nuevo")

        badges = []
        if n_mod:
            badges.append(f"<span class='badge badge--warn'>{n_mod} modificado{'s' if n_mod != 1 else ''}</span>")
        if n_eq:
            badges.append(f"<span class='badge badge--ok'>{n_eq} sin cambios</span>")
        if n_new:
            badges.append(f"<span class='badge'>{n_new} nuevo{'s' if n_new != 1 else ''}</span>")
        if badges:
            st.markdown("&nbsp;&nbsp;".join(badges), unsafe_allow_html=True)

        for campo in CAMPOS_TEXTO:
            val_a = fila_antes.get(campo, "") if fila_antes is not None else ""
            val_h = fila_ahora.get(campo, "")
            estado = estados[campo]
            ahora_spell = resaltar_ortografia_html(val_h)

            if estado == "nuevo":
                titulo_con_tooltip(campo, seccion="datos_generales")
                st.success("🆕 Nuevo")
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("Antes")
                    st.caption("— Sin datos en corte anterior —")
                with col2:
                    st.caption("Ahora")
                    st.markdown(
                        f"<div style='{_STY_AHORA}'>{ahora_spell}</div>",
                        unsafe_allow_html=True,
                    )

            elif estado == "modificado":
                titulo_con_tooltip(campo, seccion="datos_generales")
                st.info("🔄 Modificado")
                a_html, h_html = _diff_html(val_a, val_h)
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("Antes")
                    st.markdown(
                        f"<div style='{_STY_ANTES}'>{a_html}</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.caption("Ahora")
                    st.markdown(
                        f"<div style='{_STY_AHORA}'>{h_html}</div>",
                        unsafe_allow_html=True,
                    )
                with st.expander("📝 Revisión ortográfica del texto actual", expanded=False):
                    st.markdown(
                        f"<div style='border:1px dashed #fecaca;padding:6px;word-break:break-word'>{ahora_spell}</div>",
                        unsafe_allow_html=True,
                    )

            else:  # sin_cambios
                with st.expander(f"✔ {campo} — Sin cambios", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("Antes")
                        st.markdown(
                            f"<div style='{_STY_ANTES}'>{html.escape(str(val_a))}</div>",
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.caption("Ahora")
                        st.markdown(
                            f"<div style='{_STY_AHORA}'>{ahora_spell}</div>",
                            unsafe_allow_html=True,
                        )

        lineas = [
            f'Clave Q: "{clave_q}"',
            f'Nombre del Proyecto: "{nombre_proyecto}"',
        ] + [f'{c}: "{fila_ahora.get(c, "")}"' for c in CAMPOS_TEXTO]
        #with st.expander("📋 Texto estructurado para evaluación en ChatGPT"):
        #    st.code("\n".join(lineas), language="plaintext")


# ---------------------- TAB 2: METAS (delegado) ----------------------
render_tab_metas(
    tabs[1],
    metas_antes, metas_ahora,
    metas_crono_antes, metas_crono_ahora,
    metas_partidas_antes, metas_partidas_ahora,
    cumplimiento_antes, cumplimiento_ahora,
    META_COL, clave_q,
)


# ---------------------- TAB 3: BENEFICIARIOS ----------------------
with tabs[2]:
    st.subheader("👥 Beneficiarios")

    if beneficiarios_df is None or beneficiarios_df.empty:
        st.info("Carga ambos cortes de **Detalle de Qs 2** en el panel lateral y selecciona una **Clave Q** para visualizar esta sección.")
    else:
        ben_a = beneficiarios_df[beneficiarios_df["Versión"] == "Antes"].copy()
        ben_h = beneficiarios_df[beneficiarios_df["Versión"] == "Ahora"].copy()

        # Descripción del Beneficio
        st.markdown("#### 📝 Descripción del Beneficio")

        desc_a = _first_nonempty(ben_a.get("Descripción del Beneficio", pd.Series([], dtype=object))) if not ben_a.empty else ""
        desc_h = _first_nonempty(ben_h.get("Descripción del Beneficio", pd.Series([], dtype=object))) if not ben_h.empty else ""

        colA, colH = st.columns(2)
        if str(desc_a) != str(desc_h):
            st.info("🔄 Modificado")
            a_html, h_html = _diff_html(desc_a, desc_h)
            with colA:
                st.markdown("**Antes:**")
                st.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{a_html}</div>", unsafe_allow_html=True)
            with colH:
                st.markdown("**Ahora:**")
                st.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{h_html}</div>", unsafe_allow_html=True)
        else:
            st.success("✔ Sin cambios")
            with colA:
                st.markdown("**Antes:**")
                st.write(desc_a)
            with colH:
                st.markdown("**Ahora:**")
                st.write(desc_h)

        st.markdown("---")

        # Comparativo por categoría
        st.markdown("#### 📊 Comparativo por categoría")

        categorias = [
            {"etq": "Beneficiarios Directos",
             "nombre": "Nombre (Beneficiarios Directos)",
             "carac": "Caracteristicas Generales (Beneficiarios Directos)",
             "cant": "Cantidad (Beneficiarios Directos)"},
            {"etq": "Población Objetivo",
             "nombre": "Nombre (Población Objetivo)",
             "carac": "Caracteristicas Generales (Población Objetivo)",
             "cant": "Cantidad (Población Objetivo)"},
            {"etq": "Población Universo",
             "nombre": "Nombre (Población Universo)",
             "carac": "Caracteristicas Generales (Población Universo)",
             "cant": "Cantidad (Población Universo)"},
            {"etq": "Beneficiarios Indirectos",
             "nombre": "Nombre (Beneficiarios Indirectos)",
             "carac": "Caracteristicas Generales (Beneficiarios Indirectos)",
             "cant": "Cantidad (Beneficiarios Indirectos)"},
        ]

        st.markdown("""
        <style>
        .section-title { font-weight:700; font-size:1.05rem; margin: 6px 0 12px 0; display:flex; align-items:center; gap:.4rem; }
        .label { font-size: .82rem; color:#475569; margin-bottom:6px; font-weight:600; }
        .diffbox { border:1px solid #e5e7eb; border-radius:8px; padding:8px; background:#ffffff; }
        </style>
        """, unsafe_allow_html=True)

        def _texto_o_diff(txt_a: str, txt_h: str):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<span class='badge'>Antes</span>", unsafe_allow_html=True)
                if str(txt_a) != str(txt_h):
                    a_html, _ = _diff_html(txt_a, txt_h)
                    st.markdown(f"<div class='diffbox'>{a_html}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='diffbox'>{html.escape(str(txt_a or ''))}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<span class='badge'>Ahora</span>", unsafe_allow_html=True)
                if str(txt_a) != str(txt_h):
                    _, h_html = _diff_html(txt_a, txt_h)
                    st.markdown(f"<div class='diffbox'>{h_html}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='diffbox'>{html.escape(str(txt_h or ''))}</div>", unsafe_allow_html=True)

        def _render_categoria(etq: str, col_nombre: str, col_carac: str, col_cant: str, ben_a_df: pd.DataFrame, ben_h_df: pd.DataFrame):
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-title'>👥 {etq}</div>", unsafe_allow_html=True)

            nom_a = _first_nonempty(ben_a_df.get(col_nombre, pd.Series([], dtype=object))) if not ben_a_df.empty else ""
            nom_h = _first_nonempty(ben_h_df.get(col_nombre, pd.Series([], dtype=object))) if not ben_h_df.empty else ""
            st.markdown("<div class='label'>Nombre</div>", unsafe_allow_html=True)
            _texto_o_diff(nom_a, nom_h)

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            car_a = _first_nonempty(ben_a_df.get(col_carac, pd.Series([], dtype=object))) if not ben_a_df.empty else ""
            car_h = _first_nonempty(ben_h_df.get(col_carac, pd.Series([], dtype=object))) if not ben_h_df.empty else ""
            st.markdown("<div class='label'>Características</div>", unsafe_allow_html=True)
            _texto_o_diff(car_a, car_h)

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            try:
                q_a = float(pd.to_numeric(ben_a_df.get(col_cant, pd.Series([0])), errors="coerce").sum())
            except Exception:
                q_a = 0.0
            try:
                q_h = float(pd.to_numeric(ben_h_df.get(col_cant, pd.Series([0])), errors="coerce").sum())
            except Exception:
                q_h = 0.0

            k1, k2 = st.columns(2)
            with k1:
                st.markdown("<div class='kpi'><div class='caption'>Cantidad (Antes)</div><div class='value'>{:,.0f}</div></div>".format(q_a), unsafe_allow_html=True)
            with k2:
                st.markdown("<div class='kpi'><div class='caption'>Cantidad (Ahora)</div><div class='value'>{:,.0f}</div></div>".format(q_h), unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        for c in categorias:
            _render_categoria(c["etq"], c["nombre"], c["carac"], c["cant"], ben_a, ben_h)
