"""
Entrena el clasificador de la segmentación y lo mide contra la regla.

    docker compose exec api python manage.py entrenar_segmentacion joyas-ye

Imprime el informe completo y lo guarda en `data/modelos/` como JSON. El
modelo entrenado se guarda **solo si le gana a la regla**: un modelo que no la
supera no tiene nada que hacer en el sistema, y guardarlo igual invita a que
alguien lo enchufe.

Lo que se guarda en `data/modelos/` no se versiona: sale de las compras de
clientes reales.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.analitica import clasificador, segmentos
from apps.tiendas.models import Tienda

#: Dónde quedan el informe y el modelo. `./data` está montado ahí en Docker.
CARPETA = Path("/datos/modelos")


def _cifras(m: dict) -> str:
    return (
        f"precisión {m['precision']:.3f} · exhaustividad {m['exhaustividad']:.3f} · "
        f"F1 {m['f1']:.3f}  ({m['verdaderos_positivos']} aciertos, "
        f"{m['falsos_positivos']} falsas alarmas, {m['falsos_negativos']} perdidos)"
    )


class Command(BaseCommand):
    help = "Entrena el clasificador de segmentación y lo compara con la regla."

    def add_arguments(self, parser):
        parser.add_argument("tienda", help="slug de la tienda")
        parser.add_argument(
            "--carpeta",
            default=str(CARPETA),
            help="dónde guardar el informe y el modelo",
        )

    def handle(self, *args, **opciones):
        tienda = Tienda.objects.filter(slug=opciones["tienda"]).first()
        if tienda is None:
            raise CommandError(f"No existe la tienda «{opciones['tienda']}».")

        compras = segmentos._compras_por_cliente(tienda)
        horizonte, calculado = segmentos.umbral_de_abandono(compras)
        try:
            informe = clasificador.evaluar(compras, horizonte)
        except ValueError as error:
            raise CommandError(str(error)) from error

        escribir = self.stdout.write
        escribir(f"Tienda: {tienda.nombre}")
        escribir(
            f"Pregunta: ¿vuelve a comprar en los próximos {horizonte} días?"
            + ("" if calculado else " (plazo por omisión)")
        )
        escribir(
            f"Entrenamiento: {len(informe.cortes_de_entrenamiento)} cortes, "
            f"{informe.filas_de_entrenamiento} filas. "
            f"Validación: {informe.corte_de_validacion:%d-%m-%Y}. "
            f"Prueba: {informe.corte_de_prueba:%d-%m-%Y}, "
            f"{informe.clientes_en_prueba} clientes, "
            f"{informe.vuelven_en_prueba} volvieron."
        )
        escribir("")
        escribir(f"  Regla por recencia   {_cifras(informe.regla)}")
        for nombre, r in informe.modelos.items():
            marca = " ← elegido en validación" if nombre == informe.elegido else ""
            escribir(f"  {nombre:<20} {_cifras(r['prueba'])}{marca}")
        bajo, alto = informe.intervalo
        escribir("")
        escribir(
            f"Diferencia de F1 del elegido contra la regla, al 95%: "
            f"entre {bajo:+.3f} y {alto:+.3f}."
        )

        carpeta = Path(opciones["carpeta"])
        carpeta.mkdir(parents=True, exist_ok=True)
        base = carpeta / f"segmentacion-{tienda.slug}"

        if informe.gana:
            import joblib

            modelo = clasificador.entrenar_final(compras, horizonte, informe.elegido)
            joblib.dump(
                {
                    "modelo": modelo,
                    "variables": clasificador.VARIABLES,
                    "umbral": informe.umbral_de_probabilidad,
                    "horizonte": horizonte,
                    "metodo": informe.elegido,
                },
                base.with_suffix(".joblib"),
            )
            veredicto = f"Le gana a la regla. Modelo guardado en {base}.joblib."
        else:
            veredicto = (
                "No le gana a la regla: el intervalo incluye el cero. "
                "No se guarda el modelo y la pantalla sigue con la regla."
            )
        escribir(veredicto)

        base.with_suffix(".json").write_text(
            json.dumps(
                {
                    "tienda": tienda.slug,
                    "horizonte": horizonte,
                    "corte_de_validacion": informe.corte_de_validacion.isoformat(),
                    "corte_de_prueba": informe.corte_de_prueba.isoformat(),
                    "cortes_de_entrenamiento": [
                        c.isoformat() for c in informe.cortes_de_entrenamiento
                    ],
                    "clientes_en_prueba": informe.clientes_en_prueba,
                    "vuelven_en_prueba": informe.vuelven_en_prueba,
                    "regla": informe.regla,
                    "modelos": informe.modelos,
                    "elegido": informe.elegido,
                    "intervalo_diferencia_f1": list(informe.intervalo),
                    "importancia": informe.importancia,
                    "gana": informe.gana,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
