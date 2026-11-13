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

## Las líneas base

Están construidas y probadas **antes que los modelos**, a propósito. Una línea base que
aparece después del modelo se termina escribiendo para que el modelo la gane.

Las dos declaran su método en la respuesta de la API, y las pantallas lo muestran. Mientras
el dueño no pueda distinguir una medición de una estimación, no sabe cuánto confiar en el
número que está mirando.

### Pronóstico: promedio móvil de tres meses

`apps/analitica/pronostico.py`. Por producto, no por categoría: en Joyas_ye los tres
productos por gramo tienen quince meses de historia cada uno y los lotes no tienen ninguna,
así que agrupar por categoría daría el mismo «datos insuficientes» con otro nombre.

Tres meses: suficiente para que un mes raro no mande, corto para que un cambio de nivel se
note.

**El mes en curso no entra.** Va por la mitad, así que suma menos que un mes cerrado: si
entrara, la proyección bajaría cada vez que alguien abre la pantalla a principio de mes y
subiría sola hacia fin de mes.

**No se proyecta con menos de seis meses de ventas.** Un producto con tres meses no tiene
una serie de tiempo, tiene tres números, y repetir el último mes no es un pronóstico. La
respuesta dice cuántos meses lleva y la pantalla lo muestra. Hoy: 3 productos con
proyección y 87 sin ella.

### La regla de la alerta de quiebre

No es un modelo aparte. Es el stock dividido por el ritmo proyectado:

    días hasta el quiebre = stock ÷ (proyección mensual ÷ 30)

Con dos negativas:

- **Sin pronóstico no hay alerta.** Sin saber cuánto se vende no se puede decir cuándo se
  acaba, y un plazo inventado en una pantalla de inventario hace que el dueño compre
  mercadería con él.
- **Quien no lleva inventario no recibe alerta.** La tienda no registra cuánto le queda de
  su granel. Se muestra la proyección y nada más.

En la pantalla, treinta días o menos es lo que se destaca arriba: es el plazo en que el
cliente alcanza a reponer con su proveedor.

### Segmentación: regla por recencia

`apps/analitica/segmentos.py`. Se agrupa por recencia, frecuencia y monto, pero **la que
decide es la recencia**: cuánto gastó alguien el año pasado no dice si va a volver.

**El umbral sale de los datos de cada tienda.** Es el percentil 90 de los días que pasan
entre dos compras de un mismo cliente: si nueve de cada diez veces alguien vuelve antes de
ese plazo, quien lo pasó rompió su propio patrón. En Joyas_ye son 104 días. Una tienda sin
suficientes compras repetidas cae a un plazo por omisión de 90 días y la respuesta declara
que no se midió.

| Grupo | Regla |
|---|---|
| Habitual | Dos o más compras y volvió dentro del umbral |
| Nuevo | Una compra, dentro del umbral |
| En riesgo | Pasó el umbral y no el doble |
| Perdido | Pasó el doble del umbral |

«Perdido» empieza al doble y no al umbral porque entre uno y otro hay alguien a quien
todavía tiene sentido escribirle, y mezclarlo con quien se fue hace un año haría que el
dueño no le escriba a ninguno.

Sobre el historial del cliente: 88 habituales, 123 nuevos, 304 en riesgo y 1.201 perdidos.
Esa proporción es consistente con la caída de alcance descrita más arriba.

## El clasificador de la segmentación

`apps/analitica/clasificador.py`, y se corre con:

    docker compose exec api python manage.py entrenar_segmentacion joyas-ye

Imprime el informe y lo guarda en `data/modelos/`, que no se versiona. El modelo entrenado
se guarda **solo si le gana a la regla**.

### Qué pregunta responde

Para cada cliente que ya compró: **¿vuelve a comprar en los próximos 104 días?** Ciento
cuatro es el umbral de la tienda, el mismo plazo con que la regla decide quién se fue, así
que modelo y regla responden exactamente la misma pregunta y se pueden comparar.

### Por qué se mide sobre «vuelve» y no sobre «se va»

Dentro del plazo vuelve entre el 5% y el 13% de los clientes, según la fecha. Medido sobre
«se va», decir que todos se van da un F1 cercano a 0,95 y cualquier regla parece excelente.
Medido sobre «vuelve», ese atajo da cero. Es además la pregunta que le sirve al dueño: a
quién le conviene escribir.

La métrica que decide es **el F1 de la clase «vuelve»**, fijada antes de ver los resultados.
Precisión y exhaustividad se reportan al lado.

### Las variables

Siete, todas calculadas solo con las compras hasta la fecha de corte: recencia,
frecuencia, monto, ticket promedio, antigüedad, días entre compras y compras de los últimos
90 días. Ninguna dice quién es la persona.

### Cómo se evita mirar el futuro

Es lo que más fácil invalida un resultado, y por eso tiene sus propias pruebas.

- **Fechas de corte, una por mes.** Las variables salen de lo anterior al corte; la
  etiqueta, de los 104 días siguientes. Una compra posterior no mueve ninguna variable.
- **La prueba va después de todo.** Es el último corte cuya etiqueta ya se conoce entera
  (15-07-2026). Se entrena con los cortes cuya etiqueta termina antes de esa fecha.
- **El modelo y su umbral de probabilidad se eligen en validación** (el corte del
  29-03-2026), entrenando solo con lo anterior. La prueba se mira una sola vez.
- **La regla tampoco ve el futuro:** su umbral se recalcula en cada corte con lo que se
  sabía en esa fecha.
- **Nunca se mezclan filas al azar.** Con un negocio que cambia en el tiempo, mezclar al
  azar le enseña el futuro al modelo y el resultado no se repite al usarlo.

### Qué se comparó

| | Precisión | Exhaustividad | F1 |
|---|---|---|---|
| Regla por recencia (línea base) | 0,168 | 0,530 | **0,255** |
| Regresión logística | 0,140 | 0,783 | 0,238 |
| XGBoost (elegido en validación) | 0,156 | 0,663 | **0,253** |

Sobre 1.562 clientes en el corte de prueba, de los cuales volvieron 83. La diferencia de F1
entre XGBoost y la regla, remuestreando los clientes mil veces, va de −0,034 a +0,032 al
95%: **incluye el cero, así que no se puede decir que ninguno gane.**

**El modelo no se integra.** La pantalla sigue con la regla, que además es más fácil de
explicarle al dueño.

### Por qué no le gana

Lo que sigue se miró **después** de ver la prueba, así que explica el resultado pero no lo
cambia.

- **La tasa de retorno cae con el tiempo.** Es 9,6% en los cortes de entrenamiento y 5,3%
  en el de prueba: es la caída de alcance descrita más arriba. Un umbral de probabilidad
  elegido con la tasa de antes marca a demasiada gente después. Por eso los dos modelos
  tienen buena exhaustividad y mala precisión.
- **Ordenar mejor tampoco se sostiene.** Con el mismo número de contactos que marca la
  regla, en la prueba la regresión logística acierta con 56 clientes y la regla con 44.
  Pero en validación pasa al revés: la regla acierta con 54 y los modelos con 41 y 43. Una
  ventaja que cambia de lado según el período es ruido, no una mejora.
- **La recencia ya lleva casi toda la información.** Las variables que más pesan en
  XGBoost —compras de los últimos 90 días, frecuencia, recencia— son las que la regla ya
  mira. Con siete variables de comportamiento no hay mucho más que aprender.

### Qué haría falta para que gane

- **Más tiempo.** Con quince meses hay una sola temporada y la tasa de retorno no se ha
  estabilizado. Cada mes nuevo de ventas es un corte más para entrenar.
- **Variables que la regla no tiene**: qué productos compra, si compra por gramo o por lote,
  el canal por el que llegó. Hoy la planilla del cliente no las trae.
- **Recalibrar el umbral de probabilidad** con la tasa de retorno más reciente, y fijar esa
  regla **antes** de evaluarla en un corte que todavía no se haya mirado.

## El asistente

`apps/asistente/`. Responde preguntas del vendedor sobre su propia tienda.

### Qué puede contestar

| Pregunta | De dónde sale |
|---|---|
| Cómo van mis ventas este mes | Panel de ventas |
| Qué productos me dejaron más | Panel de ventas, últimos 90 días |
| Qué llevo sin vender | Panel de ventas |
| Qué pedidos tengo pendientes | Bandeja de pedidos |
| Cuánto voy a vender el próximo mes | Pronóstico |
| Qué se me va a acabar | Pronóstico, alerta de quiebre |
| Qué clientes dejaron de comprarme | Segmentos, grupo «en riesgo» |
| Cómo se reparten mis clientes | Segmentos |

Nada más. Cuando no entiende, lo dice y enumera esta lista. No conversa, no
recuerda la pregunta anterior y no opina.

### Por qué el modelo de lenguaje no ve los datos

Es la decisión que sostiene todo lo demás. El modelo —cuando se configure uno—
hace **una sola cosa**: mirar la pregunta y devolver a cuál de esas ocho
intenciones se parece. Una etiqueta de una lista cerrada, nada más. La
respuesta la arma el backend leyendo la base con el filtro de tienda de
siempre.

Lo que eso compra:

- **Una instrucción inyectada en la pregunta no tiene a qué acceder.** El peor
  caso es que la clasificación salga mal y el vendedor reciba la respuesta a
  otra pregunta sobre su propio negocio. No hay camino desde el texto que
  escribe una persona hasta la base de datos.
- **No puede inventar cifras.** Salen de las mismas funciones que pintan el
  panel, así que el asistente y las pantallas no se pueden contradecir.
- **Funciona sin clave de API.** Hoy la clasificación es por palabras clave:
  entiende menos variantes de la misma pregunta, pero entiende. El modelo es
  una mejora de la comprensión, no un requisito para que el asistente exista.

La frontera está en `clasificador._es_valida`: cualquier respuesta de un
clasificador externo que no sea una intención conocida se trata como «no
entendí». La pregunta además se recorta a 500 caracteres y se limpia de todo
lo que no sea letra, número o espacio **antes** de mirarla.

### Lo que se niega a responder

- Sin historial suficiente, el pronóstico dice que no puede proyectar y
  cuántos meses hacen falta.
- Sin pronóstico, no anuncia quiebres: sin saber a qué ritmo se vende, no se
  puede decir cuándo se acaba.
- Sin ventas en el mes, lo dice en vez de mostrar un cero, que se leería como
  un resultado y no como una ausencia de datos.

## Registro de resultados

Cada vez que se evalúa un modelo, se anota acá: fecha, versión, métrica obtenida y el
valor de la línea base en el mismo conjunto de prueba. Sin el número de la línea base al
lado, el resultado no significa nada.

| Fecha | Modelo | Versión | Métrica | Resultado | Línea base | ¿Se integra? |
|---|---|---|---|---|---|---|
| 12-11-2026 | Segmentación · XGBoost | 1 | F1 de «vuelve», corte 15-07-2026 | 0,253 | 0,255 | No: diferencia entre −0,034 y +0,032 |
| 12-11-2026 | Segmentación · regresión logística | 1 | F1 de «vuelve», corte 15-07-2026 | 0,238 | 0,255 | No |
