from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import DetalleVenta, Venta


@receiver(post_save, sender=DetalleVenta)
def recalcular_total_al_guardar(sender, instance, **kwargs):
    # Se ejecuta automáticamente cada vez que se guarda un DetalleVenta.
    # Recalcula el total de la venta asociada para mantenerlo sincronizado.
    if instance.venta_id:
        instance.venta.calcular_total()


@receiver(post_delete, sender=DetalleVenta)
def recalcular_total_al_eliminar(sender, instance, **kwargs):
    # Se ejecuta automáticamente cada vez que se elimina un DetalleVenta.
    # Recalcula el total de la venta para reflejar el detalle eliminado.
    if instance.venta_id:
        venta = Venta.objects.filter(pk=instance.venta_id).first()
        if venta:
            venta.calcular_total()