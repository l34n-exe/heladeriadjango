from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import MinValueValidator


# Validadores reutilizables 

def validar_positivo(value):
    if value <= 0:
        raise ValidationError('El valor debe ser mayor a cero.')

def validar_no_negativo(value):
    if value < 0:
        raise ValidationError('El valor no puede ser negativo.')



class Proveedor(models.Model):
    nombre   = models.CharField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    email    = models.EmailField(blank=True)
    activo   = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    class Puestos(models.TextChoices):
        GERENTE  = 'gerente',  'Gerente'
        CAJERO   = 'cajero',   'Cajero'
        LIMPIEZA = 'limpieza', 'Limpieza'

    PUESTOS_CON_ACCESO_VENTA = [Puestos.GERENTE, Puestos.CAJERO]

    nombre    = models.CharField(max_length=100)
    apellido  = models.CharField(max_length=100)
    email     = models.EmailField(unique=True)
    telefono  = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    puesto    = models.CharField(max_length=20, choices=Puestos.choices)

    def puede_realizar_ventas(self):
        return self.puesto in self.PUESTOS_CON_ACCESO_VENTA

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Cliente(models.Model):
    nombre    = models.CharField(max_length=100)
    apellido  = models.CharField(max_length=100)
    email     = models.EmailField(unique=True)
    telefono  = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    socio     = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Categoria(models.Model):
    class Tipos(models.TextChoices):
        CREMA    = 'crema',    'Crema'
        AGUA     = 'agua',     'Agua'
        SIN_TACC = 'sin_tacc', 'Sin TACC'

    nombre = models.CharField(max_length=100, unique=True, choices=Tipos.choices)

    def __str__(self):
        return self.nombre


class Sabor(models.Model):
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    disponible  = models.BooleanField(default=True)
    stock_kg    = models.FloatField(default=0, validators=[validar_no_negativo])
    proveedor   = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='sabores')

    def __str__(self):
        return self.nombre
    
    # Validación para asegurar que el stock no sea negativo y actualizar la disponibilidad automáticamente
    def clean(self):
        if self.stock_kg < 0:
            raise ValidationError({'stock_kg': 'El stock no puede ser negativo.'})
        # Si el stock llega a 0 se marca como no disponible automáticamente
        if self.stock_kg == 0:
            self.disponible = False


class Producto(models.Model):
    class Presentacion(models.TextChoices):
        KILO      = 'kilo',      'Por kilo'
        MEDIO     = 'medio',     'Medio kilo'
        CUCURUCHO = 'cucurucho', 'Cucurucho'
        POTE      = 'pote',      'Pote'
        UNIDAD    = 'unidad',    'Unidad'

    nombre         = models.CharField(max_length=100, unique=True)
    categoria      = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    presentacion   = models.CharField(max_length=20, choices=Presentacion.choices)
    precio         = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    sabores        = models.ManyToManyField(Sabor, related_name='productos', blank=True)
    stock_unidades = models.FloatField(default=0, validators=[validar_no_negativo])
    activo         = models.BooleanField(default=True)
    
    # Validación para asegurar que el precio sea positivo y el stock no sea negativo
    def clean(self):
        if self.precio <= 0:
            raise ValidationError({'precio': 'El precio debe ser mayor a cero.'})
        if self.stock_unidades < 0:
            raise ValidationError({'stock_unidades': 'El stock no puede ser negativo.'})
    # Método para verificar si hay stock suficiente antes de realizar una venta
    def tiene_stock(self, cantidad):
        return self.stock_unidades >= cantidad

    def __str__(self):
        sabor = f'{self.sabores.first()} - ' if self.sabores.exists() else ''
        return f'{sabor}{self.nombre} ({self.get_presentacion_display()}) - ${self.precio}'  # type: ignore


class Venta(models.Model):
    class MedioPago(models.TextChoices):
        EFECTIVO      = 'efectivo',      'Efectivo'
        DEBITO        = 'debito',        'Débito'
        TRANSFERENCIA = 'transferencia', 'Transferencia / QR'

    class Estados(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PAGADA    = 'pagada',    'Pagada'
        ANULADA   = 'anulada',   'Anulada'

    empleado   = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='ventas')
    cliente    = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    fecha      = models.DateTimeField(auto_now_add=True)
    medio_pago = models.CharField(max_length=20, choices=MedioPago.choices, default=MedioPago.EFECTIVO)
    total      = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    estado     = models.CharField(max_length=20, choices=Estados.choices, default=Estados.PENDIENTE)

    # Validar que el empleado tenga permiso para registrar ventas
    def clean(self):
        if self.empleado_id and not self.empleado.puede_realizar_ventas(): # type: ignore
            raise ValidationError(
                f'El empleado {self.empleado} tiene puesto '
                f'"{self.empleado.get_puesto_display()}" y no puede registrar ventas.'
            )
    # Método para verificar si la venta está cerrada (pagada o anulada)
    def esta_cerrada(self):
        return self.estado == self.Estados.ANULADA
    
    # Método para calcular el total de la venta sumando los subtotales de los detalles
    def calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles.all()) # type: ignore
        self.save(update_fields=['total'])

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"  # type: ignore


class DetalleVenta(models.Model):
    venta           = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad        = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    
    # Validación para asegurar que la cantidad sea positiva, el producto esté activo y haya stock suficiente
    def clean(self):
        # No se puede agregar detalles a una venta cerrada
        if self.venta_id and self.venta.esta_cerrada(): # type: ignore
            raise ValidationError('No se pueden agregar detalles a una venta pagada o anulada.')

        # El producto debe estar activo
        if self.producto_id and not self.producto.activo: # type: ignore
            raise ValidationError({'producto': f'El producto "{self.producto.nombre}" no está activo.'})

        # Debe haber stock suficiente
        if self.producto_id and self.cantidad and not self.producto.tiene_stock(float(self.cantidad)): # type: ignore
            raise ValidationError(
                {'cantidad': f'Stock insuficiente. Disponible: {self.producto.stock_unidades} unidades.'}
            )
    # Al guardar el detalle, se actualiza el subtotal y se descuenta el stock del producto automáticamente
    def save(self, *args, **kwargs):
        self.full_clean()  # ejecuta clean() antes de guardar
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        self.subtotal = self.precio_unitario * self.cantidad

        # Descuenta el stock del producto automáticamente
        if not self.pk:  # solo al crear, no al editar
            self.producto.stock_unidades -= float(self.cantidad)
            self.producto.save(update_fields=['stock_unidades'])

        super().save(*args, **kwargs)

        # Recalcula el total de la venta cada vez que se guarda un detalle
        self.venta.calcular_total()

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad} = ${self.subtotal}'