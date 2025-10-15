# ========= BLOQUE 1 · CONFIGURACIÓN INICIAL + HELPERS =========

import streamlit as st
import pandas as pd
import plotly.express as px
import difflib
import unicodedata
import html
#import geopandas as gpd
import folium
from streamlit_folium import st_folium
import numpy as np
import re


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

#@st.cache_data(show_spinner=False)
#def cargar_shapefile_rds() -> gpd.GeoDataFrame:
#    """Carga shapefile municipal una sola vez y lo proyecta a WGS84."""
#    return gpd.read_file("app/gtoSHP/mun_test_wgs.shp").to_crs(4326)

@st.cache_data(show_spinner=False)
def _prep_beneficiarios_unificado(ben_antes: pd.DataFrame, ben_ahora: pd.DataFrame) -> pd.DataFrame:
    """
    Une cortes Antes/Ahora en un solo DF largo con columna 'Versión'.
    - Garantiza columnas esperadas (crea vacías si faltan).
    - Limpia texto con _limpiar_texto (si existe).
    - Convierte columnas de 'Cantidad (...)' a numérico (float).
    """
    # Columnas estándar que queremos conservar
    cols_std = [
        "Clave Q",
        "Descripción del Beneficio",
        "Nombre (Beneficiarios Directos)",
        "Cantidad (Beneficiarios Directos)",
        "Caracteristicas Generales (Beneficiarios Directos)",
        "Nombre (Población Objetivo)",
        "Cantidad (Población Objetivo)",
        "Caracteristicas Generales (Población Objetivo)",
        "Nombre (Población Universo)",
        "Cantidad (Población Universo)",
        "Caracteristicas Generales (Población Universo)",
        "Nombre (Beneficiarios Indirectos)",
        "Cantidad (Beneficiarios Indirectos)",
        "Caracteristicas Generales (Beneficiarios Indirectos)",
    ]

    def _ensure_and_clean(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            # devuelve DF vacío con columnas estándar
            return pd.DataFrame(columns=cols_std)
        df = df.copy()

        # Asegura todas las columnas estándar (si falta alguna, créala vacía)
        for c in cols_std:
            if c not in df.columns:
                df[c] = pd.NA

        # Limpieza básica de textos (si tienes _limpiar_texto ya definida)
        text_cols = [c for c in cols_std if (c != "Clave Q" and not c.startswith("Cantidad ("))]
        for c in text_cols:
            try:
                df[c] = df[c].apply(_limpiar_texto)
            except Exception:
                # fallback suave
                df[c] = df[c].astype(str).str.replace("\n", " ").str.replace("\r", " ").str.strip()

        # Normaliza Clave Q como string
        df["Clave Q"] = df["Clave Q"].astype(str).str.strip()

        # Convierte cantidades a numérico
        qty_cols = [c for c in cols_std if c.startswith("Cantidad (")]
        for c in qty_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)

        # Devuelve solo columnas esperadas (ordenadas)
        return df[cols_std]

    a = _ensure_and_clean(ben_antes)
    h = _ensure_and_clean(ben_ahora)

    if a.empty and h.empty:
        return pd.DataFrame(columns=cols_std + ["Versión"])

    if not a.empty:
        a["Versión"] = "Antes"
    if not h.empty:
        h["Versión"] = "Ahora"

    out = pd.concat([a, h], ignore_index=True)
    # Orden final
    return out[cols_std + ["Versión"]]



#====Helper para aplicar formato de ticks en ejes de tiempo (Plotly)====

from dateutil.relativedelta import relativedelta

def agregar_bandas_mensuales(fig, df, col_inicio="Fecha de Inicio", col_fin="Fecha de Termino",
                             fill_rgba="rgba(0,0,0,0.04)"):
    """
    Agrega bandas verticales alternadas por mes al fondo del Gantt.
    No toca el rango del eje X ni agrega grid denso.
    """
    if df.empty or col_inicio not in df or col_fin not in df:
        return fig

    x0 = pd.to_datetime(df[col_inicio], errors="coerce").min()
    x1 = pd.to_datetime(df[col_fin],    errors="coerce").max()
    if pd.isna(x0) or pd.isna(x1):
        return fig

    # Limites a inicios de mes y un mes extra al final para cubrir completamente
    start = pd.Timestamp(x0.year, x0.month, 1)
    end   = pd.Timestamp(x1.year, x1.month, 1) + relativedelta(months=1)

    meses = pd.date_range(start, end, freq="MS")
    if len(meses) <= 1:
        return fig  # rango muy corto; nada que sombrear

    shapes = list(getattr(fig.layout, "shapes", []))
    toggle = False
    for i in range(len(meses)-1):
        if toggle:
            shapes.append(dict(
                type="rect",
                xref="x", yref="paper",
                x0=meses[i], x1=meses[i+1],
                y0=0, y1=1,
                fillcolor=fill_rgba,   # gris MUY sutil
                line=dict(width=0),
                layer="below"
            ))
        toggle = not toggle

    fig.update_layout(shapes=shapes)
    return fig


# Normalización simple para comparar texto: minúsculas, trim y colapsar espacios
def _norm_simple(s):
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def _first_nonempty(series: pd.Series) -> str:
    for v in series:
        if pd.notna(v) and str(v).strip() != "":
            return str(v)
    return ""

def _to_set(series: pd.Series) -> set:
    if series is None:
        return set()
    vals = [str(x).strip() for x in series if pd.notna(x) and str(x).strip() != ""]
    return set(vals)

# Agrega la hoja "Sección de Metas" por ID Meta (o Clave de Meta si faltara)
def _agregar_por_meta_simple(df: pd.DataFrame, meta_key: str) -> pd.DataFrame:
    df = df.copy()

    if meta_key not in df.columns:
        # Fallo explícito para que el usuario cambie la llave
        return pd.DataFrame()

    # ✅ Llave única, sin fallback
    df["llave_meta"] = df[meta_key].astype(str)


    # Asegurar columnas numéricas presentes (si no existen, crearlas en 0)
    num_cols = [
        "Cantidad Estatal","Monto Estatal",
        "Cantidad Federal","Monto Federal",
        "Cantidad Municipal","Monto Municipal",
    ]
    for c in num_cols:
        if c not in df.columns:
            df[c] = 0
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    g = df.groupby("llave_meta", dropna=False)

    # Agregados simples
    agg = {}
    if "Descripción de la Meta" in df.columns:
        agg["Descripción de la Meta"] = _first_nonempty
    if "Unidad de Medida" in df.columns:
        agg["Unidad de Medida"] = _first_nonempty
    if "ID Meta" in df.columns:
        agg["ID Meta"] = "first"
    if "Clave de Meta" in df.columns:
        agg["Clave de Meta"] = "first"
    for c in num_cols:
        agg[c] = "sum"

    base = g.agg(agg)

    # Sets
    base["set_municipio"] = g["Municipio"].apply(_to_set) if "Municipio" in df.columns else g.size().apply(lambda _: set())
    base["set_rp"]        = g["Registro Presupuestal"].apply(_to_set) if "Registro Presupuestal" in df.columns else g.size().apply(lambda _: set())

    # Normalizados para comparación
    base["desc_norm"] = base["Descripción de la Meta"].apply(_norm_simple) if "Descripción de la Meta" in base.columns else ""
    base["um_norm"]   = base["Unidad de Medida"].apply(_norm_simple) if "Unidad de Medida" in base.columns else ""

    base = base.reset_index()
    return base

def construir_control_cambios_metas_info(metas_antes: pd.DataFrame, metas_ahora: pd.DataFrame, meta_key: str) -> pd.DataFrame:
    A = _agregar_por_meta_simple(metas_antes, meta_key)
    H = _agregar_por_meta_simple(metas_ahora, meta_key)

    # Hacer merge outer por llave_meta
    df = pd.merge(
        A, H,
        on="llave_meta", how="outer", suffixes=("_A", "_H")
    )

    # Normalizar columnas de conjuntos: NaN -> set()
    for col in ["set_municipio_A", "set_municipio_H", "set_rp_A", "set_rp_H"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: x if isinstance(x, set)
                else (set() if pd.isna(x) else {str(x).strip()} if str(x).strip() else set())
            )


    # Flags de presencia
    solo_ahora = df["llave_meta"].notna() & df["ID Meta_A"].isna() & df["ID Meta_H"].notna()
    solo_antes = df["llave_meta"].notna() & df["ID Meta_A"].notna() & df["ID Meta_H"].isna()
    en_ambas   = df["ID Meta_A"].notna() & df["ID Meta_H"].notna()

    # -------- Comparaciones (estrictas) --------
    # Texto
    desc_changed = en_ambas & (df.get("desc_norm_A","") != df.get("desc_norm_H",""))
    um_changed   = en_ambas & (df.get("um_norm_A","")   != df.get("um_norm_H",""))

    # Sets
    def _sets_changed(row, col):
        a = row.get(col + "_A", set()) or set()
        h = row.get(col + "_H", set()) or set()
        return (a ^ h) != set()  # diferencia simétrica no vacía
    muni_changed = df.apply(lambda r: _sets_changed(r, "set_municipio"), axis=1) & en_ambas
    rp_changed   = df.apply(lambda r: _sets_changed(r, "set_rp"), axis=1) & en_ambas

    # Numéricos por fuente
    def _num_changed(col):
        a = pd.to_numeric(df.get(col + "_A"), errors="coerce").fillna(0.0)
        h = pd.to_numeric(df.get(col + "_H"), errors="coerce").fillna(0.0)
        return en_ambas & (a != h)

    c_est_changed = _num_changed("Cantidad Estatal")
    m_est_changed = _num_changed("Monto Estatal")
    c_fed_changed = _num_changed("Cantidad Federal")
    m_fed_changed = _num_changed("Monto Federal")
    c_mun_changed = _num_changed("Cantidad Municipal")
    m_mun_changed = _num_changed("Monto Municipal")

    # Estado por meta
    estado = np.where(solo_ahora, "✚ Nueva",
              np.where(solo_antes, "✖ Eliminada",
              np.where(
                  desc_changed | um_changed | muni_changed | rp_changed |
                  c_est_changed | m_est_changed | c_fed_changed | m_fed_changed | c_mun_changed | m_mun_changed,
                  "✎ Modificada", "✔ Sin cambios"
              )))

    # Identificador visible
    id_visible = df["ID Meta_H"].fillna(df["ID Meta_A"])
    clave_meta_vis = df.get("Clave de Meta_H", pd.Series(dtype=object)).fillna(df.get("Clave de Meta_A", ""))

    # Δ total $ (solo para priorizar; suma de Montos Est/Fed/Mun)
    montos_a = (
        pd.to_numeric(df.get("Monto Estatal_A"), errors="coerce").fillna(0.0) +
        pd.to_numeric(df.get("Monto Federal_A"), errors="coerce").fillna(0.0) +
        pd.to_numeric(df.get("Monto Municipal_A"), errors="coerce").fillna(0.0)
    )
    montos_h = (
        pd.to_numeric(df.get("Monto Estatal_H"), errors="coerce").fillna(0.0) +
        pd.to_numeric(df.get("Monto Federal_H"), errors="coerce").fillna(0.0) +
        pd.to_numeric(df.get("Monto Municipal_H"), errors="coerce").fillna(0.0)
    )
    delta_total = montos_h - montos_a

    # Marcadores visuales ●/○
    def mark(s): return np.where(s, "●", "○")

    out = pd.DataFrame({
        "Estado": estado,
        "ID Meta": id_visible.astype(str),
        "Clave de Meta": clave_meta_vis.astype(str),

        "Desc": mark(desc_changed | solo_ahora | solo_antes),
        "UM":   mark(um_changed   | solo_ahora | solo_antes),
        "Municipios": mark(muni_changed | solo_ahora | solo_antes),
        "RP":         mark(rp_changed   | solo_ahora | solo_antes),

        "Cant. Est.": mark(c_est_changed | solo_ahora | solo_antes),
        "Mto. Est.":  mark(m_est_changed | solo_ahora | solo_antes),
        "Cant. Fed.": mark(c_fed_changed | solo_ahora | solo_antes),
        "Mto. Fed.":  mark(m_fed_changed | solo_ahora | solo_antes),
        "Cant. Mun.": mark(c_mun_changed | solo_ahora | solo_antes),
        "Mto. Mun.":  mark(m_mun_changed | solo_ahora | solo_antes),

        "Δ total $": delta_total
    })

    # Orden sugerido
    cat = pd.CategoricalDtype(["✚ Nueva","✖ Eliminada","✎ Modificada","✔ Sin cambios"], ordered=True)
    out["Estado"] = out["Estado"].astype(cat)
    out = out.sort_values(["Estado","Δ total $"], ascending=[True, False]).reset_index(drop=True)

    return out


#=====================helper tooltip Cronograma==================================

# === Tooltip Cronograma Dinámico y Compacto ===
from manual_extractos import MANUAL

_Q_PREFIX_MAP = {
    "QA": "Obra",
    "QB": "Subprograma – Obra",
    "QC": "Accion",  # caso especial: mostrar TODOS los subprogramas Acción en columnas
    "QD": "Subprograma – Acción/Investigación (con servicios)",
}

# Llaves EXACTAS como en MANUAL['metas']['cronograma']['tipos_proyecto']
_ACCION_KEYS = [
    "Subprograma – Acción (con apoyos)",
    "Subprograma – Acción (con adquisiciones)",
    "Subprograma – Acción/Investigación (con servicios)",
]

def inferir_tipo_desde_clave_q(clave_q: str) -> str:
    if not clave_q:
        return ""
    pref = str(clave_q).strip().upper()[:2]
    return _Q_PREFIX_MAP.get(pref, "")

def _render_bullets(items: list[str]):
    for it in items:
        st.markdown(f"- {it}")

def render_tooltip_cronograma_qaware(manual_crono: dict, clave_q: str, columnas_accion: int = 2):
    """
    Expander compacto. Para QC muestra todos los subprogramas de Acción en columnas.
    Para QA/QB/QD muestra primero el bloque del tipo detectado y el resto como referencia.
    """
    if not manual_crono:
        return

    desc   = manual_crono.get("descripcion", "")
    tipos  = manual_crono.get("tipos_proyecto", {}) or {}
    buenas = manual_crono.get("buenas_practicas", [])
    adv    = manual_crono.get("advertencias", [])
    ref    = manual_crono.get("referencia", "")

    tipo_base = inferir_tipo_desde_clave_q(clave_q)

    # ===== estilos compactos (forzados) =====
    st.markdown("""
    <style>
    .crono-tip { 
        font-size:0.5rem !important;
        line-height:1.25 !important;
    }
    .crono-tip p, .crono-tip ul, .crono-tip li, .crono-tip div, .crono-tip span, .crono-tip strong, .crono-tip em {
        font-size:0.78rem !important;
        line-height:1.25 !important;
        margin-top:0.2rem; 
        margin-bottom:0.2rem;
    }
    .crono-section{
        background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px;
        padding:6px 10px; margin-bottom:6px;
    }
    .crono-title{ font-weight:700; margin:.25rem 0 .25rem 0; font-size:0.82rem !important; }
    </style>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Elementos de Cronograma (Guía rápida)", expanded=False):
        st.markdown("<div class='crono-tip'>", unsafe_allow_html=True)

        # Descripción general

        if tipo_base == "Accion":
            # QC: mostrar TODOS los subprogramas Acción en columnas
            accion_existentes = [k for k in _ACCION_KEYS if k in tipos]
            if accion_existentes:
                st.markdown("<div class='crono-title'>Componentes mínimos para Subprograma – Acción:</div>", unsafe_allow_html=True)
                n = len(accion_existentes)
                cols = st.columns(min(max(1, columnas_accion), n))
                for i, key in enumerate(accion_existentes):
                    with cols[i % len(cols)]:
                        st.markdown(f"<div class='crono-section'><strong>{key}</strong></div>", unsafe_allow_html=True)
                        _render_bullets(tipos.get(key, []))
                st.markdown("---")
        else:
            # Mostrar el bloque del tipo detectado (si existe)
            if tipo_base and tipo_base in tipos:
                st.markdown("<div class='crono-title'>Componentes sugeridos (según tipo de proyecto):</div>", unsafe_allow_html=True)
                st.markdown("<div class='crono-section'>", unsafe_allow_html=True)
                _render_bullets(tipos[tipo_base])
                st.markdown("</div>", unsafe_allow_html=True)

            # Otros tipos como referencia (acordeones compactos)
            otros = {k: v for k, v in tipos.items() if k != tipo_base}
            if otros:
                st.markdown("<div class='crono-title'>Otros tipos de referencia:</div>", unsafe_allow_html=True)
                for k, items in otros.items():
                    with st.expander(k, expanded=False):
                        _render_bullets(items)

        if ref:
            st.caption(ref)

        st.markdown("</div>", unsafe_allow_html=True)







# ========= FIN BLOQUE 1 =========
# ========= BLOQUE 2 · SIDEBAR: CARGA Y FILTROS (Eje → Dependencia → Clave Q) =========

#=====================CARGA DE REPORTES========================================

with st.sidebar:
    
    # --- Carga de archivos ---
    with st.expander("📤 Cargar Detalle de Qs", expanded=True):
        archivo_antes = st.file_uploader("Archivo - Corte Antes", type=["xlsx"], key="archivo_antes")
        archivo_ahora = st.file_uploader("Archivo - Corte Ahora", type=["xlsx"], key="archivo_ahora")
    with st.expander("📥 Beneficiarios — Detalle de Qs 2", expanded=False):
        ben_antes_file = st.file_uploader(
            "Corte ANTES (Detalle de Qs 2)",
            type=["xlsx"], key="ben_antes_file"
        )
        ben_ahora_file = st.file_uploader(
            "Corte AHORA (Detalle de Qs 2)",
            type=["xlsx"], key="ben_ahora_file"
        )

with st.sidebar:
    st.markdown("### 🔑 Llave para comparar metas")
    llave_opcion = st.radio(
        "¿Tus reportes ya cuentan con claves estandarizadas de metas? Selecciona Clave de meta:",
        ["No, usar ID Meta", "Sí, usar Clave de Meta"],
        horizontal=True,
        key="llave_meta_opcion"
    )


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

    1. 📂 **Carga los archivos** correspondientes a los cortes **Antes** y **Ahora** del reporte Detalle de Qs.
    2. 🧭 **Selecciona un Eje**.
    3. 🏛️ **Selecciona la Dependencia o Entidad**.
    4. 🔑 **Elige la Clave Q** del proyecto que deseas revisar.
                
    **¡Ahora incluye un comparativo para Beneficiarios 👥!** si lo necesitas solo carga los archivos adicionales 📑.           

    Una vez cargados seleccionada una Clave Q, se mostrarán las distintas secciones comparativas para facilitar el análisis entre fechas de corte.
    """)
    st.stop()



# ========= FIN BLOQUE 2 =========
# ========= BLOQUE 3 · CARGA DE HOJAS + LIMPIEZA + TOTALES + FILTRO POR CLAVE Q =========

# Llave operativa de metas (según selección del usuario)
META_COL = "ID Meta" if llave_opcion == "ID Meta" else "Clave de Meta"


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
    "Clave Q", "ID Meta", "Clave de Meta", "Clave de Actividad /Hito", "Descripción", "Partida", "Monto Anual",
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

# ✅ Sin renombrar: exigimos la columna seleccionada por el usuario
if META_COL not in cumplimiento_ahora.columns or META_COL not in cumplimiento_antes.columns:
    st.error(f"No se encontró la columna **{META_COL}** en la hoja 'Sección de Metas-Cumplimiento'. "
             f"Cambia la opción de llave o revisa el archivo.")
    st.stop()

# Limpieza: eliminar filas sin ID Meta
cumplimiento_ahora = cumplimiento_ahora.dropna(subset=[META_COL])
cumplimiento_antes = cumplimiento_antes.dropna(subset=[META_COL])

# (Opcional) Nombre del proyecto para encabezados posteriores
nombre_proyecto_vals = datos_ahora["Nombre del Proyecto (Ejercicio Actual)"].values
nombre_proyecto = nombre_proyecto_vals[0] if len(nombre_proyecto_vals) else ""


# ---- 3.8 Cargar BENEFICIARIOS (ambos cortes) con cargar_hoja + filtro por Clave Q ----

# ---- 3.1 Cargar Datos Generales (ambos cortes) ----


COLUMNAS_BENEFICIARIOS = [
    "Clave Q",
    "Descripción del Beneficio",
    "Nombre (Beneficiarios Directos)",
    "Cantidad (Beneficiarios Directos)",
    "Caracteristicas Generales (Beneficiarios Directos)",
    "Nombre (Población Objetivo)",
    "Cantidad (Población Objetivo)",
    "Caracteristicas Generales (Población Objetivo)",
    "Nombre (Población Universo)",
    "Cantidad (Población Universo)",
    "Caracteristicas Generales (Población Universo)",
    "Nombre (Beneficiarios Indirectos)",
    "Cantidad (Beneficiarios Indirectos)",
    "Caracteristicas Generales (Beneficiarios Indirectos)"
]

# Lee con tu helper estándar (header=7). Si falta la hoja o no hay archivo, devuelve DF vacío.
if ben_ahora_file is not None:
    try:
        beneficiarios_ahora = cargar_hoja(ben_ahora_file, "Beneficiarios", COLUMNAS_BENEFICIARIOS).copy()
    except Exception:
        beneficiarios_ahora = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)
else:
    beneficiarios_ahora = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)

if ben_antes_file is not None:
    try:
        beneficiarios_antes = cargar_hoja(ben_antes_file, "Beneficiarios", COLUMNAS_BENEFICIARIOS).copy()
    except Exception:
        beneficiarios_antes = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)
else:
    beneficiarios_antes = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)

# Filtro por la misma Clave Q del sidebar
if not beneficiarios_ahora.empty:
    beneficiarios_ahora = beneficiarios_ahora[beneficiarios_ahora["Clave Q"] == clave_q]
if not beneficiarios_antes.empty:
    beneficiarios_antes = beneficiarios_antes[beneficiarios_antes["Clave Q"] == clave_q]

# Unifica cortes (Antes/Ahora) -> beneficiarios_df (usando los helpers que ya añadimos)
beneficiarios_df = _prep_beneficiarios_unificado(beneficiarios_antes, beneficiarios_ahora)


# ========= FIN BLOQUE 3 =========



# ========= FIN BLOQUE 4 =========

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




# ---------------------- TAB 2: METAS (con subpestañas) ----------------------
with tabs[1]:
    st.subheader("🎯 Metas")
    # --------- Selección de Meta por ID ---------
    if metas_ahora.empty:
        st.info("No hay datos de metas para esta Clave Q.")
        st.stop()


#========Controles de cambios======================
    with st.expander("📊 Control de cambios – Metas (Información)", expanded=True):
        ICONO_ESTADO = {
        "✚ Nueva": "🗽 Nueva",
        "✖ Eliminada": "🗑️ Eliminada",
        "✎ Modificada": "🔄 Modificada",
        "✔ Sin cambios": "🟰 Sin cambios",
    }
        ICONO_CAMBIO = {"●": "🚨", "○": "➖"}  # ● = cambió, ○ = no cambió


        st.caption("Comparativo rápido a nivel proyecto (corte Antes vs Ahora).")

        # 1) Construir comparativo base (no cambies esta llamada)
        tabla_cc = construir_control_cambios_metas_info(metas_antes, metas_ahora, META_COL)

        # 2) Crear versión para mostrar (sin tocar los datos base)
        tabla_show = tabla_cc.copy()

        # 2.1) Reemplazar 'Estado' por icono SOLO para la vista  ✅ FIX
        estado_str = tabla_show["Estado"].astype(str)  # quitar dtype categorical
        tabla_show["Estado (icono)"] = estado_str.map(ICONO_ESTADO).fillna(estado_str)


        # 2.2) Reemplazar marcadores de campos (●/○) por tus iconos (🚨 / ➖)  ✅ FIX
        cols_campos = [
            "Desc","UM","Municipios","RP",
            "Cant. Est.","Mto. Est.","Cant. Fed.","Mto. Fed.","Cant. Mun.","Mto. Mun."
        ]
        for c in cols_campos:
            if c in tabla_show.columns:
                tabla_show[c] = tabla_show[c].astype(object).replace(ICONO_CAMBIO)


        # 2.3) Formatear Δ total $ solo para mostrar (mantén numérico en tabla_cc)
        if "Δ total $" in tabla_show.columns:
            tabla_show["Δ total $"] = tabla_show["Δ total $"].apply(
                lambda v: f"${v:,.0f}" if pd.notna(v) else "—"
            )

        # 3) Filtro rápido por Estado (usa las etiquetas internas, no los iconos)
        estado_sel = st.multiselect(
            "Filtrar por estado",
            options=["✚ Nueva","✖ Eliminada","✎ Modificada","✔ Sin cambios"],
            default=["✚ Nueva","✖ Eliminada","✎ Modificada","✔ Sin cambios"]
        )
        if estado_sel:
            tabla_filtrada = tabla_show[tabla_show["Estado"].isin(estado_sel)].reset_index(drop=True)
        else:
            tabla_filtrada = tabla_show

        # 4) Mostrar tabla (enseñamos la columna con icono)
        columnas_vista = [
            "Estado (icono)","ID Meta","Clave de Meta",
            "Desc","UM","Municipios","RP",
            "Cant. Est.","Mto. Est.","Cant. Fed.","Mto. Fed.","Cant. Mun.","Mto. Mun.",
            "Δ total $"
        ]
        columnas_vista = [c for c in columnas_vista if c in tabla_filtrada.columns]  # por si faltara alguna

        st.dataframe(
            tabla_filtrada[columnas_vista],
            use_container_width=True,
            hide_index=True
        )

#=====FIN CONTROL DE CAMBIOS=====


    metas_disponibles = (
        metas_ahora[[META_COL, "Descripción de la Meta"]]
        .dropna(subset=[META_COL])
        .drop_duplicates()
        .copy()
    )

    def _fmt_meta_val(x):
        return _fmt_id_meta(x) if META_COL == "ID Meta" else ("" if pd.isna(x) else str(x))

    metas_disponibles["Etiqueta"] = metas_disponibles[META_COL].apply(_fmt_meta_val) + " - " + metas_disponibles["Descripción de la Meta"].astype(str)
    metas_disponibles = metas_disponibles.sort_values("Etiqueta")

    id_meta_label = st.selectbox(
        "Selecciona una Meta",
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
            def _info_meta(df_antes: pd.DataFrame, df_ahora: pd.DataFrame, meta_key: str, meta_val: str):
                if meta_key not in df_antes.columns or meta_key not in df_ahora.columns:
                    return pd.DataFrame(), pd.DataFrame()
                def _norm(v):  # para que funcione igual con ID (num) o Clave (texto)
                    return _fmt_id_meta(v) if meta_key == "ID Meta" else ("" if pd.isna(v) else str(v))
                f_ahora = df_ahora[df_ahora[meta_key].apply(_norm) == meta_val]
                f_antes = df_antes[df_antes[meta_key].apply(_norm) == meta_val]
                return f_antes.copy(), f_ahora.copy()

            df_antes_meta, df_ahora_meta = _info_meta(metas_antes, metas_ahora, META_COL, id_meta_sel)

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
            
            def _sombrear_antes(df: pd.DataFrame):
                """Devuelve estilos de fondo gris claro para columnas que contienen '(Antes)'."""
                styles = pd.DataFrame("", index=df.index, columns=df.columns)
                for c in df.columns:
                    if "(Antes)" in c:
                        styles[c] = "background-color:#f2f2f2"
                return styles

            formato = {c: "${:,.2f}" for c in df_comp_mpio.columns if c.startswith("Monto ")}
            formato.update({c: "{:,.2f}" for c in df_comp_mpio.columns if c.startswith("Cantidad ")})

            def _agregar_totales(df: pd.DataFrame, filtro_reg: str) -> pd.DataFrame:
                if df.empty:
                    return df

                # Asegurar que columnas numéricas sean numéricas
                num_cols = df.select_dtypes(include="number").columns.tolist()

                filas = []

                # --- Fila TOTAL (todas las filas)
                totales = df[num_cols].sum(numeric_only=True)
                fila_total = {col: totales.get(col, "") for col in df.columns}
                fila_total["Municipio"] = "TOTAL"
                filas.append(fila_total)

                # --- Subtotales por Registro Presupuestal (solo si filtro = "Todos")
                if filtro_reg == "Todos" and "Registro Presupuestal" in df_antes_meta.columns:
                    for reg in ["Centralizado", "Descentralizado", "Sin Registro"]:
                        mask = (
                            (df_antes_meta["Registro Presupuestal"] == reg) |
                            (df_ahora_meta["Registro Presupuestal"] == reg)
                        )
                        if mask.any():
                            # extraemos municipios de ese grupo en comp
                            municipios_reg = pd.concat([
                                df_antes_meta.loc[df_antes_meta["Registro Presupuestal"] == reg, "Municipio"],
                                df_ahora_meta.loc[df_ahora_meta["Registro Presupuestal"] == reg, "Municipio"]
                            ]).unique()
                            sub = df[df["Municipio"].isin(municipios_reg)]
                            if not sub.empty:
                                subtotales = sub[num_cols].sum(numeric_only=True)
                                fila_sub = {col: subtotales.get(col, "") for col in df.columns}
                                fila_sub["Municipio"] = f" ↘️ {reg}"
                                filas.append(fila_sub)

                # Concatenamos totales y la tabla original
                df_out = pd.concat([pd.DataFrame(filas), df], ignore_index=True)
                return df_out
            
            df_comp_mpio = _agregar_totales(df_comp_mpio, registro_opcion)
            

            def _estilo_totales(df: pd.DataFrame):
                styles = pd.DataFrame("", index=df.index, columns=df.columns)
                for i, val in enumerate(df["Municipio"]):
                    if str(val).startswith("TOTAL"):
                        styles.iloc[i, :] = "font-weight:bold; background-color:#d9ead3"
                    elif str(val).startswith(" ↘️ "):
                        styles.iloc[i, :] = "font-weight:bold; background-color:#fce5cd"
                return styles


            st.dataframe(
                df_comp_mpio.style
                    .apply(_resaltar_cambios, axis=1)
                    .apply(_sombrear_antes, axis=None)
                    .apply(_estilo_totales, axis=None)
                    .format(formato),
                use_container_width=True
            )



# ================== SUBTAB 2: Cronograma y Partidas ==================
with subtabs[1]:
    # ---------- Partidas ----------
    @st.cache_data(show_spinner=False)
    def _partidas_resumen(pa: pd.DataFrame, ph: pd.DataFrame, id_meta_str: str | None, meta_key: str):
        """
        Devuelve:
        - comp: comparativo por Partida (Antes/Ahora) a nivel proyecto o meta
        - df_mensual: totales mensuales (Antes/Ahora) para la selección actual (sin filtrar por Partida)
        - a, h: dataframes de partidas (Antes/Ahora) ya filtrados por meta si aplica
        """
        meses_cols = [
            "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
            "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
            "Monto Octubre", "Monto Noviembre", "Monto Diciembre"
        ]

        a = pa.copy()
        h = ph.copy()

        # 🔎 Filtro por Meta SOLO si hay selección
        if id_meta_str:
            target = str(id_meta_str)
            a = a[a[meta_key].apply(lambda v: _norm_meta_val(meta_key, v)) == target]
            h = h[h[meta_key].apply(lambda v: _norm_meta_val(meta_key, v)) == target]

        # Partida a 4 dígitos (robusto)
        for dfp in (a, h):
            if "Partida" in dfp.columns:
                dfp["Partida_fmt"] = dfp["Partida"].apply(
                    lambda x: str(int(float(x)))[:4] if pd.notnull(x) and str(x).strip() != "" else None
                )
        a = a[a.get("Partida_fmt").notna()] if "Partida_fmt" in a.columns else a
        h = h[h.get("Partida_fmt").notna()] if "Partida_fmt" in h.columns else h

        # Comparativo por partida (monto anual)
        res_h = (h.groupby("Partida_fmt")["Monto Anual"].sum().reset_index()
                 .rename(columns={"Monto Anual": "Monto Anual (Ahora)"})) if not h.empty else pd.DataFrame(columns=["Partida_fmt", "Monto Anual (Ahora)"])
        res_a = (a.groupby("Partida_fmt")["Monto Anual"].sum().reset_index()
                 .rename(columns={"Monto Anual": "Monto Anual (Antes)"})) if not a.empty else pd.DataFrame(columns=["Partida_fmt", "Monto Anual (Antes)"])
        comp = pd.merge(res_a, res_h, on="Partida_fmt", how="outer").fillna(0)
        if not comp.empty:
            comp["Diferencia"] = comp["Monto Anual (Ahora)"] - comp["Monto Anual (Antes)"]

        # Totales mensuales (a nivel proyecto o meta según filtro)
        sum_m_ahora = h[meses_cols].sum(numeric_only=True) if not h.empty else pd.Series([0]*12, index=meses_cols)
        sum_m_antes = a[meses_cols].sum(numeric_only=True) if not a.empty else pd.Series([0]*12, index=meses_cols)
        df_mensual = pd.DataFrame({
            "Mes": [m.replace("Monto ", "") for m in meses_cols],
            "Antes": sum_m_antes.values,
            "Ahora": sum_m_ahora.values
        })

        return comp, df_mensual, a, h

    df_comp_part, df_mensual, dfp_a, dfp_h = _partidas_resumen(
        metas_partidas_antes, metas_partidas_ahora, id_meta_sel if id_meta_sel else None, META_COL
    )

    st.markdown("##### Partidas de Gasto")

    # ====== 1) Distribución mensual (selector + gráfico) ======
    # Lista de partidas disponibles a partir de ambos cortes
    partidas_disponibles = sorted(
        pd.Index(
            pd.concat([
                dfp_a.get("Partida_fmt", pd.Series(dtype=object)),
                dfp_h.get("Partida_fmt", pd.Series(dtype=object))
            ], ignore_index=True)
        ).dropna().astype(str).unique().tolist()
    )

    # --- Filtro de partidas (más limpio, dentro de un expander) ---
    st.write("**Selecciona una meta para visualizar su calendarizado (Por default se muestra del proyecto completo)**")

    with st.expander("🎚️ Filtro de partidas", expanded=False):
        col1, col2 = st.columns([3, 1])
        todas_on = col2.checkbox(
            "Todas",
            value=False,
            key=f"chk_todas_{_fmt_id_meta(id_meta_sel)}"
        )

        if todas_on:
            filtro_partidas = partidas_disponibles
        else:
            filtro_partidas = col1.multiselect(
                "Selecciona partidas:",
                options=partidas_disponibles,
                default=[],
                key=f"ms_partidas_{_fmt_id_meta(id_meta_sel)}",
                placeholder="Escribe o selecciona una o más partidas..."
            )

    # Si no hay selección, mostrar todas
    if not filtro_partidas:
        filtro_partidas = partidas_disponibles

    # Resumen del filtro activo
    st.caption(f"Mostrando {len(filtro_partidas)} de {len(partidas_disponibles)} partidas disponibles.")

    # Filtrado
    df_mes_a = dfp_a[dfp_a["Partida_fmt"].astype(str).isin(filtro_partidas)]
    df_mes_h = dfp_h[dfp_h["Partida_fmt"].astype(str).isin(filtro_partidas)]

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

    # --- Gráfico mensual con etiquetas SOLO en "Ahora" (K/M/B y sin ceros) ---
    def _humanize_kmb(x):
        if pd.isna(x): return ""
        try: v = float(x)
        except Exception: return ""
        if v == 0: return ""
        a = abs(v)
        if a >= 1_000_000_000: return f"${v/1_000_000_000:.2f}B"
        if a >= 1_000_000:     return f"${v/1_000_000:.2f}M"
        if a >= 1_000:         return f"${v/1_000:.0f}K"
        return f"${v:,.0f}"

    labels_ahora = [_humanize_kmb(v) for v in df_mensual_sel["Ahora"].values]

    titulo_scope = (
        f"Meta ({'ID ' if META_COL=='ID Meta' else ''}{META_COL} {id_meta_sel})"
        if id_meta_sel else "Proyecto completo"
    )

    fig_mes = px.bar(
        df_mensual_sel,
        x="Mes",
        y=["Antes", "Ahora"],
        barmode="group",
        title=f"Calendarizado Mensual – {titulo_scope}",
        labels={"value": "Monto", "variable": "Versión"},
        color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"}
    )

    def _apply_text_to_ahora(trace):
        if trace.name == "Ahora":
            trace.update(text=labels_ahora, texttemplate="%{text}", textposition="outside", textfont_size=11)
        else:
            trace.update(text=None)

    fig_mes.for_each_trace(_apply_text_to_ahora)
    fig_mes.update_layout(height=480, uniformtext_minsize=10, uniformtext_mode="hide")
    st.plotly_chart(fig_mes, use_container_width=True)

    # ====== 2) Partidas por Actividad / Hito ======
    st.markdown("##### Partidas por Actividad ")

    # Incluir META_COL en los detalles para que podamos mostrar la llave
    _det_a = dfp_a[["Partida_fmt", "Clave de Actividad /Hito", META_COL, "Descripción", "Monto Anual"]].copy()
    _det_h = dfp_h[["Partida_fmt", "Clave de Actividad /Hito", META_COL, "Descripción", "Monto Anual"]].copy()

    _det_a.rename(columns={"Descripción": "Desc_A", "Monto Anual": "Monto Anual (Antes)"}, inplace=True)
    _det_h.rename(columns={"Descripción": "Desc_H", "Monto Anual": "Monto Anual (Ahora)"}, inplace=True)

    # Merge por Partida_fmt + Clave; la llave META_COL puede venir en A o en H → hacemos coalesce después
    _unificada = pd.merge(
        _det_a, _det_h,
        on=["Partida_fmt", "Clave de Actividad /Hito"],
        how="outer",
        suffixes=("_A", "_H")
    )

    # Coalesce de la llave (ID Meta o Clave de Meta, según tu selector)
    if f"{META_COL}_H" in _unificada.columns or f"{META_COL}_A" in _unificada.columns:
        _unificada[META_COL] = _unificada.get(f"{META_COL}_H").combine_first(_unificada.get(f"{META_COL}_A"))

    # Descripción preferente: Ahora > Antes
    _unificada["Descripción"] = _unificada["Desc_H"].combine_first(_unificada["Desc_A"])

    # Números + diferencia
    for c in ["Monto Anual (Antes)", "Monto Anual (Ahora)"]:
        _unificada[c] = pd.to_numeric(_unificada[c], errors="coerce").fillna(0.0)
    _unificada["Diferencia"] = _unificada["Monto Anual (Ahora)"] - _unificada["Monto Anual (Antes)"]

    # --- Join catálogo (robusto) para descripción, restringida y validador
    def _pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
        for c in candidates:
            if c in df.columns:
                return c
        return None

    desc_candidates  = ["Definición", "Definicion", "Descripción", "Descripcion",
                        "Descripción de la Partida", "Descripcion de la Partida",
                        "Desc Partida", "Descripcion Partida"]
    restr_candidates = ["Restringida", "Restringido", "Restriccion", "Restricción"]
    valid_candidates = ["Validador", "Validador Partida", "Validador_Partida"]

    desc_col  = _pick_col(CATALOGO_PARTIDAS, desc_candidates)
    restr_col = _pick_col(CATALOGO_PARTIDAS, restr_candidates)
    valid_col = _pick_col(CATALOGO_PARTIDAS, valid_candidates)

    cat_cols = ["Partida_fmt"] + [c for c in [desc_col, restr_col, valid_col] if c]
    _catalogo = CATALOGO_PARTIDAS[cat_cols].drop_duplicates().copy() if cat_cols else pd.DataFrame(columns=["Partida_fmt"])

    _unificada = _unificada.merge(_catalogo, on="Partida_fmt", how="left")

    # Renombres y defaults
    rename_map = {"Partida_fmt": "Partida"}
    if desc_col:  rename_map[desc_col]  = "Descripción de la Partida"
    if restr_col: rename_map[restr_col] = "Restringida"
    if valid_col: rename_map[valid_col] = "Validador"
    _unificada = _unificada.rename(columns=rename_map)
    if "Descripción de la Partida" not in _unificada.columns: _unificada["Descripción de la Partida"] = ""
    if "Restringida" not in _unificada.columns:               _unificada["Restringida"] = False
    if "Validador" not in _unificada.columns:                 _unificada["Validador"] = ""

    # CHIP en "Descripción de la Partida" cuando esté restringida
    import html as _html_mod
    def _to_bool(v):
        if pd.isna(v): return False
        if isinstance(v, (bool,)): return bool(v)
        if isinstance(v, (int, float)): return v != 0
        s = str(v).strip().lower()
        return s in {"true", "1", "sí", "si", "yes", "y"}

    def _desc_with_chip(row):
        desc = _html_mod.escape(str(row.get("Descripción de la Partida", "") or ""))
        if _to_bool(row.get("Restringida")):
            val = (row.get("Validador") or "").strip()
            if val:
                return f"{desc} <span class='chip chip--lock'>🔒 {val}</span>"
            return f"{desc} <span class='chip chip--lock'>🔒</span>"
        return desc

    _unificada["Descripción de la Partida"] = _unificada.apply(_desc_with_chip, axis=1)

    # Etiqueta amigable para la llave
    meta_label = "ID de Meta" if META_COL == "ID Meta" else "Clave de Meta"

    # Columnas visibles (incluye la llave META_COL)
    _cols_finales = [
        META_COL,
        "Partida",
        "Descripción de la Partida",
        "Actividad (Cronograma)",
        "Monto Anual (Antes)",
        "Monto Anual (Ahora)",
        "Diferencia",
    ]

    # Arma la tabla final con la llave
    _tabla_unica = (
        _unificada.rename(columns={"Partida_fmt": "Partida", "Descripción": "Actividad (Cronograma)"})
        .reindex(columns=[c for c in _cols_finales if c in (_unificada.columns.tolist() + ["Partida","Descripción de la Partida","Actividad (Cronograma)"])])
        .copy()
    )

    # Renombra la columna de la llave a una etiqueta legible
    if META_COL in _tabla_unica.columns:
        _tabla_unica.rename(columns={META_COL: meta_label}, inplace=True)

    # Filtro: mostrar solo filas con monto ≠ 0 (Antes o Ahora)
    _eps = 1e-9
    _mask_nonzero = (_tabla_unica["Monto Anual (Antes)"].abs() > _eps) | (_tabla_unica["Monto Anual (Ahora)"].abs() > _eps)
    _tabla_unica = _tabla_unica[_mask_nonzero].sort_values(["Partida", "Actividad (Cronograma)"], kind="stable")

    # Controles de orden (por defecto: Monto Ahora desc)
    with st.expander("⚙️ Opciones de ordenamiento", expanded=False):
        col_ord1, col_ord2, col_mode = st.columns([2, 1, 1])
        opciones_sort = [
            "Diferencia",
            "Monto Anual (Ahora)",
            "Monto Anual (Antes)",
            "Partida",
            "Actividad (Cronograma)",
        ]
        sort_col = col_ord1.selectbox(
            "Ordenar por",
            opciones_sort,
            index=1,
            key=f"sortcol_{_fmt_id_meta(id_meta_sel)}"
        )
        asc = col_ord2.toggle(
            "Ascendente",
            value=False,
            key=f"sortasc_{_fmt_id_meta(id_meta_sel)}"
        )
        modo_interactivo = col_mode.toggle(
            "Tabla interactiva",
            value=False,
            help="Permite ordenar clicando en el encabezado (sin ‘chip’ 🔒).",
            key=f"modo_inter_{_fmt_id_meta(id_meta_sel)}"
        )

    # Orden final
    _tabla_ordenada = _tabla_unica.sort_values(sort_col, ascending=asc, kind="stable").copy()

    if modo_interactivo:
        # Vista interactiva: sin HTML del chip para que el sorting por columna funcione con clic
        import re
        df_inter = _tabla_ordenada.copy()

        def _strip_html(x):
            return re.sub(r"<.*?>", "", str(x)) if isinstance(x, str) else x

        if "Descripción de la Partida" in df_inter.columns:
            df_inter["Descripción de la Partida"] = df_inter["Descripción de la Partida"].map(_strip_html)

        st.dataframe(
            df_inter,
            use_container_width=True,
            hide_index=True,
            column_config={
                meta_label: st.column_config.TextColumn(width="small"),
                "Partida": st.column_config.TextColumn(width="small"),
                "Descripción de la Partida": st.column_config.TextColumn(width="large"),
                "Actividad (Cronograma)": st.column_config.TextColumn(width="medium"),
                "Monto Anual (Antes)": st.column_config.NumberColumn(format="%,.2f"),
                "Monto Anual (Ahora)": st.column_config.NumberColumn(format="%,.2f"),
                "Diferencia": st.column_config.NumberColumn(format="%,.2f"),
            },
        )
    else:
        # Vista con CHIP y resaltado en Diferencia
        def _bg_delta_cell(v):
            if pd.isna(v):
                return ""
            return "background-color:#fff3cd" if abs(v) != 0 else ""

        styled_unica = (
            _tabla_ordenada
            .style
            .format({
                "Monto Anual (Antes)": "${:,.2f}",
                "Monto Anual (Ahora)": "${:,.2f}",
                "Diferencia": "${:,.2f}"
            })
            .applymap(_bg_delta_cell, subset=["Diferencia"])
            .hide(axis="index")
        )
        st.markdown(styled_unica.to_html(escape=False), unsafe_allow_html=True)

            if not id_meta_sel:
                st.info("Selecciona una Meta (ID) para ver Cronograma")
            else:
                # ---------- Cronograma (función única, cacheada) ----------
                @st.cache_data(show_spinner=False)
                def _cronograma_df(cr_a: pd.DataFrame, cr_h: pd.DataFrame, meta_key: str, meta_val: str) -> pd.DataFrame:
                    def _norm(v):
                        return _fmt_id_meta(v) if meta_key == "ID Meta" else ("" if pd.isna(v) else str(v))
                    a = cr_a[cr_a[meta_key].apply(_norm) == meta_val].copy()
                    h = cr_h[cr_h[meta_key].apply(_norm) == meta_val].copy()
                    if a.empty and h.empty:
                        return pd.DataFrame()
                    a["Versión"] = "Antes"; h["Versión"] = "Ahora"
                    out = pd.concat([a, h], ignore_index=True)
                    out["Clave Num"] = pd.to_numeric(out.get("Clave de Actividad /Hito"), errors="coerce")
                    mismo_dia = (out["Fecha de Inicio"] == out["Fecha de Termino"])
                    out.loc[mismo_dia, "Fecha de Termino"] = out.loc[mismo_dia, "Fecha de Termino"] + pd.Timedelta(days=1)
                    return out
    
                df_crono = _cronograma_df(metas_crono_antes, metas_crono_ahora, META_COL, id_meta_sel)
                
                
                st.markdown("##### Detalle de Actividades / Hitos (Cronograma Actual)")
    
                if df_crono.empty:
                    st.info("No se encontraron actividades o hitos para esta meta en ninguna de las versiones.")
                else:
                    # === Tabla "Ahora" (vista rápida)
                    columnas_tabla = [
                        "Clave de Actividad /Hito", "Fase Actividad / Hito", "Tipo", "Descripción",
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
    
    
                    # Tooltip contextual dinámico por Clave Q (QA/QB/QC/QD)
                    
    
    
                    try:
                        manual_crono = MANUAL.get("metas", {}).get("cronograma", {})
                        render_tooltip_cronograma_qaware(manual_crono, clave_q, columnas_accion=3)  # usa 2 o 3 columnas a tu gusto
                    except Exception:
                        pass
    
    
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
    
                    # === Etiquetas de monto (UI existente) + regla fija: solo mostrar si monto ≠ 0 ===
    
                    # 1) Asegura columna numérica ANTES de construir la etiqueta (para la regla fija)
                    df_crono["Monto_val"] = pd.to_numeric(
                        df_crono.get("Monto Actividad / Hito", pd.Series([None]*len(df_crono))),
                        errors="coerce"
                    ).fillna(0.0)
    
                    # 2) Mantén tus opciones actuales en el expander (SIN añadir toggle para ≠ 0)
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
    
                    # 3) Construcción de la etiqueta con la REGLA FIJA: no mostrar si monto == 0
                    def _pick_label(row):
                        # Regla fija (sin UI): solo etiquetar montos distintos de cero
                        if row["Monto_val"] == 0:
                            return ""
                        # Resto de opciones (las que ya tienes en el expander)
                        if hide_on_short_bars and row["DuracionDias"] < min_days_short:
                            return ""
                        if show_only_now and row.get("Versión") != "Ahora":
                            return ""
                        return row["Monto_compact"] if use_compact_amount else row["Monto_full"]
    
                    df_crono["MontoLabel"] = df_crono.apply(_pick_label, axis=1)
    
    
                    # === Filtro: mostrar solo 'Ahora' y/o monto ≠ 0 (para el gráfico) + ORDEN DEL EJE Y
                    with st.expander("🔎 Filtros del Cronograma", expanded=True):
                        show_only_version_now = st.toggle(
                            "Mostrar solo versión 'Ahora'",
                            value=False,
                            help="Oculta las barras de 'Antes' y muestra únicamente las actividades/hitos actuales."
                        )
                        only_nonzero_amounts = st.toggle(
                            "Mostrar solo actividades/hitos con monto distinto de cero",
                            value=False,
                            help="Oculta barras con monto 0 o sin monto."
                        )
    
                        # --- NUEVO: orden del eje Y
                        modo_orden_y = st.radio(
                            "Ordenar actividades en el eje Y por:",
                            options=["Por ID de actividad", "Por fecha de inicio (antiguas arriba)"],
                            index=0,
                            horizontal=True,
                            key=f"orden_y_{_fmt_id_meta(id_meta_sel)}"
                        )
                        
    
                    df_crono["Monto_val"] = pd.to_numeric(
                        df_crono.get("Monto Actividad / Hito", pd.Series([None]*len(df_crono))),
                        errors="coerce"
                    ).fillna(0.0)
    
                    # Dataset a graficar aplicando filtros
                    df_crono_plot = df_crono.copy()
                    for c in ["Fecha de Inicio", "Fecha de Termino"]:
                        df_crono_plot[c] = pd.to_datetime(df_crono_plot[c], dayfirst=True, errors="coerce")
    
                    # Si alguna fila no tiene fin, opcionalmente ocúltala del hover:
                    df_crono_plot["FechaTermino_safe"] = df_crono_plot["Fecha de Termino"].fillna(df_crono_plot["Fecha de Inicio"])
    
                    if show_only_version_now:
                        df_crono_plot = df_crono_plot[df_crono_plot["Versión"] == "Ahora"]
                    if only_nonzero_amounts:
                        df_crono_plot = df_crono_plot[df_crono_plot["Monto_val"].abs() > 0]
    
                    if df_crono_plot.empty:
                        st.info("No hay actividades/hitos para los filtros actuales.")
                    else:
                        # === Construcción del orden del eje Y según la opción elegida
                        if modo_orden_y == "Por ID de actividad":
                            # Orden por clave numérica (como antes)
                            orden_y = (
                                df_crono_plot
                                .sort_values(["Clave Num", "Versión"], kind="stable")
                                ["EtiquetaY"].tolist()
                            )
                        else:
                            # Orden por fecha de inicio (antiguas arriba)
                            base_orden = df_crono_plot.copy()
                            base_orden["Inicio"] = pd.to_datetime(base_orden["Fecha de Inicio"], errors="coerce")
                            aux = (
                                base_orden.groupby("EtiquetaY", as_index=False)["Inicio"].min()
                                .assign(_orden=lambda d: d["Inicio"].fillna(pd.Timestamp.max))
                                .sort_values("_orden", ascending=True, kind="stable")
                            )
                            orden_y = aux["EtiquetaY"].tolist()
    
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
                            custom_data=["Tipo","Descripción","Monto_val","Fecha de Inicio","FechaTermino_safe"]
                        )
    
    
    
                        fig.update_xaxes(
                            dtick="M1",            # un tick por mes (no usa pandas.date_range)
                            tickformat="%b ’%y",   # Ene ’25, Feb ’25...
                            showgrid=True,
                                    gridwidth=1,
                                    gridcolor="light gray",
                                    griddash="dot"                           
                        )
    
                        # 2) Bandas mensuales alternadas (solo meses, sin semanas ni trimestres)
                        fig = agregar_bandas_mensuales(fig, df_crono_plot,
                                                    col_inicio="Fecha de Inicio",
                                                    col_fin="Fecha de Termino",
                                                    fill_rgba="rgba(0,0,0,0.035)")
    
    
                        # Tooltip con descripción completa + monto completo
                        fig.update_traces(
                        hovertemplate=(
                            "<b>Tipo:</b> %{customdata[0]}<br>"
                            "<b>Descripción:</b> %{customdata[1]}<br>"
                            "<b>Inicio:</b> %{customdata[3]|%d/%m/%Y}<br>"
                            "<b>Fin:</b> %{customdata[4]|%d/%m/%Y}<br>"
                            "<b>Monto:</b> $%{customdata[2]:,.2f} MXN"
                            "<extra></extra>"
                            ),
                            #texttemplate="%{text}",
                            textposition="inside",
                            insidetextanchor="middle",
                            textfont_size=11,
                            textfont_color="white",
                            cliponaxis=False,
                            marker_line_width=0,
                            texttemplate="<b>%{text}</b>",
                            textfont=dict(size=11)
                        )
    
    
                        fig.update_yaxes(
                            categoryorder="array",
                            categoryarray=orden_y,
                            autorange="reversed",
                            ticklabelposition="outside left",
                            automargin=True,
                            title="",
                            showgrid=True,
                                    gridwidth=1,
                                    gridcolor="light gray",
                                    griddash="solid",
                            tickson="boundaries"          
                        )
    
                        fig.update_layout(
                            height=altura,
                            margin=dict(l=180, r=20, t=60, b=40)
                        )
    
                        st.plotly_chart(fig, use_container_width=True)
    
                    # Fin del cronograma
    
    
    
    
            # ====== 3) Catálogo de partidas (COMPLETO, sin filtrar) ======
            with st.expander("📖 Catálogo de partidas (completo)"):
                q = st.text_input(
                    "Filtrar por código, definición o validador",
                    key=f"filtro_catalogo_full_{_fmt_id_meta(id_meta_sel)}"
                ).strip().lower()
    
                # Reusar columnas detectadas
                cat_full_cols = ["Partida_fmt"] + [c for c in [desc_col, restr_col, valid_col] if c]
                cat_full = CATALOGO_PARTIDAS[cat_full_cols].drop_duplicates().copy() if cat_full_cols else pd.DataFrame(columns=["Partida_fmt"])
    
                if q:
                    cat_show = cat_full[
                        cat_full.apply(
                            lambda r: q in f"{r.get('Partida_fmt','')} {r.get(desc_col,'')} {r.get(valid_col,'')}".lower(),
                            axis=1
                        )
                    ]
                else:
                    cat_show = cat_full
    
                vista_tabla = st.toggle("Ver como tabla compacta", value=False, key=f"vista_tabla_full_{_fmt_id_meta(id_meta_sel)}")
                if cat_show.empty:
                    st.markdown("_Sin coincidencias._")
                else:
                    if vista_tabla:
                        # Renombres seguros para mostrar
                        rename_map2 = {"Partida_fmt": "Código"}
                        if desc_col:  rename_map2[desc_col]  = "Definición"
                        if restr_col: rename_map2[restr_col] = "Restringida"
                        if valid_col: rename_map2[valid_col] = "Validador"
                        df_tabla = cat_show.rename(columns=rename_map2)
                        mostrar_cols = ["Código", "Definición"] + [c for c in ["Restringida", "Validador"] if c in df_tabla.columns]
                        st.dataframe(
                            df_tabla[mostrar_cols], use_container_width=True, hide_index=True,
                            column_config={
                                "Código": st.column_config.TextColumn(width="small"),
                                "Definición": st.column_config.TextColumn(width="large"),
                                **({"Restringida": st.column_config.CheckboxColumn("🔒", help="Requiere validador", disabled=True, width="small")} if "Restringida" in df_tabla.columns else {}),
                                **({"Validador": st.column_config.TextColumn(width="small")} if "Validador" in df_tabla.columns else {}),
                            }
                        )
                    else:
                        st.markdown('<div class="compact-list">', unsafe_allow_html=True)
                        for _, r in cat_show.iterrows():
                            lock = ""
                            if restr_col and bool(r.get(restr_col)):
                                val = r.get(valid_col) or "N/A"
                                lock = f' <span class="chip chip--lock">🔒 {val}</span>'
                            nom = r.get(desc_col, "")
                            st.markdown(
                                f"**{r.get('Partida_fmt','')}** · {nom}{lock}",
                                unsafe_allow_html=True
                            )
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
    
    
    
    #==========Bloque 5.1: Pestaña Beneficiarios ====================
    
    with tabs[2]:
        st.subheader("👥 Beneficiarios")
    
        # Si no hay datos, solo aviso
        if ("beneficiarios_df" not in locals()) or beneficiarios_df is None or beneficiarios_df.empty:
            st.info("Carga ambos cortes de **Detalle de Qs 2** en el panel lateral y selecciona una **Clave Q** para visualizar esta sección.")
        else:
            # Split por versión
            ben_a = beneficiarios_df[beneficiarios_df["Versión"] == "Antes"].copy()
            ben_h = beneficiarios_df[beneficiarios_df["Versión"] == "Ahora"].copy()
    
            # ===== Descripción del Beneficio =====
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
    
            # ===== Categorías =====
            st.markdown("#### 📊 Comparativo por categoría")
    
            categorias = [
                {"etq": "Beneficiarios Directos",
                 "nombre": "Nombre (Beneficiarios Directos)",
                 "carac": "Caracteristicas Generales (Beneficiarios Directos)",
                 "cant":  "Cantidad (Beneficiarios Directos)"},
                {"etq": "Población Objetivo",
                 "nombre": "Nombre (Población Objetivo)",
                 "carac": "Caracteristicas Generales (Población Objetivo)",
                 "cant":  "Cantidad (Población Objetivo)"},
                {"etq": "Población Universo",
                 "nombre": "Nombre (Población Universo)",
                 "carac": "Caracteristicas Generales (Población Universo)",
                 "cant":  "Cantidad (Población Universo)"},
                {"etq": "Beneficiarios Indirectos",
                 "nombre": "Nombre (Beneficiarios Indirectos)",
                 "carac": "Caracteristicas Generales (Beneficiarios Indirectos)",
                 "cant":  "Cantidad (Beneficiarios Indirectos)"},
            ]
    
            # --- Estilos globales (solo visual)
            st.markdown("""
            <style>
            .section-title { font-weight:700; font-size:1.05rem; margin: 6px 0 12px 0; display:flex; align-items:center; gap:.4rem; }
            .card { border: 1px solid #e6e7eb; border-radius: 12px; padding: 12px 14px; background:#fafbfd; margin-bottom:12px; }
            .label { font-size: .82rem; color:#475569; margin-bottom:6px; font-weight:600; }
            .kpi { border:1px solid #e5e7eb; background:#ffffff; border-radius:10px; padding:10px 12px; text-align:center; }
            .kpi .caption { font-size:.78rem; color:#64748b; margin-bottom:4px; }
            .kpi .value { font-size:1.05rem; font-weight:700; color:#0f172a; }
            .badge { display:inline-block; border-radius:999px; padding:.15rem .6rem; font-size:.74rem; font-weight:600; border:1px solid #e5e7eb; background:#f8fafc; color:#334155; }
            .diffbox { border:1px solid #e5e7eb; border-radius:8px; padding:8px; background:#ffffff; }
            </style>
            """, unsafe_allow_html=True)
    
            def _texto_o_diff(txt_a:str, txt_h:str):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"<span class='badge'>Antes</span>", unsafe_allow_html=True)
                    if str(txt_a) != str(txt_h):
                        a_html, _ = _diff_html(txt_a, txt_h)
                        st.markdown(f"<div class='diffbox'>{a_html}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='diffbox'>{html.escape(str(txt_a or ''))}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span class='badge'>Ahora</span>", unsafe_allow_html=True)
                    if str(txt_a) != str(txt_h):
                        _, h_html = _diff_html(txt_a, txt_h)
                        st.markdown(f"<div class='diffbox'>{h_html}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='diffbox'>{html.escape(str(txt_h or ''))}</div>", unsafe_allow_html=True)
    
            def _render_categoria(etq:str, col_nombre:str, col_carac:str, col_cant:str, ben_a:pd.DataFrame, ben_h:pd.DataFrame):
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='section-title'>👥 {etq}</div>", unsafe_allow_html=True)
    
                # Nombre
                nom_a = _first_nonempty(ben_a.get(col_nombre, pd.Series([], dtype=object))) if not ben_a.empty else ""
                nom_h = _first_nonempty(ben_h.get(col_nombre, pd.Series([], dtype=object))) if not ben_h.empty else ""
                st.markdown(f"<div class='label'>Nombre</div>", unsafe_allow_html=True)
                _texto_o_diff(nom_a, nom_h)
    
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    
                # Características
                car_a = _first_nonempty(ben_a.get(col_carac, pd.Series([], dtype=object))) if not ben_a.empty else ""
                car_h = _first_nonempty(ben_h.get(col_carac, pd.Series([], dtype=object))) if not ben_h.empty else ""
                st.markdown(f"<div class='label'>Características</div>", unsafe_allow_html=True)
                _texto_o_diff(car_a, car_h)
    
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    
                # Cantidades (solo valores)
                try:
                    q_a = float(pd.to_numeric(ben_a.get(col_cant, pd.Series([0])), errors="coerce").sum())
                except Exception:
                    q_a = 0.0
                try:
                    q_h = float(pd.to_numeric(ben_h.get(col_cant, pd.Series([0])), errors="coerce").sum())
                except Exception:
                    q_h = 0.0
    
                k1, k2 = st.columns(2)
                with k1:
                    st.markdown("<div class='kpi'><div class='caption'>Cantidad (Antes)</div><div class='value'>{:,.0f}</div></div>".format(q_a), unsafe_allow_html=True)
                with k2:
                    st.markdown("<div class='kpi'><div class='caption'>Cantidad (Ahora)</div><div class='value'>{:,.0f}</div></div>".format(q_h), unsafe_allow_html=True)
    
                st.markdown(f"</div>", unsafe_allow_html=True)  # /card
    
            # Render de todas las categorías
            for c in categorias:
                _render_categoria(c["etq"], c["nombre"], c["carac"], c["cant"], ben_a, ben_h)
    
    
    # ========= FIN BLOQUE 5 =========
  
    
    









