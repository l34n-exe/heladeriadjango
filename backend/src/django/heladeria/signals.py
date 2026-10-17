from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import DetalleVenta, Sabor, Venta


@receiver(m2m_changed, sender=DetalleVenta.sabores.through)
def validar_sabores_detalle(sender, instance, action, pk_set, **kwargs):
    if action not in {'pre_add', 'pre_remove', 'pre_clear'}:
        return

    if instance.venta.estado != Venta.PENDIENTE:
        raise ValidationError(
            'No se pueden modificar sabores de una venta que no está pendiente.'
        )

    if action != 'pre_add':
        return

    sabores_actuales = set(instance.sabores.values_list('pk', flat=True))
    seleccionados = sabores_actuales | set(pk_set or set())
    DetalleVenta.validar_sabores(
        instance.producto,
        Sabor.objects.filter(pk__in=seleccionados),
    )


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