"""
Carga los catálogos de demostración.

El comando es genérico: no sabe de joyería. Lo que sabe está en `TIENDAS`, y
cada entrada es **la configuración de una tienda**, no el modelo del sistema.

Son dos, a propósito:

- **Joyas_ye**, el cliente piloto. Vende por lote y por peso. Sus tramos y sus
  precios **son los que entregó, tal cual**: no se corrigen, no se redondean y
  no se "ordenan". Si un tramo parece raro, es porque así lo cobra. Sus seis
  lotes, en cambio, son inventados: llevan código `DEMO-0x` y "(ejemplo)" en el
  nombre para que nadie los presente como su catálogo real.
- **Bazar Austral**, inventada entera. Vende por unidad y lleva inventario, que
  es el caso que Joyas_ye no cubre. Está para que se vea que la plataforma no
  está hecha a la medida de una tienda, y para poder comprobar a mano que una
  no ve los datos de la otra.

El comando es idempotente: correrlo dos veces no duplica nada, y no repone el
stock ya vendido.

    docker compose exec api python manage.py cargar_demo
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogo.models import (
    Categoria,
    ComposicionLote,
    FormaVenta,
    Producto,
    UnidadMedida,
)
from apps.precios.models import TramoPrecio, UnidadUmbral
from apps.tiendas.models import Plan, Tienda

# ── Joyas_ye · configuración del cliente piloto ─────────────────────────────
#
# Los tramos salen de la lista de precios que entregó el cliente. Los umbrales
# que él expresó en pesos son `monto`; los de medio kilo y kilo, `peso`. El
# `precio_neto` de cada producto por peso es el precio de su primer tramo, que
# es con lo que se arma el monto de referencia.

JOYAS_YE_GRANEL = [
    {
        "codigo": "granel-hombre",
        "nombre": "Gramo de hombre (cadenas y pulseras)",
        "descripcion": "Enchape de plata · cadenas y pulseras.",
        "precio_neto": 650,
        "tramos": [
            (UnidadUmbral.MONTO, 20000, 650),
            (UnidadUmbral.MONTO, 100000, 600),
            (UnidadUmbral.PESO, 500, 560),
            (UnidadUmbral.PESO, 1000, 500),
        ],
    },
    {
        "codigo": "granel-mujer",
        "nombre": "Gramo de mujer (cadenas, collares, pulseras y tobilleras)",
        "descripcion": "Enchape de plata · cadenas, collares, pulseras y tobilleras.",
        "precio_neto": 900,
        "tramos": [
            (UnidadUmbral.MONTO, 20000, 900),
            (UnidadUmbral.MONTO, 100000, 850),
            (UnidadUmbral.PESO, 500, 780),
            (UnidadUmbral.PESO, 1000, 700),
        ],
    },
    {
        "codigo": "granel-colgantes-aros-anillos",
        "nombre": "Gramo de colgantes, aros y anillos",
        "descripcion": "Enchape de plata · colgantes, aros y anillos.",
        "precio_neto": 1500,
        "tramos": [
            (UnidadUmbral.MONTO, 20000, 1500),
            (UnidadUmbral.MONTO, 100000, 1300),
            (UnidadUmbral.PESO, 500, 1200),
            (UnidadUmbral.PESO, 1000, 1050),
        ],
    },
    {
        "codigo": "granel-plata-colombiana",
        "nombre": "Gramo de plata colombiana",
        "descripcion": "Plata colombiana.",
        "precio_neto": 1800,
        "tramos": [(UnidadUmbral.MONTO, 20000, 1800)],
    },
    {
        "codigo": "granel-colgantes-hombre-xl",
        "nombre": "Gramo de colgantes de hombre XL",
        "descripcion": "Enchape de plata · colgantes.",
        "precio_neto": 1000,
        "tramos": [(UnidadUmbral.MONTO, 20000, 1000)],
    },
]

JOYAS_YE_LOTES = [
    {
        "codigo": "DEMO-01",
        "nombre": "Surtido de aros (ejemplo)",
        "descripcion": "Enchape de plata.",
        "precio_neto": 45990,
        "stock": 8,
        "composicion": {"aros": 12, "anillos": 6},
    },
    {
        "codigo": "DEMO-02",
        "nombre": "Mix de cadenas de hombre (ejemplo)",
        "descripcion": "Enchape de plata.",
        "precio_neto": 89990,
        "stock": 5,
        "composicion": {"cadenas": 10, "pulseras": 5},
    },
    {
        "codigo": "DEMO-03",
        "nombre": "Colección de colgantes (ejemplo)",
        "descripcion": "Enchape de plata.",
        "precio_neto": 62990,
        "stock": 6,
        "composicion": {"colgantes": 14, "cadenas": 4},
    },
    {
        "codigo": "DEMO-04",
        "nombre": "Pieza única de plata colombiana (ejemplo)",
        "descripcion": "Plata colombiana. Se vende una sola vez.",
        "precio_neto": 129990,
        "stock": 1,
        "composicion": {"collares": 1},
    },
    {
        "codigo": "DEMO-05",
        "nombre": "Set de tobilleras y pulseras (ejemplo)",
        "descripcion": "Enchape de plata.",
        "precio_neto": 38990,
        "stock": 10,
        "composicion": {"tobilleras": 8, "pulseras": 8},
    },
    {
        "codigo": "DEMO-06",
        "nombre": "Lote mixto de temporada (ejemplo)",
        "descripcion": "Enchape de plata. Se vende una sola vez.",
        "precio_neto": 74990,
        "stock": 1,
        "composicion": {"anillos": 5, "aros": 5, "collares": 3, "cadenas": 2},
    },
]

# ── Bazar Austral · tienda inventada, vende por unidad ──────────────────────

BAZAR_PRODUCTOS = [
    {
        "codigo": "BAZ-01",
        "nombre": "Taza de cerámica (ejemplo)",
        "descripcion": "Cerámica esmaltada, 350 ml.",
        "categoria": "cocina",
        "precio_neto": 4990,
        "stock": 120,
        "tramos": [
            (UnidadUmbral.CANTIDAD, 12, 4490),
            (UnidadUmbral.CANTIDAD, 48, 3990),
        ],
    },
    {
        "codigo": "BAZ-02",
        "nombre": "Set de velas aromáticas (ejemplo)",
        "descripcion": "Tres velas de cera de soya.",
        "categoria": "hogar",
        "precio_neto": 7990,
        "stock": 60,
        "tramos": [
            (UnidadUmbral.CANTIDAD, 6, 7290),
            (UnidadUmbral.CANTIDAD, 24, 6590),
        ],
    },
    {
        "codigo": "BAZ-03",
        "nombre": "Cuaderno de tapa dura (ejemplo)",
        "descripcion": "120 hojas, tamaño carta.",
        "categoria": "escritorio",
        "precio_neto": 5490,
        "stock": 200,
        "tramos": [(UnidadUmbral.CANTIDAD, 10, 4990)],
    },
    {
        "codigo": "BAZ-04",
        "nombre": "Organizador de escritorio (ejemplo)",
        "descripcion": "Madera de pino, cuatro compartimentos.",
        "categoria": "escritorio",
        "precio_neto": 12990,
        "stock": 18,
        "tramos": [],
    },
    {
        "codigo": "BAZ-05",
        "nombre": "Tabla de picar de madera (ejemplo)",
        "descripcion": "Lenga, 30 × 20 cm. Queda una.",
        "categoria": "cocina",
        "precio_neto": 15990,
        "stock": 1,
        "tramos": [],
    },
]

# ── Las dos tiendas ─────────────────────────────────────────────────────────

TIENDAS = [
    {
        "slug": "joyas-ye",
        "nombre": "Joyas Ye",
        "plan": Plan.ULTIMATE,
        "paleta": {
            "color_primario": "#7C3AED",
            "color_primario_hover": "#6D28D9",
            "color_acento": "#C8A96A",
            "color_destacado": "#E0A526",
        },
        "categorias": [
            "anillos",
            "aros",
            "cadenas",
            "collares",
            "colgantes",
            "pulseras",
            "tobilleras",
        ],
        "por_peso": JOYAS_YE_GRANEL,
        "por_lote": JOYAS_YE_LOTES,
        "por_unidad": [],
        "notas": [
            ("normal", "Los tramos por peso son los precios reales del cliente."),
            (
                "aviso",
                "Los seis lotes DEMO-01 a DEMO-06 son inventados: no son su "
                "catálogo real.",
            ),
            (
                "normal",
                "Los tramos por cantidad de lotes quedan vacíos: el cliente no "
                "los ha definido.",
            ),
        ],
    },
    {
        "slug": "bazar-austral",
        "nombre": "Bazar Austral",
        "plan": Plan.PREMIUM,
        "paleta": {
            "color_primario": "#0F766E",
            "color_primario_hover": "#115E59",
            "color_acento": "#4A5568",
            "color_destacado": "#D97706",
        },
        "categorias": ["cocina", "escritorio", "hogar"],
        "por_peso": [],
        "por_lote": [],
        "por_unidad": BAZAR_PRODUCTOS,
        "notas": [
            (
                "aviso",
                "Bazar Austral es inventada entera: vende por unidad y lleva "
                "inventario.",
            ),
        ],
    },
]


class Command(BaseCommand):
    help = "Carga los catálogos de demostración de las dos tiendas. Idempotente."

    def handle(self, *args, **opciones):
        self.silencioso = opciones.get("verbosity", 1) == 0

        for configuracion in TIENDAS:
            with transaction.atomic():
                tienda = self._tienda(configuracion)
                categorias = self._categorias(tienda, configuracion["categorias"])

                self._por_peso(tienda, configuracion["por_peso"])
                self._por_lote(tienda, configuracion["por_lote"], categorias)
                self._por_unidad(tienda, configuracion["por_unidad"], categorias)

            self._resumen(tienda, configuracion)

    # ── Tienda ──────────────────────────────────────────────────────────────

    def _tienda(self, configuracion) -> Tienda:
        """
        La tienda con su plan y su paleta.

        Se escriben siempre y no solo al crear: son lo que define la
        demostración, y una paleta a medias deja la vitrina con los colores de
        la plataforma.
        """
        tienda, nueva = Tienda.objects.get_or_create(
            slug=configuracion["slug"], defaults={"nombre": configuracion["nombre"]}
        )
        tienda.nombre = configuracion["nombre"]
        tienda.plan = configuracion["plan"]
        for campo, valor in configuracion["paleta"].items():
            setattr(tienda, campo, valor)
        tienda.save(
            update_fields=["nombre", "plan", *configuracion["paleta"]]
        )

        if nueva:
            self._decir(f"  tienda creada: {tienda}")
        return tienda

    def _categorias(self, tienda, nombres) -> dict[str, Categoria]:
        categorias = {}
        for nombre in nombres:
            categorias[nombre], _ = Categoria.objects.get_or_create(
                tienda=tienda, nombre=nombre
            )
        self._decir(f"  categorías: {len(categorias)}")
        return categorias

    # ── Productos, una función por forma de venta ───────────────────────────

    def _por_peso(self, tienda, lineas):
        """
        Venta por gramo. No controla stock: la tienda no registra lo que le
        queda, así que el producto se activa y se desactiva a mano.
        """
        for datos in lineas:
            producto, _ = Producto.objects.update_or_create(
                tienda=tienda,
                codigo=datos["codigo"],
                defaults={
                    "nombre": datos["nombre"],
                    "descripcion": datos["descripcion"],
                    "precio_neto": datos["precio_neto"],
                    "forma_venta": FormaVenta.PESO,
                    "unidad_medida": UnidadMedida.GRAMO,
                    "controla_stock": False,
                    "stock": None,
                    "activo": True,
                },
            )
            self._tramos(tienda, producto, datos["tramos"])

        if lineas:
            self._decir(f"  productos por peso: {len(lineas)}")

    def _por_lote(self, tienda, lotes, categorias):
        for datos in lotes:
            producto = self._producto_con_stock(
                tienda,
                datos,
                forma=FormaVenta.LOTE,
                categoria=None,
                piezas=sum(datos["composicion"].values()),
            )
            for nombre, cantidad in datos["composicion"].items():
                ComposicionLote.objects.update_or_create(
                    tienda=tienda,
                    producto=producto,
                    categoria=categorias[nombre],
                    defaults={"cantidad": cantidad},
                )
            self._tramos(tienda, producto, datos.get("tramos", []))

        if lotes:
            self._decir(f"  productos por lote: {len(lotes)}")

    def _por_unidad(self, tienda, productos, categorias):
        for datos in productos:
            producto = self._producto_con_stock(
                tienda,
                datos,
                forma=FormaVenta.UNIDAD,
                categoria=categorias.get(datos.get("categoria")),
                piezas=None,
            )
            self._tramos(tienda, producto, datos.get("tramos", []))

        if productos:
            self._decir(f"  productos por unidad: {len(productos)}")

    def _producto_con_stock(self, tienda, datos, forma, categoria, piezas) -> Producto:
        """
        Un producto que lleva inventario.

        El stock se fija **solo al crear**: si el producto ya existía, volver a
        llenarlo borraría las ventas registradas y la demostración mentiría.
        """
        campos = {
            "nombre": datos["nombre"],
            "descripcion": datos["descripcion"],
            "categoria": categoria,
            "precio_neto": datos["precio_neto"],
            "forma_venta": forma,
            "unidad_medida": UnidadMedida.UNIDAD,
            "controla_stock": True,
            "cantidad_piezas": piezas,
            "activo": True,
        }

        existente = Producto.objects.filter(
            tienda=tienda, codigo=datos["codigo"]
        ).first()

        if existente is None:
            # El stock va en el INSERT: la base no acepta un producto que dice
            # controlar inventario sin saber cuánto tiene.
            return Producto.objects.create(
                tienda=tienda,
                codigo=datos["codigo"],
                stock=Decimal(datos["stock"]),
                **campos,
            )

        for campo, valor in campos.items():
            setattr(existente, campo, valor)
        existente.save(update_fields=list(campos))
        return existente

    def _tramos(self, tienda, producto, tramos):
        for unidad, umbral, precio in tramos:
            TramoPrecio.objects.update_or_create(
                tienda=tienda,
                producto=producto,
                unidad_umbral=unidad,
                umbral=Decimal(umbral),
                defaults={"valor": precio},
            )

    # ── Salida ──────────────────────────────────────────────────────────────

    def _decir(self, texto):
        if not self.silencioso:
            self.stdout.write(texto)

    def _resumen(self, tienda, configuracion):
        if self.silencioso:
            return

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Catálogo de demostración cargado en «{tienda}».")
        )
        for estilo, texto in configuracion["notas"]:
            if estilo == "aviso":
                self.stdout.write(self.style.WARNING(texto))
            else:
                self.stdout.write(texto)
        self.stdout.write("")
