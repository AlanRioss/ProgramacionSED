"""
ui_components.py - CSS consolidado, tooltips y spell-check.

Cadena de dependencias: manual_extractos <- helpers <- loaders <- ui_components
"""

import streamlit as st
import html

from manual_extractos import MANUAL
from helpers import _fmt_id_meta, inferir_tipo_desde_clave_q, _ACCION_KEYS

# --- Import condicional de LanguageTool ---
try:
    import language_tool_python
except ImportError:
    language_tool_python = None

try:
    _LT_TOOL_ES = language_tool_python.LanguageTool("es") if language_tool_python is not None else None
except Exception:
    _LT_TOOL_ES = None


# ============ Mapeos ============

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


# ============ CSS ============

_CSS_MAIN = """
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

/* Spell-check wavy underline */
.spell-error {
    text-decoration-line: underline;
    text-decoration-style: wavy;
    text-decoration-color: #ef4444;
    text-decoration-thickness: 1.5px;
}

/* Cronograma tooltip styles */
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
"""


def inject_css():
    """Inyecta el CSS consolidado de la app (llamar una sola vez al inicio)."""
    st.markdown(_CSS_MAIN, unsafe_allow_html=True)


# ============ Tooltips ============

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
        unsafe_allow_html=True,
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
        unsafe_allow_html=True,
    )


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
        unsafe_allow_html=True,
    )


# ============ Cronograma tooltip ============

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

    tipos = manual_crono.get("tipos_proyecto", {}) or {}
    ref = manual_crono.get("referencia", "")

    tipo_base = inferir_tipo_desde_clave_q(clave_q)

    with st.expander("ℹ️ Elementos de Cronograma (Guía rápida)", expanded=False):
        st.markdown("<div class='crono-tip'>", unsafe_allow_html=True)

        if tipo_base == "Accion":
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
            if tipo_base and tipo_base in tipos:
                st.markdown("<div class='crono-title'>Componentes sugeridos (según tipo de proyecto):</div>", unsafe_allow_html=True)
                st.markdown("<div class='crono-section'>", unsafe_allow_html=True)
                _render_bullets(tipos[tipo_base])
                st.markdown("</div>", unsafe_allow_html=True)

            otros = {k: v for k, v in tipos.items() if k != tipo_base}
            if otros:
                st.markdown("<div class='crono-title'>Otros tipos de referencia:</div>", unsafe_allow_html=True)
                for k, items in otros.items():
                    with st.expander(k, expanded=False):
                        _render_bullets(items)

        if ref:
            st.caption(ref)

        st.markdown("</div>", unsafe_allow_html=True)


# ============ Spell-check ============

@st.cache_data(show_spinner=False)
def resaltar_ortografia_html(texto: str) -> str:
    """
    Devuelve el texto en HTML, subrayando en rojo ondulado
    los posibles errores ortográficos/gramaticales.
    """
    s = str(texto or "")
    if not s:
        return ""
    if _LT_TOOL_ES is None:
        return html.escape(s)

    try:
        matches = _LT_TOOL_ES.check(s)
    except Exception:
        return html.escape(s)

    if not matches:
        return html.escape(s)

    partes = []
    ultimo = 0
    for m in matches:
        start = m.offset
        end = m.offset + m.errorLength
        if start < ultimo:
            continue
        partes.append(html.escape(s[ultimo:start]))
        partes.append(f"<span class='spell-error'>{html.escape(s[start:end])}</span>")
        ultimo = end

    partes.append(html.escape(s[ultimo:]))
    return "".join(partes)
