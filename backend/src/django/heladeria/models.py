from collections import defaultdict
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q, Sum
from django.utils import timezone
from django.conf import settings

# QuerySets personalizados para Venta y DetalleVenta que implementan restricciones de eliminación.
class VentaQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        if self.filter(
            estado__in={Venta.COMPLETADA, Venta.CANCELADA, Venta.REEMBOLSADA}
        ).exists():
            raise ValidationError(
                'No se pueden eliminar ventas completadas, canceladas o reembolsadas.'
            )
        return super().delete(*args, **kwargs)


class DetalleVentaQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        if self.filter(venta__estado__in={Venta.COMPLETADA, Venta.CANCELADA, Venta.REEMBOLSADA}).exists():
            raise ValidationError(
                'No se pueden eliminar detalles de una venta completada o cancelada.'
            )
        return super().delete(*args, **kwargs)

class AuditoriaQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        raise ValidationError("No está permitido eliminar registros de auditoría.")

class MovimientoStockQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        raise ValidationError("No está permitido eliminar registros de movimientos de stock.")


class MovimientoEnvaseQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        raise ValidationError("No está permitido eliminar movimientos de envases.")
    
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
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='empleado',
        null=True,
        blank=True,
        help_text='Usuario del sistema asociado a este empleado'
    )
    GERENTE = 'GERENTE'
    CAJERO = 'CAJERO'
    LIMPIADOR = 'LIMPIADOR'

    PUESTO = [
        (GERENTE, 'Gerente'),
        (CAJERO, 'Cajero'),
        (LIMPIADOR, 'Limpiador'),
    ]

    puesto = models.CharField(max_length=50, choices=PUESTO)
    fecha_contratacion = models.DateField(null=True, blank=True, default=timezone.localdate, help_text='Fecha de contratación')

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.puesto})"


class Cliente(Persona):
    es_socio = models.BooleanField(default=False)
    puntos_acumulados = models.PositiveIntegerField(
        default=0,
        help_text='Puntos disponibles del socio',
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({'Socio' if self.es_socio else 'No Socio'})"


class Sabor(models.Model):
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

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(stock_kg__gte=Decimal('0.000')),  # type: ignore[call-arg]
                name='sabor_stock_kg_no_negativo',
            ),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.categoria}"

    def save(self, *args, **kwargs):
        # Parámetros opcionales para dejar trazabilidad en el MovimientoStock
        usuario = kwargs.pop('usuario', None)
        motivo_custom = kwargs.pop('motivo', None)
        venta = kwargs.pop('venta', None)

        # Guardado + movimiento en una sola transacción: no puede quedar
        # stock modificado sin su registro.
        with transaction.atomic():
            stock_anterior = None
            if self.pk:
                stock_anterior = (
                    Sabor.objects.select_for_update().filter(pk=self.pk)
                    .values_list('stock_kg', flat=True)
                    .first()
                )

            super().save(*args, **kwargs)

            if stock_anterior is not None and self.stock_kg != stock_anterior:
                diferencia = self.stock_kg - stock_anterior
                entrada = diferencia > 0
                MovimientoStock.objects.create(
                    usuario=usuario,
                    venta=venta,
                    sabor=self,
                    tipo_movimiento=MovimientoStock.ENTRADA if entrada else MovimientoStock.SALIDA,
                    cantidad_kg=abs(diferencia),
                    stock_anterior=stock_anterior,
                    stock_nuevo=self.stock_kg,
                    motivo=motivo_custom or (
                        'Reabastecimiento manual' if entrada else 'Ajuste de stock / merma'
                    ),
                )

class Envase(models.Model):
    nombre = models.CharField(max_length=100)
    stock_unidades = models.PositiveIntegerField(default=0, help_text='Stock disponible en unidades')
    stock_minimo = models.PositiveIntegerField(default=10, help_text='Alerta de stock crítico')

    class Meta:
        ordering = ['nombre']
        constraints = [
            models.CheckConstraint(
                check=Q(stock_unidades__gte=0), # type: ignore
                name='envase_stock_unidades_no_negativo',
            ),
        ]

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock_unidades})"

class Producto(models.Model):
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
    envase = models.ForeignKey(
        Envase, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        help_text='Envase o descartable que consume este producto'
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.tipo_producto}) - ${self.precio_base} (Max {self.max_sabores} sabores)"

    def save(self, *args, **kwargs):
        defaults = self.DEFAULTS_POR_TIPO.get(self.tipo_producto)
        producto_anterior = None
        if self.pk:
            producto_anterior = Producto.objects.get(pk=self.pk)

        if defaults and self._state.adding and self.gramos == 0 and self.max_sabores == 0:
            self.gramos = defaults['gramos']
            self.max_sabores = defaults['max_sabores']
        elif (
            defaults
            and producto_anterior
            and producto_anterior.tipo_producto != self.tipo_producto
            and self.gramos == self.DEFAULTS_POR_TIPO.get(
                producto_anterior.tipo_producto, {}
            ).get('gramos')
            and self.max_sabores == self.DEFAULTS_POR_TIPO.get(
                producto_anterior.tipo_producto, {}
            ).get('max_sabores')
        ):
            self.gramos = defaults['gramos']
            self.max_sabores = defaults['max_sabores']

        return super().save(*args, **kwargs)

class Venta(models.Model):
    PENDIENTE = 'PENDIENTE'
    COMPLETADA = 'COMPLETADA'
    CANCELADA = 'CANCELADA'
    REEMBOLSADA = 'REEMBOLSADA'

    EFECTIVO = 'EFECTIVO'
    TARJETA = 'TARJETA'
    TRANSFERENCIA = 'TRANSFERENCIA'

    ESTADO_VENTA = [
        (PENDIENTE, 'Pendiente'),
        (COMPLETADA, 'Completada'),
        (CANCELADA, 'Cancelada'),
        (REEMBOLSADA, 'Reembolsada'),
    ]
    METODO_PAGO = [
        (EFECTIVO, 'Efectivo'),
        (TARJETA, 'Tarjeta'),
        (TRANSFERENCIA, 'Transferencia'),
    ]

    PUNTOS_POR_CANJE = 100
    DESCUENTO_POR_CANJE = Decimal('500.00')
    PESOS_POR_PUNTOS = Decimal('1000.00')
    PUNTOS_POR_CADA_1000 = 10

    estado = models.CharField(max_length=20, choices=ESTADO_VENTA, default=PENDIENTE)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas'
    )
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='ventas')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO, default=EFECTIVO)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    descuento_aplicado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    puntos_canjeados = models.PositiveIntegerField(default=0)
    puntos_otorgados = models.PositiveIntegerField(default=0)
    objects = VentaQuerySet.as_manager()

    class Meta:
        ordering = ['-fecha_venta']

    def __str__(self):
        cliente_nombre = f"{self.cliente.nombre} {self.cliente.apellido}" if self.cliente else "Cliente anónimo"
        return f"Venta #{self.pk} - {cliente_nombre} (${self.total})"

    def clean(self):
        super().clean()
        
        if self.pk:
            # Traemos solo el estado actual de la base de datos de manera eficiente
            venta_anterior = Venta.objects.only('estado').get(pk=self.pk)
            estado_en_db = venta_anterior.estado

            # 1. Estados terminales (CANCELADA / REEMBOLSADA): Inmutabilidad absoluta
            if estado_en_db in [self.CANCELADA, self.REEMBOLSADA]:
                if self.estado != estado_en_db:
                    raise ValidationError(
                        f"No se puede modificar ni cambiar el estado de una venta que ya ha sido {estado_en_db.lower()}."
                    )
                # Opcional: Impedir cualquier cambio en otros campos si ya es terminal
                # (Comparar campos actuales con los de la base de datos si es necesario)
            
            # 2. Si estaba COMPLETADA, solo puede transicionar a REEMBOLSADA y no se deben alterar sus datos
            elif estado_en_db == self.COMPLETADA:
                if self.estado not in [self.COMPLETADA, self.REEMBOLSADA]:
                    raise ValidationError(
                        "Una venta completada solo puede ser reembolsada."
                    )
                if self.estado == self.COMPLETADA:
                    # Comparamos directamente los objetos en lugar de usar '_id' para complacer al linter
                    original = Venta.objects.get(pk=self.pk)
                    if (self.cliente != original.cliente or 
                        self.metodo_pago != original.metodo_pago or 
                        self.empleado != original.empleado):
                        raise ValidationError(
                            "No se pueden modificar los datos de una venta que ya ha sido completada."
                        )
            
            # 3. Si estaba PENDIENTE, puede mantenerse, completarse o cancelarse
            elif estado_en_db == self.PENDIENTE:
                if self.estado not in [self.PENDIENTE, self.COMPLETADA, self.CANCELADA]:
                    raise ValidationError(
                        "Una venta pendiente solo puede ser completada o cancelada."
                    )
        else:
            if self.estado != self.PENDIENTE:
                raise ValidationError({
                    'estado': 'Una venta nueva debe comenzar en estado pendiente.'
                })

    def save(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        self.full_clean()

        with transaction.atomic():
            creada = self._state.adding
            estado_anterior = ''

            if not creada:
                estado_anterior = Venta.objects.select_for_update().get(pk=self.pk).estado

                if estado_anterior == self.PENDIENTE and self.estado == self.COMPLETADA:
                    self._procesar_salida_envases(usuario)
                    self._procesar_salida_stock(usuario)
                    self._procesar_puntos_socio()

                elif estado_anterior == self.COMPLETADA and self.estado == self.REEMBOLSADA:
                    self._procesar_devolucion_stock(usuario)
                    self._procesar_devolucion_envases(usuario)
                    self._revertir_puntos_socio()

            super().save(*args, **kwargs)

            # Solo se audita la creación y los cambios de estado (no cada save()).
            if creada or estado_anterior != self.estado:
                Auditoria.objects.create(
                    usuario=usuario,
                    venta=self,
                    estado_anterior=estado_anterior,
                    estado_nuevo=self.estado,
                    motivo=(
                        "Creación de venta" if creada
                        else f"Cambio de estado a {self.estado} (Total: ${self.total})"
                    ),
                )

    def _procesar_puntos_socio(self):
        cliente_id = getattr(self, 'cliente_id', None)
        if not cliente_id:
            self.descuento_aplicado = Decimal('0.00')
            self.puntos_otorgados = 0
            if self.puntos_canjeados:
                raise ValidationError('Solo se pueden canjear puntos para un cliente socio.')
            return

        cliente = Cliente.objects.select_for_update().get(pk=cliente_id)

        if not cliente.es_socio:
            self.descuento_aplicado = Decimal('0.00')
            self.puntos_otorgados = 0
            if self.puntos_canjeados:
                raise ValidationError('Solo los clientes socios pueden canjear puntos.')
            return

        puntos_solicitados = self.puntos_canjeados
        if puntos_solicitados:
            if puntos_solicitados % self.PUNTOS_POR_CANJE != 0:
                raise ValidationError(
                    f'Los puntos se canjean en bloques de {self.PUNTOS_POR_CANJE}.'
                )

            bloques = puntos_solicitados // self.PUNTOS_POR_CANJE
            bloques_disponibles = cliente.puntos_acumulados // self.PUNTOS_POR_CANJE
            bloques_descuento = int(self.total // self.DESCUENTO_POR_CANJE)

            if bloques > bloques_disponibles:
                raise ValidationError('El cliente no tiene suficientes puntos acumulados.')
            if bloques > bloques_descuento:
                raise ValidationError(
                    'El canje supera el descuento permitido por el total de la venta.'
                )

            descuento = self.DESCUENTO_POR_CANJE * bloques
            self.descuento_aplicado = descuento.quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            cliente.puntos_acumulados -= puntos_solicitados
        else:
            self.descuento_aplicado = Decimal('0.00')

        self.total = max(
            Decimal('0.00'),
            self.total - self.descuento_aplicado,
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        puntos = int(self.total // self.PESOS_POR_PUNTOS) * self.PUNTOS_POR_CADA_1000
        cliente.puntos_acumulados += puntos
        self.puntos_otorgados = puntos
        cliente.save(update_fields=['puntos_acumulados'])

    def _revertir_puntos_socio(self):
        cliente_id = getattr(self, 'cliente_id', None)
        if not cliente_id:
            return

        cliente = Cliente.objects.select_for_update().get(pk=cliente_id)
        cliente.puntos_acumulados = max(
            0,
            cliente.puntos_acumulados
            + self.puntos_canjeados
            - self.puntos_otorgados,
        )
        cliente.save(update_fields=['puntos_acumulados'])

    def _procesar_salida_envases(self, usuario):
        unidades_por_envase = defaultdict(int)

        for detalle in DetalleVenta.objects.filter(venta=self).select_related('producto', 'envase'):
            envase_id = getattr(detalle, 'envase_id', None) or detalle.producto.envase_id
            if envase_id:
                unidades_por_envase[envase_id] += detalle.cantidad

        if not unidades_por_envase:
            return

        envases = {
            envase.pk: envase
            for envase in Envase.objects.select_for_update().filter(
                pk__in=unidades_por_envase.keys()
            ).order_by('pk')
        }

        for envase_id in sorted(unidades_por_envase):
            envase = envases[envase_id]
            unidades = unidades_por_envase[envase_id]
            if envase.stock_unidades < unidades:
                raise ValidationError(
                    f"Stock insuficiente de envases '{envase.nombre}'. "
                    f"Disponible: {envase.stock_unidades}, requerido: {unidades}."
                )

        for envase_id in sorted(unidades_por_envase):
            envase = envases[envase_id]
            stock_anterior = envase.stock_unidades
            unidades = unidades_por_envase[envase_id]
            envase.stock_unidades -= unidades
            envase.save(update_fields=['stock_unidades'])
            MovimientoEnvase.objects.create(
                usuario=usuario,
                venta=self,
                envase=envase,
                tipo_movimiento=MovimientoEnvase.SALIDA,
                cantidad_unidades=unidades,
                stock_anterior=stock_anterior,
                stock_nuevo=envase.stock_unidades,
                motivo=f"Venta #{self.pk}",
            )

    def _procesar_devolucion_envases(self, usuario):
        unidades_por_envase = defaultdict(int)

        for detalle in DetalleVenta.objects.filter(venta=self).select_related('envase', 'producto'):
            envase_id = getattr(detalle, 'envase_id', None) or detalle.producto.envase_id
            if envase_id:
                unidades_por_envase[envase_id] += detalle.cantidad

        envases = {
            envase.pk: envase
            for envase in Envase.objects.select_for_update().filter(
                pk__in=unidades_por_envase.keys()
            ).order_by('pk')
        }

        for envase_id in sorted(unidades_por_envase):
            envase = envases[envase_id]
            stock_anterior = envase.stock_unidades
            unidades = unidades_por_envase[envase_id]
            envase.stock_unidades += unidades
            envase.save(update_fields=['stock_unidades'])
            MovimientoEnvase.objects.create(
                usuario=usuario,
                venta=self,
                envase=envase,
                tipo_movimiento=MovimientoEnvase.ENTRADA,
                cantidad_unidades=unidades,
                stock_anterior=stock_anterior,
                stock_nuevo=envase.stock_unidades,
                motivo=f"Reembolso Venta #{self.pk}",
            )

    @staticmethod
    def _repartir_kg(total_kg, cantidad_sabores):
        """
        Reparte total_kg en partes iguales (precisión de 1 g) entre los sabores.
        El resto de la división se suma a la primera parte, así la suma de las
        partes es siempre exactamente total_kg.
        """
        base = (total_kg / cantidad_sabores).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
        partes = [base] * cantidad_sabores
        partes[0] += total_kg - base * cantidad_sabores
        return partes

    def _procesar_salida_stock(self, usuario):
        """
        Descuenta el stock de los sabores de cada detalle. Los gramos del
        detalle se reparten entre sus sabores (un pote de 1 kg con 4 sabores
        descuenta 250 g de cada uno, no 1 kg de cada uno).
        """
        for detalle in self.detalles.select_related('producto').prefetch_related('sabores'):  # type: ignore[attr-defined]
            ids = sorted(sabor.pk for sabor in detalle.sabores.all())
            if not ids:
                continue

            # Usamos el snapshot guardado al vender; el producto puede haber cambiado.
            gramos = detalle.gramos_unitarios
            if gramos is None:
                gramos = detalle.producto.gramos
            total_kg = Decimal(gramos * detalle.cantidad) / Decimal(1000)
            partes = self._repartir_kg(total_kg, len(ids))

            # Se bloquean los sabores siempre en el mismo orden (pk) para evitar deadlocks.
            sabores = Sabor.objects.select_for_update().filter(pk__in=ids).order_by('pk')
            for sabor, kg in zip(sabores, partes):
                if kg <= 0:
                    continue
                if sabor.stock_kg < kg:
                    raise ValidationError(
                        f"Stock insuficiente para el sabor '{sabor.nombre}'. "
                        f"Se necesitan {kg} kg y hay {sabor.stock_kg} kg."
                    )
                sabor.stock_kg -= kg
                # Sabor.save registra el MovimientoStock (con venta y usuario).
                sabor.save(usuario=usuario, venta=self, motivo=f"Venta #{self.pk}")

    def _procesar_devolucion_stock(self, usuario):
        """
        Revierte exactamente lo que salió: por cada movimiento SALIDA de esta
        venta genera la ENTRADA correspondiente, sin recalcular nada.
        """
        salidas = self.movimientos_stock.filter(  # type: ignore[attr-defined]
            tipo_movimiento=MovimientoStock.SALIDA
        ).order_by('sabor_id', 'pk')

        for mov in salidas:
            sabor = Sabor.objects.select_for_update().get(pk=mov.sabor_id)
            sabor.stock_kg += mov.cantidad_kg
            sabor.save(usuario=usuario, venta=self, motivo=f"Reembolso Venta #{self.pk}")

    def calcular_total(self):
        """
        Recalcula el total a partir de los detalles. Usa un UPDATE directo
        (sin save()) porque es un dato derivado: no debe disparar validaciones,
        locks ni auditoría.
        """
        total = self.detalles.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')  # type: ignore[attr-defined]
        total = Decimal(total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        Venta.objects.filter(pk=self.pk).update(total=total)
        self.total = total

    @transaction.atomic
    def cambiar_estado(self, nuevo_estado, usuario=None):
        transiciones_validas = {
            self.PENDIENTE: [self.COMPLETADA, self.CANCELADA],
            self.COMPLETADA: [self.REEMBOLSADA],
            self.CANCELADA: [],
            self.REEMBOLSADA: [],
        }

        if nuevo_estado not in transiciones_validas.get(self.estado, []):
            raise ValidationError(
                f"Transición de estado inválida: no se puede pasar de '{self.estado}' a '{nuevo_estado}'."
            )

        # Delegamos el cambio y el procesamiento de stock al método save()
        self.estado = nuevo_estado
        self.save(usuario=usuario)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')
    envase = models.ForeignKey(
        Envase,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False,
        related_name='detalles_venta',
        help_text='Envase usado al crear el detalle; conserva el snapshot de la venta.',
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, default=None,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gramos_unitarios = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        editable=False,
    )
    sabores = models.ManyToManyField(
        Sabor,
        blank=True,
        related_name='detalles_venta',
        limit_choices_to={'disponible': True},
    )
    objects = DetalleVentaQuerySet.as_manager()

    def __str__(self):
        return f"Detalle #{self.pk} - {self.producto.nombre} (x{self.cantidad})"

    @staticmethod
    def validar_sabores(producto, sabores):
        sabores_seleccionados = list(sabores)

        if len(sabores_seleccionados) > producto.max_sabores:
            raise ValidationError(
                f"El producto {producto.nombre} permite un máximo de "
                f"{producto.max_sabores} sabores."
            )

        seleccionados = {getattr(sabor, 'pk', sabor) for sabor in sabores_seleccionados}
        permitidos = set(
            Sabor.objects.filter(pk__in=seleccionados, disponible=True).values_list('pk', flat=True)
        )
        if not seleccionados.issubset(permitidos):
            raise ValidationError(
                "Uno o más sabores seleccionados no están disponibles o no son válidos."
            )

    def clean(self):
        if self.pk:
            estado_en_db = Venta.objects.values_list('estado', flat=True).get(pk=self.venta.pk)
            # Incluimos REEMBOLSADA junto a COMPLETADA y CANCELADA
            if estado_en_db in {Venta.COMPLETADA, Venta.CANCELADA, Venta.REEMBOLSADA}:
                raise ValidationError(
                    "No se pueden modificar detalles de una venta que ya está completada, cancelada o reembolsada."
                )
            sabores_a_validar = self.sabores.all()
        else:
            if self.venta and self.venta.estado != Venta.PENDIENTE:
                raise ValidationError(
                    "No se pueden agregar detalles a una venta que no está pendiente."
                )
            return  

        self.validar_sabores(self.producto, sabores_a_validar)

    def save(self, *args, **kwargs):
        if self.venta and self.venta.estado == Venta.PENDIENTE:
            self.envase = self.producto.envase

        if self.pk:
            estado_en_db = Venta.objects.values_list('estado', flat=True).get(pk=self.venta.pk)
            if estado_en_db in {Venta.COMPLETADA, Venta.CANCELADA, Venta.REEMBOLSADA}:
                raise ValidationError(
                    "No se pueden modificar detalles de una venta que ya está completada, cancelada o reembolsada."
                )
        else:
            if self.venta and self.venta.estado != Venta.PENDIENTE:
                raise ValidationError(
                    "No se pueden agregar detalles a una venta que no está pendiente."
                )

        if self.precio_unitario is None:
            self.precio_unitario = self.producto.precio_base

        if self.gramos_unitarios is None:
            self.gramos_unitarios = self.producto.gramos

        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()

        subtotal = Decimal(self.cantidad) * self.precio_unitario
        self.subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pk:
            estado_en_db = Venta.objects.values_list('estado', flat=True).get(pk=self.venta.pk)
            if estado_en_db in {Venta.COMPLETADA, Venta.CANCELADA, Venta.REEMBOLSADA}:
                raise ValidationError(
                    "No se pueden eliminar detalles de una venta que ya está completada, cancelada o reembolsada."
                )
        return super().delete(*args, **kwargs)

class Auditoria(models.Model):
    ACCION_CREACION = 'CREACION'
    ACCION_ACTUALIZACION = 'ACTUALIZACION'
    ACCION_ELIMINACION = 'ELIMINACION'
    ACCION_ESTADO = 'ESTADO'
    ACCION_STOCK = 'STOCK'
    ACCION_LOGIN = 'LOGIN'
    ACCION_PERMISO = 'PERMISO'

    TIPO_ACCION = [
        (ACCION_CREACION, 'Creación'),
        (ACCION_ACTUALIZACION, 'Actualización'),
        (ACCION_ELIMINACION, 'Eliminación'),
        (ACCION_ESTADO, 'Cambio de estado'),
        (ACCION_STOCK, 'Cambio de stock'),
        (ACCION_LOGIN, 'Login'),
        (ACCION_PERMISO, 'Permiso'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    # Cambiamos a SET_NULL y permitimos nulos para conservar el historial aunque la venta se borre
    venta = models.ForeignKey(
        'Venta',
        related_name='auditorias',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20)
    motivo = models.CharField(max_length=255, blank=True)

    objects = AuditoriaQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "Auditorías"
        ordering = ['-timestamp']

    def __str__(self):
        venta_str = f"Venta #{self.venta.pk}" if self.venta else "Venta eliminada"
        return f"Auditoría #{self.pk} - {venta_str} ({self.estado_anterior} → {self.estado_nuevo})"

    def save(self, *args, **kwargs):
        # Una vez creado el registro de auditoría, es estrictamente inmutable
        if self.pk:
            raise ValidationError("Los registros de auditoría no pueden ser modificados.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("No se puede eliminar un registro de auditoría.")


class MovimientoEnvase(models.Model):
    ENTRADA = 'ENTRADA'
    SALIDA = 'SALIDA'

    TIPO_MOVIMIENTO = [
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    ]

    venta = models.ForeignKey(
        Venta,
        related_name='movimientos_envases',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    envase = models.ForeignKey(
        Envase,
        related_name='movimientos',
        on_delete=models.PROTECT,
    )
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad_unidades = models.PositiveIntegerField()
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=255, blank=True)
    objects = MovimientoEnvaseQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Movimientos de Envases'
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('Los movimientos de envases no pueden modificarse.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('No se puede eliminar un movimiento de envase.')

    def __str__(self):
        return (
            f"Movimiento #{self.pk} - {self.envase.nombre} "
            f"({self.tipo_movimiento}: {self.cantidad_unidades})"
        )


class MovimientoStock(models.Model):
    ENTRADA = 'ENTRADA'
    SALIDA = 'SALIDA'

    TIPO_MOVIMIENTO = [
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    ]

    venta = models.ForeignKey(
        Venta,
        related_name='movimientos_stock',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    sabor = models.ForeignKey(Sabor, on_delete=models.PROTECT)
    tipo_movimiento = models.CharField(
        max_length=20,
        choices=TIPO_MOVIMIENTO,
    )
    cantidad_kg = models.DecimalField(max_digits=10, decimal_places=3)
    stock_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=3,
    )
    stock_nuevo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
    )
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=255, blank=True)
    objects = MovimientoStockQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        # Una vez creado el registro de movimiento de stock, es estrictamente inmutable
        if self.pk:
            raise ValidationError("Los registros de movimientos de stock no pueden ser modificados.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("No se puede eliminar un movimiento de stock.")

    def __str__(self):
        return f"Movimiento #{self.pk} - {self.sabor.nombre} ({self.tipo_movimiento}: {self.cantidad_kg} kg)"