"""
Carga el catálogo de demostración de Joyas_ye.

Dos cosas distintas conviven acá y conviene no confundirlas:

- Las **líneas de granel y sus tramos son los precios reales que entregó el
  cliente**, tal cual los dio. No se corrigen, no se redondean y no se
  "ordenan": si un tramo parece raro, es porque así lo cobra.
- Los **seis lotes son inventados**. Llevan código `DEMO-01` a `DEMO-06` y
  "(ejemplo)" en el nombre para que nadie los presente como catálogo real del
  cliente.

El comando es idempotente: correrlo dos veces no duplica nada.

    docker compose exec api python manage.py cargar_demo
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogo.models import Categoria, ComposicionLote, LineaGranel, Lote, TipoCupo
from apps.precios.models import TramoPrecio, UnidadUmbral
from apps.tiendas.models import Plan, Tienda

SLUG = "joyas-ye"
NOMBRE_TIENDA = "Joyas Ye"

CATEGORIAS = [
    "anillos",
    "aros",
    "cadenas",
    "collares",
    "colgantes",
    "pulseras",
    "tobilleras",
]

#: Precios del cliente, tal como los entregó. (unidad, umbral, precio por gramo)
#:
#: Los umbrales en pesos van como `pesos` y los de medio kilo y kilo como
#: `gramos`, que es como él los expresó.
LINEAS_DE_GRANEL = [
    {
        "codigo": "granel-hombre",
        "nombre": "Gramo de hombre (cadenas y pulseras)",
        "material": "Enchape de plata",
        "categorias": ["cadenas", "pulseras"],
        "tramos": [
            (UnidadUmbral.PESOS, 20000, 650),
            (UnidadUmbral.PESOS, 100000, 600),
            (UnidadUmbral.GRAMOS, 500, 560),
            (UnidadUmbral.GRAMOS, 1000, 500),
        ],
    },
    {
        "codigo": "granel-mujer",
        "nombre": "Gramo de mujer (cadenas, collares, pulseras y tobilleras)",
        "material": "Enchape de plata",
        "categorias": ["cadenas", "collares", "pulseras", "tobilleras"],
        "tramos": [
            (UnidadUmbral.PESOS, 20000, 900),
            (UnidadUmbral.PESOS, 100000, 850),
            (UnidadUmbral.GRAMOS, 500, 780),
            (UnidadUmbral.GRAMOS, 1000, 700),
        ],
    },
    {
        "codigo": "granel-colgantes-aros-anillos",
        "nombre": "Gramo de colgantes, aros y anillos",
        "material": "Enchape de plata",
        "categorias": ["colgantes", "aros", "anillos"],
        "tramos": [
            (UnidadUmbral.PESOS, 20000, 1500),
            (UnidadUmbral.PESOS, 100000, 1300),
            (UnidadUmbral.GRAMOS, 500, 1200),
            (UnidadUmbral.GRAMOS, 1000, 1050),
        ],
    },
    {
        "codigo": "granel-plata-colombiana",
        "nombre": "Gramo de plata colombiana",
        "material": "Plata colombiana",
        "categorias": [],
        "tramos": [(UnidadUmbral.PESOS, 20000, 1800)],
    },
    {
        "codigo": "granel-colgantes-hombre-xl",
        "nombre": "Gramo de colgantes de hombre XL",
        "material": "Enchape de plata",
        "categorias": ["colgantes"],
        "tramos": [(UnidadUmbral.PESOS, 20000, 1000)],
    },
]

#: Lotes inventados. El nombre dice "(ejemplo)" en todos.
LOTES = [
    {
        "codigo": "DEMO-01",
        "nombre": "Surtido de aros (ejemplo)",
        "material": "Enchape de plata",
        "precio_neto": 45990,
        "tipo_cupo": TipoCupo.MULTIPLE,
        "cupos_totales": 8,
        "composicion": {"aros": 12, "anillos": 6},
    },
    {
        "codigo": "DEMO-02",
        "nombre": "Mix de cadenas de hombre (ejemplo)",
        "material": "Enchape de plata",
        "precio_neto": 89990,
        "tipo_cupo": TipoCupo.MULTIPLE,
        "cupos_totales": 5,
        "composicion": {"cadenas": 10, "pulseras": 5},
    },
    {
        "codigo": "DEMO-03",
        "nombre": "Colección de colgantes (ejemplo)",
        "material": "Enchape de plata",
        "precio_neto": 62990,
        "tipo_cupo": TipoCupo.MULTIPLE,
        "cupos_totales": 6,
        "composicion": {"colgantes": 14, "cadenas": 4},
    },
    {
        "codigo": "DEMO-04",
        "nombre": "Pieza única de plata colombiana (ejemplo)",
        "material": "Plata colombiana",
        "precio_neto": 129990,
        "tipo_cupo": TipoCupo.UNICO,
        "cupos_totales": 1,
        "composicion": {"collares": 1},
    },
    {
        "codigo": "DEMO-05",
        "nombre": "Set de tobilleras y pulseras (ejemplo)",
        "material": "Enchape de plata",
        "precio_neto": 38990,
        "tipo_cupo": TipoCupo.MULTIPLE,
        "cupos_totales": 10,
        "composicion": {"tobilleras": 8, "pulseras": 8},
    },
    {
        "codigo": "DEMO-06",
        "nombre": "Lote mixto de temporada (ejemplo)",
        "material": "Enchape de plata",
        "precio_neto": 74990,
        "tipo_cupo": TipoCupo.UNICO,
        "cupos_totales": 1,
        "composicion": {"anillos": 5, "aros": 5, "collares": 3, "cadenas": 2},
    },
]


#: La paleta de Joyas_ye, la misma que ya usa su vitrina.
PALETA = {
    "color_primario": "#7C3AED",
    "color_primario_hover": "#6D28D9",
    "color_acento": "#C8A96A",
    "color_destacado": "#E0A526",
}


class Command(BaseCommand):
    help = "Carga el catálogo de demostración de Joyas_ye. Idempotente."

    def handle(self, *args, **opciones):
        self.silencioso = opciones.get("verbosity", 1) == 0

        with transaction.atomic():
            tienda, nueva = Tienda.objects.get_or_create(
                slug=SLUG, defaults={"nombre": NOMBRE_TIENDA, "plan": Plan.ULTIMATE}
            )
            # Joyas_ye queda en Ultimate para poder mostrar el panel entero, y
            # con su paleta puesta para que la vitrina no caiga en los colores
            # de la plataforma. Se escribe siempre: es lo que define la demo.
            self._marca(tienda)
            if nueva:
                self._decir(f"  tienda creada: {tienda}")

            categorias = self._categorias(tienda)
            self._granel(tienda)
            self._lotes(tienda, categorias)

        self._resumen(tienda)

    def _marca(self, tienda):
        """Plan y paleta de la tienda de demostración."""
        tienda.plan = Plan.ULTIMATE
        for campo, valor in PALETA.items():
            setattr(tienda, campo, valor)
        tienda.save(update_fields=["plan", *PALETA])

    def _decir(self, texto):
        if not self.silencioso:
            self.stdout.write(texto)

    def _categorias(self, tienda) -> dict[str, Categoria]:
        categorias = {}
        for nombre in CATEGORIAS:
            categorias[nombre], _ = Categoria.objects.get_or_create(
                tienda=tienda, nombre=nombre
            )
        self._decir(f"  categorías: {len(categorias)}")
        return categorias

    def _granel(self, tienda):
        for datos in LINEAS_DE_GRANEL:
            linea, _ = LineaGranel.objects.update_or_create(
                tienda=tienda,
                codigo=datos["codigo"],
                defaults={
                    "nombre": datos["nombre"],
                    "material": datos["material"],
                    "categorias": ", ".join(datos["categorias"]),
                    "disponible": True,
                },
            )
            for unidad, umbral, precio in datos["tramos"]:
                TramoPrecio.objects.update_or_create(
                    tienda=tienda,
                    linea_granel=linea,
                    unidad_umbral=unidad,
                    umbral=Decimal(umbral),
                    defaults={"valor": precio},
                )

        self._decir(f"  líneas de granel: {len(LINEAS_DE_GRANEL)}")

    def _lotes(self, tienda, categorias):
        for datos in LOTES:
            piezas = sum(datos["composicion"].values())

            lote, creado = Lote.objects.update_or_create(
                tienda=tienda,
                codigo=datos["codigo"],
                defaults={
                    "nombre": datos["nombre"],
                    "material": datos["material"],
                    "cantidad_piezas": piezas,
                    "precio_neto": datos["precio_neto"],
                    "tipo_cupo": datos["tipo_cupo"],
                    "cupos_totales": datos["cupos_totales"],
                    "activo": True,
                },
            )
            # Los cupos disponibles solo se fijan al crear: si el lote ya
            # existía, volver a llenarlos borraría las ventas registradas.
            if creado:
                lote.cupos_disponibles = datos["cupos_totales"]
                lote.save(update_fields=["cupos_disponibles"])

            for nombre, cantidad in datos["composicion"].items():
                ComposicionLote.objects.update_or_create(
                    tienda=tienda,
                    lote=lote,
                    categoria=categorias[nombre],
                    defaults={"cantidad": cantidad},
                )

        self._decir(f"  lotes de ejemplo: {len(LOTES)}")

    def _resumen(self, tienda):
        if self.silencioso:
            return

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Catálogo de demostración cargado en «{tienda}».")
        )
        self.stdout.write(
            "Los tramos de granel son los precios reales que entregó el cliente."
        )
        self.stdout.write(
            self.style.WARNING(
                "Los seis lotes DEMO-01 a DEMO-06 son inventados: no son su "
                "catálogo real."
            )
        )
        self.stdout.write(
            "Los tramos por cantidad de lotes quedan vacíos: el cliente no los "
            "ha definido."
        )
