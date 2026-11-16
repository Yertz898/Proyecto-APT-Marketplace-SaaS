"""
Lleva el Instagram que cada tienda ya tenía a su lista de redes sociales.

El pie de página ahora muestra la lista; sin esto, una tienda que había cargado
su Instagram lo perdería de la vitrina al actualizar.
"""

from django.db import migrations


def copiar_instagram(apps, schema_editor):
    Tienda = apps.get_model("tiendas", "Tienda")
    for tienda in Tienda.objects.exclude(instagram=""):
        redes = list(tienda.redes_sociales or [])
        if tienda.instagram not in redes:
            redes.insert(0, tienda.instagram)
            tienda.redes_sociales = redes
            tienda.save(update_fields=["redes_sociales"])


class Migration(migrations.Migration):
    dependencies = [
        ("tiendas", "0007_tienda_pie_correo_tienda_pie_descripcion_and_more"),
    ]

    operations = [
        migrations.RunPython(copiar_instagram, migrations.RunPython.noop),
    ]
