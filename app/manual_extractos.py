# manual_extractos.py
MANUAL = {
    "datos_generales": {
        "diagnostico": (
            "**Objetivo:** Justificar la existencia del proyecto con base en datos e indicadores.\n"
            "\n**Debes incluir:**\n"
            "- Población o área de enfoque\n"
            "- Problemática central\n"
            "- Magnitud del problema (con indicadores verificables)\n"
            "\n**Recomendaciones:**\n"
            "- Usa fuentes oficiales (INEGI, CONEVAL, encuestas)\n"
            "- Evita descripciones generales sin respaldo\n"
            "- No confundir con la descripción del proyecto\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026, p. 18-19*"
        ),
        "objetivo_general": (
            "**Objetivo:** Plantear el propósito último del proyecto.\n"
            "\n**Criterios:**\n"
            "- Redactar en **infinitivo**\n"
            "- Mantenerse durante toda la ejecución\n"
            "- No incluir mecanismos, fases o actividades específicas\n"
            "\n**Ejemplos:**\n"
            "• Consolidar y mantener condiciones de operación de la infraestructura penitenciaria\n"
            "• Implementar un sistema de registro obligatorio de maquinaria agrícola\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026, p. 20*"
        ),
        "descripcion_proyecto": (
            "**Objetivo:** Describir en qué consiste el proyecto de forma clara y ejecutiva.\n"
            "\n**Debes incluir:**\n"
            "- Alcances y características principales\n"
            "- Mecánica de operación\n"
            "- Actores que intervienen\n"
            "\n**Evita:**\n"
            "- Acotarlo a metas anuales\n"
            "- Incluir alcances que no están descritos aquí\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026, p. 21-22*"
        ),
        "avance_actual": (
            "**Objetivo:** Describir la situación actual del proyecto.\n"
            "\n**Proyectos de continuidad:**\n"
            "- Logros o progresos previos con impacto verificable\n"
            "- Evidencia de resultados\n"
            "\n**Proyectos nuevos:**\n"
            "- Avance en estudios, permisos, reglas de operación\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026, p. 22-23*"
        ),
        "alcance_anual": (
            "**Objetivo:** Sintetizar las metas del ejercicio presupuestal.\n"
            "\n**Requisitos:**\n"
            "- Coherencia con el objetivo general\n"
            "- Ser claros, medibles y alcanzables\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026, p. 23-24*"
        ),
    },
    "metas": {
        "descripcion_meta": (
            "**Objetivo:** Definir la meta con claridad siguiendo metodología SMART.\n"
            "\n**Debes incluir:**\n"
            "- Qué + Cómo + Para qué + (Lugar/tiempo)\n"
            "- Unidad de medida congruente\n"
            "- Cantidad y monto estimado\n"
            "\n**Evita:**\n"
            "- Redactar en términos de actividades\n"
            "- Usar descripciones genéricas\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026, p. 25-28*"
        ),
        "distribucion_territorial": (
            "**Objetivo:** Documentar ubicación, recursos y entregables.\n"
            "\n**Debes incluir:**\n"
            "- Municipios de ejecución\n"
            "- Monto y cantidad por origen de recurso\n"
            "- Esquema de registro presupuestal\n"
            "\n**Tip:**\n"
            "- Aunque sea bajo demanda, estima distribución probable\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026, p. 29-30*"
        ),
        # Estructura para Cronograma en el diccionario
        "cronograma": {
            "descripcion": (
                "**Objetivo:** El cronograma es la programación a nivel de meta que presenta actividades, "
                "fechas planificadas, duraciones, hitos y recursos necesarios para cumplir con las metas del proyecto, "
                "conforme a los Lineamientos."
            ),
            "tipos_proyecto": {
                "Obra": [
                    "Inicio de licitación o adjudicación directa",
                    "Fallo",
                    "Contratación",
                    "Periodo de ejecución (inicio y fin)",
                    "Cierre administrativo"
                ],
                "Subprograma – Obra": [
                    "Publicación de Reglas de Operación (si aplica)",
                    "Integración de cartera de obras",
                    "Firma de convenios",
                    "Disposición del recurso",
                    "Licitación/adjudicación",
                    "Contratación",
                    "Ejecución",
                    "Cierre administrativo"
                ],
                "Subprograma – Acción (con apoyos)": [
                    "Publicación de reglas",
                    "Convocatorias",
                    "Recepción y autorización de solicitudes",
                    "Trámite y entrega de apoyos"
                ],
                "Subprograma – Acción/Investigación (con servicios)": [
                    "Elaboración de términos de referencia",
                    "Investigación de mercado",
                    "Validaciones normativas",
                    "Contratación",
                    "Desarrollo del servicio",
                    "Revisión de productos",
                    "Cierre"
                ],
                "Subprograma – Acción (con adquisiciones)": [
                    "Términos de referencia",
                    "Investigación de mercado",
                    "Validaciones",
                    "Contratación/adjudicación",
                    "Entrega",
                    "Cierre"
                ]
            },
            "buenas_practicas": [
                "Asegurar que actividades, hitos y fechas sean realistas y coherentes con el calendario de gasto",
                "Desagregar actividades para mostrar el esfuerzo real, evitando términos genéricos",
                "Incluir dependencias y secuencias lógicas entre actividades",
                "Verificar que montos y recursos asignados por actividad correspondan al presupuesto aprobado",
                "Ajustar oportunamente en caso de prórrogas o adecuaciones presupuestarias autorizadas"
            ],
            "advertencias": [
                "La falta de coherencia con el calendario físico-financiero puede generar observaciones o retrasos en la liberación de recursos",
                "Cualquier afectación significativa al cronograma debe notificarse a la DGIP en un plazo máximo de 5 días hábiles"
            ],
            "referencia": (
                "📄 *Referencia: Manual de Documentación Qs 2025-2026 Pags 30-40; * Art. 11, 12, 24 y 27 de los **Lineamientos Generales para la Aplicación de Recursos "
                "en Materia de Proyectos de Inversión 2025**"
            )
        },

# Estructura para Partidas de Gasto en el diccionario        
        "partidas_gasto": (
            "**Objetivo:** Detallar el uso de recursos por partida presupuestal.\n"
            "\n**Requisitos:**\n"
            "- Coherencia con cronograma y distribución territorial\n"
            "- Asociar partidas a actividades específicas\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026*"
        ),
# Estructura para cumplimiento en el diccionario


        "cumplimiento": (
            "**Objetivo:** Verificar el grado de avance de metas y objetivos.\n"
            "\n**Requisitos:**\n"
            "- Usar indicadores confiables\n"
            "- Contar con evidencia documental\n"
            "- Relacionar resultados con objetivo general\n"
            "\n📄 *Referencia: Manual de Documentación Qs 2025-2026*"
        ),
    }
}
