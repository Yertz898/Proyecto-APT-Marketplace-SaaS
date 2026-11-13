"""
Mide los modelos del pronóstico contra el promedio móvil.

    docker compose exec api python manage.py entrenar_pronostico joyas-ye

Imprime el informe completo y lo guarda en `data/modelos/` como JSON, que no
se versiona: sale de las ventas de un cliente real.
"""

import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.analitica import modelos_pronostico, pronostico
from apps.catalogo.models import Producto
from apps.tiendas.models import Tienda

CARPETA = Path("/datos/modelos")


def _cifras(m: dict) -> str:
    return f"MAPE {m['mape']:5.1f}%   MAE {m['mae']:7.0f}   RMSE {m['rmse']:7.0f}"


class Command(BaseCommand):
    help = "Mide los modelos del pronóstico de demanda contra el promedio móvil."

    def add_arguments(self, parser):
        parser.add_argument("tienda", help="slug de la tienda")
        parser.add_argument("--carpeta", default=str(CARPETA))

    def handle(self, *args, **opciones):
        tienda = Tienda.objects.filter(slug=opciones["tienda"]).first()
        if tienda is None:
            raise CommandError(f"No existe la tienda «{opciones['tienda']}».")

        codigos = dict(
            Producto.objects.filter(tienda=tienda).values_list("pk", "codigo")
        )
        series = {
            codigos[pk]: [(mes, float(cantidad)) for mes, cantidad in serie]
            for pk, serie in pronostico._series_por_producto(
                tienda, date.today()
            ).items()
        }
        try:
            informe = modelos_pronostico.evaluar(series)
        except ValueError as error:
            raise CommandError(str(error)) from error

        escribir = self.stdout.write
        escribir(f"Tienda: {tienda.nombre}")
        escribir(
            f"Validación: {informe.puntos_de_validacion} pronósticos. "
            f"Prueba: {informe.puntos_de_prueba} pronósticos, "
            f"de {informe.meses_de_prueba[0]} a {informe.meses_de_prueba[-1]}."
        )
        escribir("")
        escribir(f"  Promedio móvil (línea base)  {_cifras(informe.linea_base)}")
        escribir(f"  Último mes (referencia)      {_cifras(informe.referencia)}")
        for nombre, r in informe.candidatos.items():
            marca = "  ← elegido en validación" if nombre == informe.elegido else ""
            escribir(f"  {nombre:<28} {_cifras(r['prueba'])}{marca}")
        bajo, alto = informe.intervalo
        escribir("")
        escribir(
            f"Diferencia de MAPE del elegido contra la línea base, al 95%: "
            f"entre {bajo:+.1f} y {alto:+.1f} puntos."
        )
        escribir(
            f"Le gana a la línea base con {informe.parametros}."
            if informe.gana
            else "No le gana a la línea base: el intervalo incluye el cero."
        )

        carpeta = Path(opciones["carpeta"])
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / f"pronostico-{tienda.slug}.json").write_text(
            json.dumps(
                {
                    "tienda": tienda.slug,
                    "meses_de_prueba": informe.meses_de_prueba,
                    "linea_base": informe.linea_base,
                    "referencia_ultimo_mes": informe.referencia,
                    "candidatos": informe.candidatos,
                    "elegido": informe.elegido,
                    "parametros": informe.parametros,
                    "intervalo_diferencia_mape": list(informe.intervalo),
                    "gana": informe.gana,
                    "detalle_prueba": informe.detalle,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
