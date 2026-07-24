from django.db import migrations
from decimal import Decimal


def fill_precio_unitario(apps, schema_editor):
    DetalleVenta = apps.get_model('heladeria', 'DetalleVenta')
    Producto = apps.get_model('heladeria', 'Producto')

    # Para cada DetalleVenta con precio_unitario nulo, asignar producto.precio_base si existe
    for detalle in DetalleVenta.objects.filter(precio_unitario__isnull=True):
        try:
            prod = Producto.objects.get(pk=detalle.producto_id)
            precio = getattr(prod, 'precio_base', None) or Decimal('0.01')
        except Producto.DoesNotExist:
            precio = Decimal('0.01')

        detalle.precio_unitario = precio
        detalle.save(update_fields=['precio_unitario'])


def revert(apps, schema_editor):
    DetalleVenta = apps.get_model('heladeria', 'DetalleVenta')
    DetalleVenta.objects.filter(precio_unitario__isnull=False).update(precio_unitario=None)


class Migration(migrations.Migration):

    dependencies = [
        ('heladeria', '0002_alter_cliente_options_alter_detalleventa_options_and_more'),
    ]

    operations = [
        migrations.RunPython(fill_precio_unitario, revert),
    ]
