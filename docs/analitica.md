# Analítica

Los dos modelos son problemas distintos y **no se miden con las mismas métricas**.
Esta tabla es la referencia; usar la métrica equivocada produce un número que parece
válido y no lo es.

| Modelo | Tipo de problema | Métricas | Línea base |
|---|---|---|---|
| Pronóstico de demanda mensual por producto | Regresión sobre serie de tiempo | MAPE, MAE, RMSE | Promedio móvil |
| Segmentación y riesgo de abandono de clientes | Clasificación sobre variables RFM | Precisión, exhaustividad, F1 | Regla por recencia |

Reglas que no se negocian:

- Nunca usar accuracy, F1 ni matriz de confusión para el pronóstico de demanda.
- Todo modelo se contrasta con su línea base. Si no la supera, no se integra.
- El motor de recomendación de descuentos **no es un tercer modelo**: son reglas de
  negocio que consumen las salidas de los dos anteriores. Sugiere; el vendedor aprueba.
  Nunca ejecuta campañas por su cuenta.

## Registro de resultados

Cada vez que se evalúa un modelo, se anota acá: fecha, versión, métrica obtenida y el
valor de la línea base en el mismo conjunto de prueba. Sin el número de la línea base al
lado, el resultado no significa nada.

| Fecha | Modelo | Versión | Métrica | Resultado | Línea base | ¿Se integra? |
|---|---|---|---|---|---|---|
| | | | | | | |
