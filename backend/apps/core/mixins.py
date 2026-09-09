"""
Mixins de vista que aplican el filtro por tienda de forma automática.

Las vistas del resto de las apps heredan de acá en vez de repetir el filtro a
mano. Una vista que arma su queryset por su cuenta se salta el invariante.
"""
