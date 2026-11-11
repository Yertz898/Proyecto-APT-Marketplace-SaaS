# Analítica

Los dos modelos son problemas distintos y **no se miden con las mismas métricas**.
Esta tabla es la referencia; usar la métrica equivocada produce un número que parece
válido y no lo es.

| Modelo | Tipo de problema | Métricas | Línea base |
|---|---|---|---|
| Pronóstico de demanda mensual por producto o categoría | Regresión sobre serie de tiempo | MAPE, MAE, RMSE | Promedio móvil |
| Segmentación y riesgo de abandono de clientes | Clasificación sobre variables RFM | Precisión, exhaustividad, F1 | Regla por recencia |

El pronóstico es **por producto cuando hay historial suficiente y por categoría cuando no**.
En Joyas_ye es por categoría: sus lotes se venden una sola vez, así que no forman una serie
de tiempo. Los datos de entrenamiento son sintéticos, calibrados con los montos reales de
venta que entregó el cliente.

Reglas que no se negocian:

- Nunca usar accuracy, F1 ni matriz de confusión para el pronóstico de demanda.
- El pronóstico usa `predict`, nunca `predict_proba`: eso es de clasificación.
- Todo modelo se contrasta con su línea base. Si no la supera, no se integra.
- La **alerta de quiebre de stock** no es un tercer modelo: compara la demanda proyectada
  con el stock, y solo en los productos que lo controlan.
- Los descuentos están **fuera de alcance**. No hay motor de sugerencias: el precio por
  volumen se expresa con tramos, que son precios y no porcentajes.

## De dónde salen los datos

Joyas_ye **no lleva registro digital de sus ventas**. Lo único que existe es una planilla
que el dueño llevó a mano durante dos años, y sin ella no hay con qué entrenar nada.

El archivo vive en `data/` y **no se versiona**: trae 1.821 nombres de personas que no
dieron permiso para aparecer en un repositorio público. Ver `data/README.md`.

### Cómo se lee

El formato de la planilla cambió **siete veces**, siguiendo al negocio: primero vendía
piezas sueltas, después lotes y hoy vende por gramo. Cada versión dejó su propio bloque
de columnas, puestos uno al lado del otro en la misma hoja, así que no hay una tabla que
leer sino diecisiete. Hasta los nombres de las columnas cambian: lo que pagó el comprador
se llama `Monto Bruto`, `Total Venta`, `Valor total` o `Ingreso` según el año.

`apps/analitica/historial.py` reconoce los bloques por sus encabezados y los normaliza.
`manage.py importar_historial` los deja en la base. El lector **no corrige ni completa
nada**: anota lo que no pudo leer en vez de adivinarlo.

| | |
|---|---|
| Ventas leídas | 2.957, entre el 31-01-2024 y el 27-10-2025 |
| Cargadas a la base | 2.795 |
| Descartadas | 93 sin fecha utilizable y 80 filas de plantilla en blanco |
| Fuera de alcance | 162 ventas por unidad o por lote de los primeros meses: esos productos ya no existen en el catálogo |
| Clientes distintos | 1.821, de los cuales 482 (26%) compraron más de una vez |

### A qué producto va cada venta

La planilla no nombra productos: anota gramos por **tramo de costo**. El mapeo sale de los
datos y no de una suposición. Aislando las ventas de un solo tramo, el precio por gramo
que de verdad se cobró fue:

| Tramo de costo | Precio bruto por gramo | Sin IVA | Producto del catálogo |
|---|---|---|---|
| 430, 440 | ~$741 | ~$650 | `granel-hombre` ($650) |
| 560, 580, 600, 650 | ~$1.000 | ~$890 | `granel-mujer` ($900) |
| 900, 1300 | ~$1.900 | ~$1.600 | `granel-colgantes-aros-anillos` ($1.500) |

El reparto de lo vendido: 48,8% por gramo de mujer, 36,6% de hombre y 14,5% de colgantes,
aros y anillos.

### Seudonimización

Cada cliente entra como «Cliente 0427». El número se asigna por orden de primera compra,
así que es estable: dos corridas sobre el mismo archivo dan los mismos seudónimos y los
resultados se pueden comparar entre corridas.

La correspondencia se escribe junto al archivo original, fuera del repositorio, y **nunca
entra a la base**. Para agrupar por recencia, frecuencia y monto da exactamente lo mismo
cómo se llame la persona.

### Desplazamiento de fechas

La planilla termina en octubre de 2025 y el proyecto corre un año después. El historial se
adelanta **un año entero** al importarlo, con `--desplazar-anos 1`.

En años y no en meses, a propósito: así cada venta conserva su mes del año y la
estacionalidad del negocio se queda donde estaba. Corrido en meses, el peak de diciembre
aparecería en enero y el modelo aprendería una temporada que nunca existió.

Cada pedido importado dice en sus notas que su fecha fue movida.

## Dos límites de estos datos

Los dos cambian lo que un modelo puede afirmar, así que van antes de cualquier resultado.

### La caída de ventas no está explicada

El volumen cae cuatro veces entre el peak y el final de la serie:

| | Ventas por mes | Monto por mes |
|---|---|---|
| Primera mitad (jun-2024 a ene-2025) | 212 | $9.637.531 |
| Segunda mitad (feb-2025 a oct-2025) | 140 | $6.447.636 |

**No se sabe si el negocio se contrajo o si se dejó de anotar.** Lo que dicen los datos:

- El **ticket promedio no se movió**: $45.514 contra $46.128. No fue que bajaran precios.
- Los **días con registro no se desploman**: entre 10 y 20 al mes de principio a fin. Si
  hubieran dejado de anotar, esperaríamos menos días.
- Lo que cae es la actividad por día registrado: de 36 ventas en diciembre de 2024 a 5 en
  octubre de 2025.
- Y los **clientes nuevos caen de 210 al mes a 22**.

En conjunto se inclina hacia una caída real de alcance, no hacia un problema de registro.
Pero el estilo de anotación cambió de diario a por tandas en el camino, así que no es
concluyente. **Hay que preguntárselo al cliente antes de modelar**: si la caída es real, el
modelo debe aprenderla; si es falta de registro, aprendería una tendencia inventada y
predeciría menos cada mes, para siempre, sin que nada se vea raro.

### Hay una sola Navidad

La serie útil son quince meses. Noviembre, diciembre, febrero, marzo y mayo aparecen **una
sola vez**.

Un modelo con componente estacional no se puede validar así: con una sola observación de
diciembre, el modelo no puede distinguir «diciembre vende más» de «ese diciembre vendió
más». Mientras no haya una segunda temporada, la estacionalidad se trata como supuesto
declarado y no como algo aprendido de los datos, y el contraste contra la línea base de
promedio móvil pasa a ser más importante que de costumbre.

## Registro de resultados

Cada vez que se evalúa un modelo, se anota acá: fecha, versión, métrica obtenida y el
valor de la línea base en el mismo conjunto de prueba. Sin el número de la línea base al
lado, el resultado no significa nada.

| Fecha | Modelo | Versión | Métrica | Resultado | Línea base | ¿Se integra? |
|---|---|---|---|---|---|---|
| | | | | | | |
