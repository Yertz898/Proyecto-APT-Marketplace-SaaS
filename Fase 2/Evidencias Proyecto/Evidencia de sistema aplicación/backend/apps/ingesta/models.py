"""
Carga masiva del catálogo desde planillas.

Es por donde el dueño sube sus lotes, sus líneas de granel y sus fotos. No
carga historial de ventas: el cliente no lo tiene con ese detalle.

No es una operación excepcional, es rutina: el catálogo rota seguido, así que
esto se usa tanto como el panel.

Lo que entre mal validado queda en la vitrina de la tienda, así que la carga es
idempotente —la clave natural es (tienda, código)— y una fila mala no bota a
las demás: se acumulan los errores por número de fila y se devuelve un resumen.
Un lote que no viene en el archivo no se borra; solo se desactiva si el dueño
lo marca.
"""
