from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone


class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Empleado(Persona):
    GERENTE = 'GERENTE'
    CAJERO = 'CAJERO'
    LIMPIADOR = 'LIMPIADOR'

    PUESTO = [
        (GERENTE, 'Gerente'),
        (CAJERO, 'Cajero'),
        (LIMPIADOR, 'Limpiador'),
    ]

    puesto = models.CharField(max_length=50, choices=PUESTO)
    fecha_contratacion = models.DateField(null=True, blank=True, default=timezone.now, help_text='Fecha de contratación (puede ser nula si no se conoce)')

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.puesto}"


class Cliente(Persona):
    es_socio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {'Socio' if self.es_socio else 'No Socio'}"


class Sabor(models.Model):
    # Categorías de sabores disponibles en la heladería.
    CHOCOLATE = 'CHOCOLATE'
    DULCE_DE_LECHE = 'DULCE_DE_LECHE'
    FRUTAL = 'FRUTAL'
    CREMA = 'CREMA'
    VEGANO = 'VEGANO'
    OTRO = 'OTRO'

    CATEGORIA_SABOR = [
        (CHOCOLATE, 'Chocolate'),
        (DULCE_DE_LECHE, 'Dulce de Leche'),
        (FRUTAL, 'Frutal'),
        (CREMA, 'Crema'),
        (VEGANO, 'Vegano'),
        (OTRO, 'Otro'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_SABOR)
    stock_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
    )
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.categoria}"


class Producto(models.Model):
    # Tipos de productos y sus características por defecto.
    POTE_1KG = 'POTE_1KG'
    POTE_500G = 'POTE_500G'
    POTE_250G = 'POTE_250G'
    BALDE = 'BALDE'
    MILKSHAKE = 'MILKSHAKE'
    CUCURUCHO = 'CUCURUCHO'
    VASO = 'VASO'
    POSTRE = 'POSTRE'
    BOMBON = 'BOMBON'

    TIPO_PRODUCTO = [
        (POTE_1KG,   'Pote 1 KG'),
        (POTE_500G,  'Pote 1/2 KG'),
        (POTE_250G,  'Pote 1/4 KG'),
        (BALDE,      'Balde'),
        (MILKSHAKE,  'Milk Shake'),
        (CUCURUCHO,  'Cucurucho'),
        (VASO,       'Vaso'),
        (POSTRE,     'Postre'),
        (BOMBON,     'Bombón'),
    ]

    # Gramos y máximo de sabores por tipo de producto.
    # Se usan como referencia al crear productos desde el admin o fixtures.
    DEFAULTS_POR_TIPO = {
        POTE_1KG:  {'gramos': 1000, 'max_sabores': 4},
        POTE_500G: {'gramos': 500,  'max_sabores': 3},
        POTE_250G: {'gramos': 250,  'max_sabores': 2},
        BALDE:     {'gramos': 4000, 'max_sabores': 6},
        MILKSHAKE: {'gramos': 300,  'max_sabores': 2},
        CUCURUCHO: {'gramos': 150,  'max_sabores': 2},
        VASO:      {'gramos': 200,  'max_sabores': 2},
        POSTRE:    {'gramos': 0,    'max_sabores': 0},
        BOMBON:    {'gramos': 0,    'max_sabores': 0},
    }

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    max_sabores = models.PositiveIntegerField(default=0)
    tipo_producto = models.CharField(max_length=50, choices=TIPO_PRODUCTO, default=POTE_1KG)
    activo = models.BooleanField(default=True)
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.01'),
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    gramos = models.PositiveIntegerField(
        default=0,
        help_text='Gramos de helado que contiene este producto.',
    )
    sabores_disponibles = models.ManyToManyField(
        Sabor,
        blank=True,
        related_name='productos',
        limit_choices_to={'disponible': True},
        help_text='Sabores disponibles para este producto.',
    )

    def __str__(self):
        return f"{self.nombre} - {self.tipo_producto} - ${self.precio_base} - Max {self.max_sabores} sabores"


class Venta(models.Model):
    PENDIENTE = 'PENDIENTE'
    COMPLETADA = 'COMPLETADA'
    CANCELADA = 'CANCELADA'

    EFECTIVO = 'EFECTIVO'
    TARJETA = 'TARJETA'
    TRANSFERENCIA = 'TRANSFERENCIA'

    ESTADO_VENTA = [
        (PENDIENTE,  'Pendiente'),
        (COMPLETADA, 'Completada'),
        (CANCELADA,  'Cancelada'),
    ]
    METODO_PAGO = [
        (EFECTIVO,      'Efectivo'),
        (TARJETA,       'Tarjeta'),
        (TRANSFERENCIA, 'Transferencia'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_VENTA, default=PENDIENTE)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas'
    )
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='ventas')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO, default=EFECTIVO)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['-fecha_venta']

    def __str__(self):
        cliente_nombre = f"{self.cliente.nombre} {self.cliente.apellido}" if self.cliente else "Cliente anónimo"
        return f"Venta #{self.pk} - {cliente_nombre} - {self.metodo_pago} - ${self.total}"

    def save(self, *args, **kwargs):
        # Captura el estado anterior y ajusta el stock de sabores según la transición.
        # PENDIENTE → COMPLETADA: descuenta stock.
        # COMPLETADA → CANCELADA: devuelve stock.
        with transaction.atomic():
            estado_anterior = None
            if self.pk:
                estado_anterior = Venta.objects.select_for_update().get(pk=self.pk).estado

            super().save(*args, **kwargs)

            if estado_anterior != self.COMPLETADA and self.estado == self.COMPLETADA:
                self._ajustar_stock_sabores(descontar=True)
            elif estado_anterior == self.COMPLETADA and self.estado == self.CANCELADA:
                self._ajustar_stock_sabores(descontar=False)
    # Ajusta el stock de sabores según los detalles de la venta, ya sea descontando o devolviendo cantidades.
    def _ajustar_stock_sabores(self, descontar: bool):
        # Ajusta el stock de sabores para esta venta. Si descontar=True se restan las cantidades calculadas por detalle; si False se
        # devuelven (p.ej. en caso de cancelación).

        #La función agrupa por sabor la cantidad en kg requerida por todos los detalles
        #de la venta, bloquea las filas de Sabor con select_for_update para evitar
        #condiciones de carrera y aplica los cambios dentro de una transacción.
        
        detalles = list(self.detalles.prefetch_related('sabores', 'producto').all())  # type: ignore
        kg_por_sabor = defaultdict(lambda: Decimal('0.000'))

        for detalle in detalles:
            sabores = list(detalle.sabores.all())
            if not sabores or detalle.producto.gramos == 0:
                continue

            kg = (
                Decimal(detalle.producto.gramos)
                / Decimal(len(sabores))
                / Decimal('1000')
                * Decimal(str(detalle.cantidad))
            ).quantize(Decimal('0.001'))

            for sabor in sabores:
                kg_por_sabor[sabor.pk] += kg

        if not kg_por_sabor:
            return

        with transaction.atomic():
            sabores_map = {
                s.pk: s for s in
                Sabor.objects.select_for_update().filter(pk__in=kg_por_sabor.keys()).order_by('pk')
            }

            if descontar:
                for sabor_id, kg in kg_por_sabor.items():
                    sabor = sabores_map[sabor_id]
                    if sabor.stock_kg < kg:
                        raise ValidationError(
                            f"Stock insuficiente de '{sabor.nombre}'. "
                            f"Disponible: {sabor.stock_kg} kg, requerido: {kg} kg."
                        )

            for sabor_id, kg in kg_por_sabor.items():
                sabor = sabores_map[sabor_id]
                sabor.stock_kg += -kg if descontar else kg
                # Mantener 3 decimales para stock_kg
                sabor.stock_kg = Decimal(sabor.stock_kg).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
                sabor.save(update_fields=['stock_kg'])

    # Calcula el total de la venta sumando los subtotales de sus detalles y actualiza el campo total.
    def calcular_total(self):
        total = self.detalles.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')  # type: ignore
        self.total = total
        Venta.objects.filter(pk=self.pk).update(total=total)

    def delete(self, *args, **kwargs):
        # Impide eliminar ventas que ya fueron completadas o canceladas.
        if self.estado in (self.COMPLETADA, self.CANCELADA):
            raise ValidationError(
                f"No se puede eliminar una venta con estado {self.get_estado_display()}."  # type: ignore
            )
        return super().delete(*args, **kwargs)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, default=None,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sabores = models.ManyToManyField(
        Sabor,
        blank=True,
        related_name='detalles_venta',
        limit_choices_to={'disponible': True},
    )

    def __str__(self):
        return f"Detalle #{self.pk} - {self.producto.nombre} - {self.cantidad}"

    # Validaciones de modelo para asegurar que la cantidad de sabores seleccionados no exceda el máximo permitido por el producto y que los sabores seleccionados estén disponibles para ese producto.
    def clean(self):
        if self.pk is not None:
            if self.producto.max_sabores > 0 and self.sabores.count() > self.producto.max_sabores:
                raise ValidationError(
                    f"El producto {self.producto.nombre} permite un máximo de "
                    f"{self.producto.max_sabores} sabores."
                )

            if self.producto.sabores_disponibles.exists():
                permitidos = set(self.producto.sabores_disponibles.values_list('id', flat=True))
                seleccionados = set(self.sabores.values_list('id', flat=True))
                if not seleccionados.issubset(permitidos):
                    raise ValidationError(
                        "Uno o más sabores seleccionados no están disponibles para este producto."
                    )
    # Guarda el detalle, aplicando fallback de precio_unitario y calculando el subtotal
    def save(self, *args, **kwargs):

        if self.precio_unitario is None:
            # Si no se proporciona precio_unitario, usar el precio_base del producto.
            self.precio_unitario = self.producto.precio_base

        # Ejecutar validaciones de modelo por defecto
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()

        # Calcular subtotal y asegurar 2 decimales consistentes
        subtotal = Decimal(self.cantidad) * self.precio_unitario
        self.subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)