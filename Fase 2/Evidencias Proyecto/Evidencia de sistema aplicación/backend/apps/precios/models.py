"""
Listas de precios escalonados: tramos por volumen de compra.

Un mismo producto tiene precio distinto según la cantidad. Esto es lo que
resuelve la venta al detalle y al por mayor con un solo catálogo, y es el
módulo con más lógica de negocio del sistema: los tramos no se pueden
solapar y siempre debe haber uno que aplique a cualquier cantidad válida.
"""
