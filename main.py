import streamlit as st
import pandas as pd
import plotly.express as px
import difflib
import unicodedata


st.set_page_config(layout="wide")
st.title("Revisión Programación SED")

# ========== FUNCIONES UTILITARIAS ==========

@st.cache_data(show_spinner=False)
def cargar_hoja(archivo, hoja, columnas):
    df = pd.read_excel(archivo, sheet_name=hoja, header=7)
    return df[df.columns.intersection(columnas)]

@st.cache_data(show_spinner=False)
def cargar_cronograma(archivo):
    columnas = [
        "Clave Q", "Dep Siglas", "ID Meta", "Clave de Meta", "Clave de Actividad /Hito", "Tipo",
        "Fase Actividad / Hito", "Descripción", "Fecha de Inicio", "Fecha de Termino",
        "Monto Actividad / Hito"
    ]
    df = pd.read_excel(archivo, sheet_name="Sección de Metas-Cronograma", header=7)
    df = df[df.columns.intersection(columnas)]
    df["Fecha de Inicio"] = pd.to_datetime(df["Fecha de Inicio"], dayfirst=True, errors='coerce')
    df["Fecha de Termino"] = pd.to_datetime(df["Fecha de Termino"], dayfirst=True, errors='coerce')
    return df

@st.cache_data(show_spinner=False)
def agregar_totales(df):
    df = df.copy()
    df["Cantidad Total"] = df.filter(like="Cantidad").sum(axis=1, skipna=True)
    df["Monto Total"] = df.filter(like="Monto").sum(axis=1, skipna=True)
    return df


# ========== INTERFAZ LATERAL ==========

with st.sidebar:
    st.title("⚙️ Configuración")

    # --- Zona colapsable para carga de archivos
    with st.expander("📂 Cargar archivos de Excel", expanded=True):
        archivo_antes = st.file_uploader("Archivo - Corte Antes", type=["xlsx"], key="archivo_antes")
        archivo_ahora = st.file_uploader("Archivo - Corte Ahora", type=["xlsx"], key="archivo_ahora")

# ========== CARGA Y FILTRO INICIAL ==========

if archivo_antes and archivo_ahora:
    with st.spinner("Cargando y procesando archivos..."):

        def limpiar_texto(texto):
            if isinstance(texto, str):
                texto = unicodedata.normalize("NFKC", texto)  # Normaliza caracteres raros
                texto = texto.replace('\n', ' ').replace('\r', ' ')  # Elimina saltos de línea
                texto = texto.strip()  # Quita espacios al inicio y fin
            return texto    
        
        # --- Cargar hoja 'Datos Generales' para extraer Claves Q disponibles ---
        columnas_datos = [
            "Fecha", "Clave Q", "Nombre del Proyecto (Ejercicio Actual)", "Eje", "Dep Siglas",
            "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
            "Descripción del Avance Actual", "Alcance Anual"
        ]
        datos_ahora = cargar_hoja(archivo_ahora, "Datos Generales", columnas_datos)
        datos_antes = cargar_hoja(archivo_antes, "Datos Generales", columnas_datos)

        # --- Limpiar campos de texto ---
        columnas_texto = [
            "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
            "Descripción del Avance Actual", "Alcance Anual"
        ]

        for col in columnas_texto:
            if col in datos_ahora.columns:
                datos_ahora[col] = datos_ahora[col].astype(str).apply(limpiar_texto)
            if col in datos_antes.columns:
                datos_antes[col] = datos_antes[col].astype(str).apply(limpiar_texto)

        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🔎 Filtrar proyectos")

            # Ejes disponibles (siempre visible)
            ejes_disponibles = datos_ahora["Eje"].dropna().unique().tolist()
            eje_sel = st.selectbox("Eje", [""] + sorted(ejes_disponibles), key="filtro_eje")

            # Dependencias disponibles (se filtran si hay eje, o se muestran todas si no)
            if eje_sel:
                deps_filtradas = datos_ahora[datos_ahora["Eje"] == eje_sel]["Dep Siglas"].dropna().unique().tolist()
            else:
                deps_filtradas = datos_ahora["Dep Siglas"].dropna().unique().tolist()
            dep_sel = st.selectbox("Dependencia", [""] + sorted(deps_filtradas), key="filtro_dep")

            # Filtrado de proyectos con nombre visible (se adapta a los filtros previos o muestra todos)
            filtro_q = datos_ahora.copy()
            if eje_sel:
                filtro_q = filtro_q[filtro_q["Eje"] == eje_sel]
            if dep_sel:
                filtro_q = filtro_q[filtro_q["Dep Siglas"] == dep_sel]

            filtro_q = filtro_q[["Clave Q", "Nombre del Proyecto (Ejercicio Actual)"]].dropna()
            filtro_q["display"] = filtro_q["Clave Q"] + " — " + filtro_q["Nombre del Proyecto (Ejercicio Actual)"]
            filtro_q = filtro_q.sort_values("display")

            opciones_q = dict(zip(filtro_q["display"], filtro_q["Clave Q"]))
            clave_q_display = st.selectbox(
                "Clave Q",
                [""] + list(opciones_q.keys()),
                placeholder="Buscar por Clave Q o nombre...",
                key="filtro_q"
            )
            clave_q = opciones_q.get(clave_q_display)



        # --- Control de flujo: si no hay Clave Q seleccionada, detener ejecución ---
        if not clave_q:
            st.warning("Selecciona una Clave Q específica en el panel lateral para ver los datos comparativos.")
            st.stop()

        # ========== FILTRAR TODOS LOS DATAFRAMES POR CLAVE Q ANTES DE USARLOS ==========

        datos_ahora = datos_ahora[datos_ahora["Clave Q"] == clave_q]
        datos_antes = datos_antes[datos_antes["Clave Q"] == clave_q]

        # Cargar y filtrar metas
        columnas_metas = [
            "Clave Q", "ID Meta", "Clave de Meta", "Descripción de la Meta", "Unidad de Medida",
            "ID Mpio", "Municipio", "Registro Presupuestal", "Cantidad Estatal", "Monto Estatal",
            "Cantidad Federal", "Monto Federal", "Cantidad Municipal", "Monto Municipal",
            "Cantidad Ingresos Propios", "Monto Ingresos Propios", "Cantidad Otros", "Monto Otros"
        ]
        metas_ahora = cargar_hoja(archivo_ahora, "Sección de Metas", columnas_metas)
        metas_antes = cargar_hoja(archivo_antes, "Sección de Metas", columnas_metas)
        metas_ahora = agregar_totales(metas_ahora)
        metas_antes = agregar_totales(metas_antes)

        metas_ahora = metas_ahora[metas_ahora["Clave Q"] == clave_q]
        metas_antes = metas_antes[metas_antes["Clave Q"] == clave_q]

        # Cronograma
        metas_crono_ahora = cargar_cronograma(archivo_ahora)
        metas_crono_antes = cargar_cronograma(archivo_antes)

        metas_crono_ahora = metas_crono_ahora[metas_crono_ahora["Clave Q"] == clave_q]
        metas_crono_antes = metas_crono_antes[metas_crono_antes["Clave Q"] == clave_q]

        # Partidas
        columnas_partidas = [
            "Clave Q", "ID Meta", "Clave de Meta", "Partida", "Monto Anual",
            "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
            "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
            "Monto Octubre", "Monto Noviembre", "Monto Diciembre"
        ]
        metas_partidas_ahora = cargar_hoja(archivo_ahora, "Sección de Metas-Partidas", columnas_partidas)
        metas_partidas_antes = cargar_hoja(archivo_antes, "Sección de Metas-Partidas", columnas_partidas)

        metas_partidas_ahora = metas_partidas_ahora[metas_partidas_ahora["Clave Q"] == clave_q]
        metas_partidas_antes = metas_partidas_antes[metas_partidas_antes["Clave Q"] == clave_q]

        # Cumplimiento (filtrado por Clave de Meta más adelante)
        columnas_cumplimiento = ["Clave de Meta", "Cantidad"] + [f"Cumplimiento {mes}" for mes in [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]]
        cumplimiento_ahora = cargar_hoja(archivo_ahora, "Sección de Metas-Cumplimiento", columnas_cumplimiento)
        cumplimiento_antes = cargar_hoja(archivo_antes, "Sección de Metas-Cumplimiento", columnas_cumplimiento)

        cumplimiento_ahora = cumplimiento_ahora.dropna(subset=["Clave de Meta"])
        cumplimiento_antes = cumplimiento_antes.dropna(subset=["Clave de Meta"])

# ========== PESTAÑAS PRINCIPALES ==========
    nombre_proyecto = datos_ahora.loc[datos_ahora["Clave Q"] == clave_q, "Nombre del Proyecto (Ejercicio Actual)"].values

    st.markdown(f"### Proyecto: {clave_q} — {nombre_proyecto[0]}")
                   # --------- Monto total del proyecto (antes del filtro de metas) ---------
    if not metas_ahora.empty and clave_q is not None:
        monto_total_antes = metas_antes["Monto Total"].sum()
        monto_total_ahora = metas_ahora["Monto Total"].sum()
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


    tabs = st.tabs([
        "📄 Datos Generales",
        "🎯 Metas",
    ])

    ################################################ DATOS GENERALES #########################################
    with tabs[0]:  
        st.subheader("📄 Datos Generales")

        campos_texto = [
            "Diagnóstico", "Objetivo General", "Descripción del Proyecto",
            "Descripción del Avance Actual", "Alcance Anual"
        ]

        def resaltar_diferencias(texto_antes, texto_ahora):
            matcher = difflib.SequenceMatcher(None, texto_antes, texto_ahora)
            res_antes = ""
            res_ahora = ""
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    res_antes += texto_antes[i1:i2]
                    res_ahora += texto_ahora[j1:j2]
                elif tag == "replace":
                    res_antes += f"<del style='color:red'>{texto_antes[i1:i2]}</del>"
                    res_ahora += f"<span style='background-color:lightgreen'>{texto_ahora[j1:j2]}</span>"
                elif tag == "delete":
                    res_antes += f"<del style='color:red'>{texto_antes[i1:i2]}</del>"
                elif tag == "insert":
                    res_ahora += f"<span style='background-color:lightgreen'>{texto_ahora[j1:j2]}</span>"
            return res_antes, res_ahora


        if clave_q == "Todos":
            st.info("Selecciona una Clave Q específica en el panel lateral para ver los datos comparativos.")
        else:
            fila_antes = datos_antes
            fila_ahora = datos_ahora

            if fila_antes.empty or fila_ahora.empty:
                st.warning("No se encontró información para esta Clave Q.")
            else:
                for campo in campos_texto:
                    valor_antes = str(fila_antes[campo].values[0])
                    valor_ahora = str(fila_ahora[campo].values[0])

                    st.markdown(f"**{campo}**")
                    col1, col2 = st.columns(2)

                    if valor_antes != valor_ahora:
                        st.info("🔄 Modificado")
                        antes_html, ahora_html = resaltar_diferencias(valor_antes, valor_ahora)
                        with col1:
                            st.markdown("Antes:")
                            st.markdown(f"<div style='border:1px solid #ccc;padding:8px'>{antes_html}</div>", unsafe_allow_html=True)
                        with col2:
                            st.markdown("Ahora:")
                            st.markdown(f"<div style='border:1px solid #ccc;padding:8px'>{ahora_html}</div>", unsafe_allow_html=True)
                    else:
                        st.success("✔ Sin cambios")
                        with col1:
                            st.markdown("Antes:")
                            st.markdown(valor_antes)
                        with col2:
                            st.markdown("Ahora:")
                            st.markdown(valor_ahora)

                # Solo para el campo Diagnóstico, mostrar prompt de evaluación
                    if campo == "Diagnóstico":
                        with st.expander("✨ Evaluar con ChatGPT"):
                            st.markdown("#### Evaluación automática (vía ChatGPT manual)")
                            criterios_diagnostico = """- Explica claramente una problemática pública.
                            - Identifica al grupo poblacional afectado.
                            - Es específico y no genérico."""

                            prompt_diagnostico = f"""
                            Eres un evaluador de proyectos públicos. Tu tarea es revisar el siguiente texto correspondiente al campo "Diagnóstico" de una propuesta de inversión pública estatal y emitir una evaluación objetiva.

                            TEXTO A EVALUAR:
                            ---
                            {valor_ahora}
                            ---

                            Evalúa si cumple con los siguientes criterios obligatorios:

                            1. **Población o área de enfoque identificada**: ¿Se menciona claramente a quién afecta el problema?
                            2. **Problemática central, oportunidad o situación descrita*: ¿Se describe de forma clara y específica el problema público a resolver, la oportunidad o situación a atender?
                            3. **Magnitud del problema cuantificada**: ¿Se incluyen datos duros, cifras oficiales o indicadores que permitan dimensionar el problema?

                            Además, asegúrate de que el diagnóstico **no** sea simplemente una descripción del proyecto ni su justificación técnica o financiera. Su propósito es explicar la situación que origina la necesidad del proyecto.

                            INSTRUCCIONES:

                            - Indica si el texto CUMPLE o NO CUMPLE con los 3 criterios.
                            - Justifica brevemente tu respuesta.
                            - Si aplica, sugiere cómo podría mejorarse el diagnóstico.

                            Formato de salida esperado:
                            1. ¿Cumple con los criterios?: Sí / No
                            2. Justificación:
                            3. Elabora un texto breve en el que se indique cuál de los criterios no se cumplen y porque. Redactado para el capturista:
                            """.strip()


                            st.code(prompt_diagnostico, language="markdown")

                            copy_code = f"""
                            <div>
                                <button onclick="copyPrompt()" style="padding:8px 16px; font-size:14px;">📋 Copiar al portapapeles</button>
                                <span id="copiado" style="margin-left:10px; color:green; display:none;">✅ Copiado</span>

                                <script>
                                function copyPrompt() {{
                                    const text = `{prompt_diagnostico.replace("`", "\\`")}`;
                                    navigator.clipboard.writeText(text).then(function() {{
                                        var alerta = document.getElementById("copiado");
                                        alerta.style.display = "inline";
                                        setTimeout(function() {{
                                            alerta.style.display = "none";
                                        }}, 2000);
                                    }});
                                }}
                                </script>
                            </div>
                            """
                            st.components.v1.html(copy_code, height=60)


                            st.caption("Haz clic en el botón para copiar el prompt al portapapeles y pégalo en https://chat.openai.com")

        ############################## SECCIÓN DE METAS ############################################################

    with tabs[1]:  
        st.subheader("🎯 Metas")

         
        # --------- Filtro de Clave de Meta (solo si hay datos y clave_q) ---------
        if not metas_ahora.empty and clave_q is not None:
            st.markdown("### Seleccionar Meta")

            metas_disponibles = (
                metas_ahora[metas_ahora["Clave Q"] == clave_q][["Clave de Meta", "Descripción de la Meta"]]
                .dropna(subset=["Clave de Meta"])
                .drop_duplicates()
                .sort_values("Clave de Meta")
            )

            metas_disponibles["Etiqueta"] = metas_disponibles["Clave de Meta"] + " - " + metas_disponibles["Descripción de la Meta"]

            clave_meta_filtro = st.selectbox(
                "Selecciona una Clave de Meta",
                [""] + metas_disponibles["Etiqueta"].tolist(),
                key="filtro_meta"
            )

            clave_meta_filtro_valor = clave_meta_filtro.split(" - ")[0] if clave_meta_filtro else None

        else:
            clave_meta_filtro_valor = None

        ############ Subpestañas específicas
        subtabs = st.tabs([
            "📋 Información de la Meta",
            "📆 Cronograma",
            "💰 Partidas",
            "✅ Cumplimiento"
        ])
    if clave_meta_filtro_valor:
    
        with subtabs[0]:
            st.write("📋 Información de la Meta")
        
            def resaltar_diferencias(texto_antes, texto_ahora):
                matcher = difflib.SequenceMatcher(None, texto_antes, texto_ahora)
                res_antes = ""
                res_ahora = ""
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag == "equal":
                        res_antes += texto_antes[i1:i2]
                        res_ahora += texto_ahora[j1:j2]
                    elif tag == "replace":
                        res_antes += f"<del style='color:red'>{texto_antes[i1:i2]}</del>"
                        res_ahora += f"<span style='background-color:lightgreen'>{texto_ahora[j1:j2]}</span>"
                    elif tag == "delete":
                        res_antes += f"<del style='color:red'>{texto_antes[i1:i2]}</del>"
                    elif tag == "insert":
                        res_ahora += f"<span style='background-color:lightgreen'>{texto_ahora[j1:j2]}</span>"
                return res_antes, res_ahora


            if metas_ahora.empty:
                st.info("No hay datos disponibles para esta Clave Q.")
            else:
                campos_metas_texto = ["Descripción de la Meta", "Unidad de Medida"]

                claves_meta_unicas = metas_ahora["Clave de Meta"].dropna().unique()

                for clave_meta in claves_meta_unicas:
            

                    if clave_meta_filtro_valor and clave_meta != clave_meta_filtro_valor:
                        continue  # 👉 Omitir si no coincide con filtro

                    st.markdown(f"#### Meta: {clave_meta}")

                    df_ahora_meta = metas_ahora[metas_ahora["Clave de Meta"] == clave_meta]
                    df_antes_meta = metas_antes[metas_antes["Clave de Meta"] == clave_meta]

                    fila_ahora = df_ahora_meta.head(1)
                    fila_antes = df_antes_meta.head(1)

                    col1, col2 = st.columns(2)

                    # Comparativos cualitativos
                    for campo in campos_metas_texto:
                        valor_ahora = str(fila_ahora[campo].values[0]) if not fila_ahora.empty else ""
                        valor_antes = str(fila_antes[campo].values[0]) if not fila_antes.empty else ""

                        if campo == "Descripción de la Meta":
                            antes_html, ahora_html = resaltar_diferencias(valor_antes, valor_ahora)

                            col1.markdown(f"**{campo} (Antes)**")
                            col1.markdown(f"<div style='border:1px solid #ccc;padding:8px'>{antes_html}</div>", unsafe_allow_html=True)

                            col2.markdown(f"**{campo} (Ahora)**")
                            col2.markdown(f"<div style='border:1px solid #ccc;padding:8px'>{ahora_html}</div>", unsafe_allow_html=True)
                        else:
                            col1.markdown(f"**{campo} (Antes)**")
                            col1.markdown(valor_antes)
                            col2.markdown(f"**{campo} (Ahora)**")
                            col2.markdown(valor_ahora)

                    # ---------- Métricas generales ----------
                    total_antes_cantidad = df_antes_meta["Cantidad Total"].sum()
                    total_ahora_cantidad = df_ahora_meta["Cantidad Total"].sum()
                    total_antes_monto = df_antes_meta["Monto Total"].sum()
                    total_ahora_monto = df_ahora_meta["Monto Total"].sum()

                    diferencia_cantidad = total_ahora_cantidad - total_antes_cantidad
                    diferencia_monto = total_ahora_monto - total_antes_monto

                    color_cantidad = "green" if diferencia_cantidad > 0 else "red" if diferencia_cantidad < 0 else "black"
                    color_monto = "green" if diferencia_monto > 0 else "red" if diferencia_monto < 0 else "black"

                    col_total1, col_total2 = st.columns(2)
                    col_total1.metric("Cantidad Total (Ahora)", f"{total_ahora_cantidad:,.2f}")
                    col_total1.markdown(f"<span style='color:{color_cantidad}'>Diferencia: {diferencia_cantidad:,.2f}</span>", unsafe_allow_html=True)

                    col_total2.metric("Monto Total (Ahora)", f"${total_ahora_monto:,.2f}")
                    col_total2.markdown(f"<span style='color:{color_monto}'>Diferencia: ${diferencia_monto:,.2f}</span>", unsafe_allow_html=True)

                    # ---------- Comparativo por Municipio ----------
                    st.markdown("##### Comparativo por Municipio")

                    # Determinar valores únicos de "Registro Presupuestal" disponibles en ambos DataFrames
                    registros_disponibles = pd.concat([
                        df_antes_meta["Registro Presupuestal"],
                        df_ahora_meta["Registro Presupuestal"]
                    ]).dropna().unique().tolist()

                    # Ordenar si es posible
                    orden_preferido = ["Centralizado", "Descentralizado", "Sin Registro"]
                    registros_filtrados = [r for r in orden_preferido if r in registros_disponibles]

                    # Agregar opción "Todos"
                    opciones_radio = ["Todos"] + registros_filtrados

                    # Mostrar filtro dinámico
                    if opciones_radio and len(opciones_radio) > 0:
                        registro_opcion = st.radio(
                            "Filtrar por Registro Presupuestal:",
                            opciones_radio,
                            horizontal=True,
                            key=f"radio_registro_{clave_meta_filtro_valor}"
                        )
                    else:
                        registro_opcion = None

                    # Aplicar filtro según selección
                    if registro_opcion != "Todos":
                        df_antes_meta = df_antes_meta[df_antes_meta["Registro Presupuestal"] == registro_opcion]
                        df_ahora_meta = df_ahora_meta[df_ahora_meta["Registro Presupuestal"] == registro_opcion]

                    # Agrupar y resumir por municipio
                    resumen_antes = df_antes_meta.groupby("Municipio")[["Cantidad Total", "Monto Total"]].sum().reset_index()
                    resumen_ahora = df_ahora_meta.groupby("Municipio")[["Cantidad Total", "Monto Total"]].sum().reset_index()

                    # Renombrar columnas
                    resumen_antes = resumen_antes.rename(columns={
                        "Cantidad Total": "Cantidad Total (Antes)",
                        "Monto Total": "Monto Total (Antes)"
                    })
                    resumen_ahora = resumen_ahora.rename(columns={
                        "Cantidad Total": "Cantidad Total (Ahora)",
                        "Monto Total": "Monto Total (Ahora)"
                    })

                    # Unir ambos resúmenes
                    resumen_comparativo = pd.merge(resumen_antes, resumen_ahora, on="Municipio", how="outer").fillna(0)

                    # Calcular columna de diferencia de monto
                    resumen_comparativo["Diferencia de Monto"] = resumen_comparativo["Monto Total (Ahora)"] - resumen_comparativo["Monto Total (Antes)"]

                    # Reordenar columnas
                    resumen_comparativo = resumen_comparativo[[
                        "Municipio",
                        "Cantidad Total (Antes)", "Cantidad Total (Ahora)",
                        "Monto Total (Antes)", "Monto Total (Ahora)",
                        "Diferencia de Monto"
                    ]]

                    # Función para resaltar diferencias
                    def resaltar_diferencias_montos(fila):
                        try:
                            if fila["Diferencia de Monto"] != 0:
                                return [""]*3 + ["background-color: #fff3cd"]*3
                        except:
                            pass
                        return [""] * len(fila)

                    # Preparar estilo y formato
                    styled_df = resumen_comparativo.style.apply(resaltar_diferencias_montos, axis=1).format({
                        "Cantidad Total (Antes)": "{:,.2f}",
                        "Cantidad Total (Ahora)": "{:,.2f}",
                        "Monto Total (Antes)": "${:,.2f}",
                        "Monto Total (Ahora)": "${:,.2f}",
                        "Diferencia de Monto": "${:,.2f}"
                    })

                    # Mostrar
                    st.dataframe(styled_df, use_container_width=True)

    else: 
        st.info("Selecciona una Clave de Meta para ver el comparativo de metas, cronograma, partidas y cumplimiento.")


############################## SECCIÓN DE CRONOGRAMA ############################################################

    if clave_meta_filtro_valor:
        with subtabs[1]:
            st.write("📆 Cronograma")
       
            clave_meta_seleccionada = clave_meta_filtro_valor

            df_crono_ahora_qm = metas_crono_ahora[metas_crono_ahora["Clave de Meta"] == clave_meta_seleccionada]
            df_crono_antes_qm = metas_crono_antes[metas_crono_antes["Clave de Meta"] == clave_meta_seleccionada]

            if df_crono_ahora_qm.empty and df_crono_antes_qm.empty:
                st.info("No se encontraron actividades o hitos para esta meta en ninguna de las versiones.")
            else:
                # Marcar versión
                df_crono_ahora_qm = df_crono_ahora_qm.copy()
                df_crono_ahora_qm["Versión"] = "Ahora"

                df_crono_antes_qm = df_crono_antes_qm.copy()
                df_crono_antes_qm["Versión"] = "Antes"

                df_crono_comparado = pd.concat([df_crono_antes_qm, df_crono_ahora_qm], ignore_index=True)

                # Convertir clave numérica
                df_crono_comparado["Clave Num"] = pd.to_numeric(
                    df_crono_comparado["Clave de Actividad /Hito"], errors="coerce"
                )

                df_crono_comparado["Actividad"] = (
                    df_crono_comparado["Clave de Actividad /Hito"].astype(str) +
                    " - " + df_crono_comparado["Descripción"].astype(str) +
                    " (" + df_crono_comparado["Versión"] + ")"
                )

                orden_y = df_crono_comparado.sort_values("Clave Num")["Actividad"].tolist()

                # Ajustar fechas iguales (inicio = término)
                mismo_dia = (
                    df_crono_comparado["Fecha de Inicio"] == df_crono_comparado["Fecha de Termino"]
                )
                df_crono_comparado.loc[mismo_dia, "Fecha de Termino"] += pd.Timedelta(days=1)

                # Gantt
                fig = px.timeline(
                    df_crono_comparado,
                    x_start="Fecha de Inicio",
                    x_end="Fecha de Termino",
                    y="Actividad",
                    color="Versión",
                    color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"},
                    title=f"Cronograma de Actividades / Hitos - Meta {clave_meta_seleccionada}"
                )

                fig.update_yaxes(categoryorder="array", categoryarray=orden_y)
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(height=600)

                st.plotly_chart(fig, use_container_width=True)

                # Tabla de detalle (solo versión actual)
                st.markdown("##### Detalle de Actividades / Hitos (Versión Actual)")

                columnas_tabla = [
                    "Clave de Actividad /Hito", "Fase Actividad / Hito", "Descripción",
                    "Fecha de Inicio", "Fecha de Termino", "Monto Actividad / Hito"
                ]

                tabla_actual = df_crono_ahora_qm[columnas_tabla].sort_values("Clave de Actividad /Hito").copy()

                tabla_actual["Monto Actividad / Hito"] = tabla_actual["Monto Actividad / Hito"].apply(
                    lambda x: f"${x:,.2f}" if pd.notna(x) else ""
                )
                tabla_actual["Fecha de Inicio"] = tabla_actual["Fecha de Inicio"].dt.strftime("%d/%m/%Y")
                tabla_actual["Fecha de Termino"] = tabla_actual["Fecha de Termino"].dt.strftime("%d/%m/%Y")

                st.dataframe(tabla_actual, use_container_width=True)
    else: "Selecciona una Clave de Meta para ver las secciones de Cronograma, Partidas y Cumplimiento"           


############################## SECCIÓN DE METAS-PARTIDAS ############################################################

    if clave_meta_filtro_valor:
        with subtabs[2]:
            st.write("💰 Partidas")

            clave_meta = clave_meta_filtro_valor

            df_partidas_ahora_qm = metas_partidas_ahora[metas_partidas_ahora["Clave de Meta"] == clave_meta].copy()
            df_partidas_antes_qm = metas_partidas_antes[metas_partidas_antes["Clave de Meta"] == clave_meta].copy()

            # Convertir Partida a formato 4 caracteres, omitiendo NaN
            df_partidas_ahora_qm["Partida_fmt"] = df_partidas_ahora_qm["Partida"].apply(
                lambda x: str(int(float(x)))[:4] if pd.notnull(x) else None
            )
            df_partidas_antes_qm["Partida_fmt"] = df_partidas_antes_qm["Partida"].apply(
                lambda x: str(int(float(x)))[:4] if pd.notnull(x) else None
            )

            # Eliminar filas con Partida no válida
            df_partidas_ahora_qm = df_partidas_ahora_qm[df_partidas_ahora_qm["Partida_fmt"].notna()]
            df_partidas_antes_qm = df_partidas_antes_qm[df_partidas_antes_qm["Partida_fmt"].notna()]

            # Comparativo de montos anuales por partida
            resumen_ahora = (
                df_partidas_ahora_qm.groupby("Partida_fmt")["Monto Anual"].sum().reset_index()
                .rename(columns={"Monto Anual": "Monto Anual (Ahora)"})
            )
            resumen_antes = (
                df_partidas_antes_qm.groupby("Partida_fmt")["Monto Anual"].sum().reset_index()
                .rename(columns={"Monto Anual": "Monto Anual (Antes)"})
            )

            df_comparativo = pd.merge(resumen_antes, resumen_ahora, on="Partida_fmt", how="outer").fillna(0)
            df_comparativo["Diferencia"] = (
                df_comparativo["Monto Anual (Ahora)"] - df_comparativo["Monto Anual (Antes)"]
            )

            # Estilizado
            def resaltar_diferencias(val):
                return "background-color: #fff3cd" if val != 0 else ""

            styled_df = df_comparativo.style.applymap(resaltar_diferencias, subset=["Diferencia"]).format({
                "Monto Anual (Antes)": "${:,.2f}",
                "Monto Anual (Ahora)": "${:,.2f}",
                "Diferencia": "${:,.2f}"
            })

            st.markdown("##### Comparativo de Montos por Partida")
            st.dataframe(styled_df, use_container_width=True)

            # --- Distribución mensual ---
            meses = [
                "Monto Enero", "Monto Febrero", "Monto Marzo", "Monto Abril", "Monto Mayo",
                "Monto Junio", "Monto Julio", "Monto Agosto", "Monto Septiembre",
                "Monto Octubre", "Monto Noviembre", "Monto Diciembre"
            ]

            partidas_disponibles = sorted(df_comparativo["Partida_fmt"].unique().tolist())
            partidas_mostrar = ["Todas"] + partidas_disponibles

            partida_seleccionada = st.radio("Selecciona una partida", partidas_mostrar, horizontal=True)

            if partida_seleccionada == "Todas":
                df_mes_ahora = df_partidas_ahora_qm
                df_mes_antes = df_partidas_antes_qm
            else:
                df_mes_ahora = df_partidas_ahora_qm[df_partidas_ahora_qm["Partida_fmt"] == partida_seleccionada]
                df_mes_antes = df_partidas_antes_qm[df_partidas_antes_qm["Partida_fmt"] == partida_seleccionada]

            sum_mensual_ahora = df_mes_ahora[meses].sum()
            sum_mensual_antes = df_mes_antes[meses].sum()

            df_mensual = pd.DataFrame({
                "Mes": [mes.replace("Monto ", "") for mes in meses],
                "Antes": sum_mensual_antes.values,
                "Ahora": sum_mensual_ahora.values
            })

            fig = px.bar(
                df_mensual,
                x="Mes",
                y=["Antes", "Ahora"],
                barmode="group",
                title=f"Distribución Mensual de Montos - Meta {clave_meta}",
                labels={"value": "Monto", "variable": "Versión"},
                color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"}
            )

            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)




 ############################## SECCIÓN DE METAS - CUMPLIMIENTO ############################################################
    if clave_meta_filtro_valor:

        with subtabs[3]:
            st.write("✅ Cumplimiento Programado")

            clave_meta = clave_meta_filtro_valor

            df_cump_ahora = cumplimiento_ahora[ cumplimiento_ahora["Clave de Meta"] == clave_meta ]
            df_cump_antes = cumplimiento_antes[ cumplimiento_antes["Clave de Meta"] == clave_meta ]

            # Obtener cantidad programada
            cantidad_ahora = df_cump_ahora["Cantidad"].values[0] if not df_cump_ahora.empty else None
            cantidad_antes = df_cump_antes["Cantidad"].values[0] if not df_cump_antes.empty else None

            # Mostrar métricas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cantidad Programada (Ahora)", f"{cantidad_ahora:.2f}" if cantidad_ahora is not None else "—")
            with col2:
                st.metric("Cantidad Programada (Antes)", f"{cantidad_antes:.2f}" if cantidad_antes is not None else "—")

            # Gráfico de cumplimiento mensual
            meses = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            columnas_mensuales = [f"Cumplimiento {mes}" for mes in meses]

            valores_ahora = (
                df_cump_ahora.iloc[0][columnas_mensuales].fillna(0).values if not df_cump_ahora.empty else [0] * 12
            )
            valores_antes = (
                df_cump_antes.iloc[0][columnas_mensuales].fillna(0).values if not df_cump_antes.empty else [0] * 12
            )

            df_cumplimiento = pd.DataFrame({
                "Mes": meses * 2,
                "Valor": list(valores_antes) + list(valores_ahora),
                "Versión": ["Antes"] * 12 + ["Ahora"] * 12
            })

            fig_cump = px.bar(
                df_cumplimiento,
                x="Mes",
                y="Valor",
                color="Versión",
                barmode="group",
                color_discrete_map={"Antes": "steelblue", "Ahora": "seagreen"},
                title=f"Cumplimiento Programado por Mes - Meta {clave_meta}"
            )
            fig_cump.update_layout(xaxis_tickangle=-45, height=400)

            st.plotly_chart(fig_cump, use_container_width=True)



else:
    st.markdown("""
    ## 👋 Bienvenido a la app de Revisión de Programación SED

    Para comenzar, sigue estos pasos desde el panel lateral:

    1. 📂 **Carga los archivos** correspondientes a los cortes **Antes** y **Ahora**.
    2. 🧭 **Selecciona un Eje**.
    3. 🏛️ **Selecciona la Dependencia o Entidad**.
    4. 🔑 **Elige la Clave Q** del proyecto que deseas revisar.

    Una vez seleccionada una Clave Q, se mostrarán las distintas secciones comparativas para facilitar el análisis de la información entre fechas de corte.

    > Si no ves nada aún, asegúrate de haber subido ambos archivos y de haber seleccionado una Clave Q válida.
    """)
