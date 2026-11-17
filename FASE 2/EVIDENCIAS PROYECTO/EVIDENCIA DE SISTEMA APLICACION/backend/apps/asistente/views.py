"""
Vistas de la API de `asistente`.

La tienda sale del token. El asistente responde sobre un solo negocio —el de
quien pregunta— y eso no es una comprobación que se haga: es que no existe
forma de pedirle otro.
"""

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.asistente import ficha, intenciones, modelo
from apps.asistente.clasificador import (
    LARGO_MAXIMO,
    POR_MODELO,
    clasificar_con_origen,
    normalizar,
)
from apps.core.permissions import TrabajaEnLaTienda


class Preguntar(generics.GenericAPIView):
    """
    POST /api/panel/asistente  {"pregunta": "¿cómo van mis ventas?"}

    Si la pregunta es una de las conocidas, la respuesta la arma el backend
    (`intenciones.py`). Si no, el modelo la redacta con la ficha de la tienda
    (`ficha.py`), que también arma el backend con el filtro de tienda.
    """

    permission_classes = [TrabajaEnLaTienda]

    def get(self, request):
        """Qué sabe contestar. Lo usa la pantalla para ofrecer las preguntas."""
        return Response(
            {
                "preguntas": [
                    {"intencion": clave, "texto": texto}
                    for clave, texto in intenciones.DESCRIPCION.items()
                ],
                "largoMaximo": LARGO_MAXIMO,
            }
        )

    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValidationError({"pregunta": "Escribe una pregunta."})

        tienda = request.user.tienda
        intencion, origen = clasificar_con_origen(pregunta)
        respuesta = intenciones.responder(tienda, intencion)

        # El modelo redacta con la ficha de la tienda (`ficha.py`) en dos casos:
        # - la pregunta no es ninguna de las conocidas («no entendí»);
        # - el modelo está configurado pero no alcanzó a clasificar, y la
        #   intención la eligieron las palabras clave. Esas aciertan con las
        #   preguntas conocidas, pero ante «¿cuánto vendí el 15 de diciembre?»
        #   contestan el mes en curso porque ven la palabra «vendí».
        # Si no hay modelo, o también falla al redactar, queda lo de arriba.
        clasifico_el_modelo = origen == POR_MODELO
        if modelo.disponible() and (
            respuesta.intencion == "no_entendi" or not clasifico_el_modelo
        ):
            texto = normalizar(pregunta)
            libre = modelo.responder_libre(texto, ficha.armar(tienda, pregunta=texto))
            if libre:
                respuesta = intenciones.Respuesta("consulta_libre", libre)
                origen = POR_MODELO
        return Response(
            {
                "intencion": respuesta.intencion,
                "texto": respuesta.texto,
                "seccion": respuesta.seccion,
                # Quién entendió la pregunta: «modelo» o «palabras clave». Las
                # cifras salen siempre de la base: en las preguntas conocidas
                # las redacta el backend, y en las libres el modelo las toma
                # de la ficha, que también arma el backend.
                "clasificadoPor": origen,
            }
        )
