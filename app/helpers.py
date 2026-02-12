"""
helpers.py - Funciones puras de datos (sin streamlit).

Cadena de dependencias: manual_extractos <- helpers
"""

import pandas as pd
import numpy as np
import unicodedata
import re
import html
import difflib

# ============ Constantes ============

MESES_MONTO = [
    "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
    "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
    "Monto Octubre", "Monto Noviembre", "Monto Diciembre",
]

EPS_NUM = 1e-6  # umbral anti-ruido para comparar números

_Q_PREFIX_MAP = {
    "QA": "Obra",
    "QB": "Subprograma – Obra",
    "QC": "Accion",
    "QD": "Subprograma – Acción/Investigación (con servicios)",
}

_ACCION_KEYS = [
    "Subprograma – Acción (con apoyos)",
    "Subprograma – Acción (con adquisiciones)",
    "Subprograma – Acción/Investigación (con servicios)",
]


# ============ Formateo / normalización ============

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


def _fmt_meta_val(meta_col: str, x):
    """Formatea valor de meta según la llave (ID Meta o Clave de Meta)."""
    return _fmt_id_meta(x) if meta_col == "ID Meta" else ("" if pd.isna(x) else str(x))


def _limpiar_texto(x: str) -> str:
    if isinstance(x, str):
        x = unicodedata.normalize("NFKC", x)
        x = x.replace("\n", " ").replace("\r", " ").strip()
    return x


def _norm_simple(s):
    """Normalización simple: minúsculas, trim, colapsar espacios."""
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _norm_txt(s):
    """Normalización fuerte para matching de municipios: upper, sin diacríticos."""
    if pd.isna(s):
        return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s


def _norm_meta_val(meta_key: str, v):
    """Normaliza el valor de meta según la llave elegida."""
    if meta_key == "ID Meta":
        return _fmt_id_meta(v)
    if pd.isna(v):
        return ""
    return str(v).strip()


# ============ Utilidades de colecciones ============

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


# ============ Agregación por meta ============

def _agregar_por_meta_simple(df: pd.DataFrame, meta_key: str) -> pd.DataFrame:
    df = df.copy()
    if meta_key not in df.columns:
        return pd.DataFrame()

    df["llave_meta"] = df[meta_key].astype(str)

    num_cols = [
        "Cantidad Estatal", "Monto Estatal",
        "Cantidad Federal", "Monto Federal",
        "Cantidad Municipal", "Monto Municipal",
    ]
    for c in num_cols:
        if c not in df.columns:
            df[c] = 0
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    g = df.groupby("llave_meta", dropna=False)

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

    base["set_municipio"] = g["Municipio"].apply(_to_set) if "Municipio" in df.columns else g.size().apply(lambda _: set())
    base["set_rp"] = g["Registro Presupuestal"].apply(_to_set) if "Registro Presupuestal" in df.columns else g.size().apply(lambda _: set())

    base["desc_norm"] = base["Descripción de la Meta"].apply(_norm_simple) if "Descripción de la Meta" in base.columns else ""
    base["um_norm"] = base["Unidad de Medida"].apply(_norm_simple) if "Unidad de Medida" in base.columns else ""

    base = base.reset_index()
    return base


def construir_control_cambios_metas_info(metas_antes: pd.DataFrame, metas_ahora: pd.DataFrame, meta_key: str) -> pd.DataFrame:
    A = _agregar_por_meta_simple(metas_antes, meta_key)
    H = _agregar_por_meta_simple(metas_ahora, meta_key)

    df = pd.merge(A, H, on="llave_meta", how="outer", suffixes=("_A", "_H"))

    for col in ["set_municipio_A", "set_municipio_H", "set_rp_A", "set_rp_H"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: x if isinstance(x, set)
                else (set() if pd.isna(x) else {str(x).strip()} if str(x).strip() else set())
            )

    solo_ahora = df["llave_meta"].notna() & df["ID Meta_A"].isna() & df["ID Meta_H"].notna()
    solo_antes = df["llave_meta"].notna() & df["ID Meta_A"].notna() & df["ID Meta_H"].isna()
    en_ambas = df["ID Meta_A"].notna() & df["ID Meta_H"].notna()

    desc_changed = en_ambas & (df.get("desc_norm_A", "") != df.get("desc_norm_H", ""))
    um_changed = en_ambas & (df.get("um_norm_A", "") != df.get("um_norm_H", ""))

    def _sets_changed(row, col):
        a = row.get(col + "_A", set()) or set()
        h = row.get(col + "_H", set()) or set()
        return (a ^ h) != set()

    muni_changed = df.apply(lambda r: _sets_changed(r, "set_municipio"), axis=1) & en_ambas
    rp_changed = df.apply(lambda r: _sets_changed(r, "set_rp"), axis=1) & en_ambas

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

    estado = np.where(solo_ahora, "✚ Nueva",
              np.where(solo_antes, "✖ Eliminada",
              np.where(
                  desc_changed | um_changed | muni_changed | rp_changed |
                  c_est_changed | m_est_changed | c_fed_changed | m_fed_changed | c_mun_changed | m_mun_changed,
                  "✎ Modificada", "✔ Sin cambios"
              )))

    id_visible = df["ID Meta_H"].fillna(df["ID Meta_A"])
    clave_meta_vis = df.get("Clave de Meta_H", pd.Series(dtype=object)).fillna(df.get("Clave de Meta_A", ""))

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

    def mark(s):
        return np.where(s, "●", "○")

    out = pd.DataFrame({
        "Estado": estado,
        "ID Meta": id_visible.astype(str),
        "Clave de Meta": clave_meta_vis.astype(str),
        "Desc": mark(desc_changed | solo_ahora | solo_antes),
        "UM": mark(um_changed | solo_ahora | solo_antes),
        "Municipios": mark(muni_changed | solo_ahora | solo_antes),
        "RP": mark(rp_changed | solo_ahora | solo_antes),
        "Cant. Est.": mark(c_est_changed | solo_ahora | solo_antes),
        "Mto. Est.": mark(m_est_changed | solo_ahora | solo_antes),
        "Cant. Fed.": mark(c_fed_changed | solo_ahora | solo_antes),
        "Mto. Fed.": mark(m_fed_changed | solo_ahora | solo_antes),
        "Cant. Mun.": mark(c_mun_changed | solo_ahora | solo_antes),
        "Mto. Mun.": mark(m_mun_changed | solo_ahora | solo_antes),
        "Δ total $": delta_total,
    })

    cat = pd.CategoricalDtype(["✚ Nueva", "✖ Eliminada", "✎ Modificada", "✔ Sin cambios"], ordered=True)
    out["Estado"] = out["Estado"].astype(cat)
    out = out.sort_values(["Estado", "Δ total $"], ascending=[True, False]).reset_index(drop=True)

    return out


# ============ Inferencia de tipo de proyecto ============

def inferir_tipo_desde_clave_q(clave_q: str) -> str:
    if not clave_q:
        return ""
    pref = str(clave_q).strip().upper()[:2]
    return _Q_PREFIX_MAP.get(pref, "")


# ============ Municipios en meta ============

def marcar_municipios_en_meta(gdf, name_col, municipios_meta):
    """
    gdf: GeoDataFrame del shapefile
    name_col: columna con el nombre del municipio en el shapefile
    municipios_meta: lista de strings o string con municipios separados por comas
    """
    if isinstance(municipios_meta, str):
        partes = re.split(r",|;|/|\||\s+y\s", municipios_meta, flags=re.IGNORECASE)
        municipios = [p.strip() for p in partes if p and p.strip()]
    elif isinstance(municipios_meta, (list, tuple, set)):
        municipios = list(municipios_meta)
    else:
        municipios = []

    municipios_norm = {_norm_txt(x) for x in municipios if x}

    if any(_norm_txt(x) == "COBERTURA ESTATAL" for x in municipios_norm):
        gdf = gdf.copy()
        gdf["en_meta"] = True
        return gdf

    if (not municipios_norm) or any(_norm_txt(x) == "POR DETERMINAR" for x in municipios_norm):
        gdf = gdf.copy()
        gdf["en_meta"] = False
        return gdf

    gdf = gdf.copy()
    gdf["_name_norm"] = gdf[name_col].astype(str).map(_norm_txt)
    gdf["en_meta"] = gdf["_name_norm"].isin(municipios_norm)
    return gdf


# ============ Formateo compacto ============

def _kmb(v: float) -> str:
    """Formateo compacto K/M/B para narrativas o métricas."""
    try:
        x = float(v)
    except Exception:
        return "—"
    a = abs(x)
    if a >= 1_000_000_000:
        return f"${x/1_000_000_000:.2f}B"
    if a >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if a >= 1_000:
        return f"${x/1_000:.0f}K"
    return f"${x:,.0f}"


def _partida_fmt4(x):
    """Devuelve la partida a 4 dígitos o None si no se puede parsear."""
    try:
        if pd.isna(x) or str(x).strip() == "":
            return None
        return str(int(float(x)))[:4]
    except Exception:
        return None


# ============ Diff HTML ============

def _diff_html(a: str, b: str) -> tuple[str, str]:
    """Resalta diferencias (Antes vs Ahora) con difflib."""
    a = html.escape(str(a or ""))
    b = html.escape(str(b or ""))
    if a == b:
        return a, b
    matcher = difflib.SequenceMatcher(None, a, b)
    res_a, res_b = "", ""
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            res_a += a[i1:i2]
            res_b += b[j1:j2]
        elif tag == "replace":
            res_a += f"<del style='color:#b91c1c'>{a[i1:i2]}</del>"
            res_b += f"<span style='background-color:#dcfce7'>{b[j1:j2]}</span>"
        elif tag == "delete":
            res_a += f"<del style='color:#b91c1c'>{a[i1:i2]}</del>"
        elif tag == "insert":
            res_b += f"<span style='background-color:#dcfce7'>{b[j1:j2]}</span>"
    return res_a, res_b
