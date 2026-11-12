"""
Vistas de la API de `analitica`.

La tienda sale del token, nunca de la URL: lo que se devuelve acá es cuánto
vende un negocio, que es de lo más privado que guarda la plataforma.
"""

from rest_framework import generics
from rest_framework.response import Response

from apps.analitica import pronostico, segmentos, ventas
from apps.core.permissions import TrabajaEnLaTienda


class ResumenDeVentas(generics.GenericAPIView):
    """
    GET /api/panel/ventas

    Lo que la tienda vendió: el mes en curso contra el anterior, lo que falta
    coordinar, los productos que más dejaron y los que llevan tiempo quietos.

    Son hechos sumados de pedidos existentes. Lo estimado —pronóstico de
    demanda, segmentos— no se mezcla acá: en una misma pantalla nadie
    distinguiría qué está medido y qué está proyectado.
    """

    permission_classes = [TrabajaEnLaTienda]

    def get(self, request):
        return Response(ventas.resumen(request.user.tienda))


class PronosticoDeDemanda(generics.GenericAPIView):
    """
    GET /api/panel/pronostico

    Cuánto se espera vender de cada producto el próximo mes, y cuáles se van
    a quedar sin stock antes.

    Lo que hoy responde es **la línea base**, un promedio móvil de tres
    meses. Va declarado en cada fila, en `metodo`: la pantalla tiene que
    poder decirle al dueño con qué se calculó lo que está mirando.
    """

    permission_classes = [TrabajaEnLaTienda]

    def get(self, request):
        proyecciones = pronostico.proyectar(request.user.tienda)
        return Response(
            {
                "minimoDeMeses": pronostico.MINIMO_DE_MESES,
                "productos": [
                    {
                        "codigo": p.codigo,
                        "nombre": p.nombre,
                        "unidad": p.unidad,
                        "mesesConVentas": p.meses_con_ventas,
                        "suficiente": p.suficiente,
                        "esperado": float(p.esperado) if p.esperado else None,
                        "metodo": p.metodo if p.suficiente else None,
                        "stock": float(p.stock) if p.stock is not None else None,
                        "diasHastaQuiebre": p.dias_hasta_quiebre,
                        "serie": [
                            {"mes": mes, "cantidad": float(cantidad)}
                            for mes, cantidad in (p.serie or [])
                        ],
                    }
                    for p in proyecciones
                ],
            }
        )


class SegmentosDeCompradores(generics.GenericAPIView):
    """
    GET /api/panel/segmentos

    En qué grupo cae cada comprador: habitual, nuevo, en riesgo o perdido.

    Igual que el pronóstico, hoy responde la línea base —una regla por
    recencia— y lo declara en `metodo`. El umbral viene en la respuesta
    porque sale de los datos de cada tienda y el dueño tiene derecho a saber
    de dónde salió el número que decide quién está «perdido».
    """

    permission_classes = [TrabajaEnLaTienda]

    def get(self, request):
        resumen = segmentos.segmentar(request.user.tienda)
        return Response(
            {
                "metodo": resumen.metodo,
                "umbralDeDias": resumen.umbral,
                "umbralCalculado": resumen.umbral_calculado,
                "descripciones": segmentos.DESCRIPCION,
                "conteo": resumen.conteo,
                # Los que más gastaron **de cada grupo**, no los que más
                # gastaron en total. Ordenados por prioridad, los primeros
                # cincuenta salían todos «en riesgo» y el dueño no tenía forma
                # de mirar a sus habituales. Mandar los mil setecientos
                # tampoco: a una pantalla no le sirven.
                "clientes": [
                    {
                        "nombre": c.nombre,
                        "segmento": c.segmento,
                        "recencia": c.recencia,
                        "frecuencia": c.frecuencia,
                        "monto": c.monto,
                    }
                    for c in _mejores_de_cada_grupo(resumen.clientes)
                ],
            }
        )


#: Cuántos clientes se mandan por grupo.
#:
#: Doce: alcanzan para una pantalla de lista y para que el dueño reconozca a
#: quién escribirle. El resto no se mira.
POR_GRUPO = 12


def _mejores_de_cada_grupo(clientes):
    """Los que más gastaron dentro de cada grupo, conservando el orden general."""
    cuenta: dict[str, int] = {}
    elegidos = []
    for cliente in clientes:
        vistos = cuenta.get(cliente.segmento, 0)
        if vistos >= POR_GRUPO:
            continue
        cuenta[cliente.segmento] = vistos + 1
        elegidos.append(cliente)
    return elegidos
