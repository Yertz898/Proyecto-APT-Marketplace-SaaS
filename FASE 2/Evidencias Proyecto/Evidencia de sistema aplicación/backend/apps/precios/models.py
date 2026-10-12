"""
Precios por tramos, para lotes y para granel.

Es el módulo con más lógica de negocio del sistema, y el que más fácil se
calcula mal.

En el granel los umbrales en gramos (medio kilo, kilo) tienen prioridad. Si la
cantidad no alcanza ninguno, se arma un monto de referencia con el precio del
primer tramo y se aplica el tramo en pesos que ese monto alcance. Bajo $20.000
de referencia la compra se rechaza. Los umbrales son inclusivos.

Dos reglas que no son de estilo:

- Los precios se guardan netos. El IVA (19%) se calcula aparte y se muestra
  separado del neto y del total.
- El cálculo va con `Decimal` y `ROUND_HALF_UP`. El `round()` de Python
  redondea al par más cercano y deja el total un peso corto en casos como
  3.828,50.

Los tramos por cantidad de lotes todavía no los dijo el cliente: quedan
configurables por tienda, nunca escritos en el código.
"""
