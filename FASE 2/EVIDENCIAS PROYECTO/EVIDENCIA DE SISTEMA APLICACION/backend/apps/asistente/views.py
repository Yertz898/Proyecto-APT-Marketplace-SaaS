"""
Vistas de la API de `asistente`.

La tienda sale del token. El asistente responde sobre un solo negocio —el de
quien pregunta— y eso no es una comprobación que se haga: es que no existe
forma de pedirle otro.
"""

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.asistente import intenciones
from apps.asistente.clasificador import LARGO_MAXIMO, clasificar
from apps.core.permissions import TrabajaEnLaTienda


class Preguntar(generics.GenericAPIView):
    """
    POST /api/panel/asistente  {"pregunta": "¿cómo van mis ventas?"}

    Clasifica la pregunta en una de las intenciones conocidas y responde con
    datos de la tienda del usuario. Ver `apps/asistente/intenciones.py` para
    por qué la respuesta la arma el backend y no un modelo de lenguaje.
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

        respuesta = intenciones.responder(request.user.tienda, clasificar(pregunta))
        return Response(
            {
                "intencion": respuesta.intencion,
                "texto": respuesta.texto,
                "seccion": respuesta.seccion,
            }
        )
