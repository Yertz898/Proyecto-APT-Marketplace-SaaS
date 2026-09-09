"""
Managers y querysets que acotan el acceso a la tienda del usuario autenticado.

Acá vive el filtro por tienda, una sola vez. Ningún modelo con `tienda_id` debe
exponer un manager que devuelva filas sin filtrar: `Model.objects.all()` sobre
una tabla multi-tienda es el error que este módulo existe para impedir.
"""
