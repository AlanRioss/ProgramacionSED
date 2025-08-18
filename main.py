# ========= BLOQUE 1 · CONFIGURACIÓN INICIAL + HELPERS =========

import streamlit as st
import pandas as pd
import plotly.express as px
import difflib
import unicodedata
import html
import json
import folium
from streamlit_folium import st_folium

from manual_extractos import MANUAL  # ← se mantiene

# Config general
st.set_page_config(layout="wide")
st.title("Revisión Programación SED")

# ====== Mapeos (se mantienen los nombres usados en el resto del código) ======
CAMPO_KEY = {
    "Diagnóstico": "diagnostico",
    "Objetivo General": "objetivo_general",
    "Descripción del Proyecto": "descripcion_proyecto",
    "Descripción del Avance Actual": "avance_actual",
    "Alcance Anual": "alcance_anual",
}
CAMPO_KEY_METAS = {
    "Información de la Meta": "descripcion_meta",
    "Distribución Territorial": "distribucion_territorial",
    "Cronograma": "cronograma",
    "Partidas": "partidas_gasto",
    "Cumplimiento": "cumplimiento",
}

# ========= CSS consolidado (se elimina duplicado de tooltips) =========
st.markdown("""
<style>
:root{
  --brand:#b20d30; --brand-600:#990b29; --brand-50:#f8e9ed;
  --ink:#222; --muted:#6b7280; --surface:#fafafa;
  --ok:#10b981; --warn:#f59e0b; --bad:#ef4444;
}
html, body, [class*="block-container"]{ font-variant-ligatures:none; }
h1, h2, h3, h4, h5, h6{ color:var(--ink); letter-spacing:.2px; }
h2, .stMarkdown h2{ font-size:1.6rem; border-left:4px solid var(--brand); padding-left:.6rem; }
h3, .stMarkdown h3{ font-size:1.25rem; color:var(--brand-600); margin-top:1.2rem; }
h4, .stMarkdown h4{ font-size:1.05rem; font-weight:700; margin:.8rem 0 .4rem; }
h5, .stMarkdown h5{ font-size:.95rem; color:var(--muted); text-transform:uppercase; letter-spacing:.6px; }

.section-sub{ display:flex; align-items:center; gap:.5rem; margin:.75rem 0 .5rem; }
.section-sub:after{ content:""; flex:1; height:1px; background:linear-gradient(90deg, var(--brand-50), transparent); }

hr{ border:none; height:1px; background:linear-gradient(90deg,#e5e7eb,transparent); margin:1.2rem 0; }
.block-gap{ margin-top:1.2rem; }

.card{ background:var(--surface); border:1px solid #e5e7eb; border-radius:10px; padding:.9rem 1rem; box-shadow:0 1px 0 rgba(0,0,0,.02); }
.card--ok{ border-color:rgba(16,185,129,.25); background:rgba(16,185,129,.06); }
.card--warn{ border-color:rgba(245,158,11,.25); background:rgba(245,158,11,.07); }
.card--bad{ border-color:rgba(239,68,68,.25); background:rgba(239,68,68,.07); }
.kpi{ font-weight:700; font-size:1.25rem; }
.kpi .sub{ display:block; font-weight:500; color:var(--muted); font-size:.85rem; }

.stTabs [data-baseweb="tab-list"]{ gap:.25rem; border-bottom:1px solid #eee; }
.stTabs [data-baseweb="tab"]{ border:1px solid #eee; border-bottom:none; background:#fafafa; color:#374151;
  padding:.45rem .8rem; border-top-left-radius:8px; border-top-right-radius:8px; }
.stTabs [aria-selected="true"]{ background:white; color:var(--brand-600); border-color:#e5e7eb; box-shadow:0 -2px 0 0 var(--brand) inset; }

.dg-help{ display:inline-flex; align-items:center; gap:6px; }
.tooltip{ position:relative; display:inline-block; cursor:help; user-select:none; line-height:1; }
.tooltip .tooltip-btn{ border:1px solid #ddd; border-radius:50%; width:18px; height:18px;
  display:inline-flex; align-items:center; justify-content:center; font-size:12px; background:#f6f6f6; color:#333; }
.tooltip .tip-box{ visibility:hidden; opacity:0; transition:opacity .15s ease; position:absolute; z-index:1000; left:1.2rem; top:1.4rem;
  max-width:70vw; min-width:300px; white-space:normal; word-break:break-word; text-align:left;
  background:#111; color:#fff; padding:8px 10px; border-radius:6px; font-size:12px; line-height:1.3; box-shadow:0 6px 16px rgba(0,0,0,.25); }
.tooltip:hover .tip-box, .tooltip:focus-within .tip-box{ visibility:visible; opacity:1; }
.tooltip .tip-arrow{ position:absolute; top:-6px; left:8px; width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-bottom:6px solid #111; }
.tooltip .tip-title{ font-weight:600; margin-bottom:4px; }
.tooltip .tip-meta{ opacity:.8; font-size:11px; margin-top:6px; }

.streamlit-expanderHeader{ font-weight:700; color:var(--brand-600); }
.streamlit-expanderContent{ background:#fff; border-left:3px solid var(--brand-50); padding-left:.75rem; }

.stButton>button{ border-radius:8px; border:1px solid #e5e7eb; padding:.5rem .9rem; background:#fff; color:#111; transition:.15s ease; }
.stButton>button:hover{ border-color:var(--brand-600); box-shadow:0 1px 6px rgba(0,0,0,.06); }
.stButton>button:focus{ outline:3px solid var(--brand-50); }

.stTextInput>div>div>input, .stSelectbox>div>div>div{ border-radius:8px !important; }
.stRadio>div{ gap:1rem; }

.dataframe tbody tr:nth-child(odd){ background:#fcfcfc; }
.dataframe td, .dataframe th{ padding:.45rem .6rem !important; }
.dataframe th{ position:sticky; top:0; background:#f7f7f7; z-index:1; }
.num-right{ text-align:right !important; font-variant-numeric:tabular-nums; }

.badge{ display:inline-block; padding:.12rem .45rem; border-radius:999px; font-size:.75rem; font-weight:600;
  background:#eef2ff; color:#3730a3; border:1px solid #e0e7ff; }
.badge--ok{ background:#ecfdf5; color:#065f46; border-color:#d1fae5; }
.badge--warn{ background:#fffbeb; color:#92400e; border-color:#fde68a; }
.badge--bad{ background:#fef2f2; color:#991b1b; border-color:#fecaca; }

.note{ display:flex; gap:.5rem; align-items:flex-start; background:#fff; border-left:3px solid var(--brand);
  padding:.5rem .75rem; border-radius:6px; color:#374151; font-size:.92rem; }
.note i{ opacity:.9; }

.js-plotly-plot .plotly{ direction:ltr; }

.compact-list p{ margin:.15rem 0 !important; }
.chip{ display:inline-flex; align-items:center; gap:6px; padding:2px 6px; border-radius:10px; background:#f0f2f6; font-size:12px; line-height:1; }
.chip--lock{ background:#fdecea; color:#b71c1c; }
</style>
""", unsafe_allow_html=True)

# ========= Funciones de UI (tooltips) =========
def titulo_con_tooltip(titulo: str, seccion: str, manual_key: str | None = None):
    """Renderiza un título con ícono de ayuda tomando extractos del MANUAL."""
    if manual_key is None:
        if seccion == "datos_generales":
            clave_manual = CAMPO_KEY.get(titulo)
        elif seccion == "metas":
            clave_manual = CAMPO_KEY_METAS.get(titulo)
        else:
            clave_manual = None
    else:
        clave_manual = manual_key

    texto_ayuda = MANUAL.get(seccion, {}).get(clave_manual or "", "")
    if not texto_ayuda:
        st.markdown(f"**{titulo}**")
        return

    tip_text = html.escape(texto_ayuda)
    st.markdown(
        f"""<div class="dg-help">
               <strong>{html.escape(titulo)}</strong>
               <span class="tooltip" tabindex="0" aria-label="Ayuda de {html.escape(titulo)}">
                 <span class="tooltip-btn">?</span>
                 <span class="tip-box" role="note">
                   <div class="tip-arrow"></div>
                   <div class="tip-title">Criterios del manual</div>
                   <div>{tip_text}</div>
                   <div class="tip-meta">Manual · Extracto breve</div>
                 </span>
               </span>
             </div>""",
        unsafe_allow_html=True
    )

def header_with_tooltip_distribucion():
    """Encabezado 'Comparativo por Municipio' con tooltip de Distribución Territorial."""
    texto = MANUAL.get("metas", {}).get("distribucion_territorial", "")
    tip = html.escape(texto)
    st.markdown(
        f"""
        <div class="dg-help">
          <h5 style="margin:0">Comparativo por Municipio</h5>
          <span class="tooltip" tabindex="0" aria-label="Ayuda: Distribución Territorial">
            <span class="tooltip-btn">?</span>
            <span class="tip-box" role="note">
              <div class="tip-arrow"></div>
              <div class="tip-title">Distribución Territorial</div>
              <div>{tip}</div>
              <div class="tip-meta">Manual · Extracto breve</div>
            </span>
          </span>
        </div>
        """,
        unsafe_allow_html=True
    )

def _fmt_id_meta(x):
    """Formatea ID Meta para etiquetas amigables (sin .0 si viene como float)."""
    if pd.isna(x):
        return ""
    try:
        nx = pd.to_numeric(x, errors="coerce")
        if pd.notna(nx):
            if float(nx).is_integer():
                return str(int(nx))
            return str(nx)
    except Exception:
        pass
    return str(x)

def header_with_tooltip_meta(id_meta):
    """Encabezado 'Meta (ID): ...' con tooltip de 'Descripción de la Meta'."""
    texto = MANUAL.get("metas", {}).get("descripcion_meta", "")
    tip = html.escape(texto)
    st.markdown(
        f"""
        <div class="dg-help">
          <h4 style="margin:0">Meta (ID): {_fmt_id_meta(id_meta)}</h4>
          <span class="tooltip" tabindex="0" aria-label="Ayuda: Descripción de la Meta">
            <span class="tooltip-btn">?</span>
            <span class="tip-box" role="note">
              <div class="tip-arrow"></div>
              <div class="tip-title">Descripción de la Meta</div>
              <div>{tip}</div>
              <div class="tip-meta">Manual · Extracto breve</div>
            </span>
          </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ========= Helpers de datos (cacheados) =========
def _limpiar_texto(x: str) -> str:
    if isinstance(x, str):
        x = unicodedata.normalize("NFKC", x)
        x = x.replace("\n", " ").replace("\r", " ").strip()
    return x

@st.cache_data(show_spinner=False)
def cargar_hoja(archivo, hoja: str, columnas: list[str]) -> pd.DataFrame:
    """Lee una hoja con header en fila 8 (índice 7) y devuelve solo columnas solicitadas."""
    df = pd.read_excel(archivo, sheet_name=hoja, header=7)
    return df[df.columns.intersection(columnas)]

@st.cache_data(show_spinner=False)
def cargar_cronograma(archivo) -> pd.DataFrame:
    """Lee cronograma con conversión de fechas."""
    columnas = [
        "Clave Q", "Dep Siglas", "ID Meta", "Clave de Meta", "Clave de Actividad /Hito", "Tipo",
        "Fase Actividad / Hito", "Descripción", "Fecha de Inicio", "Fecha de Termino",
        "Monto Actividad / Hito"
    ]
    df = pd.read_excel(archivo, sheet_name="Sección de Metas-Cronograma", header=7)
    df = df[df.columns.intersection(columnas)].copy()
    if "Fecha de Inicio" in df.columns:
        df["Fecha de Inicio"] = pd.to_datetime(df["Fecha de Inicio"], dayfirst=True, errors="coerce")
    if "Fecha de Termino" in df.columns:
        df["Fecha de Termino"] = pd.to_datetime(df["Fecha de Termino"], dayfirst=True, errors="coerce")
    return df

@st.cache_data(show_spinner=False)
def agregar_totales(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas 'Cantidad Total' y 'Monto Total' sumando por-prefijo."""
    out = df.copy()
    out["Cantidad Total"] = out.filter(like="Cantidad").sum(axis=1, skipna=True)
    out["Monto Total"] = out.filter(like="Monto").sum(axis=1, skipna=True)
    return out

from pathlib import Path

@st.cache_data(show_spinner=False)
def cargar_geometria_municipal(geojson_path: str | Path = "gtoSHP/mun_test_wgs.geojson") -> dict:
    """
    Carga el GeoJSON de municipios (EPSG:4326) desde rutas relativas seguras.
    Devuelve el dict ya parseado.
    """
    base = Path(__file__).parent
    candidates = [
        base / geojson_path,
        Path.cwd() / geojson_path,
        base.parent / geojson_path,
    ]
    for p in candidates:
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(
        f"No encontré {geojson_path}. Sube gtoSHP/mun_test_wgs.geojson al repo."
    )

def _geojson_bounds(geojson: dict) -> tuple[float, float, float, float]:
    """
    Calcula (minx, miny, maxx, maxy) recorriendo coordenadas del GeoJSON.
    Soporta Polygon/MultiPolygon.
    """
    import math
    minx = miny = math.inf
    maxx = maxy = -math.inf

    def _walk(coords):
        nonlocal minx, miny, maxx, maxy
        if isinstance(coords[0], (float, int)):  # [x, y]
            x, y = coords[:2]
            minx = min(minx, x); miny = min(miny, y)
            maxx = max(maxx, x); maxy = max(maxy, y)
        else:
            for c in coords:
                _walk(c)

    for feat in geojson.get("features", []):
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates")
        if coords:
            _walk(coords)

    if not all(map(math.isfinite, [minx, miny, maxx, maxy])):
        # Fallback genérico
        return (-103.0, 18.0, -96.0, 23.0)
    return (minx, miny, maxx, maxy)

# ========= FIN BLOQUE 1 =========
# ========= BLOQUE 2 · SIDEBAR: CARGA Y FILTROS (Eje → Dependencia → Clave Q) =========

with st.sidebar:
    st.title("⚙️ Configuración")

    # --- Carga de archivos ---
    with st.expander("📂 Cargar archivos de Excel", expanded=True):
        archivo_antes = st.file_uploader("Archivo - Corte Antes", type=["xlsx"], key="archivo_antes")
        archivo_ahora = st.file_uploader("Archivo - Corte Ahora", type=["xlsx"], key="archivo_ahora")

# Columnas mínimas para poblar filtros
COLUMNAS_DATOS_GENERALES = [
    "Fecha", "Clave Q", "Nombre del Proyecto (Ejercicio Actual)", "Eje", "Dep Siglas",
    "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
    "Descripción del Avance Actual", "Alcance Anual"
]

# Variables de selección (se usarán en bloques siguientes)
eje_sel = ""
dep_sel = ""
clave_q = None
clave_q_display = ""
opciones_q = {}

if archivo_antes and archivo_ahora:
    # Carga mínima para filtros (solo del corte "Ahora")
    datos_ahora_min = cargar_hoja(archivo_ahora, "Datos Generales", COLUMNAS_DATOS_GENERALES)

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔎 Filtrar proyectos")

        # ----- Filtro Eje -----
        ejes_disponibles = sorted([e for e in datos_ahora_min["Eje"].dropna().unique().tolist() if str(e).strip() != ""])
        eje_sel = st.selectbox("Eje", [""] + ejes_disponibles, key="filtro_eje")

        # ----- Filtro Dependencia (condicionado por Eje) -----
        if eje_sel:
            deps_filtradas = datos_ahora_min.loc[datos_ahora_min["Eje"] == eje_sel, "Dep Siglas"].dropna().unique().tolist()
        else:
            deps_filtradas = datos_ahora_min["Dep Siglas"].dropna().unique().tolist()
        deps_filtradas = sorted([d for d in deps_filtradas if str(d).strip() != ""])
        dep_sel = st.selectbox("Dependencia", [""] + deps_filtradas, key="filtro_dep")

        # ----- Lista de proyectos (Clave Q + nombre) -----
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
            key="filtro_q"
        )
        clave_q = opciones_q.get(clave_q_display)

    # Si no hay Clave Q seleccionada, detenemos render hasta que elija una
    if not clave_q:
        st.warning("Selecciona una Clave Q específica en el panel lateral para ver los datos comparativos.")
        st.stop()

else:
    # Mensaje inicial si no se han cargado ambos archivos
    st.markdown("""
    ## 👋 Bienvenido a la app de Revisión de Programación SED

    Para comenzar, sigue estos pasos desde el panel lateral:

    1. 📂 **Carga los archivos** correspondientes a los cortes **Antes** y **Ahora**.
    2. 🧭 **Selecciona un Eje**.
    3. 🏛️ **Selecciona la Dependencia o Entidad**.
    4. 🔑 **Elige la Clave Q** del proyecto que deseas revisar.

    Una vez seleccionada una Clave Q, se mostrarán las distintas secciones comparativas para facilitar el análisis entre fechas de corte.
    """)
    st.stop()

# ========= FIN BLOQUE 2 =========
# ========= BLOQUE 3 · CARGA DE HOJAS + LIMPIEZA + TOTALES + FILTRO POR CLAVE Q =========

META_COL = "ID Meta"  # Llave operativa de metas

# ---- 3.1 Cargar Datos Generales (ambos cortes) ----
COLUMNAS_DATOS_GENERALES = [
    "Fecha", "Clave Q", "Nombre del Proyecto (Ejercicio Actual)", "Eje", "Dep Siglas",
    "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
    "Descripción del Avance Actual", "Alcance Anual"
]
datos_ahora = cargar_hoja(archivo_ahora, "Datos Generales", COLUMNAS_DATOS_GENERALES)
datos_antes = cargar_hoja(archivo_antes, "Datos Generales", COLUMNAS_DATOS_GENERALES)

# ---- 3.2 Limpieza de texto (una sola pasada por columna) ----
COLUMNAS_TEXTO = [
    "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
    "Descripción del Avance Actual", "Alcance Anual"
]
for col in COLUMNAS_TEXTO:
    if col in datos_ahora.columns:
        datos_ahora[col] = datos_ahora[col].astype(str).map(_limpiar_texto)
    if col in datos_antes.columns:
        datos_antes[col] = datos_antes[col].astype(str).map(_limpiar_texto)

# ---- 3.3 Filtrar todo por Clave Q seleccionada ----
datos_ahora = datos_ahora[datos_ahora["Clave Q"] == clave_q]
datos_antes = datos_antes[datos_antes["Clave Q"] == clave_q]

# ---- 3.4 Cargar METAS (ambos cortes) y agregar totales ----
COLUMNAS_METAS = [
    "Clave Q", "ID Meta", "Clave de Meta", "Descripción de la Meta", "Unidad de Medida",
    "ID Mpio", "Municipio", "Registro Presupuestal",
    "Cantidad Estatal", "Monto Estatal",
    "Cantidad Federal", "Monto Federal",
    "Cantidad Municipal", "Monto Municipal",
    "Cantidad Ingresos Propios", "Monto Ingresos Propios",
    "Cantidad Otros", "Monto Otros"
]
metas_ahora = agregar_totales(cargar_hoja(archivo_ahora, "Sección de Metas", COLUMNAS_METAS))
metas_antes = agregar_totales(cargar_hoja(archivo_antes, "Sección de Metas", COLUMNAS_METAS))

metas_ahora = metas_ahora[metas_ahora["Clave Q"] == clave_q]
metas_antes = metas_antes[metas_antes["Clave Q"] == clave_q]

# ---- 3.5 Cargar CRONOGRAMA (ambos cortes) ----
metas_crono_ahora = cargar_cronograma(archivo_ahora)
metas_crono_antes = cargar_cronograma(archivo_antes)
metas_crono_ahora = metas_crono_ahora[metas_crono_ahora["Clave Q"] == clave_q]
metas_crono_antes = metas_crono_antes[metas_crono_antes["Clave Q"] == clave_q]

# ---- 3.6 Cargar PARTIDAS (ambos cortes) ----
COLUMNAS_PARTIDAS = [
    "Clave Q", "ID Meta", "Clave de Meta", "Partida", "Monto Anual",
    "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
    "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
    "Monto Octubre", "Monto Noviembre", "Monto Diciembre"
]
metas_partidas_ahora = cargar_hoja(archivo_ahora, "Sección de Metas-Partidas", COLUMNAS_PARTIDAS)
metas_partidas_antes = cargar_hoja(archivo_antes, "Sección de Metas-Partidas", COLUMNAS_PARTIDAS)
metas_partidas_ahora = metas_partidas_ahora[metas_partidas_ahora["Clave Q"] == clave_q]
metas_partidas_antes = metas_partidas_antes[metas_partidas_antes["Clave Q"] == clave_q]

# ---- 3.7 Cargar CUMPLIMIENTO (ambos cortes) con fallback suave a 'Clave de Meta' ----
#      Nota: Pedimos también "Clave de Meta" en columnas por si la hoja aún no migra a ID Meta.
COLUMNAS_CUMPLIMIENTO = (
    [META_COL, "Clave de Meta", "Cantidad"] +
    [f"Cumplimiento {mes}" for mes in [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]]
)

cumplimiento_ahora = cargar_hoja(archivo_ahora, "Sección de Metas-Cumplimiento", COLUMNAS_CUMPLIMIENTO).copy()
cumplimiento_antes = cargar_hoja(archivo_antes, "Sección de Metas-Cumplimiento", COLUMNAS_CUMPLIMIENTO).copy()

# Fallback: si no hay ID Meta pero sí Clave de Meta, renombrar
if META_COL not in cumplimiento_ahora.columns and "Clave de Meta" in cumplimiento_ahora.columns:
    cumplimiento_ahora.rename(columns={"Clave de Meta": META_COL}, inplace=True)
if META_COL not in cumplimiento_antes.columns and "Clave de Meta" in cumplimiento_antes.columns:
    cumplimiento_antes.rename(columns={"Clave de Meta": META_COL}, inplace=True)

# Limpieza: eliminar filas sin ID Meta
cumplimiento_ahora = cumplimiento_ahora.dropna(subset=[META_COL])
cumplimiento_antes = cumplimiento_antes.dropna(subset=[META_COL])

# (Opcional) Nombre del proyecto para encabezados posteriores
nombre_proyecto_vals = datos_ahora["Nombre del Proyecto (Ejercicio Actual)"].values
nombre_proyecto = nombre_proyecto_vals[0] if len(nombre_proyecto_vals) else ""

# ========= FIN BLOQUE 3 =========
# ========= BLOQUE 4 · INFO DEL PROYECTO (MONTOS) =========

# Encabezado con Clave Q y nombre del proyecto
st.markdown(f"### Proyecto: {clave_q} — {nombre_proyecto}")

# Monto total del proyecto (suma de 'Monto Total' en Sección de Metas)
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
    delta_color="normal"
)

st.markdown("---")
# ========= FIN BLOQUE 4 =========
# ========= BLOQUE 5 · PESTAÑAS (procesamiento bajo demanda) =========

from catalogo_partidas import CATALOGO_PARTIDAS  # usado en subpestaña Partidas

tabs = st.tabs(["📄 Datos Generales", "🎯 Metas"])

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

    def _diff_html(a: str, b: str) -> tuple[str, str]:
        """Resalta diferencias (Antes vs Ahora) con difflib; evita trabajo si son iguales."""
        a = html.escape(str(a or ""))
        b = html.escape(str(b or ""))
        if a == b:
            return a, b
        matcher = difflib.SequenceMatcher(None, a, b)
        res_a, res_b = "", ""
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                res_a += a[i1:i2]; res_b += b[j1:j2]
            elif tag == "replace":
                res_a += f"<del style='color:#b91c1c'>{a[i1:i2]}</del>"
                res_b += f"<span style='background-color:#dcfce7'>{b[j1:j2]}</span>"
            elif tag == "delete":
                res_a += f"<del style='color:#b91c1c'>{a[i1:i2]}</del>"
            elif tag == "insert":
                res_b += f"<span style='background-color:#dcfce7'>{b[j1:j2]}</span>"
        return res_a, res_b

    if datos_antes.empty or datos_ahora.empty:
        st.warning("No se encontró información para esta Clave Q.")
    else:
        fila_antes = datos_antes.iloc[0]
        fila_ahora = datos_ahora.iloc[0]

        for campo in CAMPOS_TEXTO:
            titulo_con_tooltip(campo, seccion="datos_generales")
            val_a = fila_antes.get(campo, "")
            val_h = fila_ahora.get(campo, "")
            col1, col2 = st.columns(2)

            if str(val_a) != str(val_h):
                st.info("🔄 Modificado")
                a_html, h_html = _diff_html(val_a, val_h)
                with col1:
                    st.markdown("Antes:")
                    st.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{a_html}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("Ahora:")
                    st.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{h_html}</div>", unsafe_allow_html=True)
            else:
                st.success("✔ Sin cambios")
                with col1:
                    st.markdown("Antes:")
                    st.write(val_a)
                with col2:
                    st.markdown("Ahora:")
                    st.write(val_h)

        # Texto estructurado para copiar
        lineas = [
            f'Clave Q: "{clave_q}"',
            f'Nombre del Proyecto: "{nombre_proyecto}"',
        ] + [f'{c}: "{fila_ahora.get(c, "")}"' for c in CAMPOS_TEXTO]
        with st.expander("📋 Texto estructurado para evaluación en ChatGPT"):
            st.code("\n".join(lineas), language="plaintext")


# ---------------------- TAB 2: METAS (con subpestañas) ----------------------
with tabs[1]:
    st.subheader("🎯 Metas")
    # --------- Selección de Meta por ID ---------
    if metas_ahora.empty:
        st.info("No hay datos de metas para esta Clave Q.")
        st.stop()

    metas_disponibles = (
        metas_ahora[[META_COL, "Descripción de la Meta"]]
        .dropna(subset=[META_COL])
        .drop_duplicates()
        .copy()
    )
    metas_disponibles["Etiqueta"] = metas_disponibles[META_COL].apply(_fmt_id_meta) + " - " + metas_disponibles["Descripción de la Meta"].astype(str)
    metas_disponibles = metas_disponibles.sort_values("Etiqueta")

    id_meta_label = st.selectbox(
        "Selecciona una Meta (ID)",
        [""] + metas_disponibles["Etiqueta"].tolist(),
        key="filtro_meta"
    )
    id_meta_sel = id_meta_label.split(" - ")[0] if id_meta_label else None

    # Subpestañas
    subtabs = st.tabs([
        "📋 Información de la Meta",
        "📆 Cronograma y 💰 Partidas",
        "✅ Cumplimiento"
    ])

    # ================== SUBTAB 1: Información de la Meta ==================
    with subtabs[0]:
        if not id_meta_sel:
            st.info("Selecciona una Meta (ID) para ver la información comparativa.")
        else:
            header_with_tooltip_meta(id_meta_sel)

            @st.cache_data(show_spinner=False)
            def _info_meta(df_antes: pd.DataFrame, df_ahora: pd.DataFrame, id_meta_str: str):
                # Filtrar dataframes por meta
                f_ahora = df_ahora[df_ahora[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)]
                f_antes = df_antes[df_antes[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)]
                return (f_antes.copy(), f_ahora.copy())

            df_antes_meta, df_ahora_meta = _info_meta(metas_antes, metas_ahora, id_meta_sel)

            # --- Comparativos cualitativos (Descripción / Unidad de Medida)
            col1, col2 = st.columns(2)

            def _comparar_texto(label: str, a: str, h: str):
                if str(a) == str(h):
                    col1.markdown(f"**{label} (Antes)**"); col1.write(a)
                    col2.markdown(f"**{label} (Ahora)**"); col2.write(h)
                    st.success(f"✔ {label}: sin cambios")
                else:
                    antes_html, ahora_html = _diff_html(a, h)
                    col1.markdown(f"**{label} (Antes)**")
                    col1.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{antes_html}</div>", unsafe_allow_html=True)
                    col2.markdown(f"**{label} (Ahora)**")
                    col2.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{ahora_html}</div>", unsafe_allow_html=True)
                    st.info(f"🔄 {label}: modificado")

            desc_a = df_antes_meta["Descripción de la Meta"].iloc[0] if "Descripción de la Meta" in df_antes_meta.columns and not df_antes_meta.empty else ""
            desc_h = df_ahora_meta["Descripción de la Meta"].iloc[0] if "Descripción de la Meta" in df_ahora_meta.columns and not df_ahora_meta.empty else ""
            _comparar_texto("Descripción de la Meta", desc_a, desc_h)

            um_a = df_antes_meta["Unidad de Medida"].iloc[0] if "Unidad de Medida" in df_antes_meta.columns and not df_antes_meta.empty else ""
            um_h = df_ahora_meta["Unidad de Medida"].iloc[0] if "Unidad de Medida" in df_ahora_meta.columns and not df_ahora_meta.empty else ""
            _comparar_texto("Unidad de Medida", um_a, um_h)

            # --- Métricas generales (Cantidad Total / Monto Total)
            total_antes_cantidad = float(df_antes_meta["Cantidad Total"].sum()) if not df_antes_meta.empty else 0.0
            total_ahora_cantidad = float(df_ahora_meta["Cantidad Total"].sum()) if not df_ahora_meta.empty else 0.0
            total_antes_monto = float(df_antes_meta["Monto Total"].sum()) if not df_antes_meta.empty else 0.0
            total_ahora_monto = float(df_ahora_meta["Monto Total"].sum()) if not df_ahora_meta.empty else 0.0

            dif_cant = total_ahora_cantidad - total_antes_cantidad
            dif_monto = total_ahora_monto - total_antes_monto

            col_total1, col_total2 = st.columns(2)
            col_total1.metric("Cantidad Total (Ahora)", f"{total_ahora_cantidad:,.2f}", delta=f"{dif_cant:,.2f}")
            col_total2.metric("Monto Total (Ahora)", f"${total_ahora_monto:,.2f}", delta=f"${dif_monto:,.2f}")

            st.markdown("---")
            header_with_tooltip_distribucion()

            # --- Comparativo por Municipio (con filtro por Registro Presupuestal)
            registros = pd.concat([
                df_antes_meta.get("Registro Presupuestal", pd.Series(dtype=object)),
                df_ahora_meta.get("Registro Presupuestal", pd.Series(dtype=object)),
            ], ignore_index=True).dropna().unique().tolist()

            orden_pref = ["Centralizado", "Descentralizado", "Sin Registro"]
            opciones_radio = ["Todos"] + [r for r in orden_pref if r in registros]
            registro_opcion = st.radio(
                "Filtrar por Registro Presupuestal:",
                opciones_radio,
                horizontal=True,
                key=f"radio_registro_{_fmt_id_meta(id_meta_sel)}"
            ) if opciones_radio else "Todos"

            @st.cache_data(show_spinner=False)
            def _resumen_municipal(df_a: pd.DataFrame, df_h: pd.DataFrame, filtro_reg: str) -> pd.DataFrame:
                usar_cols = []
                for base in ["Estatal", "Federal", "Municipal"]:
                    for pref in ["Cantidad", "Monto"]:
                        c = f"{pref} {base}"
                        if (c in df_a.columns) or (c in df_h.columns):
                            usar_cols.append(c)

                if filtro_reg != "Todos":
                    df_a = df_a[df_a.get("Registro Presupuestal", "") == filtro_reg]
                    df_h = df_h[df_h.get("Registro Presupuestal", "") == filtro_reg]

                # Agrupar por Municipio y sumar
                res_a = df_a.groupby("Municipio")[usar_cols].sum(min_count=1).reset_index() if not df_a.empty else pd.DataFrame(columns=["Municipio"] + usar_cols)
                res_h = df_h.groupby("Municipio")[usar_cols].sum(min_count=1).reset_index() if not df_h.empty else pd.DataFrame(columns=["Municipio"] + usar_cols)

                res_a = res_a.rename(columns={c: f"{c} (Antes)" for c in usar_cols})
                res_h = res_h.rename(columns={c: f"{c} (Ahora)" for c in usar_cols})
                comp = pd.merge(res_a, res_h, on="Municipio", how="outer").fillna(0)

                # Reordenar columnas por pares
                orden_cols = ["Municipio"]
                for base in ["Estatal", "Federal", "Municipal"]:
                    for pref in ["Cantidad", "Monto"]:
                        a, h = f"{pref} {base} (Antes)", f"{pref} {base} (Ahora)"
                        if a in comp.columns: orden_cols.append(a)
                        if h in comp.columns: orden_cols.append(h)
                return comp[orden_cols]

            df_comp_mpio = _resumen_municipal(df_antes_meta.copy(), df_ahora_meta.copy(), registro_opcion)

            def _resaltar_cambios(row):
                pares = []
                for base in ["Estatal", "Federal", "Municipal"]:
                    for pref in ["Cantidad", "Monto"]:
                        a, h = f"{pref} {base} (Antes)", f"{pref} {base} (Ahora)"
                        if a in row.index and h in row.index:
                            pares.append((a, h))
                hay = any(abs(row[a] - row[h]) > 0 for a, h in pares if pd.notna(row[a]) and pd.notna(row[h]))
                return [""] + (["background-color:#fff7e6"] * (len(row) - 1) if hay else [""] * (len(row) - 1))

            formato = {c: "${:,.2f}" for c in df_comp_mpio.columns if c.startswith("Monto ")}
            formato.update({c: "{:,.2f}" for c in df_comp_mpio.columns if c.startswith("Cantidad ")})

            st.dataframe(df_comp_mpio.style.apply(_resaltar_cambios, axis=1).format(formato), use_container_width=True)

            # --- Mapa municipal usando GeoJSON (robusto ante ausencia de campo de nombre) ---
            with st.expander("🗺️ Mapa municipal (En Desarrollo)", expanded=False):
                col_opts1, col_opts2 = st.columns([1, 1])
                with col_opts1:
                    zoom_start = st.slider("Zoom inicial", 6, 12, 8, 1, key=f"zoom_{_fmt_id_meta(id_meta_sel)}")
                with col_opts2:
                    mapa_height = st.slider("Alto del mapa (px)", 360, 800, 520, 40, key=f"height_{_fmt_id_meta(id_meta_sel)}")
            
                geojson_data = cargar_geometria_municipal("gtoSHP/mun_test_wgs.geojson")
                minx, miny, maxx, maxy = _geojson_bounds(geojson_data)
                center_lat = (miny + maxy) / 2
                center_lon = (minx + maxx) / 2
            
                # Detectar el campo de nombre en las properties del primer feature
                name_candidates = ["NOMGEO", "NOM_MUN", "MUNICIPIO", "NOMBRE", "name"]
                example_props = (geojson_data.get("features") or [{}])[0].get("properties") or {}
            
                # 1) intenta alguno de los candidatos conocidos (que sea escalar legible)
                name_col = next(
                    (c for c in name_candidates if c in example_props and isinstance(example_props[c], (str, int, float))),
                    None
                )
                # 2) si no hay, toma el primer campo escalar que encuentres
                if not name_col:
                    for k, v in example_props.items():
                        if isinstance(v, (str, int, float)):
                            name_col = k
                            break
            
                m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles="CartoDB positron")
            
                # Construir tooltip SOLO si hay un campo válido
                tooltip = folium.GeoJsonTooltip(
                    fields=[name_col],
                    aliases=["Municipio:"]
                ) if name_col else None
            
                folium.GeoJson(
                    geojson_data,
                    tooltip=tooltip,  # None si no hay name_col -> Folium lo ignora y no rompe
                    style_function=lambda f: {"color": "#555", "weight": 1, "fillColor": "#2b8cbe", "fillOpacity": 0.25},
                    highlight_function=lambda f: {"weight": 2, "fillOpacity": 0.45}
                ).add_to(m)
            
                # Enfocar a la extensión real
                m.fit_bounds([[miny, minx], [maxy, maxx]])
            
                st_folium(m, use_container_width=True, height=mapa_height)



# ================== SUBTAB 2: Cronograma y Partidas ==================
with subtabs[1]:
    if not id_meta_sel:
        st.info("Selecciona una Meta (ID) para ver Cronograma y Partidas.")
    else:
        # ---------- Cronograma (función única, cacheada) ----------
        @st.cache_data(show_spinner=False)
        def _cronograma_df(cr_a: pd.DataFrame, cr_h: pd.DataFrame, id_meta_str: str) -> pd.DataFrame:
            a = cr_a[cr_a[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()
            h = cr_h[cr_h[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()
            if a.empty and h.empty:
                return pd.DataFrame()
            a["Versión"] = "Antes"
            h["Versión"] = "Ahora"
            out = pd.concat([a, h], ignore_index=True)
            out["Clave Num"] = pd.to_numeric(out["Clave de Actividad /Hito"], errors="coerce")

            # Si inicio==fin, alarga 1 día para que sea visible
            mismo_dia = (out["Fecha de Inicio"] == out["Fecha de Termino"])
            out.loc[mismo_dia, "Fecha de Termino"] = out.loc[mismo_dia, "Fecha de Termino"] + pd.Timedelta(days=1)
            return out

        df_crono = _cronograma_df(metas_crono_antes, metas_crono_ahora, id_meta_sel)
        st.markdown("##### Detalle de Actividades / Hitos (Cronograma Actual)")

        if df_crono.empty:
            st.info("No se encontraron actividades o hitos para esta meta en ninguna de las versiones.")
        else:
            # === Tabla "Ahora" (vista rápida)
            columnas_tabla = [
                "Clave de Actividad /Hito", "Fase Actividad / Hito", "Descripción",
                "Fecha de Inicio", "Fecha de Termino", "Monto Actividad / Hito"
            ]
            tabla_actual = df_crono[df_crono["Versión"] == "Ahora"][columnas_tabla].sort_values("Clave de Actividad /Hito").copy()
            if "Monto Actividad / Hito" in tabla_actual.columns:
                tabla_actual["Monto Actividad / Hito"] = tabla_actual["Monto Actividad / Hito"].apply(
                    lambda x: f"${x:,.2f}" if pd.notna(x) else ""
                )
            for fecha_col in ["Fecha de Inicio", "Fecha de Termino"]:
                if fecha_col in tabla_actual.columns:
                    tabla_actual[fecha_col] = pd.to_datetime(tabla_actual[fecha_col], errors="coerce").dt.strftime("%d/%m/%Y")
            st.dataframe(tabla_actual, use_container_width=True)

            # === 1) Etiquetas truncadas + tooltip completo
            MAX_LABEL_CHARS = 60  # ajusta si quieres más/menos compacto

            def _shorten(s: str, n: int) -> str:
                if not isinstance(s, str):
                    return ""
                s = s.strip()
                if len(s) <= n:
                    return s
                corte = s[:n].rsplit(" ", 1)[0]
                if len(corte) < int(0.6 * n):  # si quedó muy corto, corta duro
                    corte = s[:n]
                return corte + "…"

            # Formateador compacto de monto (K/M/B)
            def _humanize_currency(x):
                if pd.isna(x):
                    return "—"
                try:
                    v = float(x)
                except Exception:
                    return "—"
                a = abs(v)
                if a >= 1_000_000_000:
                    return f"${v/1_000_000_000:.2f}B"
                elif a >= 1_000_000:
                    return f"${v/1_000_000:.2f}M"
                elif a >= 1_000:
                    return f"${v/1_000:.0f}K"
                return f"${v:,.0f}"

            df_crono = df_crono.copy()
            df_crono["DescCorta"] = df_crono["Descripción"].astype(str).map(lambda s: _shorten(s, MAX_LABEL_CHARS))
            df_crono["EtiquetaY"] = (
                df_crono["Clave de Actividad /Hito"].astype(str) + " - " +
                df_crono["DescCorta"] + " (" + df_crono["Versión"] + ")"
            )
            # Texto completo para tooltip
            df_crono["Actividad_full"] = (
                df_crono["Clave de Actividad /Hito"].astype(str) + " - " +
                df_crono["Descripción"].astype(str) + " (" + df_crono["Versión"] + ")"
            )

            # Monto completo (tooltip) y compacto (etiqueta en barra)
            df_crono["Monto_full"] = df_crono.get("Monto Actividad / Hito", pd.Series([None]*len(df_crono))).map(
                lambda x: f"${x:,.2f}" if pd.notna(x) else "—"
            )
            df_crono["Monto_compact"] = df_crono.get("Monto Actividad / Hito", pd.Series([None]*len(df_crono))).map(_humanize_currency)

            # Duración (para decidir si ocultar etiqueta en barras cortas)
            df_crono["DuracionDias"] = (df_crono["Fecha de Termino"] - df_crono["Fecha de Inicio"]).dt.days

            # === Opciones de etiquetas de monto en barras ===
            with st.expander("💬 Opciones de etiquetas de monto", expanded=False):
                use_compact_amount = st.toggle(
                    "Usar formato compacto (K/M/B) en las barras",
                    value=True,
                    help="Muestra 1.2K / 3.4M / 2.1B en la barra; el monto completo se conserva en el tooltip."
                )
                show_only_now = st.toggle(
                    "Mostrar montos solo para 'Ahora'",
                    value=True,
                    help="Reduce el ruido visual mostrando montos solo en la versión 'Ahora'."
                )
                hide_on_short_bars = st.toggle(
                    "Ocultar etiquetas en barras muy cortas",
                    value=True,
                    help="Evita sobreposición de textos ocultando etiquetas cuando la barra es demasiado corta."
                )
                min_days_short = st.slider(
                    "Umbral de días para considerar 'corta'",
                    1, 30, 3, 1,
                    help="Si la duración (Fin-Inicio) es menor a este umbral, se oculta la etiqueta.",
                    disabled=not hide_on_short_bars
                )

            def _pick_label(row):
                if hide_on_short_bars and row["DuracionDias"] < min_days_short:
                    return ""
                if show_only_now and row.get("Versión") != "Ahora":
                    return ""
                return row["Monto_compact"] if use_compact_amount else row["Monto_full"]

            df_crono["MontoLabel"] = df_crono.apply(_pick_label, axis=1)

            # === Filtro: mostrar solo actividades con monto ≠ 0 (para el gráfico)
            with st.expander("🔎 Filtros del Cronograma", expanded=True):
                only_nonzero_amounts = st.toggle(
                    "Mostrar solo actividades/hitos con monto distinto de cero",
                    value=False,
                    help="Oculta barras con monto 0 o sin monto."
                )

            df_crono["Monto_val"] = pd.to_numeric(
                df_crono.get("Monto Actividad / Hito", pd.Series([None]*len(df_crono))),
                errors="coerce"
            ).fillna(0.0)

            df_crono_plot = df_crono
            if only_nonzero_amounts:
                df_crono_plot = df_crono[df_crono["Monto_val"].abs() > 0].copy()
                if df_crono_plot.empty:
                    st.info("No hay actividades/hitos con monto distinto de cero bajo el criterio actual.")

            # Orden del eje Y por clave numérica (sobre dataset a graficar)
            orden_y = df_crono_plot.sort_values("Clave Num")["EtiquetaY"].tolist()

            # === Altura dinámica según número de filas (más filas -> más alto)
            filas = df_crono_plot["EtiquetaY"].nunique()
            ALTURA_BASE = 420
            ALTURA_POR_FILA = 26
            altura = max(ALTURA_BASE, ALTURA_POR_FILA * filas + 140)

            # ---------- Gráfico Gantt ----------
            fig = px.timeline(
                df_crono_plot,
                x_start="Fecha de Inicio",
                x_end="Fecha de Termino",
                y="EtiquetaY",
                color="Versión",
                text="MontoLabel",
                color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"},
                title=f"Cronograma de Actividades / Hitos - Meta (ID) {_fmt_id_meta(id_meta_sel)}",
                custom_data=["Actividad_full", "Monto_full"]
            )

            # Tooltip con descripción completa + monto completo
            fig.update_traces(
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Inicio: %{x|%d/%m/%Y}<br>"
                    "Fin: %{x_end|%d/%m/%Y}<br>"
                    "Monto: %{customdata[1]}<extra></extra>"
                ),
                texttemplate="%{text}",
                textposition="inside",
                insidetextanchor="middle",
                textfont_size=11,
                textfont_color="white",
                cliponaxis=False
            )

            fig.update_yaxes(
                categoryorder="array",
                categoryarray=orden_y,
                autorange="reversed",
                ticklabelposition="outside left",
                automargin=True
            )

            fig.update_layout(
                height=altura,
                margin=dict(l=180, r=20, t=60, b=40)
            )

            st.plotly_chart(fig, use_container_width=True)



            # ---------- Partidas ----------
            @st.cache_data(show_spinner=False)
            def _partidas_resumen(pa: pd.DataFrame, ph: pd.DataFrame, id_meta_str: str):
                meses_cols = [
                    "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
                    "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
                    "Monto Octubre", "Monto Noviembre", "Monto Diciembre"
                ]
                a = pa[pa[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()
                h = ph[ph[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()

                # Partida a 4 dígitos
                for dfp in (a, h):
                    if "Partida" in dfp.columns:
                        dfp["Partida_fmt"] = dfp["Partida"].apply(lambda x: str(int(float(x)))[:4] if pd.notnull(x) else None)
                a = a[a["Partida_fmt"].notna()]
                h = h[h["Partida_fmt"].notna()]

                res_h = h.groupby("Partida_fmt")["Monto Anual"].sum().reset_index().rename(columns={"Monto Anual": "Monto Anual (Ahora)"})
                res_a = a.groupby("Partida_fmt")["Monto Anual"].sum().reset_index().rename(columns={"Monto Anual": "Monto Anual (Antes)"})
                comp = pd.merge(res_a, res_h, on="Partida_fmt", how="outer").fillna(0)
                comp["Diferencia"] = comp["Monto Anual (Ahora)"] - comp["Monto Anual (Antes)"]

                # Sumas mensuales (para gráfica)
                sum_m_ahora = h[meses_cols].sum(numeric_only=True)
                sum_m_antes = a[meses_cols].sum(numeric_only=True)
                df_mensual = pd.DataFrame({
                    "Mes": [m.replace("Monto ", "") for m in meses_cols],
                    "Antes": sum_m_antes.values,
                    "Ahora": sum_m_ahora.values
                })
                return comp, df_mensual, a, h

            df_comp_part, df_mensual, dfp_a, dfp_h = _partidas_resumen(metas_partidas_antes, metas_partidas_ahora, id_meta_sel)

            st.markdown("##### Comparativo de Montos por Partida")

            # Distribución mensual (selector rápido)
            partidas_disponibles = sorted(df_comp_part["Partida_fmt"].astype(str).unique().tolist())
            partida_sel = st.radio("Selecciona una partida para ver distribución mensual", ["Todas"] + partidas_disponibles, horizontal=True)

            if partida_sel == "Todas":
                df_mes_a = dfp_a
                df_mes_h = dfp_h
            else:
                df_mes_a = dfp_a[dfp_a["Partida_fmt"] == partida_sel]
                df_mes_h = dfp_h[dfp_h["Partida_fmt"] == partida_sel]

            meses_cols = [
                "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
                "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
                "Monto Octubre", "Monto Noviembre", "Monto Diciembre"
            ]
            sum_m_ahora = df_mes_h[meses_cols].sum(numeric_only=True)
            sum_m_antes = df_mes_a[meses_cols].sum(numeric_only=True)
           
            # --- Distribución mensual (tabla con etiquetas + barras con labels) ---
            meses_cols = [
                "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
                "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
                "Monto Octubre", "Monto Noviembre", "Monto Diciembre"
            ]

            sum_m_ahora = df_mes_h[meses_cols].sum(numeric_only=True)
            sum_m_antes = df_mes_a[meses_cols].sum(numeric_only=True)

            df_mensual_sel = pd.DataFrame({
                "Mes": [m.replace("Monto ", "") for m in meses_cols],
                "Antes": sum_m_antes.values,
                "Ahora": sum_m_ahora.values
            })

            # ===== Tabla mensual con etiquetas de montos =====
            df_tab = df_mensual_sel.copy()
            df_tab["Δ"] = df_tab["Ahora"] - df_tab["Antes"]

            def _bg_delta(v):
                if pd.isna(v): 
                    return ""
                return "background-color:#fff3cd" if abs(v) > 0 else ""

            styled_tab = (
                df_tab.style
                .format({"Antes": "${:,.2f}", "Ahora": "${:,.2f}", "Δ": "${:,.2f}"})
                .applymap(_bg_delta, subset=["Δ"])
            )



            # ===== Gráfico mensual con etiquetas SOLO en "Ahora" (K/M/B y sin ceros) =====

            def _humanize_kmb(x):
                if pd.isna(x):
                    return ""
                try:
                    v = float(x)
                except Exception:
                    return ""
                if v == 0:
                    return ""
                a = abs(v)
                if a >= 1_000_000_000:
                    return f"${v/1_000_000_000:.2f}B"
                elif a >= 1_000_000:
                    return f"${v/1_000_000:.2f}M"
                elif a >= 1_000:
                    return f"${v/1_000:.0f}K"
                return f"${v:,.0f}"

            # Etiquetas solo para la serie "Ahora"; para "Antes" se deja sin texto
            labels_ahora = [_humanize_kmb(v) for v in df_mensual_sel["Ahora"].values]

            fig_mes = px.bar(
                df_mensual_sel,
                x="Mes",
                y=["Antes", "Ahora"],
                barmode="group",
                title=f"Distribución Mensual de Montos - Meta (ID) {_fmt_id_meta(id_meta_sel)}",
                labels={"value": "Monto", "variable": "Versión"},
                color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"}
            )

            # Asignar texto SOLO al trace "Ahora" y dejar vacío el de "Antes"
            def _apply_text_to_ahora(trace):
                if trace.name == "Ahora":
                    trace.update(text=labels_ahora, texttemplate="%{text}", textposition="outside", textfont_size=11)
                else:
                    trace.update(text=None)

            fig_mes.for_each_trace(_apply_text_to_ahora)

            fig_mes.update_layout(
                height=480,
                uniformtext_minsize=10,
                uniformtext_mode="hide"  # oculta textos si no caben
            )

            st.plotly_chart(fig_mes, use_container_width=True)

           
           # st.dataframe(styled_df, use_container_width=True)

            st.markdown("##### Tabla mensual (Antes vs Ahora)")
            st.dataframe(styled_tab, use_container_width=True, hide_index=True)

            # Catálogo de partidas (filtrado por las visibles en 'Ahora')
            partidas_visibles = (
                dfp_h.get("Partida_fmt", pd.Series([], dtype=object))
                .dropna().astype(str).str[:4].drop_duplicates().sort_values().tolist()
            )
            cat_meta = CATALOGO_PARTIDAS[CATALOGO_PARTIDAS["Partida_fmt"].isin(partidas_visibles)].copy()
            faltantes = sorted(set(partidas_visibles) - set(cat_meta["Partida_fmt"]))
            if faltantes:
                st.info("Partidas sin entrada en catálogo: " + ", ".join(faltantes))

            with st.expander("📖 Catálogo de partidas (según Meta filtrada)"):
                q = st.text_input("Filtrar por código, definición o validador", key=f"filtro_catalogo_{_fmt_id_meta(id_meta_sel)}").strip().lower()
                df_show = cat_meta
                if q:
                    df_show = df_show[
                        df_show.apply(lambda r: q in f"{r['Partida_fmt']} {r['Definición']} {r['Validador']}".lower(), axis=1)
                    ]

                vista_tabla = st.toggle("Ver como tabla compacta", value=False, key=f"vista_tabla_{_fmt_id_meta(id_meta_sel)}")
                if df_show.empty:
                    st.markdown("_Sin coincidencias._")
                else:
                    if vista_tabla:
                        df_tabla = df_show.rename(columns={"Partida_fmt":"Código", "Definición":"Definición", "Restringida":"Restringida", "Validador":"Validador"})[["Código","Definición","Restringida","Validador"]]
                        st.dataframe(
                            df_tabla, use_container_width=True, hide_index=True,
                            column_config={
                                "Código": st.column_config.TextColumn(width="small"),
                                "Definición": st.column_config.TextColumn(width="large"),
                                "Restringida": st.column_config.CheckboxColumn("🔒", help="Requiere validador", disabled=True, width="small"),
                                "Validador": st.column_config.TextColumn(width="small"),
                            }
                        )
                    else:
                        st.markdown('<div class="compact-list">', unsafe_allow_html=True)
                        for _, r in df_show.iterrows():
                            lock = ""
                            if bool(r["Restringida"]):
                                val = r["Validador"] or "N/A"
                                lock = f' <span class="chip chip--lock">🔒 {val}</span>'
                            st.markdown(f"**{r['Partida_fmt']}** · {r['Definición']}{lock}", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

    # ================== SUBTAB 3: Cumplimiento ==================
    with subtabs[2]:
        if not id_meta_sel:
            st.info("Selecciona una Meta (ID) para ver el Cumplimiento.")
        else:
            @st.cache_data(show_spinner=False)
            def _cumplimiento_df(ca: pd.DataFrame, ch: pd.DataFrame, id_meta_str: str):
                a = ca[ca[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()
                h = ch[ch[META_COL].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()
                return a, h

            df_cump_a, df_cump_h = _cumplimiento_df(cumplimiento_antes, cumplimiento_ahora, id_meta_sel)

            cantidad_ahora = float(df_cump_h["Cantidad"].iloc[0]) if (not df_cump_h.empty and "Cantidad" in df_cump_h.columns and pd.notna(df_cump_h["Cantidad"].iloc[0])) else None
            cantidad_antes = float(df_cump_a["Cantidad"].iloc[0]) if (not df_cump_a.empty and "Cantidad" in df_cump_a.columns and pd.notna(df_cump_a["Cantidad"].iloc[0])) else None

            col1, col2 = st.columns(2)
            col1.metric("Cantidad Programada (Ahora)", f"{cantidad_ahora:.2f}" if cantidad_ahora is not None else "—")
            col2.metric("Cantidad Programada (Antes)", f"{cantidad_antes:.2f}" if cantidad_antes is not None else "—")

            meses = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            cols_mensuales = [f"Cumplimiento {m}" for m in meses]

            valores_ahora = (df_cump_h.iloc[0][cols_mensuales].fillna(0).values if (not df_cump_h.empty and all(c in df_cump_h.columns for c in cols_mensuales)) else [0]*12)
            valores_antes = (df_cump_a.iloc[0][cols_mensuales].fillna(0).values if (not df_cump_a.empty and all(c in df_cump_a.columns for c in cols_mensuales)) else [0]*12)

            df_cumplimiento = pd.DataFrame({
                "Mes": meses * 2,
                "Valor": list(valores_antes) + list(valores_ahora),
                "Versión": ["Antes"] * 12 + ["Ahora"] * 12
            })
            fig_cump = px.bar(
                df_cumplimiento, x="Mes", y="Valor", color="Versión", barmode="group",
                color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"},
                title=f"Cumplimiento Programado por Mes - Meta (ID) {_fmt_id_meta(id_meta_sel)}"
            )
            fig_cump.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_cump, use_container_width=True)

# ========= FIN BLOQUE 5 =========
# ========= BLOQUE 6 · DIAGNÓSTICO, LOGGING Y MANTENIMIENTO =========
import time
from contextlib import contextmanager

# --- Estado para logs de rendimiento ---
if "_perf_logs" not in st.session_state:
    st.session_state["_perf_logs"] = []
if "_perf_on" not in st.session_state:
    st.session_state["_perf_on"] = False

# --- Utilidades de rendimiento/diagnóstico ---
@contextmanager
def perf_timer(etiqueta: str):
    """Context manager para medir tiempos. Úsalo alrededor de bloques pesados."""
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

# --- Panel de control en sidebar ---
#with st.sidebar:
#    with st.expander("🧪 Diagnóstico & rendimiento", expanded=False):
#        st.session_state["_perf_on"] = st.toggle("Activar logging de rendimiento", value=st.session_state["_perf_on"])
#        if st.button("🧹 Limpiar caché de datos"):
#            st.cache_data.clear()
#            st.success("Caché de datos limpiada.")
#        if st.button("🗑️ Borrar logs de rendimiento"):
#            st.session_state["_perf_logs"].clear()
#            st.success("Logs de rendimiento borrados.")

# --- Resumen rápido de dataframes filtrados por Clave Q ---
with st.expander("📊 Resumen técnico de dataframes (filtrados por Clave Q)"):
    resumen = []
    resumen.append(("datos_antes",    df_stats(datos_antes)))
    resumen.append(("datos_ahora",    df_stats(datos_ahora)))
    resumen.append(("metas_antes",    df_stats(metas_antes)))
    resumen.append(("metas_ahora",    df_stats(metas_ahora)))
    resumen.append(("metas_crono_antes", df_stats(metas_crono_antes)))
    resumen.append(("metas_crono_ahora", df_stats(metas_crono_ahora)))
    resumen.append(("metas_partidas_antes", df_stats(metas_partidas_antes)))
    resumen.append(("metas_partidas_ahora", df_stats(metas_partidas_ahora)))
    resumen.append(("cumplimiento_antes", df_stats(cumplimiento_antes)))
    resumen.append(("cumplimiento_ahora", df_stats(cumplimiento_ahora)))

    df_resumen = pd.DataFrame(
        [(nombre, info["filas"], info["columnas"], round(info["mem_mb"], 3)) for nombre, info in resumen],
        columns=["DataFrame", "Filas", "Columnas", "Memoria (MB)"]
    )
#    st.dataframe(df_resumen, use_container_width=True, hide_index=True)

# --- Visualizar logs de rendimiento, si existen ---
if st.session_state["_perf_logs"]:
    with st.expander("⏱️ Logs de rendimiento (secciones instrumentadas)"):
        df_logs = pd.DataFrame(st.session_state["_perf_logs"], columns=["Sección", "Segundos"])
        df_logs["Segundos"] = df_logs["Segundos"].map(lambda x: round(x, 4))
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
        st.caption("Sugerencia: rodea bloques costosos con `with perf_timer('nombre_de_bloque'):` para registrarlos aquí.")

# === Ejemplo de uso de perf_timer (opcional): ===
# with perf_timer("cálculo_municipal"):
#     df_comp_mpio = _resumen_municipal(df_antes_meta.copy(), df_ahora_meta.copy(), registro_opcion)

# ========= FIN BLOQUE 6 =========










