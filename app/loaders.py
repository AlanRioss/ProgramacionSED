"""
loaders.py - Funciones @st.cache_data de carga de datos.

Cadena de dependencias: manual_extractos <- helpers <- loaders
"""

import json
import pathlib

import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta

from helpers import (
    _fmt_id_meta, _norm_meta_val, _limpiar_texto,
    _first_nonempty, _norm_simple,
    construir_control_cambios_metas_info,
)

# --- Import condicional de geopandas / folium / streamlit_folium ---
try:
    import geopandas as gpd
    _HAS_GPD = True
except ImportError:
    gpd = None
    _HAS_GPD = False

try:
    import folium
    from streamlit_folium import st_folium
    _HAS_FOLIUM = True
except ImportError:
    folium = None
    st_folium = None
    _HAS_FOLIUM = False


# ============ Constante unificada (antes duplicada en L786 y L875) ============

COLUMNAS_DATOS_GENERALES = [
    "Fecha", "Clave Q", "Nombre del Proyecto (Ejercicio Actual)", "Eje", "Dep Siglas",
    "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
    "Descripción del Avance Actual", "Alcance Anual",
]

COLUMNAS_METAS = [
    "Clave Q", "ID Meta", "Clave de Meta", "Descripción de la Meta", "Unidad de Medida",
    "ID Mpio", "Municipio", "Registro Presupuestal",
    "Cantidad Estatal", "Monto Estatal",
    "Cantidad Federal", "Monto Federal",
    "Cantidad Municipal", "Monto Municipal",
    "Cantidad Ingresos Propios", "Monto Ingresos Propios",
    "Cantidad Otros", "Monto Otros",
]

COLUMNAS_PARTIDAS = [
    "Clave Q", "ID Meta", "Clave de Meta", "Clave de Actividad /Hito", "Descripción",
    "Partida", "Monto Anual",
    "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
    "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
    "Monto Octubre", "Monto Noviembre", "Monto Diciembre",
]

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
    "Caracteristicas Generales (Beneficiarios Indirectos)",
]

_COLUMNAS_TEXTO = [
    "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
    "Descripción del Avance Actual", "Alcance Anual",
]


# ============ Funciones de carga ============

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
        "Monto Actividad / Hito",
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


@st.cache_data(show_spinner=False)
def cargar_shapefile_municipal():
    """Carga el shapefile municipal. Devuelve GeoDataFrame o None si geopandas no está."""
    if not _HAS_GPD:
        return None
    try:
        gdf = gpd.read_file("app/gtoSHP/mun_test_wgs.shp").to_crs(epsg=4326)
        return gdf
    except Exception as e:
        st.error(f"Error al cargar el shapefile: {e}")
        return None


_GEOJSON_PATH = pathlib.Path("app/gtoSHP/mun_test_wgs.geojson")


@st.cache_data(show_spinner=False)
def cargar_geojson_municipal() -> dict | None:
    """Carga el GeoJSON municipal (no requiere geopandas)."""
    try:
        with open(_GEOJSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def _prep_beneficiarios_unificado(ben_antes: pd.DataFrame, ben_ahora: pd.DataFrame) -> pd.DataFrame:
    """
    Une cortes Antes/Ahora en un solo DF largo con columna 'Versión'.
    """
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
            return pd.DataFrame(columns=cols_std)
        df = df.copy()
        for c in cols_std:
            if c not in df.columns:
                df[c] = pd.NA
        text_cols = [c for c in cols_std if (c != "Clave Q" and not c.startswith("Cantidad ("))]
        for c in text_cols:
            try:
                df[c] = df[c].apply(_limpiar_texto)
            except Exception:
                df[c] = df[c].astype(str).str.replace("\n", " ").str.replace("\r", " ").str.strip()
        df["Clave Q"] = df["Clave Q"].astype(str).str.strip()
        qty_cols = [c for c in cols_std if c.startswith("Cantidad (")]
        for c in qty_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)
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
    return out[cols_std + ["Versión"]]


def agregar_bandas_mensuales(fig, df, col_inicio="Fecha de Inicio", col_fin="Fecha de Termino",
                             fill_rgba="rgba(0,0,0,0.04)"):
    """Agrega bandas verticales alternadas por mes al fondo del Gantt."""
    if df.empty or col_inicio not in df or col_fin not in df:
        return fig

    x0 = pd.to_datetime(df[col_inicio], errors="coerce").min()
    x1 = pd.to_datetime(df[col_fin], errors="coerce").max()
    if pd.isna(x0) or pd.isna(x1):
        return fig

    start = pd.Timestamp(x0.year, x0.month, 1)
    end = pd.Timestamp(x1.year, x1.month, 1) + relativedelta(months=1)

    meses = pd.date_range(start, end, freq="MS")
    if len(meses) <= 1:
        return fig

    shapes = list(getattr(fig.layout, "shapes", []))
    toggle = False
    for i in range(len(meses) - 1):
        if toggle:
            shapes.append(dict(
                type="rect",
                xref="x", yref="paper",
                x0=meses[i], x1=meses[i + 1],
                y0=0, y1=1,
                fillcolor=fill_rgba,
                line=dict(width=0),
                layer="below",
            ))
        toggle = not toggle

    fig.update_layout(shapes=shapes)
    return fig


# ============ Funciones de vista cacheadas ============

@st.cache_data(show_spinner=False)
def _info_meta(df_antes: pd.DataFrame, df_ahora: pd.DataFrame, meta_key: str, meta_val: str):
    if meta_key not in df_antes.columns or meta_key not in df_ahora.columns:
        return pd.DataFrame(), pd.DataFrame()

    def _norm(v):
        return _fmt_id_meta(v) if meta_key == "ID Meta" else ("" if pd.isna(v) else str(v))

    f_ahora = df_ahora[df_ahora[meta_key].apply(_norm) == meta_val]
    f_antes = df_antes[df_antes[meta_key].apply(_norm) == meta_val]
    return f_antes.copy(), f_ahora.copy()


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

    res_a = df_a.groupby("Municipio")[usar_cols].sum(min_count=1).reset_index() if not df_a.empty else pd.DataFrame(columns=["Municipio"] + usar_cols)
    res_h = df_h.groupby("Municipio")[usar_cols].sum(min_count=1).reset_index() if not df_h.empty else pd.DataFrame(columns=["Municipio"] + usar_cols)

    res_a = res_a.rename(columns={c: f"{c} (Antes)" for c in usar_cols})
    res_h = res_h.rename(columns={c: f"{c} (Ahora)" for c in usar_cols})
    comp = pd.merge(res_a, res_h, on="Municipio", how="outer").fillna(0)

    orden_cols = ["Municipio"]
    for base in ["Estatal", "Federal", "Municipal"]:
        for pref in ["Cantidad", "Monto"]:
            a, h = f"{pref} {base} (Antes)", f"{pref} {base} (Ahora)"
            if a in comp.columns:
                orden_cols.append(a)
            if h in comp.columns:
                orden_cols.append(h)
    return comp[orden_cols]


@st.cache_data(show_spinner=False)
def _partidas_resumen(pa: pd.DataFrame, ph: pd.DataFrame, id_meta_str: str | None, meta_key: str):
    """Devuelve: comp, df_mensual, a, h"""
    meses_cols = [
        "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
        "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
        "Monto Octubre", "Monto Noviembre", "Monto Diciembre",
    ]

    a = pa.copy()
    h = ph.copy()

    if id_meta_str:
        target = str(id_meta_str)
        a = a[a[meta_key].apply(lambda v: _norm_meta_val(meta_key, v)) == target]
        h = h[h[meta_key].apply(lambda v: _norm_meta_val(meta_key, v)) == target]

    for dfp in (a, h):
        if "Partida" in dfp.columns:
            dfp["Partida_fmt"] = dfp["Partida"].apply(
                lambda x: str(int(float(x)))[:4] if pd.notnull(x) and str(x).strip() != "" else None
            )
    a = a[a.get("Partida_fmt").notna()] if "Partida_fmt" in a.columns else a
    h = h[h.get("Partida_fmt").notna()] if "Partida_fmt" in h.columns else h

    res_h = (h.groupby("Partida_fmt")["Monto Anual"].sum().reset_index()
             .rename(columns={"Monto Anual": "Monto Anual (Ahora)"})) if not h.empty else pd.DataFrame(columns=["Partida_fmt", "Monto Anual (Ahora)"])
    res_a = (a.groupby("Partida_fmt")["Monto Anual"].sum().reset_index()
             .rename(columns={"Monto Anual": "Monto Anual (Antes)"})) if not a.empty else pd.DataFrame(columns=["Partida_fmt", "Monto Anual (Antes)"])
    comp = pd.merge(res_a, res_h, on="Partida_fmt", how="outer").fillna(0)
    if not comp.empty:
        comp["Diferencia"] = comp["Monto Anual (Ahora)"] - comp["Monto Anual (Antes)"]

    sum_m_ahora = h[meses_cols].sum(numeric_only=True) if not h.empty else pd.Series([0] * 12, index=meses_cols)
    sum_m_antes = a[meses_cols].sum(numeric_only=True) if not a.empty else pd.Series([0] * 12, index=meses_cols)
    df_mensual = pd.DataFrame({
        "Mes": [m.replace("Monto ", "") for m in meses_cols],
        "Antes": sum_m_antes.values,
        "Ahora": sum_m_ahora.values,
    })

    return comp, df_mensual, a, h


@st.cache_data(show_spinner=False)
def _cronograma_df(cr_a: pd.DataFrame, cr_h: pd.DataFrame, meta_key: str, meta_val: str) -> pd.DataFrame:
    def _norm(v):
        return _fmt_id_meta(v) if meta_key == "ID Meta" else ("" if pd.isna(v) else str(v))

    a = cr_a[cr_a[meta_key].apply(_norm) == meta_val].copy()
    h = cr_h[cr_h[meta_key].apply(_norm) == meta_val].copy()
    if a.empty and h.empty:
        return pd.DataFrame()
    a["Versión"] = "Antes"
    h["Versión"] = "Ahora"
    out = pd.concat([a, h], ignore_index=True)
    out["Clave Num"] = pd.to_numeric(out.get("Clave de Actividad /Hito"), errors="coerce")
    mismo_dia = (out["Fecha de Inicio"] == out["Fecha de Termino"])
    out.loc[mismo_dia, "Fecha de Termino"] = out.loc[mismo_dia, "Fecha de Termino"] + pd.Timedelta(days=1)
    return out


@st.cache_data(show_spinner=False)
def _cumplimiento_df(ca: pd.DataFrame, ch: pd.DataFrame, meta_col: str, id_meta_str: str):
    a = ca[ca[meta_col].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()
    h = ch[ch[meta_col].apply(_fmt_id_meta) == _fmt_id_meta(id_meta_str)].copy()
    return a, h


# ============ Funciones cacheadas de alto nivel ============

@st.cache_data(show_spinner="Procesando datos del proyecto…")
def cargar_proyecto_filtrado(archivo_antes, archivo_ahora, clave_q, llave_opcion):
    """Carga, limpia y filtra todos los DataFrames para un proyecto (Clave Q).

    Agrupa la lectura de todas las hojas + limpieza de texto + filtrado
    en una sola función cacheada, eliminando recálculos en cada rerun.
    """
    META_COL = "ID Meta" if llave_opcion == "No, usar ID Meta" else "Clave de Meta"

    # 1) Datos Generales
    datos_ahora = cargar_hoja(archivo_ahora, "Datos Generales", COLUMNAS_DATOS_GENERALES)
    datos_antes = cargar_hoja(archivo_antes, "Datos Generales", COLUMNAS_DATOS_GENERALES)

    for col in _COLUMNAS_TEXTO:
        if col in datos_ahora.columns:
            datos_ahora[col] = datos_ahora[col].astype(str).map(_limpiar_texto)
        if col in datos_antes.columns:
            datos_antes[col] = datos_antes[col].astype(str).map(_limpiar_texto)

    datos_ahora = datos_ahora[datos_ahora["Clave Q"] == clave_q]
    datos_antes = datos_antes[datos_antes["Clave Q"] == clave_q]

    # 2) Metas
    metas_ahora = agregar_totales(cargar_hoja(archivo_ahora, "Sección de Metas", COLUMNAS_METAS))
    metas_antes = agregar_totales(cargar_hoja(archivo_antes, "Sección de Metas", COLUMNAS_METAS))
    metas_ahora = metas_ahora[metas_ahora["Clave Q"] == clave_q]
    metas_antes = metas_antes[metas_antes["Clave Q"] == clave_q]

    # 3) Cronograma
    crono_ahora = cargar_cronograma(archivo_ahora)
    crono_antes = cargar_cronograma(archivo_antes)
    crono_ahora = crono_ahora[crono_ahora["Clave Q"] == clave_q]
    crono_antes = crono_antes[crono_antes["Clave Q"] == clave_q]

    # 4) Partidas
    partidas_ahora = cargar_hoja(archivo_ahora, "Sección de Metas-Partidas", COLUMNAS_PARTIDAS)
    partidas_antes = cargar_hoja(archivo_antes, "Sección de Metas-Partidas", COLUMNAS_PARTIDAS)
    partidas_ahora = partidas_ahora[partidas_ahora["Clave Q"] == clave_q]
    partidas_antes = partidas_antes[partidas_antes["Clave Q"] == clave_q]

    # 5) Cumplimiento
    COLUMNAS_CUMPLIMIENTO = (
        [META_COL, "Clave de Meta", "Cantidad"] +
        [f"Cumplimiento {mes}" for mes in [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
        ]]
    )
    cumplimiento_ahora = cargar_hoja(archivo_ahora, "Sección de Metas-Cumplimiento", COLUMNAS_CUMPLIMIENTO).copy()
    cumplimiento_antes = cargar_hoja(archivo_antes, "Sección de Metas-Cumplimiento", COLUMNAS_CUMPLIMIENTO).copy()

    meta_col_ok = META_COL in cumplimiento_ahora.columns and META_COL in cumplimiento_antes.columns
    if meta_col_ok:
        cumplimiento_ahora = cumplimiento_ahora.dropna(subset=[META_COL])
        cumplimiento_antes = cumplimiento_antes.dropna(subset=[META_COL])

    # Nombre del proyecto
    nombre_vals = datos_ahora["Nombre del Proyecto (Ejercicio Actual)"].values
    nombre_proyecto = nombre_vals[0] if len(nombre_vals) else ""

    return {
        "META_COL": META_COL,
        "meta_col_ok": meta_col_ok,
        "nombre_proyecto": nombre_proyecto,
        "datos_ahora": datos_ahora,
        "datos_antes": datos_antes,
        "metas_ahora": metas_ahora,
        "metas_antes": metas_antes,
        "crono_ahora": crono_ahora,
        "crono_antes": crono_antes,
        "partidas_ahora": partidas_ahora,
        "partidas_antes": partidas_antes,
        "cumplimiento_ahora": cumplimiento_ahora,
        "cumplimiento_antes": cumplimiento_antes,
    }


@st.cache_data(show_spinner=False)
def cargar_beneficiarios_filtrado(ben_antes_file, ben_ahora_file, clave_q):
    """Carga y filtra datos de beneficiarios por Clave Q."""
    if ben_ahora_file is not None:
        try:
            ben_ahora = cargar_hoja(ben_ahora_file, "Beneficiarios", COLUMNAS_BENEFICIARIOS).copy()
        except Exception:
            ben_ahora = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)
    else:
        ben_ahora = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)

    if ben_antes_file is not None:
        try:
            ben_antes = cargar_hoja(ben_antes_file, "Beneficiarios", COLUMNAS_BENEFICIARIOS).copy()
        except Exception:
            ben_antes = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)
    else:
        ben_antes = pd.DataFrame(columns=COLUMNAS_BENEFICIARIOS)

    if not ben_ahora.empty:
        ben_ahora = ben_ahora[ben_ahora["Clave Q"] == clave_q]
    if not ben_antes.empty:
        ben_antes = ben_antes[ben_antes["Clave Q"] == clave_q]

    return _prep_beneficiarios_unificado(ben_antes, ben_ahora)


@st.cache_data(show_spinner=False)
def control_cambios_metas_cached(metas_antes: pd.DataFrame, metas_ahora: pd.DataFrame, meta_key: str) -> pd.DataFrame:
    """Wrapper cacheado de construir_control_cambios_metas_info."""
    return construir_control_cambios_metas_info(metas_antes, metas_ahora, meta_key)
