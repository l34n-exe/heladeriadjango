from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

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
    PUESTO = [
        ('GERENTE', 'Gerente'),
        ('CAJERO', 'Cajero'),
        ('LIMPIADOR', 'Limpiador')
    ]

    puesto = models.CharField(max_length=50, choices=PUESTO)
    fecha_contratacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.puesto}"
    
class Cliente(Persona):
    es_socio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {'Socio' if self.es_socio else 'No Socio'}"
    

class Sabor(models.Model):
    CATEGORIA_SABOR = [
        ('CHOCOLATE', 'Chocolate'),
        ('DULCE DE LECHE', 'Dulce de Leche'),
        ('FRUTAL', 'Frutal'),
        ('CREMA', 'Crema'),
        ('VEGANO', 'Vegano'),
        ('OTRO', 'Otro')
    ]
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_SABOR)
    stock_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    disponible = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.nombre} - {self.categoria}"
    

class Producto(models.Model):
    TIPO_PRODUCTO = [
        ('POTE 1 KG', 'Pote 1 KG'),
        ('POTE 1/2 KG', 'Pote 1/2 KG'),
        ('POTE 1/4 KG', 'Pote 1/4 KG'),
        ('BALDE', 'Balde'),
        ('MILKSHAKE', 'Milk Shake'),
        ('CUCURUCHO', 'Cucurucho'),
        ('VASO', 'Vaso'),
        ('POSTRE', 'Postre'),
        ('BOMBÓN', 'Bombón')
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    max_sabores = models.PositiveIntegerField(default=0)
    tipo_producto = models.CharField(max_length=50, choices=TIPO_PRODUCTO, default='POTE 1 KG')
    activo = models.BooleanField(default=True)
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.01'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    sabores_disponibles = models.ManyToManyField(Sabor, blank=True, related_name='productos', help_text='Sabores disponibles para este producto')


    def __str__(self):
        return f"{self.nombre} - {self.tipo_producto} - ${self.precio_base} - Max {self.max_sabores} sabores"
    
class Venta(models.Model):
    ESTADO_VENTA = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada')
    ]
    METODO_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia')
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_VENTA, default='PENDIENTE')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='ventas')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO, default='EFECTIVO')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        cliente_nombre = f"{self.cliente.nombre} {self.cliente.apellido}" if self.cliente else "Cliente anónimo"
        return f"Venta #{self.pk} - {cliente_nombre} - {self.metodo_pago} - ${self.total}"
    
    def calcular_total(self):
        total = self.detalles.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00') # type: ignore
        self.total = total
        self.save(update_fields=['total'])

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')    
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sabores = models.ManyToManyField(Sabor, blank=True, related_name='detalles_venta')

    def __str__(self):
        return f"Detalle #{self.pk} - {self.producto.nombre} - {self.cantidad}"

    def clean(self):
        # Validar que la cantidad de sabores no exceda el máximo permitido por el producto
        if self.producto.max_sabores > 0 and self.sabores.count() > self.producto.max_sabores:
            raise ValidationError(f"El producto {self.producto.nombre} permite un máximo de {self.producto.max_sabores} sabores.")
        # Validar que los sabores seleccionados estén disponibles para el producto
        if self.producto.sabores_disponibles.exists():
            permitidos = set(self.producto.sabores_disponibles.values_list('id', flat=True))
            seleccionados = set(self.sabores.values_list('id', flat=True))
            
            if not seleccionados.issubset(permitidos):
                raise ValidationError("Uno o más sabores seleccionados no están disponibles para este producto.")
        
    def save(self, *args, **kwargs):
        # Si no se proporcionó precio_unitario, tomar precio_base del producto como fallback
        if self.precio_unitario is None:
            try:
                if self.producto and getattr(self.producto, 'precio_base', None) is not None:
                    self.precio_unitario = self.producto.precio_base
            except Exception:
                # En caso de referencia inconsistente, dejar precio_unitario como None y manejar abajo
                pass

        # Validar y calcular subtotal automáticamente al guardar
        self.full_clean()  # Llamar a clean() para validar antes de guardar

        if self.precio_unitario is None:
            # Si aún no hay precio, usamos 0.00 para evitar errores y marcar el subtotal
            self.subtotal = Decimal('0.00')
        else:
            self.subtotal = self.cantidad * self.precio_unitario

        super().save(*args, **kwargs)