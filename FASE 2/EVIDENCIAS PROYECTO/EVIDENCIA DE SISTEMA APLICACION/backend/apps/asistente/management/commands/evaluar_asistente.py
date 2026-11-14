"""
Mide cuántas preguntas entiende el asistente, por palabras clave y con Gemini.

    docker compose exec api python manage.py evaluar_asistente

Usa `apps/asistente/preguntas_de_prueba.json`, escrito antes de conectar el
modelo. Sin `GEMINI_API_KEY` mide solo las palabras clave.

Con el modelo, cada pregunta es una llamada al plan gratuito de Gemini: se
espera un momento entre una y otra para no topar el límite por minuto.
"""

import json
import time
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.asistente import clasificador, modelo

PREGUNTAS = Path(__file__).resolve().parents[2] / "preguntas_de_prueba.json"


def cargar_preguntas(ruta=PREGUNTAS) -> list[dict]:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))["preguntas"]


def medir(preguntas, clasificar) -> dict:
    """Aciertos de una forma de clasificar sobre el set, con los errores."""
    errores = []
    for p in preguntas:
        obtenida = clasificar(p["pregunta"])
        if obtenida != p["intencion"]:
            errores.append({**p, "obtenida": obtenida})
    total = len(preguntas)
    return {
        "aciertos": total - len(errores),
        "total": total,
        "porcentaje": 100 * (total - len(errores)) / total if total else 0.0,
        "errores": errores,
    }


class Command(BaseCommand):
    help = "Mide cuántas preguntas entiende el asistente, con y sin modelo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pausa",
            type=float,
            default=4.5,
            help="segundos entre llamadas al modelo, por el límite del plan gratuito",
        )

    def handle(self, *args, **opciones):
        preguntas = cargar_preguntas()
        escribir = self.stdout.write

        palabras = medir(preguntas, clasificador.por_palabras_clave)
        escribir(f"Set: {len(preguntas)} preguntas.\n")
        escribir(
            f"  Palabras clave  {palabras['aciertos']}/{palabras['total']}  "
            f"({palabras['porcentaje']:.0f}%)"
        )

        if not modelo.disponible():
            escribir("\nSin GEMINI_API_KEY: no se mide el modelo.")
            self._errores("palabras clave", palabras)
            return

        sin_respuesta = 0

        def con_modelo(pregunta):
            nonlocal sin_respuesta
            time.sleep(opciones["pausa"])
            etiqueta, origen = clasificador.clasificar_con_origen(pregunta)
            if origen != clasificador.POR_MODELO:
                sin_respuesta += 1
            return etiqueta

        gemini = medir(preguntas, con_modelo)
        escribir(
            f"  Con Gemini      {gemini['aciertos']}/{gemini['total']}  "
            f"({gemini['porcentaje']:.0f}%)"
        )
        if sin_respuesta:
            escribir(
                f"\n{sin_respuesta} preguntas no las contestó el modelo y se "
                "clasificaron por palabras clave."
            )
        self._errores("palabras clave", palabras)
        self._errores("Gemini", gemini)

    def _errores(self, nombre, resultado):
        if not resultado["errores"]:
            return
        self.stdout.write(f"\nLo que no entendió {nombre}:")
        for e in resultado["errores"]:
            self.stdout.write(
                f"  «{e['pregunta']}»  esperaba {e['intencion']}, dio {e['obtenida']}"
            )
