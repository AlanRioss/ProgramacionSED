"""
tab_metas.py - Tab 2 completo (3 subtabs: Info Meta, Cronograma/Partidas, Cumplimiento).

Cadena de dependencias: manual_extractos <- helpers <- loaders <- ui_components <- tab_metas
"""

import re
import html as _html_mod

import streamlit as st
import pandas as pd
import plotly.express as px

from manual_extractos import MANUAL
from catalogo_partidas import CATALOGO_PARTIDAS

from helpers import (
    _fmt_id_meta, _fmt_meta_val, _diff_html, _norm_meta_val, _norm_txt,
)
from loaders import (
    _info_meta, _resumen_municipal, _partidas_resumen,
    _cronograma_df, _cumplimiento_df, agregar_bandas_mensuales,
    control_cambios_metas_cached, cargar_geojson_municipal,
)
from ui_components import (
    header_with_tooltip_meta, header_with_tooltip_distribucion,
    render_tooltip_cronograma_qaware,
)



def _fila_cambio_html(tipo: str, id_val: str, extra: str, monto_str: str, positivo: bool, campos: str | None = None) -> str:
    clase_amt = "chg-amt--pos" if positivo else "chg-amt--neg"
    extra_html = f" <span class='chg-extra'>{_html_mod.escape(extra)}</span>" if extra else ""
    campos_html = f"<div class='chg-fields'>Campos modificados: {_html_mod.escape(campos)}</div>" if campos else ""
    return (
        f"<div class='chg-row chg-row--{tipo}'>"
        f"<div><div class='chg-main'><b>{_html_mod.escape(id_val)}</b>{extra_html}</div>{campos_html}</div>"
        f"<div class='chg-amt {clase_amt}'>{_html_mod.escape(monto_str)}</div>"
        f"</div>"
    )


def _render_resumen_cambios(tabla_cc: pd.DataFrame, meta_key: str) -> None:
    """Resumen programático de cambios entre cortes (sin API externa)."""
    CAMPOS_LEGIBLES = {
        "Desc":       "Descripción",
        "UM":         "Unidad de medida",
        "Municipios": "Municipios",
        "RP":         "Registro presupuestal",
        "Cant. Est.": "Cantidad estatal",
        "Mto. Est.":  "Monto estatal",
        "Cant. Fed.": "Cantidad federal",
        "Mto. Fed.":  "Monto federal",
        "Cant. Mun.": "Cantidad municipal",
        "Mto. Mun.":  "Monto municipal",
    }

    n_nuevas      = int((tabla_cc["Estado"] == "✚ Nueva").sum())
    n_eliminadas  = int((tabla_cc["Estado"] == "✖ Eliminada").sum())
    n_modificadas = int((tabla_cc["Estado"] == "✎ Modificada").sum())
    n_sin_cambios = int((tabla_cc["Estado"] == "✔ Sin cambios").sum())
    n_total       = n_nuevas + n_eliminadas + n_modificadas
    delta_total   = float(tabla_cc["Δ total $"].sum()) if "Δ total $" in tabla_cc.columns else 0.0

    other_key = "Clave de Meta" if meta_key == "ID Meta" else "ID Meta"

    def _id_line(row):
        id_val    = str(row.get(meta_key, "?")).strip()
        other_val = str(row.get(other_key, "")).strip()
        extra = f"· {other_key}: {other_val}" if other_val not in ("", "nan") else ""
        return id_val, extra

    # --- Balance neto (siempre visible) ---
    signo = "+" if delta_total >= 0 else ""
    color = "#2e7d32" if delta_total >= 0 else "#c62828"
    sin_cambios_txt = f" &nbsp;·&nbsp; <span style='color:#6b7280'>{n_sin_cambios} sin cambios</span>" if n_sin_cambios else ""
    st.markdown(
        f"**Balance neto de monto:** "
        f"<span style='color:{color}; font-weight:bold'>{signo}${delta_total:,.0f} MXN</span>"
        f"{sin_cambios_txt}",
        unsafe_allow_html=True,
    )

    if n_total == 0:
        st.success("No hubo cambios entre cortes.")
        return

    st.markdown("---")

    # --- Chips de filtro ---
    opciones = [f"Todas · {n_total}"]
    if n_nuevas:
        opciones.append(f"🆕 Nuevas · {n_nuevas}")
    if n_eliminadas:
        opciones.append(f"🗑️ Eliminadas · {n_eliminadas}")
    if n_modificadas:
        opciones.append(f"🔄 Modificadas · {n_modificadas}")

    if len(opciones) > 1:
        filtro = st.pills(
            "Filtrar por tipo de cambio", opciones, default=opciones[0], label_visibility="collapsed",
        ) or opciones[0]
    else:
        filtro = opciones[0]

    ver_nuevas      = filtro.startswith("Todas") or filtro.startswith("🆕")
    ver_eliminadas  = filtro.startswith("Todas") or filtro.startswith("🗑️")
    ver_modificadas = filtro.startswith("Todas") or filtro.startswith("🔄")

    filas = []

    if ver_nuevas and n_nuevas:
        for _, row in tabla_cc[tabla_cc["Estado"] == "✚ Nueva"].iterrows():
            id_val, extra = _id_line(row)
            delta = float(row.get("Δ total $", 0) or 0)
            filas.append(_fila_cambio_html("nueva", id_val, extra, f"+${delta:,.0f} MXN", True))

    if ver_eliminadas and n_eliminadas:
        for _, row in tabla_cc[tabla_cc["Estado"] == "✖ Eliminada"].iterrows():
            id_val, extra = _id_line(row)
            delta = float(row.get("Δ total $", 0) or 0)
            filas.append(_fila_cambio_html("eliminada", id_val, extra, f"−${abs(delta):,.0f} MXN", False))

    if ver_modificadas and n_modificadas:
        modificadas = (
            tabla_cc[tabla_cc["Estado"] == "✎ Modificada"]
            .assign(_abs=tabla_cc["Δ total $"].abs())
            .sort_values("_abs", ascending=False)
        )
        for _, row in modificadas.iterrows():
            id_val, extra = _id_line(row)
            delta = float(row.get("Δ total $", 0) or 0)
            campos = [desc for col, desc in CAMPOS_LEGIBLES.items() if row.get(col) == "●"]
            monto_str = f"{'+' if delta >= 0 else '−'}${abs(delta):,.0f} MXN" if delta != 0 else "Sin cambio de monto"
            filas.append(_fila_cambio_html(
                "modificada", id_val, extra, monto_str, delta >= 0,
                campos=", ".join(campos) if campos else "—",
            ))

    if filas:
        st.markdown("".join(filas), unsafe_allow_html=True)
    else:
        st.markdown("<div class='chg-empty'>Sin resultados para este filtro.</div>", unsafe_allow_html=True)


@st.fragment
def _metas_body(metas_antes, metas_ahora, crono_antes, crono_ahora,
                partidas_antes, partidas_ahora, cumpl_antes, cumpl_ahora,
                META_COL, clave_q):
    """Contenido interactivo del tab Metas (fragment para evitar reset de tabs principales)."""

    if metas_antes.empty:
        st.info("🆕 Este proyecto no existía en el corte anterior. Se muestran solo las metas actuales.")

    # ========== Resumen de cambios ==========
    st.markdown("#### 📊 Resumen de cambios – Metas")
    st.caption("Comparativo a nivel proyecto (corte Antes vs Ahora).")
    tabla_cc = control_cambios_metas_cached(metas_antes, metas_ahora, META_COL)
    _render_resumen_cambios(tabla_cc, META_COL)
    st.markdown("---")

    # ========== Selector de meta ==========
    metas_disponibles = (
        metas_ahora[[META_COL, "Descripción de la Meta"]]
        .dropna(subset=[META_COL])
        .drop_duplicates()
        .copy()
    )
    # Filtrar también filas con valores vacíos o solo espacios
    metas_disponibles = metas_disponibles[
        metas_disponibles[META_COL].astype(str).str.strip().ne("")
    ]
    if metas_disponibles.empty:
        st.warning(
            f"⚠️ Los reportes no contienen datos en la columna **{META_COL}**. "
            "Cambia la llave a **ID Meta** en la barra lateral."
        )
        return
    metas_disponibles["_key"] = metas_disponibles[META_COL].apply(lambda x: _fmt_meta_val(META_COL, x))
    metas_disponibles["Etiqueta"] = (
        metas_disponibles["_key"] + " - " + metas_disponibles["Descripción de la Meta"].astype(str)
    )

    # Metas eliminadas (en Antes pero no en Ahora)
    keys_ahora = set(metas_disponibles["_key"])
    if not metas_antes.empty and META_COL in metas_antes.columns:
        metas_antes_unicas = (
            metas_antes[[META_COL, "Descripción de la Meta"]]
            .dropna(subset=[META_COL])
            .drop_duplicates()
            .copy()
        )
        metas_antes_unicas["_key"] = metas_antes_unicas[META_COL].apply(lambda x: _fmt_meta_val(META_COL, x))
        metas_eliminadas = metas_antes_unicas[~metas_antes_unicas["_key"].isin(keys_ahora)].copy()
        metas_eliminadas["Etiqueta"] = (
            "ELIMINADA) - " + metas_eliminadas["_key"] + " - " + metas_eliminadas["Descripción de la Meta"].astype(str)
        )
    else:
        metas_eliminadas = pd.DataFrame(columns=["_key", "Etiqueta"])

    todas_metas = pd.concat(
        [metas_disponibles[["_key", "Etiqueta"]], metas_eliminadas[["_key", "Etiqueta"]]],
        ignore_index=True,
    ).sort_values("Etiqueta")

    meta_lookup = dict(zip(todas_metas["Etiqueta"], todas_metas["_key"]))

    id_meta_label = st.selectbox(
        "Selecciona una Meta",
        [""] + todas_metas["Etiqueta"].tolist(),
        key="filtro_meta",
    )
    id_meta_sel = meta_lookup.get(id_meta_label)

    subtabs = st.tabs([
        "📋 Información de la Meta",
        "📆 Cronograma y 💰 Partidas",
        "✅ Cumplimiento",
    ])

    # ================== SUBTAB 1: Información de la Meta ==================
    with subtabs[0]:
        if not id_meta_sel:
            st.info("Selecciona una Meta (ID) para ver la información comparativa.")
        else:
            header_with_tooltip_meta(id_meta_sel)

            df_antes_meta, df_ahora_meta = _info_meta(metas_antes, metas_ahora, META_COL, id_meta_sel)

            meta_es_nueva = df_antes_meta.empty and not df_ahora_meta.empty
            meta_fue_eliminada = df_ahora_meta.empty and not df_antes_meta.empty

            col1, col2 = st.columns(2)

            def _comparar_texto(label: str, a: str, h: str):
                if meta_es_nueva:
                    st.markdown(f"**{label}** <span class='badge'>🆕 Nuevo</span>", unsafe_allow_html=True)
                    col1.caption("Antes"); col1.caption("— Sin datos en corte anterior —")
                    col2.caption("Ahora"); col2.write(h)
                elif meta_fue_eliminada:
                    st.markdown(f"**{label}** <span class='badge badge--bad'>🗑️ Eliminada</span>", unsafe_allow_html=True)
                    col1.caption("Antes"); col1.write(a)
                    col2.caption("Ahora"); col2.caption("— Meta eliminada en corte actual —")
                elif str(a) == str(h):
                    st.markdown(f"**{label}** <span class='badge badge--ok'>✔ Sin cambios</span>", unsafe_allow_html=True)
                    col1.caption("Antes"); col1.write(a)
                    col2.caption("Ahora"); col2.write(h)
                else:
                    st.markdown(f"**{label}** <span class='badge badge--warn'>🔄 Modificado</span>", unsafe_allow_html=True)
                    antes_html, ahora_html = _diff_html(a, h)
                    col1.caption("Antes")
                    col1.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{antes_html}</div>", unsafe_allow_html=True)
                    col2.caption("Ahora")
                    col2.markdown(f"<div style='border:1px solid #e5e7eb;padding:8px'>{ahora_html}</div>", unsafe_allow_html=True)

            desc_a = df_antes_meta["Descripción de la Meta"].iloc[0] if "Descripción de la Meta" in df_antes_meta.columns and not df_antes_meta.empty else ""
            desc_h = df_ahora_meta["Descripción de la Meta"].iloc[0] if "Descripción de la Meta" in df_ahora_meta.columns and not df_ahora_meta.empty else ""
            _comparar_texto("Descripción de la Meta", desc_a, desc_h)

            um_a = df_antes_meta["Unidad de Medida"].iloc[0] if "Unidad de Medida" in df_antes_meta.columns and not df_antes_meta.empty else ""
            um_h = df_ahora_meta["Unidad de Medida"].iloc[0] if "Unidad de Medida" in df_ahora_meta.columns and not df_ahora_meta.empty else ""
            _comparar_texto("Unidad de Medida", um_a, um_h)

            # Métricas
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

            # Mapa de participación municipal: distingue entre corte anterior y actual
            mpios_norm_antes = {_norm_txt(m) for m in df_antes_meta["Municipio"].dropna()} if not df_antes_meta.empty else set()
            mpios_norm_ahora = {_norm_txt(m) for m in df_ahora_meta["Municipio"].dropna()}

            por_determinar_antes  = "POR DETERMINAR"   in mpios_norm_antes
            por_determinar_ahora  = "POR DETERMINAR"   in mpios_norm_ahora
            cobertura_estatal_antes = "COBERTURA ESTATAL" in mpios_norm_antes
            cobertura_estatal_ahora = "COBERTURA ESTATAL" in mpios_norm_ahora

            geojson = cargar_geojson_municipal()
            mostrar_mapa = False
            fig_mapa = None

            hay_municipios = bool(mpios_norm_antes or mpios_norm_ahora)

            if geojson and hay_municipios:
                _ORDEN_CAT = ["Permanece", "Se agregó", "Se retiró", "Sin participación"]
                _COLOR_MAP  = {
                    "Permanece":         "#1e40af",
                    "Se agregó":         "#15803d",
                    "Se retiró":         "#f97316",
                    "Sin participación": "#e5e7eb",
                }

                datos_mapa = []
                for feat in geojson["features"]:
                    nom = feat["properties"]["nom_mun"]
                    n = _norm_txt(nom)
                    en_antes = False if por_determinar_antes  else (True if cobertura_estatal_antes  else n in mpios_norm_antes)
                    en_ahora = False if por_determinar_ahora  else (True if cobertura_estatal_ahora  else n in mpios_norm_ahora)
                    if en_antes and en_ahora:
                        estado = "Permanece"
                    elif en_ahora:
                        estado = "Se agregó"
                    elif en_antes:
                        estado = "Se retiró"
                    else:
                        estado = "Sin participación"
                    datos_mapa.append({"Municipio": nom, "Participación": estado})

                df_mapa = pd.DataFrame(datos_mapa)

                cats_presentes = df_mapa["Participación"].unique()
                color_map_fig  = {k: v for k, v in _COLOR_MAP.items()  if k in cats_presentes}
                orden_fig      = [c for c in _ORDEN_CAT if c in cats_presentes]

                if por_determinar_ahora:
                    color_map_fig["Sin participación"] = "#fecaca"

                fig_mapa = px.choropleth(
                    df_mapa,
                    geojson=geojson,
                    locations="Municipio",
                    featureidkey="properties.nom_mun",
                    color="Participación",
                    color_discrete_map=color_map_fig,
                    category_orders={"Participación": orden_fig},
                    hover_data={"Participación": True, "Municipio": True},
                )
                fig_mapa.update_geos(fitbounds="locations", visible=False)
                fig_mapa.update_layout(
                    margin={"r": 0, "t": 0, "l": 0, "b": 0},
                    height=420,
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.01,
                        xanchor="center", x=0.5,
                    ),
                )
                mostrar_mapa = True

            # Layout: mapa izquierda | tabla derecha
            if mostrar_mapa:
                col_mapa, col_tabla = st.columns([2, 3])
            else:
                col_mapa, col_tabla = None, st.container()

            # Conteos de municipios
            mpios_antes = set(df_antes_meta["Municipio"].dropna().unique()) if not df_antes_meta.empty else set()
            mpios_ahora = set(df_ahora_meta["Municipio"].dropna().unique())
            mpios_comunes = mpios_antes & mpios_ahora

            cols_num = [c for c in ["Cantidad Estatal", "Monto Estatal", "Cantidad Federal", "Monto Federal",
                                     "Cantidad Municipal", "Monto Municipal"] if c in df_ahora_meta.columns or c in df_antes_meta.columns]
            n_modificados = 0
            for m in mpios_comunes:
                fa = df_antes_meta[df_antes_meta["Municipio"] == m][cols_num].sum()
                fh = df_ahora_meta[df_ahora_meta["Municipio"] == m][cols_num].sum()
                if not fa.equals(fh):
                    n_modificados += 1

            if mostrar_mapa and col_mapa is not None:
                with col_mapa:
                    if por_determinar_ahora:
                        st.error("La distribución territorial indica **\"Por Determinar\"**. Se deben asignar municipios.")
                    st.plotly_chart(fig_mapa, use_container_width=True)
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("Antes", len(mpios_antes))
                    mc2.metric("Ahora", len(mpios_ahora), delta=f"{len(mpios_ahora) - len(mpios_antes):+d}" if mpios_antes else None)
                    mc3.metric("Modificados", n_modificados)

            # Comparativo por Municipio (tabla)
            with col_tabla:
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
                    key=f"radio_registro_{_fmt_id_meta(id_meta_sel)}",
                ) if opciones_radio else "Todos"

                df_comp_mpio = _resumen_municipal(df_antes_meta.copy(), df_ahora_meta.copy(), registro_opcion)

                # Ocultar columnas de fuentes sin datos (todas 0/NaN en Antes y Ahora)
                cols_drop = []
                for base in ["Estatal", "Federal", "Municipal"]:
                    grupo = [c for c in df_comp_mpio.columns if base in c]
                    if grupo and (df_comp_mpio[grupo].fillna(0) == 0).all().all():
                        cols_drop.extend(grupo)
                if cols_drop:
                    df_comp_mpio = df_comp_mpio.drop(columns=cols_drop)

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
                    num_cols = df.select_dtypes(include="number").columns.tolist()
                    filas = []

                    totales = df[num_cols].sum(numeric_only=True)
                    fila_total = {col_name: totales.get(col_name, "") for col_name in df.columns}
                    fila_total["Municipio"] = "TOTAL"
                    filas.append(fila_total)

                    if filtro_reg == "Todos" and "Registro Presupuestal" in df_antes_meta.columns:
                        for reg in ["Centralizado", "Descentralizado", "Sin Registro"]:
                            mask = (
                                (df_antes_meta["Registro Presupuestal"] == reg) |
                                (df_ahora_meta["Registro Presupuestal"] == reg)
                            )
                            if mask.any():
                                municipios_reg = pd.concat([
                                    df_antes_meta.loc[df_antes_meta["Registro Presupuestal"] == reg, "Municipio"],
                                    df_ahora_meta.loc[df_ahora_meta["Registro Presupuestal"] == reg, "Municipio"],
                                ]).unique()
                                sub = df[df["Municipio"].isin(municipios_reg)]
                                if not sub.empty:
                                    subtotales = sub[num_cols].sum(numeric_only=True)
                                    fila_sub = {col_name: subtotales.get(col_name, "") for col_name in df.columns}
                                    fila_sub["Municipio"] = f" ↘️ {reg}"
                                    filas.append(fila_sub)

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
                    use_container_width=True,
                )

    # ================== SUBTAB 2: Cronograma y Partidas ==================
    with subtabs[1]:
        # ---------- Partidas ----------
        df_comp_part, df_mensual, dfp_a, dfp_h = _partidas_resumen(
            partidas_antes, partidas_ahora,
            id_meta_sel if id_meta_sel else None,
            META_COL,
        )

        st.markdown("##### Partidas de Gasto")

        partidas_disponibles = sorted(
            pd.Index(
                pd.concat([
                    dfp_a.get("Partida_fmt", pd.Series(dtype=object)),
                    dfp_h.get("Partida_fmt", pd.Series(dtype=object)),
                ], ignore_index=True)
            ).dropna().astype(str).unique().tolist()
        )

        st.write("**Selecciona una meta para visualizar su calendarizado (Por default se muestra del proyecto completo)**")

        with st.expander("⚙️ Configuración de Partidas", expanded=False):
            st.markdown("**Partidas a mostrar**")
            col1, col2 = st.columns([3, 1])
            todas_on = col2.checkbox(
                "Todas",
                value=False,
                key=f"chk_todas_{_fmt_id_meta(id_meta_sel)}",
            )

            if todas_on:
                filtro_partidas = partidas_disponibles
            else:
                filtro_partidas = col1.multiselect(
                    "Selecciona partidas:",
                    options=partidas_disponibles,
                    default=[],
                    key=f"ms_partidas_{_fmt_id_meta(id_meta_sel)}",
                    placeholder="Escribe o selecciona una o más partidas...",
                )

            st.markdown("**Orden de la tabla \"Partidas por Actividad\"**")
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
                key=f"sortcol_{_fmt_id_meta(id_meta_sel)}",
            )
            asc = col_ord2.toggle(
                "Ascendente",
                value=False,
                key=f"sortasc_{_fmt_id_meta(id_meta_sel)}",
            )
            modo_interactivo = col_mode.toggle(
                "Tabla interactiva",
                value=False,
                help="Permite ordenar clicando en el encabezado (sin 'chip' 🔒).",
                key=f"modo_inter_{_fmt_id_meta(id_meta_sel)}",
            )

        if not filtro_partidas:
            filtro_partidas = partidas_disponibles

        st.caption(f"Mostrando {len(filtro_partidas)} de {len(partidas_disponibles)} partidas disponibles.")

        df_mes_a = dfp_a[dfp_a["Partida_fmt"].astype(str).isin(filtro_partidas)]
        df_mes_h = dfp_h[dfp_h["Partida_fmt"].astype(str).isin(filtro_partidas)]

        meses_cols = [
            "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
            "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
            "Monto Octubre", "Monto Noviembre", "Monto Diciembre",
        ]

        sum_m_ahora = df_mes_h[meses_cols].sum(numeric_only=True)
        sum_m_antes = df_mes_a[meses_cols].sum(numeric_only=True)

        df_mensual_sel = pd.DataFrame({
            "Mes": [m.replace("Monto ", "") for m in meses_cols],
            "Antes": sum_m_antes.values,
            "Ahora": sum_m_ahora.values,
        })

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
            if a >= 1_000_000:
                return f"${v/1_000_000:.2f}M"
            if a >= 1_000:
                return f"${v/1_000:.0f}K"
            return f"${v:,.0f}"

        labels_ahora = [_humanize_kmb(v) for v in df_mensual_sel["Ahora"].values]

        titulo_scope = (
            f"Meta ({META_COL}) {id_meta_sel}"
            if id_meta_sel else "Proyecto completo"
        )

        fig_mes = px.bar(
            df_mensual_sel,
            x="Mes",
            y=["Antes", "Ahora"],
            barmode="group",
            title=f"Calendarizado Mensual – {titulo_scope}",
            labels={"value": "Monto", "variable": "Versión"},
            color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"},
        )

        def _apply_text_to_ahora(trace):
            if trace.name == "Ahora":
                trace.update(text=labels_ahora, texttemplate="%{text}", textposition="outside", textfont_size=11)
            else:
                trace.update(text=None)

        fig_mes.for_each_trace(_apply_text_to_ahora)
        fig_mes.update_layout(height=480, uniformtext_minsize=10, uniformtext_mode="hide")
        st.plotly_chart(fig_mes, use_container_width=True)

        # ====== Partidas por Actividad / Hito ======
        st.markdown("##### Partidas por Actividad ")

        _det_a = dfp_a[["Partida_fmt", "Clave de Actividad /Hito", META_COL, "Descripción", "Monto Anual"]].copy()
        _det_h = dfp_h[["Partida_fmt", "Clave de Actividad /Hito", META_COL, "Descripción", "Monto Anual"]].copy()

        _det_a.rename(columns={"Descripción": "Desc_A", "Monto Anual": "Monto Anual (Antes)"}, inplace=True)
        _det_h.rename(columns={"Descripción": "Desc_H", "Monto Anual": "Monto Anual (Ahora)"}, inplace=True)

        _unificada = pd.merge(
            _det_a, _det_h,
            on=["Partida_fmt", "Clave de Actividad /Hito"],
            how="outer",
            suffixes=("_A", "_H"),
        )

        if f"{META_COL}_H" in _unificada.columns or f"{META_COL}_A" in _unificada.columns:
            _unificada[META_COL] = _unificada.get(f"{META_COL}_H").combine_first(_unificada.get(f"{META_COL}_A"))

        _unificada["Descripción"] = _unificada["Desc_H"].combine_first(_unificada["Desc_A"])

        for c in ["Monto Anual (Antes)", "Monto Anual (Ahora)"]:
            _unificada[c] = pd.to_numeric(_unificada[c], errors="coerce").fillna(0.0)
        _unificada["Diferencia"] = _unificada["Monto Anual (Ahora)"] - _unificada["Monto Anual (Antes)"]

        # --- Join catálogo ---
        def _pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
            for c in candidates:
                if c in df.columns:
                    return c
            return None

        desc_candidates = [
            "Definición", "Definicion", "Descripción", "Descripcion",
            "Descripción de la Partida", "Descripcion de la Partida",
            "Desc Partida", "Descripcion Partida",
        ]
        restr_candidates = ["Restringida", "Restringido", "Restriccion", "Restricción"]
        valid_candidates = ["Validador", "Validador Partida", "Validador_Partida"]

        desc_col = _pick_col(CATALOGO_PARTIDAS, desc_candidates)
        restr_col = _pick_col(CATALOGO_PARTIDAS, restr_candidates)
        valid_col = _pick_col(CATALOGO_PARTIDAS, valid_candidates)

        cat_cols = ["Partida_fmt"] + [c for c in [desc_col, restr_col, valid_col] if c]
        _catalogo = CATALOGO_PARTIDAS[cat_cols].drop_duplicates().copy() if cat_cols else pd.DataFrame(columns=["Partida_fmt"])

        _unificada = _unificada.merge(_catalogo, on="Partida_fmt", how="left")

        rename_map = {"Partida_fmt": "Partida"}
        if desc_col:
            rename_map[desc_col] = "Descripción de la Partida"
        if restr_col:
            rename_map[restr_col] = "Restringida"
        if valid_col:
            rename_map[valid_col] = "Validador"
        _unificada = _unificada.rename(columns=rename_map)
        if "Descripción de la Partida" not in _unificada.columns:
            _unificada["Descripción de la Partida"] = ""
        if "Restringida" not in _unificada.columns:
            _unificada["Restringida"] = False
        if "Validador" not in _unificada.columns:
            _unificada["Validador"] = ""

        def _to_bool(v):
            if pd.isna(v):
                return False
            if isinstance(v, bool):
                return bool(v)
            if isinstance(v, (int, float)):
                return v != 0
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

        meta_label = "ID de Meta" if META_COL == "ID Meta" else "Clave de Meta"

        _cols_finales = [
            META_COL,
            "Partida",
            "Descripción de la Partida",
            "Actividad (Cronograma)",
            "Monto Anual (Antes)",
            "Monto Anual (Ahora)",
            "Diferencia",
        ]

        _tabla_unica = (
            _unificada.rename(columns={"Partida_fmt": "Partida", "Descripción": "Actividad (Cronograma)"})
            .reindex(columns=[c for c in _cols_finales if c in _unificada.columns or c in ["Partida", "Descripción de la Partida", "Actividad (Cronograma)"]])
            .copy()
        )

        if META_COL in _tabla_unica.columns:
            _tabla_unica.rename(columns={META_COL: meta_label}, inplace=True)

        _eps = 1e-9
        _mask_nonzero = (_tabla_unica["Monto Anual (Antes)"].abs() > _eps) | (_tabla_unica["Monto Anual (Ahora)"].abs() > _eps)
        _tabla_unica = _tabla_unica[_mask_nonzero].sort_values(["Partida", "Actividad (Cronograma)"], kind="stable")

        def _bg_delta_cell(v):
            if pd.isna(v):
                return ""
            return "background-color:#fff3cd" if abs(v) != 0 else ""

        _tabla_ordenada = _tabla_unica.sort_values(sort_col, ascending=asc, kind="stable").copy()

        if modo_interactivo:
            def _strip_html(x):
                return re.sub(r"<.*?>", "", str(x)) if isinstance(x, str) else x

            df_inter = _tabla_ordenada.copy()
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
            styled_unica = (
                _tabla_ordenada
                .style
                .format({
                    "Monto Anual (Antes)": "${:,.2f}",
                    "Monto Anual (Ahora)": "${:,.2f}",
                    "Diferencia": "${:,.2f}",
                })
                .applymap(_bg_delta_cell, subset=["Diferencia"])
                .hide(axis="index")
            )
            st.markdown(styled_unica.to_html(escape=False), unsafe_allow_html=True)

        # ---------- Cronograma ----------
        if not id_meta_sel:
            st.info("Selecciona una Meta (ID) para ver Cronograma")
        else:
            df_crono = _cronograma_df(crono_antes, crono_ahora, META_COL, id_meta_sel)

            st.markdown("##### Detalle de Actividades / Hitos (Cronograma Actual)")

            if df_crono.empty:
                st.info("No se encontraron actividades o hitos para esta meta en ninguna de las versiones.")
            else:
                columnas_tabla = [
                    "Clave de Actividad /Hito", "Fase Actividad / Hito", "Tipo", "Descripción",
                    "Fecha de Inicio", "Fecha de Termino", "Monto Actividad / Hito",
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

                try:
                    manual_crono = MANUAL.get("metas", {}).get("cronograma", {})
                    render_tooltip_cronograma_qaware(manual_crono, clave_q, columnas_accion=3)
                except Exception:
                    pass

                MAX_LABEL_CHARS = 60

                def _shorten(s: str, n: int) -> str:
                    if not isinstance(s, str):
                        return ""
                    s = s.strip()
                    if len(s) <= n:
                        return s
                    corte = s[:n].rsplit(" ", 1)[0]
                    if len(corte) < int(0.6 * n):
                        corte = s[:n]
                    return corte + "…"

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
                df_crono["Actividad_full"] = (
                    df_crono["Clave de Actividad /Hito"].astype(str) + " - " +
                    df_crono["Descripción"].astype(str) + " (" + df_crono["Versión"] + ")"
                )

                df_crono["Monto_full"] = df_crono.get("Monto Actividad / Hito", pd.Series([None] * len(df_crono))).map(
                    lambda x: f"${x:,.2f}" if pd.notna(x) else "—"
                )
                df_crono["Monto_compact"] = df_crono.get("Monto Actividad / Hito", pd.Series([None] * len(df_crono))).map(_humanize_currency)
                df_crono["DuracionDias"] = (df_crono["Fecha de Termino"] - df_crono["Fecha de Inicio"]).dt.days

                df_crono["Monto_val"] = pd.to_numeric(
                    df_crono.get("Monto Actividad / Hito", pd.Series([None] * len(df_crono))),
                    errors="coerce",
                ).fillna(0.0)

                with st.expander("⚙️ Configuración del Cronograma", expanded=False):
                    st.markdown("**Etiquetas de monto en las barras**")
                    use_compact_amount = st.toggle(
                        "Usar formato compacto (K/M/B) en las barras",
                        value=True,
                        help="Muestra 1.2K / 3.4M / 2.1B en la barra; el monto completo se conserva en el tooltip.",
                    )
                    show_only_now = st.toggle(
                        "Mostrar montos solo para 'Ahora'",
                        value=True,
                        help="Reduce el ruido visual mostrando montos solo en la versión 'Ahora'.",
                    )
                    hide_on_short_bars = st.toggle(
                        "Ocultar etiquetas en barras muy cortas",
                        value=True,
                        help="Evita sobreposición de textos ocultando etiquetas cuando la barra es demasiado corta.",
                    )
                    min_days_short = st.slider(
                        "Umbral de días para considerar 'corta'",
                        1, 30, 3, 1,
                        help="Si la duración (Fin-Inicio) es menor a este umbral, se oculta la etiqueta.",
                        disabled=not hide_on_short_bars,
                    )

                    st.markdown("**Filtros del Cronograma**")
                    show_only_version_now = st.toggle(
                        "Mostrar solo versión 'Ahora'",
                        value=False,
                        help="Oculta las barras de 'Antes' y muestra únicamente las actividades/hitos actuales.",
                    )
                    only_nonzero_amounts = st.toggle(
                        "Mostrar solo actividades/hitos con monto distinto de cero",
                        value=False,
                        help="Oculta barras con monto 0 o sin monto.",
                    )
                    modo_orden_y = st.radio(
                        "Ordenar actividades en el eje Y por:",
                        options=["Por ID de actividad", "Por fecha de inicio (antiguas arriba)"],
                        index=0,
                        horizontal=True,
                        key=f"orden_y_{_fmt_id_meta(id_meta_sel)}",
                    )

                def _pick_label(row):
                    if row["Monto_val"] == 0:
                        return ""
                    if hide_on_short_bars and row["DuracionDias"] < min_days_short:
                        return ""
                    if show_only_now and row.get("Versión") != "Ahora":
                        return ""
                    return row["Monto_compact"] if use_compact_amount else row["Monto_full"]

                df_crono["MontoLabel"] = df_crono.apply(_pick_label, axis=1)

                df_crono_plot = df_crono.copy()
                for c in ["Fecha de Inicio", "Fecha de Termino"]:
                    df_crono_plot[c] = pd.to_datetime(df_crono_plot[c], dayfirst=True, errors="coerce")

                df_crono_plot["FechaTermino_safe"] = df_crono_plot["Fecha de Termino"].fillna(df_crono_plot["Fecha de Inicio"])

                if show_only_version_now:
                    df_crono_plot = df_crono_plot[df_crono_plot["Versión"] == "Ahora"]
                if only_nonzero_amounts:
                    df_crono_plot = df_crono_plot[df_crono_plot["Monto_val"].abs() > 0]

                if df_crono_plot.empty:
                    st.info("No hay actividades/hitos para los filtros actuales.")
                else:
                    if modo_orden_y == "Por ID de actividad":
                        orden_y = (
                            df_crono_plot
                            .sort_values(["Clave Num", "Versión"], kind="stable")
                            ["EtiquetaY"].tolist()
                        )
                    else:
                        base_orden = df_crono_plot.copy()
                        base_orden["Inicio"] = pd.to_datetime(base_orden["Fecha de Inicio"], errors="coerce")
                        aux = (
                            base_orden.groupby("EtiquetaY", as_index=False)["Inicio"].min()
                            .assign(_orden=lambda d: d["Inicio"].fillna(pd.Timestamp.max))
                            .sort_values("_orden", ascending=True, kind="stable")
                        )
                        orden_y = aux["EtiquetaY"].tolist()

                    filas = df_crono_plot["EtiquetaY"].nunique()
                    ALTURA_BASE = 420
                    ALTURA_POR_FILA = 26
                    altura = max(ALTURA_BASE, ALTURA_POR_FILA * filas + 140)

                    fig = px.timeline(
                        df_crono_plot,
                        x_start="Fecha de Inicio",
                        x_end="Fecha de Termino",
                        y="EtiquetaY",
                        color="Versión",
                        text="MontoLabel",
                        color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"},
                        title=f"Cronograma de Actividades / Hitos - Meta (ID) {_fmt_id_meta(id_meta_sel)}",
                        custom_data=["Tipo", "Descripción", "Monto_val", "Fecha de Inicio", "FechaTermino_safe"],
                    )

                    fig.update_xaxes(
                        dtick="M1",
                        tickformat="%b '%y",
                        showgrid=True,
                        gridwidth=1,
                        gridcolor="light gray",
                        griddash="dot",
                    )

                    fig = agregar_bandas_mensuales(
                        fig, df_crono_plot,
                        col_inicio="Fecha de Inicio",
                        col_fin="Fecha de Termino",
                        fill_rgba="rgba(0,0,0,0.035)",
                    )

                    fig.update_traces(
                        hovertemplate=(
                            "<b>Tipo:</b> %{customdata[0]}<br>"
                            "<b>Descripción:</b> %{customdata[1]}<br>"
                            "<b>Inicio:</b> %{customdata[3]|%d/%m/%Y}<br>"
                            "<b>Fin:</b> %{customdata[4]|%d/%m/%Y}<br>"
                            "<b>Monto:</b> $%{customdata[2]:,.2f} MXN"
                            "<extra></extra>"
                        ),
                        textposition="inside",
                        insidetextanchor="middle",
                        textfont_size=11,
                        textfont_color="white",
                        cliponaxis=False,
                        marker_line_width=0,
                        texttemplate="<b>%{text}</b>",
                        textfont=dict(size=11),
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
                        tickson="boundaries",
                    )

                    fig.update_layout(
                        height=altura,
                        margin=dict(l=180, r=20, t=60, b=40),
                    )

                    st.plotly_chart(fig, use_container_width=True)

        # ====== Catálogo de partidas (COMPLETO) ======
        with st.expander("📖 Catálogo de partidas (completo)"):
            q = st.text_input(
                "Filtrar por código, definición o validador",
                key=f"filtro_catalogo_full_{_fmt_id_meta(id_meta_sel)}",
            ).strip().lower()

            cat_full_cols = ["Partida_fmt"] + [c for c in [desc_col, restr_col, valid_col] if c]
            cat_full = CATALOGO_PARTIDAS[cat_full_cols].drop_duplicates().copy() if cat_full_cols else pd.DataFrame(columns=["Partida_fmt"])

            if q:
                cat_show = cat_full[
                    cat_full.apply(
                        lambda r: q in f"{r.get('Partida_fmt', '')} {r.get(desc_col, '')} {r.get(valid_col, '')}".lower(),
                        axis=1,
                    )
                ]
            else:
                cat_show = cat_full

            vista_tabla = st.toggle("Ver como tabla compacta", value=False, key=f"vista_tabla_full_{_fmt_id_meta(id_meta_sel)}")
            if cat_show.empty:
                st.markdown("_Sin coincidencias._")
            else:
                if vista_tabla:
                    rename_map2 = {"Partida_fmt": "Código"}
                    if desc_col:
                        rename_map2[desc_col] = "Definición"
                    if restr_col:
                        rename_map2[restr_col] = "Restringida"
                    if valid_col:
                        rename_map2[valid_col] = "Validador"
                    df_tabla = cat_show.rename(columns=rename_map2)
                    mostrar_cols = ["Código", "Definición"] + [c for c in ["Restringida", "Validador"] if c in df_tabla.columns]
                    st.dataframe(
                        df_tabla[mostrar_cols], use_container_width=True, hide_index=True,
                        column_config={
                            "Código": st.column_config.TextColumn(width="small"),
                            "Definición": st.column_config.TextColumn(width="large"),
                            **({"Restringida": st.column_config.CheckboxColumn("🔒", help="Requiere validador", disabled=True, width="small")} if "Restringida" in df_tabla.columns else {}),
                            **({"Validador": st.column_config.TextColumn(width="small")} if "Validador" in df_tabla.columns else {}),
                        },
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
                            f"**{r.get('Partida_fmt', '')}** · {nom}{lock}",
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

    # ================== SUBTAB 3: Cumplimiento ==================
    with subtabs[2]:
        if not id_meta_sel:
            st.info("Selecciona una Meta (ID) para ver el Cumplimiento.")
        else:
            df_cump_a, df_cump_h = _cumplimiento_df(cumpl_antes, cumpl_ahora, META_COL, id_meta_sel)

            cantidad_ahora = float(df_cump_h["Cantidad"].iloc[0]) if (not df_cump_h.empty and "Cantidad" in df_cump_h.columns and pd.notna(df_cump_h["Cantidad"].iloc[0])) else None
            cantidad_antes = float(df_cump_a["Cantidad"].iloc[0]) if (not df_cump_a.empty and "Cantidad" in df_cump_a.columns and pd.notna(df_cump_a["Cantidad"].iloc[0])) else None

            dif_cantidad_cump = (
                cantidad_ahora - cantidad_antes
                if cantidad_ahora is not None and cantidad_antes is not None else None
            )

            col1, col2 = st.columns(2)
            col1.metric("Cantidad Programada (Antes)", f"{cantidad_antes:.2f}" if cantidad_antes is not None else "—")
            col2.metric(
                "Cantidad Programada (Ahora)",
                f"{cantidad_ahora:.2f}" if cantidad_ahora is not None else "—",
                delta=f"{dif_cantidad_cump:+.2f}" if dif_cantidad_cump is not None else None,
            )

            meses = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
            ]
            cols_mensuales = [f"Cumplimiento {m}" for m in meses]

            valores_ahora = (df_cump_h.iloc[0][cols_mensuales].fillna(0).values if (not df_cump_h.empty and all(c in df_cump_h.columns for c in cols_mensuales)) else [0] * 12)
            valores_antes = (df_cump_a.iloc[0][cols_mensuales].fillna(0).values if (not df_cump_a.empty and all(c in df_cump_a.columns for c in cols_mensuales)) else [0] * 12)

            df_cumplimiento = pd.DataFrame({
                "Mes": meses * 2,
                "Valor": list(valores_antes) + list(valores_ahora),
                "Versión": ["Antes"] * 12 + ["Ahora"] * 12,
            })
            fig_cump = px.bar(
                df_cumplimiento, x="Mes", y="Valor", color="Versión", barmode="group",
                color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"},
                title=f"Cumplimiento Programado por Mes - Meta (ID) {_fmt_id_meta(id_meta_sel)}",
            )
            fig_cump.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_cump, use_container_width=True)


def render_tab_metas(
    tab,
    metas_antes, metas_ahora,
    crono_antes, crono_ahora,
    partidas_antes, partidas_ahora,
    cumpl_antes, cumpl_ahora,
    META_COL, clave_q,
):
    """Renderiza el Tab 2 completo (Metas) dentro del contenedor tab."""

    with tab:
        st.subheader("🎯 Metas")

        if metas_ahora.empty:
            st.info("No hay datos de metas para esta Clave Q.")
            return

        _metas_body(
            metas_antes, metas_ahora, crono_antes, crono_ahora,
            partidas_antes, partidas_ahora, cumpl_antes, cumpl_ahora,
            META_COL, clave_q,
        )
