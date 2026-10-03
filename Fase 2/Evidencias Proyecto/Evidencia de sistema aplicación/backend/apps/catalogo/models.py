"""
Catálogo: lotes y líneas de granel.

Son las dos formas de vender, y no se parecen entre sí:

- Un **lote** es una unidad cerrada que se compra entera. Lo que se cuenta no
  es stock de piezas sino cupos: cuántas veces más se puede vender ese lote.
  Un lote de cupo único se vende una sola vez.
- Una **línea de granel** se vende por gramo. No tiene stock, porque el cliente
  no registra gramos: lleva un interruptor de disponibilidad que el dueño
  enciende y apaga a mano.

Un lote no es una lista de piezas concretas: es una composición, cuántas piezas
de cada categoría, porque los modelos varían según lo que le llega al cliente.
La suma de esa composición tiene que cuadrar con la cantidad de piezas del
lote, y eso se valida al guardar.

Acá no hay productos ni variantes.
"""
