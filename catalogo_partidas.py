# catalogo_partidas.py
import io
import re
import pandas as pd

TABLA = """Partida\tDefinición\tRestringida\tValidador
1000\tSERVICIOS PERSONALES\t\t
1100\t REMUNERACIONES AL PERSONAL DE CARÁCTER PERMANENTE\t\t
1110\tDietas\t\t
1120\tHaberes\t\t
1130\tSueldos base al personal permanente\t\t
1140\tRemuneraciones por adscripción laboral en el extranjero\t\t
1200\tREMUNERACIONES AL PERSONAL DE CARÁCTER TRANSITORIO\t\t
1210\t Honorarios asimilables a salarios\t\t
1220\tSueldos base al personal eventual\t\t
1230\t Retribuciones por servicios de carácter social\t\t
1240\tRetribución a los representantes de los trabajadores y de los patrones en la Junta  de Conciliación y Arbitraje\t\t
1300\t REMUNERACIONES ADICIONALES Y ESPECIALES\t\t
1310\tPrimas por años de servicios efectivos prestados\t\t
1320\tPrimas de vacaciones, dominical y gratificación de fin de año\t\t
1330\tHoras extraordinarias\t\t
1340\tCompensaciones\t\t
1350\tSobrehaberes\t\t
1360\tAsignaciones de técnico, de mando, por comisión, de vuelo y de técnico especial\t\t
1370\t Honorarios especiales\t\t
1380\tParticipaciones por vigilancia en el cumplimiento de las leyes y custodia de valores\t\t
1400\tSEGURIDAD SOCIAL\t\t
1410\tAportaciones de seguridad social\t\t
1420\tAportaciones a fondos de vivienda\t\t
1430\tAportaciones al sistema para el retiro\t\t
1440\t Aportaciones para seguros\t\t
1500\tOTRAS PRESTACIONES SOCIALES Y ECONÓMICAS\t\t
1510\tCuotas para el fondo de ahorro y fondo de trabajo\t\t
1520\tIndemnizaciones\t\t
1530\tPrestaciones y haberes de retiro\t\t
1540\tPrestaciones contractuales\t\t
1550\tApoyos a la capacitación de los servidores públicos\t\t
1590\tOTRAS PRESTACIONES SOCIALES Y ECONÓMICAS\t\t
1600\tPREVISIONES\t\t
1610\tPrevisiones de carácter laboral, económica y de seguridad social\t\t
1700\tPAGO DE ESTÍMULOS A SERVIDORES PÚBLICOS\t\t
1710\tEstímulos\t\t
1720\tRecompensas\t\t
2000\tMATERIALES Y SUMINISTROS\t\t
2100\t MATERIALES DE ADMINISTRACIÓN, EMISIÓN DE DOCUMENTOS Y ARTÍCULOS OFICIALES\t\t
2110\tMateriales, útiles y equipos menores de oficina\t\t
2120\tMateriales y útiles de impresión y reproducción\t\t
2130\tMaterial estadístico y geográfico\t\t
2140\tMateriales, útiles y equipos menores de tecnologías de la información y comunicaciones\tsi\tDGTIT
2150\tMaterial impreso e información digital\t\t
2160\t Material de limpieza\t\t
2170\tMateriales y útiles de enseñanza\t\t
2180\tMateriales para el registro e identificación de bienes y personas\t\t
2200\tALIMENTOS Y UTENSILIOS\t\t
2210\tProductos alimenticios para personas\t\t
2220\tProductos alimenticios para animales\t\t
2230\tUtensilios para el servicio de alimentación\t\t
2300\t MATERIAS PRIMAS Y MATERIALES DE PRODUCCIÓN Y COMERCIALIZACIÓN\t\t
2310\tProductos alimenticios, agropecuarios y forestales adquiridos como materia prima\t\t
2320\tInsumos textiles adquiridos como materia prima\t\t
2330\tProductos de papel, cartón e impresos adquiridos como materia prima\t\t
2340\tCombustibles, lubricantes, aditivos, carbón y sus derivados adquiridos como materia prima\t\t
2350\tProductos químicos, farmacéuticos y de laboratorio adquiridos como materia prima\t\t
2360\tProductos metálicos y a base de minerales no metálicos adquiridos como materia prima\t\t
2370\tProductos de cuero, piel, plástico y hule adquiridos como materia prima\t\t
2380\tMercancías adquiridas para su comercialización\t\t
2390\tOtros productos adquiridos como materia prima\t\t
2400\t MATERIALES Y ARTÍCULOS DE CONSTRUCCIÓN Y DE REPARACIÓN\t\t
2410\tProductos minerales no metálicos\t\t
2420\tCemento y productos de concreto\t\t
2430\tCal, yeso y productos de yeso\t\t
2440\tMadera y productos de madera\t\t
2450\tVidrio y productos de vidrio\t\t
2460\tMaterial eléctrico y electrónico\t\t
2470\tArtículos metálicos para la construcción\t\t
2480\tMateriales complementarios\t\t
2490\tOtros materiales y artículos de construcción y reparación\t\t
2500\tPRODUCTOS QUÍMICOS, FARMACÉUTICOS Y DE LABORATORIO\t\t
2510\tProductos químicos básicos\t\t
2520\tFertilizantes, pesticidas y otros agroquímicos\t\t
2530\tMedicinas y productos farmacéuticos\t\t
2540\tMateriales, accesorios y suministros médicos\t\t
2550\tMateriales, accesorios y suministros de laboratorio\t\t
2560\tFibras sintéticas, hules, plásticos y derivados\t\t
2590\tOtros productos químicos\t\t
2600\tCOMBUSTIBLES, LUBRICANTES Y ADITIVOS\t\t
2610\tCOMBUSTIBLES, LUBRICANTES Y ADITIVOS\tsi\tDGREMSGyC
2620\tCarbón y sus derivados\t\t
2700\tVESTUARIO, BLANCOS, PRENDAS DE PROTECCIÓN Y ARTÍCULOS DEPORTIVOS\t\t
2710\t Vestuario y uniformes\tsi\tDGREMSGyC
2720\t Prendas de seguridad y protección personal\t\t
2730\tArtículos deportivos\t\t
2740\tProductos textiles\t\t
2750\t Blancos y otros productos textiles, excepto prendas de vestir\t\t
2800\tMATERIALES Y SUMINISTROS PARA SEGURIDAD\t\t
2810\tSustancias y materiales explosivos\t\t
2820\tMateriales de seguridad pública\t\t
2830\tPrendas de protección para seguridad pública y nacional\t\t
2900\tHERRAMIENTAS, REFACCIONES Y ACCESORIOS MENORES\t\t
2910\tHerramientas menores\t\t
2920\tRefacciones y accesorios menores de edificios\t\t
2930\t Refacciones y accesorios menores de mobiliario y equipo de administración, educacional y recreativo\t\t
2940\tRefacciones y accesorios menores de equipo de cómputo y tecnologías de la información\tsi\tDGTIT
2950\tRefacciones y accesorios menores de equipo e instrumental médico y de laboratorio\t\t
2960\tRefacciones y accesorios menores de equipo de transporte\t\t
2970\tRefacciones y accesorios menores de equipo de defensa y seguridad\t\t
2980\tRefacciones y accesorios menores de maquinaria y otros equipos\t\t
2990\t Refacciones y accesorios menores otros bienes muebles\t\t
3000\tSERVICIOS GENERALES\t\t
3100\tSERVICIOS BÁSICOS\t\t
3110\tEnergía eléctrica\tsi\tDGREMSGyC
3120\tGas\t\t
3130\tAgua\tsi\tDGREMSGyC
3140\tTelefonía tradicional\tsi\tDGREMSGyC
3150\tTelefonía celular\tsi\tDGREMSGyC
3160\tServicios de telecomunicaciones y satélites\tsi\tDGREMSGyC
3170\tServicios de acceso a Internet, redes y procesamiento de información\tsi\tDGREMSGyC
3180\tServicios postales y telegráficos\t\t
3190\tServicios integrales y otros servicios\t\t
3200\t SERVICIOS DE ARRENDAMIENTO\tsi\tDGREMSGyC
3210\tArrendamiento de terrenos\tsi\tDGREMSGyC
3220\tArrendamiento de edificios\tsi\tDGREMSGyC
3230\tArrendamiento de mobiliario y equipo de administración, educacional y recreativo\t\t
3240\tArrendamiento de equipo e instrumental médico y de laboratorio\t\t
3250\tArrendamiento de equipo de transporte\tsi*\tDGREMSGyC
3260\tArrendamiento de maquinaria, otros equipos y herramientas\t\t
3270\tArrendamiento de activos intangibles\tsi\tDGTIT
3280\tArrendamiento financiero\t\t
3290\tOtros arrendamientos\tsi*\tDGREMSGyC
3300\tSERVICIOS PROFESIONALES, CIENTÍFICOS, TÉCNICOS Y OTROS SERVICIOS\t\t
3310\tServicios legales, de contabilidad, auditoría y relacionados\tsi\tSA
3320\tServicios de diseño, arquitectura, ingeniería y actividades relacionadas\t\t
3330\tServicios de consultoría administrativa, procesos, técnica y en tecnologías de la información\tsi\tSA
3340\tServicios de capacitación\tsi\tSA
3350\tServicios de investigación científica y desarrollo\t\t
3360\tServicios de apoyo administrativo, traducción, fotocopiado e impresión\tsi\tDGREMSGyC
3370\tServicios de protección y seguridad\t\t
3380\tServicios de vigilancia\tsi\tDGREMSGyC
3390\tServicios profesionales, científicos y técnicos integrales\tsi\tDGREMSGyC
3400\tSERVICIOS FINANCIEROS, BANCARIOS Y COMERCIALES\t\t
3410\tServicios financieros y bancarios\t\t
3420\tServicios de cobranza, investigación crediticia y similar\t\t
3430\tServicios de recaudación, traslado y custodia de valores\t\t
3440\tSeguros de responsabilidad patrimonial y fianzas\tsi\tDGREMSGyC
3450\tSeguros de bienes patrimoniales\tsi\tDGREMSGyC
3460\tAlmacenaje, envase y embalaje\t\t
3470\tFletes y maniobras\t\t
3480\tComisiones por ventas\t\t
3490\tServicios financieros, bancarios y comerciales integrales\t\t
3500\tSERVICIOS DE INSTALACIÓN, REPARACIÓN, MANTENIMIENTO Y CONSERVACIÓN\t\t
3510\tConservación y mantenimiento menor de inmuebles\tsi*\tDGREMSGyC
3520\tInstalación, reparación y mantenimiento de mobiliario y equipo de administración, educacional y recreativo\t\t
3530\tInstalación, reparación y mantenimiento de equipo de cómputo y tecnologías de la información\tsi\tDGTIT
3540\tInstalación, reparación y mantenimiento de equipo e instrumental médico y de laboratorio\t\t
3550\tReparación y mantenimiento de equipo de transporte\tsi\tDGREMSGyC
3560\tReparación y mantenimiento de equipo de defensa y seguridad\t\t
3570\tInstalación, reparación y mantenimiento de maquinaria, otros equipos y herramienta\t\t
3580\tServicios de limpieza y manejo de desechos\tsi\tDGREMSGyC
3590\tServicios de jardinería y fumigación\tsi\tDGREMSGyC
3600\t SERVICIOS DE COMUNICACIÓN SOCIAL Y PUBLICIDAD\tsi\tCGCS
3611\tDifusión por radio, televisión y prensa sobre programas y actividades gubernamentales\tsi\tCGCS
3612\tDifusión por medio alternativos sobre programas y actividades gubernamentales\tsi\tCGCS
3620\tDifusión por radio, televisión, y otros medios de mensajes comerciales para promover la venta de bienes y servicios\tsi\tCGCS
3630\tServicios de creatividad, preproducción y producción de publicidad, excepto Internet\tsi\tCGCS
3640\tServicios de revelado de fotografías\tsi\tCGCS
3650\tServicios de la industria fílmica, del sonido y del video\tsi\tCGCS
3660\tServicio de creación y difusión de contenido exclusivamente a través de Internet\tsi\tCGCS
3690\tOtros servicios de información\tsi\tCGCS
3700\tSERVICIOS DE TRASLADO Y VIÁTICOS\t\t
3710\t Pasajes aéreos\tsi*\tSA
3720\tPasajes terrestres\t\t
3730\tPasajes marítimos, lacustres y fluviales\t\t
3740\t Autotransporte\t\t
3750\tViáticos en el país\t\t
3760\t Viáticos en el extranjero\tsi*\tSA
3770\tGastos de instalación y traslado de menaje\t\t
3780\tServicios integrales de traslado y viáticos\t\t
3790\t Otros servicios de traslado y hospedaje\t\t
3800\tSERVICIOS OFICIALES\t\t
3810\tGastos de ceremonial\tsi*\tSA
3820\tGastos de orden social y cultural\tsi*\tSA
3830\tCongresos y convenciones\tsi*\tSA
3840\tExposiciones\t\t
3850\t Gastos de representación\t\t
3900\tOTROS SERVICIOS GENERALES\t\t
3910\tServicios funerarios y de cementerios\t\t
3920\tImpuestos y derechos\t\t
3930\tImpuestos y derechos de importación\t\t
3940\tSentencias y resoluciones judiciales\t\t
3950\tPenas, multas, accesorios y actualizaciones\t\t
3960\tOtros gastos por responsabilidades\t\t
3980\tImpuesto sobre nóminas y otros que se deriven de una relación laboral\t\t
3990\tOTROS SERVICIOS GENERALES\t\t
4000\tTRANSFERENCIAS, ASIGNACIONES, SUBSIDIOS Y OTRAS AYUDAS\t\t
4100\tTRANSFERENCIAS INTERNAS Y ASIGNACIONES AL SECTOR PÚBLICO\t\t
4111\tAsignaciones presupuestarias al Poder Ejecutivo para servicios personales\t\t
4112\tAsignaciones presupuestarias al Poder Ejecutivo para materiales y suministros\t\t
4113\tAsignaciones presupuestarias al Poder Ejecutivo para servicios generales\t\t
4114\tAsignaciones presupuestarias al Poder Ejecutivo de gasto corriente para asignaciones, subsidios y otras ayudas\t\t
4115\tAsignaciones presupuestarias al Poder Ejecutivo para bienes muebles, inmuebles e intangibles\t\t
4116\tAsignaciones presupuestarias al Poder Ejecutivo para inversión pública\t\t
4117\tAsignaciones presupuestarias al Poder Ejecutivo de gasto corriente para inversiones financieras y otras provisiones\t\t
4118\tAsignaciones presupuestarias al Poder Ejecutivo de gasto de capital para asignaciones, subsidios y otras ayudas\t\t
4119\tAsignaciones presupuestarias al Poder Ejecutivo de gasto de capital para inversiones financieras y otras provisiones\t\t
4121\tAsignaciones presupuestarias al Poder Legislativo para servicios personales\t\t
4122\tAsignaciones presupuestarias al Poder Legislativo para materiales y suministros\t\t
4123\tAsignaciones presupuestarias al Poder Legislativo para servicios generales\t\t
4124\tAsignaciones presupuestarias al Poder Legislativo de gasto corriente para asignaciones, subsidios y otras ayudas\t\t
4125\tAsignaciones presupuestarias al Poder Legislativo para bienes muebles, inmuebles e intangibles\t\t
4126\tAsignaciones presupuestarias al Poder Legislativo para inversión pública\t\t
4127\tAsignaciones presupuestarias al Poder Legislativo de gasto corriente para inversiones financieras y otras provisiones\t\t
4128\tAsignaciones presupuestarias al Poder Legislativo de gasto de capital para asignaciones, subsidios y otras ayudas\t\t
4129\tAsignaciones presupuestarias al Poder Legislativo de gasto de capital para inversiones financieras y otras provisiones\t\t
4131\tAsignaciones presupuestarias al Poder Judicial para servicios personales\t\t
4132\tAsignaciones presupuestarias al Poder Judicial para materiales y suministros\t\t
4133\tAsignaciones presupuestarias al Poder Judicial para servicios generales\t\t
4134\tAsignaciones presupuestarias al Poder Judicial de gasto corriente para asignaciones, subsidios y otras ayudas\t\t
4135\tAsignaciones presupuestarias al Poder Judicial para bienes muebles, inmuebles e intangibles\t\t
4136\tAsignaciones presupuestarias al Poder Judicial para inversión pública\t\t
4137\tAsignaciones presupuestarias al Poder Judicial de gasto corriente para inversiones financieras y otras provisiones\t\t
4138\tAsignaciones presupuestarias al Poder Judicial de gasto de capital para asignaciones, subsidios y otras ayudas\t\t
4139\tAsignaciones presupuestarias al Poder Judicial de gasto de capital para inversiones financieras y otras provisiones\t\t
4141\tAsignaciones presupuestarias a Organismos Autónomos para servicios personales\t\t
4142\tAsignaciones presupuestarias a Organismos Autónomos para materiales y suministros\t\t
4143\tAsignaciones presupuestarias a Organismos Autónomos para servicios generales\t\t
4144\t Asignaciones presupuestarias a Organismos Autónomos de gasto corriente para asignaciones, subsidios y otras ayudas\t\t
4145\tAsignaciones presupuestarias a Organismos Autónomos para bienes muebles, inmuebles e intangibles\t\t
4146\tAsignaciones presupuestarias a Organismos Autónomos para inversión pública\t\t
4147\tAsignaciones presupuestarias a Organismos Autónomos de gasto corriente para inversiones financieras y otras provisiones\t\t
4148\tAsignaciones presupuestarias a Organismos Autónomos de gasto de capital para asignaciones, subsidios y otras ayudas\t\t
4149\tAsignaciones presupuestarias a Organismos Autónomos de gasto de capital para inversiones financieras y otras provisiones\t\t
4151\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras para servicios personales\t\t
4152\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras para materiales y suministros\t\t
4153\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras para servicios generales\t\t
4154\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras de gasto corriente para asignaciones, subsidios y otras ayudas\t\t
4155\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras para bienes muebles, inmuebles e intangibles\t\t
4156\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras para inversión pública\t\t
4157\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras de gasto corriente para inversiones financieras y otras provisiones\t\t
4158\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras de gasto de capital para asignaciones, subsidios y otras ayudas\t\t
4159\tTransferencias internas otorgadas a entidades paraestatales no empresariales y no financieras de gasto de capital para inversiones financieras y otras provisiones\t\t
4161\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras para servicios personales\t\t
4162\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras para materiales y suministros\t\t
4163\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras para servicios generales\t\t
4164\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras de gasto corriente para asignaciones, subsidios y otras ayudas\t\t
4165\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras para bienes muebles, inmuebles e intangibles\t\t
4166\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras para inversión pública\t\t
4167\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras de gasto corriente para inversiones financieras y otras provisiones\t\t
4168\tTransferencias internas otorgadas a entidades paraestatales empresariales y no\t\t
4169\tTransferencias internas otorgadas a entidades paraestatales empresariales y no financieras de gasto de capital para inversiones financieras y otras provisiones\t\t
4170\tTransferencias internas otorgadas a fideicomisos públicos empresariales y no financieros\t\t
4180\tTransferencias internas otorgadas a instituciones paraestatales públicas financieras\t\t
4190\tTransferencias internas otorgadas a fideicomisos públicos financieros\t\t
4200\tTRANSFERENCIAS AL RESTO DEL SECTOR PÚBLICO\t\t
4211\tTransferencias otorgadas a entidades paraestatales no empresariales y no financieras para gasto corriente\t\t
4212\tTransferencias otorgadas a entidades paraestatales no empresariales y no financieras para gasto corriente financieras para gasto de capital\t\t
4221\tTransferencias otorgadas a entidades paraestatales empresariales y no financieras para gasto corriente\t\t
4222\t Transferencias otorgadas a entidades paraestatales empresariales y no financieras para gasto de capital\t\t
4230\tTransferencias otorgadas a instituciones paraestatales públicas financieras\t\t
4241\tTransferencias otorgadas a entidades federativas y municipios para gasto corriente\t\t
4242\t Transferencias otorgadas a entidades federativas y municipios para gasto de capital\t\t
4250\t Transferencias a fideicomisos de entidades federativas y municipios\t\t
4300\tSUBSIDIOS Y SUBVENCIONES\t\t
4310\tSubsidios a la producción\t\t
4320\tSubsidios a la distribución\t\t
4330\tSubsidios a la inversión\t\t
4340\tSubsidios a la prestación de servicios públicos\t\t
4350\tSubsidios para cubrir diferenciales de tasas de interés\t\t
4360\tSubsidios a la vivienda\t\t
4370\tSubvenciones al consumo\t\t
4400\tAYUDAS SOCIALES\t\t
4410\tAyudas sociales a personas\t\t
4420\tBecas y otras ayudas para programas de capacitación\t\t
4430\tAyudas sociales a instituciones de enseñanza\t\t
4440\tAyudas sociales a actividades científicas o académicas\t\t
4450\tAyudas sociales a instituciones sin fines de lucro\t\t
4460\tAyudas sociales a cooperativas\t\t
4470\tAyudas sociales a entidades de interés público\t\t
4480\tAyudas por desastres naturales y otros siniestro\t\t
4500\tPENSIONES Y JUBILACIONES\t\t
4510\tPensiones\t\t
4520\tJubilaciones\t\t
4590\tOtras pensiones y jubilaciones\t\t
4600\tTRANSFERENCIAS A FIDEICOMISOS, MANDATOS Y OTROS ANÁLOGOS\t\t
4610\tTransferencias a fideicomisos del Poder Ejecutivo\t\t
4620\tTransferencias a fideicomisos del Poder Legislativo\t\t
4630\tTransferencias a fideicomisos del Poder Judicial\t\t
4640\tTransferencias a fideicomisos públicos de entidades paraestatales no empresariale y no financieras\t\t
4650\tTransferencias a fideicomisos públicos de entidades paraestatales empresariales y no financieras\t\t
4660\tTransferencias a fideicomisos de instituciones públicas financieras\t\t
4900\tTRANSFERENCIAS AL EXTERIOR\t\t
4910\tTransferencias para gobiernos extranjeros\t\t
4920\tTransferencias para organismos internacionales\t\t
4930\tTransferencias para el sector privado externo\t\t
5000\tBIENES MUEBLES, INMUEBLES E INTANGIBLES\t\t
5100\tMOBILIARIO Y EQUIPO DE ADMINISTRACIÓN\t\t
5110\tMuebles de oficina y estantería\tsi*\tDGREMSGyC
5120\tMuebles, excepto de oficina y estantería\t\t
5130\tBienes artísticos, culturales y científicos\t\t
5140\tObjetos de valor\t\t
5150\tEquipo de cómputo y de tecnologías de la información\tsi*\tDGTIT
5190\tOtros mobiliarios y equipos de administración\tsi*\tDGREMSGyC
5200\tMOBILIARIO YEQUIPO EDUCACIONAL Y RECREATIVO\t\t
5210\tEquipos y aparatos audiovisuales\t\t
5220\tAparatos deportivos\t\t
5230\tCámaras fotográficas y de video\t\t
5290\tOtro mobiliario y equipo educacional y recreativo\t\t
5300\tEQUIPO E INSTRUMENTAL MÉDICO Y DE LABORATORIO\t\t
5310\tEquipo médico y de laboratorio\t\t
5320\tInstrumental médico y de laboratorio\t\t
5400\tVEHÍCULOS Y EQUIPO DE TRANSPORTE\t\t
5410\tAutomóviles y camiones\tsi*\tDGREMSGyC
5420\tCarrocerías y remolques\t\t
5430\tEquipo aeroespacial\t\t
5440\tEquipo ferroviario\t\t
5450\tEmbarcaciones\t\t
5490\tOtros equipos de transporte\tsi*\tDGREMSGyC
5500\tEQUIPO DE DEFENSA Y SEGURIDAD\t\t
5510\tEQUIPO DE DEFENSA Y SEGURIDAD\t\t
5600\tMAQUINARIA, OTROS EQUIPOS Y HERRAMIENTAS\t\t
5610\tMaquinaria y equipo agropecuario\t\t
5620\tMaquinaria y equipo industrial\t\t
5630\tMaquinaria y equipo de construcción\t\t
5640\tSistemas de aire acondicionado, calefacción y de refrigeración industrial y comercial\t\t
5650\tEquipo de comunicación y telecomunicación\t\t
5660\tEquipos de generación eléctrica, aparatos y accesorios eléctricos\t\t
5670\tHerramientas y máquinas - herramienta\t\t
5690\tOtros equipos\t\t
5700\tACTIVOS BIOLÓGICOS\t\t
5710\tBovinos\t\t
5720\tPorcinos\t\t
5730\tAves\t\t
5740\tOvinos y caprinos\t\t
5750\tPeces y acuicultura\t\t
5760\tEquinos\t\t
5770\tEspecies menores y de zoológico\t\t
5780\tÁrboles y plantas\t\t
5790\tOtros activos biológicos\t\t
5800\tBIENES INMUEBLES\t\t
5810\tTerrenos\t\t
5820\tViviendas\t\t
5830\tEdificios no residenciales\t\t
5890\tOtros bienes inmuebles\t\t
5900\tACTIVOS INTANGIBLES\t\t
5910\tSoftware\t\t
5920\tPatentes\t\t
5930\tMarcas\t\t
5940\tDerechos\t\t
5950\tConcesiones\t\t
5960\tFranquicias\t\t
5970\tLicencias informáticas e intelectuales\t\t
5980\tLicencias industriales, comerciales y otras\t\t
5990\tOtros activos intangibles\t\t
6000\tINVERSIÓN PÚBLICA\t\t
6100\tOBRA PÚBLICA EN BIENES DE DOMINIO PÚBLICO\t\t
6110\tEdificación habitacional\t\t
6120\tEdificación no habitacional\t\t
6130\tConstrucción de obras para el abastecimiento de agua, petróleo, gas, electricidad y telecomunicaciones\t\t
6140\tDivisión de terrenos y construcción de obras de urbanización\t\t
6150\tConstrucción de vías de comunicación\t\t
6160\tOtras construcciones de ingeniería civil u obra pesada\t\t
6170\tInstalaciones y equipamiento en construcciones\t\t
6190\tTrabajos de acabados en edificaciones y otros trabajos especializados\t\t
6200\tOBRA PÚBLICA EN BIENES PROPIOS\t\t
6210\tEdificación habitacional\t\t
6220\tEdificación no habitacional\t\t
6230\tConstrucción de obras para el abastecimiento de agua, petróleo, gas, electricidad y telecomunicaciones\t\t
6240\tDivisión de terrenos y construcción de obras de urbanización\t\t
6250\tConstrucción de vías de comunicación\t\t
6260\tOtras construcciones de ingeniería civil u obra pesada\t\t
6270\tInstalaciones y equipamiento en construcciones\t\t
6290\tTrabajos de acabados en edificaciones y otros trabajos especializados\t\t
6300\tPROYECTOS PRODUCTIVOS Y ACCIONES DE FOMENTO\t\t
6310\tEstudios, formulación y evaluación de proyectos productivos no incluidos en conceptos anteriores de este capítulo\t\t
6320\tEjecución de proyectos productivos no incluidos en conceptos anteriores de este capítulo\t\t
7000\t INVERSIONES FINANCIERAS Y OTRAS PROVISIONES\t\t
7100\tINVERSIONES PARA EL FOMENTO DE ACTIVIDADES PRODUCTIVAS\t\t
7110\tCréditos otorgados por entidades federativas y municipios al sector social y privado para el fomento de actividades productivas\t\t
7120\tCréditos otorgados por las entidades federativas a municipios para el fomento de actividades productivas\t\t
7200\tACCIONES Y PARTICIPACIONES DE CAPITAL\t\t
7210\tAcciones y participaciones de capital en entidades paraestatales no empresariales y no financieras con fines de política económica\t\t
7220\tAcciones y participaciones de capital en entidades paraestatales empresariales y no financieras con fines de política económica\t\t
7230\tAcciones y participaciones de capital en instituciones paraestatales públicas financieras con fines de política económica\t\t
7240\t Acciones y participaciones de capital en el sector privado con fines de política económica\t\t
7250\tAcciones y participaciones de capital en organismos internacionales con fines de política económica\t\t
7260\tAcciones y participaciones de capital en el sector externo con fines de gestión de liquidez\t\t
7270\tAcciones y participaciones de capital en el sector público con fines de gestión de liquidez\t\t
7280\tAcciones y participaciones de capital en el sector privado con fines de gestión de liquidez\t\t
7300\tCOMPRA DE TÍTULOS Y VALORES\t\t
7310\tBonos\t\t
7320\tValores representativos de deuda adquiridos con fines de política económica\t\t
7330\tValores representativos de deuda adquiridos con fines de gestión de liquidez\t\t
7340\tObligaciones negociables adquiridas con fines de política económica\t\t
7350\tObligaciones negociables adquiridas con fines de gestión de liquidez\t\t
7390\tOtros valores\t\t
7400\tCONCESIÓN DE PRÉSTAMOS\t\t
7410\tConcesión de préstamos a entidades paraestatales no empresariales y no financieras  con fines de política económica\t\t
7420\tConcesión de préstamos a entidades paraestatales empresariales y no financieras  con fines de política económica\t\t
7430\tConcesión de préstamos a instituciones paraestatales públicas financieras con fines  de política económica\t\t
7440\tConcesión de préstamos a entidades federativas y municipios con fines de política  económica\t\t
7450\tConcesión de préstamos al sector privado con fines de política económica\t\t
7451\tConcesión de préstamos para liquidez al sector privado con fines de política  económica (Uso exclusivo del ISSEG)\t\t
7452\tConcesión de préstamos en garantía hipotecaria al sector privado con fines de 17  política económica (Uso exclusivo del ISSEG)\t\t
7460\tConcesión de préstamos al sector externo con fines de política económica\t\t
7470\tConcesión de préstamos al sector público con fines de gestión de liquidez\t\t
7480\tConcesión de préstamos al sector privado con fines de gestión de liquidez\t\t
7490\tConcesión de préstamos al sector externo con fines de gestión de liquidez\t\t
7500\tINVERSIONES EN FIDEICOMISOS, MANDATOS Y OTROS ANÁLOGOS\t\t
7511\tInversiones en fideicomisos del Poder Ejecutivo para gasto corriente\t\t
7512\tInversiones en fideicomisos del Poder Ejecutivo para gasto de capital\t\t
7520\tInversiones en fideicomisos del Poder Legislativo\t\t
7530\tInversiones en fideicomisos del Poder Judicial\t\t
7540\tInversiones en fideicomisos públicos no empresariales y no financieros\t\t
7550\tInversiones en fideicomisos públicos empresariales y no financieros\t\t
7560\tInversiones en fideicomisos públicos financieros\t\t
7570\tInversiones en fideicomisos de entidades federativas\t\t
7580\tInversiones en fideicomisos de municipios\t\t
7590\tFideicomisos de empresas privadas y particulares\t\t
7600\tOTRAS INVERSIONES FINANCIERAS\t\t
7610\tDepósitos a largo plazo en moneda nacional\t\t
7620\tDepósitos a largo plazo en moneda extranjera\t\t
7900\tPROVISIONES PARA CONTINGENCIAS Y OTRAS EROGACIONES  ESPECIALES   ESPECIALES\t\t
7910\tContingencias por fenómenos naturales\t\t
7920\tContingencias socioeconómicas\t\t
7930\tErogaciones complementarias\t\t
7990\tOtras erogaciones especiales\t\t
8000\tPARTICIPACIONES Y APORTACIONES\t\t
8100\tPARTICIPACIONES\t\t
8110\tFondo general de participaciones\t\t
8120\tFondo de fomento municipal\t\t
8131\tParticipaciones de las entidades federativas a los municipios del Fondo General de  Participaciones\t\t
8132\tParticipaciones de las entidades federativas a los municipios del Fondo de Fomento  Municipal\t\t
8133\tParticipaciones de las entidades federativas a los municipios del Impuesto sobre  tenencia y uso de vehículos\t\t
8134\tParticipaciones de las entidades federativas a los municipios del Impuesto especial  sobre producción y servicios\t\t
8135\tParticipaciones de las entidades federativas a los municipios del Impuesto sobre  automóviles nuevos\t\t
8136\tParticipaciones de las entidades federativas a los municipios de Derechos por  expedición y refrendo de licencias de alcoholes\t\t
8137\tParticipaciones de las entidades federativas a los municipios del IEPS – gasolina y  diesel\t\t
8138\tParticipaciones de las entidades federativas a los municipios del Fondo de  Fiscalización (FOFIES)\t\t
8140\tOtros conceptos participables de la Federación a entidades federativas\t\t
8150\tOtros conceptos participables de la Federación a municipios\t\t
8160\tConvenios de colaboración administrativa\t\t
8300\tAPORTACIONES\t\t
8310\tAportaciones de la Federación a las entidades federativas\t\t
8320\tAportaciones de la Federación a municipios\t\t
8330\tAportaciones de las entidades federativas a los municipios\t\t
8340\tAportaciones previstas en leyes y decretos al sistema de protección social\t\t
8350\tAportaciones previstas en leyes y decretos compensatorias a entidades federativas  y municipios\t\t
8500\tCONVENIOS\t\t
8510\tConvenios de reasignación\t\t
8520\tConvenios de descentralización\t\t
8530\tOtros convenios\t\t
9000\tDEUDA PÚBLICA\t\t
9100\tAMORTIZACIÓN DE LA DEUDA PÚBLICA\t\t
9110\tAmortización de la deuda interna con instituciones de crédito\t\t
9110\tAmortización de la deuda interna por emisión de títulos y valores\t\t
9130\tAmortización de arrendamientos financieros nacionales\t\t
9140\tAmortización de la deuda externa con instituciones de crédito\t\t
9150\tAmortización de deuda externa con organismos financieros internacionales\t\t
9160\tAmortización de la deuda bilateral\t\t
9170\tAmortización de la deuda externa por emisión de títulos y valores\t\t
9180\tAmortización de arrendamientos financieros internacionales\t\t
9200\tINTERESES DE LA DEUDA PÚBLICA\t\t
9210\tIntereses de la deuda interna con instituciones de crédito\t\t
9220\tIntereses derivados de la colocación de títulos y valores\t\t
9230\tIntereses por arrendamientos financieros nacionales\t\t
9240\tIntereses de la deuda externa con instituciones de crédito\t\t
9250\tIntereses de la deuda con organismos financieros Internacionales\t\t
9260\tIntereses de la deuda bilateral\t\t
9270\tIntereses derivados de la colocación de títulos y valores en el exterior\t\t
9280\tIntereses por arrendamientos financieros internacionales\t\t
9300\tCOMISIONES DE LA DEUDA PÚBLICA\t\t
9310\tComisiones de la deuda pública interna\t\t
9320\tComisiones de la deuda pública externa\t\t
9400\tGASTOS DE LA DEUDA PÚBLICA\t\t
9410\tGastos de la deuda pública interna\t\t
9420\tGastos de la deuda pública externa\t\t
9500\tCOSTO POR COBERTURAS\t\t
9510\tCostos por cobertura de la deuda pública interna\t\t
9520\tCostos por cobertura de la deuda pública externa\t\t
9600\tAPOYOS FINANCIEROS\t\t
9610\tApoyos a intermediarios financieros\t\t
9620\tApoyos a ahorradores y deudores del Sistema Financiero Nacional\t\t
9900\tADEUDOS DE EJERCICIOS FISCALES ANTERIORES (ADEFAS)\t\t
9910\tADEFAS\t\t
"""

def _clean_str(s: str) -> str:
    # quita dobles espacios, tabs residuales y espacios a los lados
    return re.sub(r"\s+", " ", (s or "")).strip()

def _to_bool_si(s: str) -> bool:
    # "si", "si*", "SI", "" -> bool
    s = (s or "").strip().lower()
    return s.startswith("si")

def load_catalogo_df() -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(TABLA), sep="\t", dtype=str).fillna("")
    # Normaliza columnas y códigos a 4 dígitos
    df.columns = [c.strip().replace("ó","o").replace("í","i") for c in df.columns]
    # Asegura nombres esperados
    rename_map = {"Definicion": "Definición"} if "Definicion" in df.columns else {}
    if rename_map:
        df = df.rename(columns=rename_map)

    df["Partida_fmt"] = df["Partida"].astype(str).str.extract(r"(\d{4})", expand=False)
    df["Definición"] = df["Definición"].map(_clean_str)
    df["Restringida"] = df["Restringida"].map(_to_bool_si)
    df["Validador"] = df["Validador"].map(_clean_str)

    # Limpia duplicados (9110 aparece 2 veces en tu fuente)
    df = df.drop_duplicates(subset=["Partida_fmt"], keep="first")
    # Ordena por código
    df = df.sort_values("Partida_fmt").reset_index(drop=True)

    # Selección final de columnas
    return df[["Partida_fmt", "Definición", "Restringida", "Validador"]]

CATALOGO_PARTIDAS = load_catalogo_df()
