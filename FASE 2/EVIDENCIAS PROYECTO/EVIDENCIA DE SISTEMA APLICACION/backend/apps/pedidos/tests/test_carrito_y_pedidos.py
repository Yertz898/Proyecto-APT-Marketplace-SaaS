"""
El carrito y los pedidos.

Lo que más se prueba acá es que **el carrito no invente precios**. La cuenta
vive en `precios.servicios` y el carrito la consulta; cuando no lo hacía, la
ficha del producto mostraba el precio por tramo y el carrito cobraba el
precio base, con 30% de diferencia en el cliente piloto y sin que ninguna
prueba se enterara.

Lo segundo es el aislamiento entre tiendas, en los dos sentidos: que una
tienda no pueda pedir lo ajeno y que no pueda ver ni tocar los pedidos de
otra.
"""

from decimal import Decimal

import pytest

from apps.catalogo.models import Producto
from apps.pedidos.models import Pedido
from apps.precios.models import TramoPrecio, UnidadUmbral

pytestmark = pytest.mark.django_db

# Los pedidos de estas pruebas se hacen sin cuenta, así que llevan lo que se le
# pide a un visitante: RUT y correo además del nombre y el teléfono.
CONTACTO = {
    "nombre_contacto": "Yerko Pérez",
    "telefono_contacto": "+56 9 1234 5678",
    "rut_contacto": "11.111.111-1",
    "email_contacto": "yerko@example.com",
}


def como(client, usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


def cotizar_carrito(client, slug, lineas):
    return client.post(
        f"/api/t/{slug}/carrito/cotizar",
        {"lineas": lineas},
        content_type="application/json",
    )


def confirmar(client, slug, lineas, **contacto):
    cuerpo = {**CONTACTO, **contacto, "lineas": lineas}
    return client.post(
        f"/api/t/{slug}/pedidos", cuerpo, content_type="application/json"
    )


def cambiar_estado(client, pk, estado):
    return client.patch(
        f"/api/panel/pedidos/{pk}/estado/",
        {"estado": estado},
        content_type="application/json",
    )


# ── Cotizar usa el motor de precios ─────────────────────────────────────────


def test_el_carrito_aplica_el_tramo_por_peso(client, tienda_a, crear_granel):
    """
    La prueba que faltaba.

    El carrito calculaba por su cuenta y cobraba el precio base: mil gramos a
    $650 en vez de a $500, treinta por ciento de más, mientras la ficha del
    producto mostraba el precio correcto.
    """
    producto = crear_granel(tienda_a)
    TramoPrecio.objects.create(
        tienda=tienda_a,
        producto=producto,
        unidad_umbral=UnidadUmbral.PESO,
        umbral=1000,
        valor=500,
    )

    cuerpo = cotizar_carrito(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1000}]
    ).json()

    assert cuerpo["neto"] == 500_000
    assert cuerpo["rechazo"] is None


def test_el_carrito_avisa_cuando_llevar_mas_sale_mas_barato(
    client, tienda_a, crear_granel
):
    """El aviso tiene que llegar al carrito, no solo a la ficha del producto."""
    producto = crear_granel(tienda_a)
    TramoPrecio.objects.create(
        tienda=tienda_a,
        producto=producto,
        unidad_umbral=UnidadUmbral.PESO,
        umbral=1000,
        valor=500,
    )

    cuerpo = cotizar_carrito(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 900}]
    ).json()

    assert cuerpo["avisoTramo"] is not None
    assert "1000" in cuerpo["avisoTramo"]


def test_el_iva_del_carrito_es_el_de_la_plataforma(client, tienda_a, crear_producto):
    """19% sobre el neto, redondeado medio hacia arriba, como en dinero.py."""
    producto = crear_producto(tienda_a, precio_neto=15966)

    cuerpo = cotizar_carrito(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1}]
    ).json()

    assert cuerpo["neto"] == 15966
    assert cuerpo["iva"] == 3034
    assert cuerpo["total"] == 19000


def test_cotizar_rechaza_bajo_la_compra_minima(client, tienda_a, crear_granel):
    producto = crear_granel(tienda_a)

    cuerpo = cotizar_carrito(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1}]
    ).json()

    assert cuerpo["rechazo"] is not None
    assert cuerpo["lineas"][0]["rechazo"] is not None
    assert cuerpo["neto"] == 0


def test_una_linea_mala_no_bota_a_las_demas(client, tienda_a, crear_producto):
    bueno = crear_producto(tienda_a, codigo="A-1", precio_neto=1000)

    cuerpo = cotizar_carrito(
        client,
        tienda_a.slug,
        [
            {"codigo": bueno.codigo, "cantidad": 2},
            {"codigo": "NO-EXISTE", "cantidad": 1},
        ],
    ).json()

    assert cuerpo["lineas"][0]["rechazo"] is None
    assert cuerpo["lineas"][1]["rechazo"] is not None
    assert cuerpo["neto"] == 2000


def test_cotizar_no_escribe_nada(client, tienda_a, crear_producto):
    producto = crear_producto(tienda_a, stock=Decimal("25"))

    cotizar_carrito(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 5}])

    producto.refresh_from_db()
    assert producto.stock == Decimal("25")
    assert not Pedido.objects.exists()


def test_una_cantidad_que_no_es_numero_se_rechaza(client, tienda_a, crear_producto):
    """Lo manda un navegador y puede venir cualquier cosa; no puede ser un 500."""
    producto = crear_producto(tienda_a)

    respuesta = cotizar_carrito(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": "muchos"}]
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["lineas"][0]["rechazo"] is not None


def test_el_carrito_no_cotiza_lo_desactivado(client, tienda_a, crear_producto):
    """Lo que no está en la vitrina no se puede pedir por su código."""
    producto = crear_producto(tienda_a, activo=False)

    cuerpo = cotizar_carrito(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1}]
    ).json()

    assert cuerpo["lineas"][0]["rechazo"] is not None
    assert cuerpo["neto"] == 0


# ── Aislamiento: no se puede pedir lo de otra tienda ────────────────────────


def test_no_se_puede_pedir_un_producto_de_otra_tienda(
    client, tienda_a, tienda_b, crear_producto
):
    ajeno = crear_producto(tienda_b, codigo="B-100")

    cuerpo = cotizar_carrito(
        client, tienda_a.slug, [{"codigo": ajeno.codigo, "cantidad": 1}]
    ).json()

    assert cuerpo["lineas"][0]["rechazo"] is not None
    assert cuerpo["neto"] == 0


def test_confirmar_con_un_producto_ajeno_no_crea_el_pedido(
    client, tienda_a, tienda_b, crear_producto
):
    ajeno = crear_producto(tienda_b, codigo="B-100")

    respuesta = confirmar(
        client, tienda_a.slug, [{"codigo": ajeno.codigo, "cantidad": 1}]
    )

    assert respuesta.status_code == 400
    assert not Pedido.objects.exists()


# ── Confirmar ───────────────────────────────────────────────────────────────


def test_confirmar_guarda_los_datos_de_contacto_del_formulario(
    client, tienda_a, crear_producto
):
    """
    Antes salían del usuario autenticado, así que un invitado quedaba como
    «Cliente Vitrina / Por coordinar» y no había cómo avisarle nada.
    """
    producto = crear_producto(tienda_a)

    respuesta = confirmar(
        client,
        tienda_a.slug,
        [{"codigo": producto.codigo, "cantidad": 1}],
        nombre_contacto="Ana Soto",
        telefono_contacto="+56912345678",
        direccion_entrega="Calle Falsa 123",
    )

    assert respuesta.status_code == 201
    pedido = Pedido.objects.get()
    assert pedido.nombre_contacto == "Ana Soto"
    assert pedido.telefono_contacto == "+56912345678"
    assert pedido.direccion_entrega == "Calle Falsa 123"
    assert pedido.comprador is None


def test_confirmar_sin_telefono_no_crea_el_pedido(client, tienda_a, crear_producto):
    producto = crear_producto(tienda_a)

    respuesta = client.post(
        f"/api/t/{tienda_a.slug}/pedidos",
        {
            "nombre_contacto": "Ana Soto",
            "lineas": [{"codigo": producto.codigo, "cantidad": 1}],
        },
        content_type="application/json",
    )

    assert respuesta.status_code == 400
    assert not Pedido.objects.exists()


def test_confirmar_descuenta_el_stock(client, tienda_a, crear_producto):
    producto = crear_producto(tienda_a, stock=Decimal("10"))

    confirmar(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 3}])

    producto.refresh_from_db()
    assert producto.stock == Decimal("7")


def test_confirmar_no_descuenta_a_quien_no_lleva_inventario(
    client, tienda_a, crear_granel
):
    """La tienda no sabe cuánto le queda del granel: no hay nada que descontar."""
    producto = crear_granel(tienda_a)

    respuesta = confirmar(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 100}]
    )

    producto.refresh_from_db()
    assert respuesta.status_code == 201
    assert producto.stock is None


def test_confirmar_guarda_el_precio_del_momento(client, tienda_a, crear_producto):
    """
    Lo cobrado no cambia aunque después cambie el catálogo.

    Si la línea apuntara al precio vigente del producto, subir los precios
    reescribiría los pedidos de la semana pasada.
    """
    producto = crear_producto(tienda_a, precio_neto=1000)
    confirmar(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 2}])

    producto.precio_neto = 5000
    producto.save(update_fields=["precio_neto"])

    linea = Pedido.objects.get().lineas.get()
    assert linea.precio_unitario_neto == 1000
    assert linea.subtotal_neto == 2000


def test_confirmar_sin_stock_suficiente_no_deja_nada_a_medias(
    client, tienda_a, crear_producto
):
    """La transacción es entera: o entra el pedido completo o no entra nada."""
    hay = crear_producto(tienda_a, codigo="A-1", stock=Decimal("10"))
    falta = crear_producto(tienda_a, codigo="A-2", stock=Decimal("1"))

    respuesta = confirmar(
        client,
        tienda_a.slug,
        [
            {"codigo": hay.codigo, "cantidad": 2},
            {"codigo": falta.codigo, "cantidad": 50},
        ],
    )

    hay.refresh_from_db()
    assert respuesta.status_code == 400
    assert not Pedido.objects.exists()
    assert hay.stock == Decimal("10")


def test_una_tienda_sin_whatsapp_no_recibe_un_enlace_inventado(
    client, tienda_a, crear_producto
):
    """
    Un enlace a un número que no es de la tienda es peor que no tener enlace:
    el comprador cree que avisó y nadie leyó nada.
    """
    producto = crear_producto(tienda_a)

    cuerpo = confirmar(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1}]
    ).json()

    assert cuerpo["enlaceWhatsapp"] is None


def test_el_enlace_de_whatsapp_lleva_el_folio(client, tienda_a, crear_producto):
    tienda_a.whatsapp = "https://wa.me/56911112222"
    tienda_a.save(update_fields=["whatsapp"])
    producto = crear_producto(tienda_a)

    cuerpo = confirmar(
        client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1}]
    ).json()

    assert cuerpo["enlaceWhatsapp"].startswith("https://wa.me/56911112222?")
    assert cuerpo["numero"] in cuerpo["enlaceWhatsapp"].replace("%20", " ").replace(
        "%3A", ":"
    )


def test_el_comprador_autenticado_queda_asociado_al_pedido(
    client, tienda_a, comprador, crear_producto
):
    producto = crear_producto(tienda_a)

    confirmar(
        como(client, comprador),
        tienda_a.slug,
        [{"codigo": producto.codigo, "cantidad": 1}],
    )

    assert Pedido.objects.get().comprador == comprador


# ── La bandeja del panel ────────────────────────────────────────────────────


def test_la_bandeja_solo_muestra_los_pedidos_de_la_tienda(
    client, tienda_a, tienda_b, dueno_a, crear_producto
):
    propio = crear_producto(tienda_a, codigo="A-1")
    ajeno = crear_producto(tienda_b, codigo="B-1")
    confirmar(client, tienda_a.slug, [{"codigo": propio.codigo, "cantidad": 1}])
    confirmar(client, tienda_b.slug, [{"codigo": ajeno.codigo, "cantidad": 1}])

    cuerpo = como(client, dueno_a).get("/api/panel/pedidos/").json()

    assert len(cuerpo) == 1
    assert cuerpo[0]["lineas"][0]["productoCodigo"] == "A-1"


def test_la_bandeja_pide_sesion(client):
    assert client.get("/api/panel/pedidos/").status_code in (401, 403)


def test_no_se_puede_cambiar_el_estado_de_un_pedido_ajeno(
    client, tienda_b, dueno_a, crear_producto
):
    """
    404 y no 403: que el pedido exista ya es información de la otra tienda.
    """
    ajeno = crear_producto(tienda_b, codigo="B-1")
    confirmar(client, tienda_b.slug, [{"codigo": ajeno.codigo, "cantidad": 1}])
    pedido = Pedido.objects.get()

    respuesta = cambiar_estado(
        como(client, dueno_a), pedido.pk, Pedido.Estado.CONFIRMADO
    )

    pedido.refresh_from_db()
    assert respuesta.status_code == 404
    assert pedido.estado == Pedido.Estado.PENDIENTE


def test_el_dueno_cambia_el_estado_de_su_pedido(
    client, tienda_a, dueno_a, crear_producto
):
    producto = crear_producto(tienda_a)
    confirmar(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1}])
    pedido = Pedido.objects.get()

    respuesta = cambiar_estado(
        como(client, dueno_a), pedido.pk, Pedido.Estado.ENTREGADO
    )

    pedido.refresh_from_db()
    assert respuesta.status_code == 200
    assert pedido.estado == Pedido.Estado.ENTREGADO


def test_un_estado_que_no_existe_se_rechaza(client, tienda_a, dueno_a, crear_producto):
    producto = crear_producto(tienda_a)
    confirmar(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 1}])
    pedido = Pedido.objects.get()

    respuesta = cambiar_estado(como(client, dueno_a), pedido.pk, "DESPACHADO")

    pedido.refresh_from_db()
    assert respuesta.status_code == 400
    assert pedido.estado == Pedido.Estado.PENDIENTE


def test_anular_devuelve_el_stock(client, tienda_a, dueno_a, crear_producto):
    producto = crear_producto(tienda_a, stock=Decimal("10"))
    confirmar(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 4}])
    pedido = Pedido.objects.get()

    cambiar_estado(como(client, dueno_a), pedido.pk, Pedido.Estado.CANCELADO)

    producto.refresh_from_db()
    assert producto.stock == Decimal("10")


def test_anular_dos_veces_no_repone_dos_veces(
    client, tienda_a, dueno_a, crear_producto
):
    producto = crear_producto(tienda_a, stock=Decimal("10"))
    confirmar(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 4}])
    pedido = Pedido.objects.get()

    cambiar_estado(como(client, dueno_a), pedido.pk, Pedido.Estado.CANCELADO)
    cambiar_estado(como(client, dueno_a), pedido.pk, Pedido.Estado.CANCELADO)

    producto.refresh_from_db()
    assert producto.stock == Decimal("10")


def test_anular_no_toca_a_quien_no_lleva_inventario(
    client, tienda_a, dueno_a, crear_granel
):
    producto = crear_granel(tienda_a)
    confirmar(client, tienda_a.slug, [{"codigo": producto.codigo, "cantidad": 100}])
    pedido = Pedido.objects.get()

    cambiar_estado(como(client, dueno_a), pedido.pk, Pedido.Estado.CANCELADO)

    producto.refresh_from_db()
    assert producto.stock is None
    assert Producto.objects.de_tienda(tienda_a).count() == 1
