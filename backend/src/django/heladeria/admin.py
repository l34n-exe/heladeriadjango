from django.contrib import admin
from .models import Empleado, Cliente, Sabor, Producto, Venta, DetalleVenta

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'puesto')
    search_fields = ('nombre', 'apellido', 'email', 'puesto')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'es_socio')
    search_fields = ('nombre', 'apellido', 'email')

@admin.register(Sabor)
class SaborAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'stock_kg', 'disponible')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'disponible')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_producto', 'precio_base', 'max_sabores')
    search_fields = ('nombre', 'tipo_producto')
    list_filter = ('tipo_producto',)
    filter_horizontal = ('sabores_disponibles',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'cliente', 'empleado', 'estado', 'total')
    search_fields = ('id', 'cliente__nombre', 'cliente__apellido', 'empleado__nombre', 'empleado__apellido')
    list_filter = ('fecha_venta', 'estado', 'metodo_pago')
    readonly_fields = ('fecha_venta', 'total')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado in {self.model.COMPLETADA, self.model.CANCELADA}:
            return [field.name for field in self.model._meta.fields]
        return self.readonly_fields

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('venta__id', 'producto__nombre')
    list_filter = ('producto__tipo_producto',)
    filter_horizontal = ('sabores',)
    readonly_fields = ('subtotal',)

