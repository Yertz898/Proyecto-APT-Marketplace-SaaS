"""
Crear y editar el catálogo desde el panel.

Lo que más se prueba acá no es el camino feliz sino que **las reglas del modelo
lleguen como 400 con su campo marcado**. Si no se validan antes, la combinación
inválida llega a PostgreSQL y vuelve como un 500 que no dice qué arreglar.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from PIL import Image

from apps.catalogo.models import Categoria, Producto
from apps.precios.models import TramoPrecio, UnidadUmbral

pytestmark = pytest.mark.django_db

CATALOGO = "/api/panel/productos"
CATEGORIAS = "/api/panel/categorias"


def como(client, usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


def crear(client, **datos):
    cuerpo = {
        "codigo": "NUEVO-1",
        "nombre": "Producto nuevo",
        "precioNeto": 4990,
        "formaVenta": "unidad",
        "unidadMedida": "unidad",
        "controlaStock": True,
        "stock": "10",
    }
    cuerpo.update(datos)
    return client.post(CATALOGO, cuerpo, content_type="application/json")


def editar(client, codigo, **datos):
    return client.patch(f"{CATALOGO}/{codigo}", datos, content_type="application/json")


def imagen(nombre="foto.png", tamano=(8, 8)):
    memoria = io.BytesIO()
    Image.new("RGB", tamano, "#7C3AED").save(memoria, format="PNG")
    return SimpleUploadedFile(nombre, memoria.getvalue(), content_type="image/png")


def subir(client, codigo, **archivos):
    """PATCH con archivos: el cliente de Django solo arma multipart en `post`."""
    return client.patch(
        f"{CATALOGO}/{codigo}",
        encode_multipart(BOUNDARY, archivos),
        content_type=MULTIPART_CONTENT,
    )


# ── Crear ───────────────────────────────────────────────────────────────────


def test_el_dueno_crea_un_producto(client, dueno_a, tienda_a):
    respuesta = crear(como(client, dueno_a))

    assert respuesta.status_code == 201
    assert respuesta.json()["codigo"] == "NUEVO-1"
    assert Producto.objects.de_tienda(tienda_a).filter(codigo="NUEVO-1").exists()


def test_el_producto_nuevo_queda_en_la_tienda_del_token(client, dueno_a, tienda_a):
    """La tienda no viaja en el cuerpo. Mandarla no sirve de nada."""
    crear(como(client, dueno_a), tienda=999)

    assert Producto.objects.get(codigo="NUEVO-1").tienda_id == tienda_a.pk


def test_el_vendedor_tambien_puede_crear(client, vendedor_b, tienda_b):
    assert crear(como(client, vendedor_b)).status_code == 201


def test_un_comprador_no_puede_crear(client, comprador):
    assert crear(como(client, comprador)).status_code == 403


def test_un_codigo_repetido_se_rechaza_con_su_campo(
    client, dueno_a, producto_a, detalles_de_error
):
    respuesta = crear(como(client, dueno_a), codigo=producto_a.codigo)

    assert respuesta.status_code == 400
    assert "codigo" in detalles_de_error(respuesta)


def test_dos_tiendas_pueden_usar_el_mismo_codigo(client, dueno_a, producto_b):
    """El código es único por tienda, no en toda la plataforma."""
    assert crear(como(client, dueno_a), codigo=producto_b.codigo).status_code == 201


def test_el_precio_tiene_que_ser_positivo(client, dueno_a, detalles_de_error):
    respuesta = crear(como(client, dueno_a), precioNeto=0)

    assert respuesta.status_code == 400
    assert "precioNeto" in detalles_de_error(respuesta)


# ── Las reglas cruzadas, que son las que reventaban ─────────────────────────


def test_un_producto_por_peso_no_se_mide_en_unidades(
    client, dueno_a, detalles_de_error
):
    respuesta = crear(como(client, dueno_a), formaVenta="peso", unidadMedida="unidad")

    assert respuesta.status_code == 400
    assert "unidad_medida" in detalles_de_error(respuesta)


def test_decir_que_controla_stock_sin_stock_se_rechaza(
    client, dueno_a, detalles_de_error
):
    respuesta = crear(como(client, dueno_a), controlaStock=True, stock=None)

    assert respuesta.status_code == 400
    assert "stock" in detalles_de_error(respuesta)


def test_no_controlar_stock_y_mandar_cantidad_se_rechaza(
    client, dueno_a, detalles_de_error
):
    respuesta = crear(como(client, dueno_a), controlaStock=False, stock="5")

    assert respuesta.status_code == 400
    assert "stock" in detalles_de_error(respuesta)


def test_solo_un_producto_por_lote_declara_piezas(client, dueno_a, detalles_de_error):
    respuesta = crear(como(client, dueno_a), formaVenta="unidad", cantidadPiezas=10)

    assert respuesta.status_code == 400
    assert "cantidad_piezas" in detalles_de_error(respuesta)


def test_un_producto_por_peso_sin_inventario_se_crea(client, dueno_a):
    respuesta = crear(
        como(client, dueno_a),
        formaVenta="peso",
        unidadMedida="g",
        controlaStock=False,
        stock=None,
    )

    assert respuesta.status_code == 201


# ── Editar ──────────────────────────────────────────────────────────────────


def test_el_dueno_cambia_el_precio(client, dueno_a, producto_a):
    respuesta = editar(como(client, dueno_a), producto_a.codigo, precioNeto=9990)

    assert respuesta.status_code == 200
    producto_a.refresh_from_db()
    assert producto_a.precio_neto == 9990


def test_desactivar_lo_saca_de_la_vitrina_sin_borrarlo(
    client, dueno_a, tienda_a, producto_a
):
    editar(como(client, dueno_a), producto_a.codigo, activo=False)

    producto_a.refresh_from_db()
    assert producto_a.activo is False
    assert producto_a not in Producto.objects.publicadas_de(tienda_a)
    assert Producto.objects.de_tienda(tienda_a).filter(pk=producto_a.pk).exists()


def test_no_se_puede_borrar_un_producto(client, dueno_a, producto_a):
    """
    En este proyecto el catálogo no se borra, se desactiva.

    Un producto borrado se lleva por delante su composición, sus tramos y las
    líneas de pedido que lo nombran.
    """
    respuesta = como(client, dueno_a).delete(f"{CATALOGO}/{producto_a.codigo}")

    assert respuesta.status_code == 405
    assert Producto.objects.filter(pk=producto_a.pk).exists()


def test_editar_tambien_valida_las_reglas_cruzadas(
    client, dueno_a, producto_a, detalles_de_error
):
    respuesta = editar(como(client, dueno_a), producto_a.codigo, controlaStock=False)

    assert respuesta.status_code == 400
    assert "stock" in detalles_de_error(respuesta)


# ── La foto ─────────────────────────────────────────────────────────────────


def test_el_dueno_sube_la_foto_de_un_producto(client, dueno_a, producto_a):
    respuesta = subir(como(client, dueno_a), producto_a.codigo, foto=imagen())

    assert respuesta.status_code == 200
    producto_a.refresh_from_db()
    assert producto_a.foto


def test_la_foto_aparece_en_la_vitrina(client, dueno_a, tienda_a, producto_a):
    subir(como(client, dueno_a), producto_a.codigo, foto=imagen())
    del client.defaults["HTTP_AUTHORIZATION"]

    cuerpo = client.get(f"/api/t/{tienda_a.slug}/productos/{producto_a.codigo}").json()

    assert cuerpo["foto"]["url"]
    assert cuerpo["foto"]["alt"] == producto_a.nombre


def test_un_archivo_que_no_es_imagen_se_rechaza(
    client, dueno_a, producto_a, detalles_de_error
):
    """
    Se revisa el contenido, no la extensión del nombre.

    La extensión la escribe quien sube el archivo y no dice nada de lo que hay
    adentro.
    """
    disfrazado = SimpleUploadedFile(
        "foto.png", b"<svg onload=alert(1)></svg>", content_type="image/png"
    )
    respuesta = subir(como(client, dueno_a), producto_a.codigo, foto=disfrazado)

    assert respuesta.status_code == 400
    assert "foto" in detalles_de_error(respuesta)
    producto_a.refresh_from_db()
    assert not producto_a.foto


# ── Categorías ──────────────────────────────────────────────────────────────


def test_el_dueno_crea_una_categoria(client, dueno_a, tienda_a):
    respuesta = como(client, dueno_a).post(
        CATEGORIAS, {"nombre": "cocina"}, content_type="application/json"
    )

    assert respuesta.status_code == 201
    assert Categoria.objects.de_tienda(tienda_a).filter(nombre="cocina").exists()


def test_una_categoria_repetida_se_rechaza(
    client, dueno_a, tienda_a, crear_categoria, detalles_de_error
):
    crear_categoria(tienda_a, nombre="cocina")

    respuesta = como(client, dueno_a).post(
        CATEGORIAS, {"nombre": "cocina"}, content_type="application/json"
    )

    assert respuesta.status_code == 400
    assert "nombre" in detalles_de_error(respuesta)


def test_el_producto_se_asigna_a_una_categoria_por_su_nombre(
    client, dueno_a, tienda_a, crear_categoria
):
    """Por nombre y no por identificador: un id en el cuerpo invita a probar ajenos."""
    crear_categoria(tienda_a, nombre="cocina")

    respuesta = crear(como(client, dueno_a), categoria="cocina")

    assert respuesta.status_code == 201
    assert Producto.objects.get(codigo="NUEVO-1").categoria.nombre == "cocina"


def test_una_categoria_que_no_existe_se_rechaza(client, dueno_a, detalles_de_error):
    respuesta = crear(como(client, dueno_a), categoria="inventada")

    assert respuesta.status_code == 400
    assert "categoria" in detalles_de_error(respuesta)


def test_no_se_borra_una_categoria_en_uso(
    client, dueno_a, tienda_a, crear_categoria, crear_producto
):
    categoria = crear_categoria(tienda_a, nombre="cocina")
    crear_producto(tienda_a, codigo="CON-CAT", categoria=categoria)

    respuesta = como(client, dueno_a).delete(f"{CATEGORIAS}/{categoria.pk}")

    assert respuesta.status_code == 400
    assert Categoria.objects.filter(pk=categoria.pk).exists()


def test_una_categoria_vacia_si_se_borra(client, dueno_a, tienda_a, crear_categoria):
    categoria = crear_categoria(tienda_a, nombre="sin-uso")

    respuesta = como(client, dueno_a).delete(f"{CATEGORIAS}/{categoria.pk}")

    assert respuesta.status_code == 204


# ── Tramos ──────────────────────────────────────────────────────────────────


def test_el_dueno_agrega_un_tramo_a_su_producto(client, dueno_a, producto_a):
    respuesta = como(client, dueno_a).post(
        f"{CATALOGO}/{producto_a.codigo}/tramos",
        {"umbral": "12", "unidadUmbral": "cantidad", "precioNeto": 4490},
        content_type="application/json",
    )

    assert respuesta.status_code == 201
    assert producto_a.tramos.count() == 1


def test_un_tramo_repetido_se_rechaza(client, dueno_a, producto_a, detalles_de_error):
    TramoPrecio.objects.create(
        tienda=producto_a.tienda,
        producto=producto_a,
        unidad_umbral=UnidadUmbral.CANTIDAD,
        umbral=12,
        valor=4490,
    )

    respuesta = como(client, dueno_a).post(
        f"{CATALOGO}/{producto_a.codigo}/tramos",
        {"umbral": "12", "unidadUmbral": "cantidad", "precioNeto": 3990},
        content_type="application/json",
    )

    assert respuesta.status_code == 400
    assert "umbral" in detalles_de_error(respuesta)


def test_el_tramo_queda_en_la_tienda_del_producto(
    client, dueno_a, tienda_a, producto_a
):
    como(client, dueno_a).post(
        f"{CATALOGO}/{producto_a.codigo}/tramos",
        {"umbral": "12", "unidadUmbral": "cantidad", "precioNeto": 4490},
        content_type="application/json",
    )

    assert TramoPrecio.objects.get().tienda_id == tienda_a.pk


def test_el_tramo_se_puede_borrar(client, dueno_a, producto_a):
    tramo = TramoPrecio.objects.create(
        tienda=producto_a.tienda,
        producto=producto_a,
        unidad_umbral=UnidadUmbral.CANTIDAD,
        umbral=12,
        valor=4490,
    )

    respuesta = como(client, dueno_a).delete(f"/api/panel/tramos/{tramo.pk}")

    assert respuesta.status_code == 204


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_no_se_edita_el_producto_de_otra_tienda(client, dueno_a, producto_b):
    """
    404 y no 403: el código viaja en la URL, así que es adivinable, y un 403
    confirmaría que existe en alguna parte.
    """
    respuesta = editar(como(client, dueno_a), producto_b.codigo, precioNeto=1)

    assert respuesta.status_code == 404
    producto_b.refresh_from_db()
    assert producto_b.precio_neto != 1


@pytest.mark.aislamiento
def test_no_se_sube_una_foto_al_producto_de_otra_tienda(client, dueno_a, producto_b):
    respuesta = subir(como(client, dueno_a), producto_b.codigo, foto=imagen())

    assert respuesta.status_code == 404
    producto_b.refresh_from_db()
    assert not producto_b.foto


@pytest.mark.aislamiento
def test_no_se_usa_una_categoria_de_otra_tienda(
    client, dueno_a, tienda_b, crear_categoria, detalles_de_error
):
    """La categoría se busca dentro de la tienda, así que la ajena no existe."""
    crear_categoria(tienda_b, nombre="ajena")

    respuesta = crear(como(client, dueno_a), categoria="ajena")

    assert respuesta.status_code == 400
    assert "categoria" in detalles_de_error(respuesta)


@pytest.mark.aislamiento
def test_no_se_borra_una_categoria_de_otra_tienda(
    client, dueno_a, tienda_b, crear_categoria
):
    ajena = crear_categoria(tienda_b, nombre="ajena")

    respuesta = como(client, dueno_a).delete(f"{CATEGORIAS}/{ajena.pk}")

    assert respuesta.status_code == 404
    assert Categoria.objects.filter(pk=ajena.pk).exists()


@pytest.mark.aislamiento
def test_no_se_agrega_un_tramo_al_producto_de_otra_tienda(
    client, dueno_a, producto_b
):
    respuesta = como(client, dueno_a).post(
        f"{CATALOGO}/{producto_b.codigo}/tramos",
        {"umbral": "12", "unidadUmbral": "cantidad", "precioNeto": 4490},
        content_type="application/json",
    )

    assert respuesta.status_code == 404
    assert not producto_b.tramos.exists()


@pytest.mark.aislamiento
def test_no_se_borra_el_tramo_de_otra_tienda(client, dueno_a, granel_b):
    ajeno = granel_b.tramos.first()

    respuesta = como(client, dueno_a).delete(f"/api/panel/tramos/{ajeno.pk}")

    assert respuesta.status_code == 404
    assert TramoPrecio.objects.filter(pk=ajeno.pk).exists()
