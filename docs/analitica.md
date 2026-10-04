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

## Registro de resultados

Cada vez que se evalúa un modelo, se anota acá: fecha, versión, métrica obtenida y el
valor de la línea base en el mismo conjunto de prueba. Sin el número de la línea base al
lado, el resultado no significa nada.

| Fecha | Modelo | Versión | Métrica | Resultado | Línea base | ¿Se integra? |
|---|---|---|---|---|---|---|
| | | | | | | |
