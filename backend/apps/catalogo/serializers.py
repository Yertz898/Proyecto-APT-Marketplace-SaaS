"""
Serializadores del catálogo público.

La forma de estas respuestas la fija el frontend, que ya está escrito: los
tipos `Lote` y `LineaGranel` de `frontend/src/lib/tipos.ts`. Por eso las claves
compuestas van en camelCase y por eso el backend entrega el IVA y el total ya
calculados: el navegador no hace aritmética de dinero.
"""

from rest_framework import serializers

from apps.catalogo.models import LineaGranel, Lote
from apps.precios.dinero import desglose
from apps.precios.models import UnidadUmbral


class ComposicionSerializer(serializers.Serializer):
    """Cuántas piezas de cada categoría. No es una lista de piezas concretas."""

    categoria = serializers.CharField(source="categoria.nombre", read_only=True)
    cantidad = serializers.IntegerField(read_only=True)


class LoteSerializer(serializers.ModelSerializer):
    tipo = serializers.ReadOnlyField(default="lote")
    piezasTotales = serializers.IntegerField(source="cantidad_piezas", read_only=True)
    composicion = ComposicionSerializer(many=True, read_only=True)

    precioNeto = serializers.IntegerField(source="precio_neto", read_only=True)
    iva = serializers.SerializerMethodField()
    precioTotal = serializers.SerializerMethodField()

    cupos = serializers.SerializerMethodField()
    agotado = serializers.ReadOnlyField()
    foto = serializers.SerializerMethodField()

    class Meta:
        model = Lote
        fields = [
            "tipo",
            "codigo",
            "nombre",
            "material",
            "piezasTotales",
            "composicion",
            "precioNeto",
            "iva",
            "precioTotal",
            "cupos",
            "agotado",
            "foto",
        ]

    def get_iva(self, lote) -> int:
        return desglose(lote.precio_neto)["iva"]

    def get_precioTotal(self, lote) -> int:  # noqa: N802 — lo fija el contrato
        return desglose(lote.precio_neto)["total"]

    def get_cupos(self, lote) -> dict:
        """
        Un lote de cupo único no dice cuántos quedan: o está o no está.

        Mostrar "queda 1" en algo que por definición es uno solo no aporta, y
        en los múltiples el número sí empuja a decidir.
        """
        if lote.tipo_cupo == "UNICO":
            return {"tipo": "UNICO"}
        return {"tipo": "MULTIPLE", "restantes": lote.cupos_disponibles}

    def get_foto(self, lote) -> dict | None:
        """
        Null mientras no haya foto: la interfaz no dibuja nada en su lugar.

        Un marcador gris se confunde con una foto que no cargó.
        """
        if not lote.foto:
            return None

        peticion = self.context.get("request")
        url = lote.foto.url
        return {
            "url": peticion.build_absolute_uri(url) if peticion else url,
            "alt": lote.nombre,
        }


class TramoSerializer(serializers.Serializer):
    umbral = serializers.SerializerMethodField()
    unidadUmbral = serializers.CharField(source="unidad_umbral", read_only=True)
    precioGramoNeto = serializers.IntegerField(source="valor", read_only=True)

    def get_umbral(self, tramo) -> float | int:
        """Entero cuando no tiene decimales, para que la vitrina no muestre «500,00»."""
        umbral = tramo.umbral
        return int(umbral) if umbral == umbral.to_integral_value() else float(umbral)


class LineaGranelSerializer(serializers.ModelSerializer):
    tipo = serializers.ReadOnlyField(default="granel")
    categorias = serializers.SerializerMethodField()
    tramos = serializers.SerializerMethodField()
    minimo = serializers.SerializerMethodField()

    class Meta:
        model = LineaGranel
        fields = [
            "tipo",
            "codigo",
            "nombre",
            "material",
            "categorias",
            "tramos",
            "minimo",
        ]

    def get_categorias(self, linea) -> list[str]:
        """El diccionario las guarda como texto separado por coma."""
        return [c.strip() for c in linea.categorias.split(",") if c.strip()]

    def get_tramos(self, linea) -> list[dict]:
        """
        Ordenados como los lee una persona: primero los de pesos, después los
        de gramos, y dentro de cada grupo de menor a mayor.
        """
        tramos = sorted(
            linea.tramos.all(),
            key=lambda t: (t.unidad_umbral != UnidadUmbral.PESOS, t.umbral),
        )
        return TramoSerializer(tramos, many=True).data

    def get_minimo(self, linea) -> str | None:
        """
        El mínimo de compra, redactado acá y no en el navegador.

        Sale del tramo en pesos más bajo: bajo ese monto de referencia la
        compra se rechaza.
        """
        en_pesos = [
            t for t in linea.tramos.all() if t.unidad_umbral == UnidadUmbral.PESOS
        ]
        if not en_pesos:
            return None

        minimo = min(int(t.umbral) for t in en_pesos)
        return f"Compra mínima de ${minimo:,.0f}".replace(",", ".")
