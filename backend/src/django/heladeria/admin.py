from django.contrib import admin
from .models import Proveedor, Empleado, Cliente, Categoria, Sabor, Producto, Venta, DetalleVenta


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'telefono', 'email', 'activo']
    list_filter   = ['activo']
    search_fields = ['nombre', 'email']


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'apellido', 'email', 'puesto']
    list_filter   = ['puesto']
    search_fields = ['nombre', 'apellido', 'email']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'apellido', 'email', 'telefono', 'socio']
    list_filter   = ['socio']
    search_fields = ['nombre', 'apellido', 'email']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ['nombre']
    search_fields = ['nombre']


@admin.register(Sabor)
class SaborAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'disponible', 'stock_kg', 'proveedor']
    list_filter   = ['disponible', 'proveedor']
    search_fields = ['nombre']


class DetalleVentaInline(admin.TabularInline):
    model  = DetalleVenta
    extra  = 1  # muestra 1 fila vacía para agregar un detalle nuevo
    fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'categoria', 'presentacion', 'precio', 'stock_unidades', 'activo']
    list_filter   = ['activo', 'categoria', 'presentacion']
    search_fields = ['nombre']
    filter_horizontal = ['sabores']  # widget cómodo para el ManyToMany


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'empleado', 'cliente', 'fecha', 'medio_pago', 'estado', 'total']
    list_filter   = ['estado', 'medio_pago', 'fecha']
    search_fields = ['empleado__nombre', 'cliente__nombre']
    readonly_fields = ['fecha', 'total']
    inlines       = [DetalleVentaInline]  # muestra los detalles dentro de la venta


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display  = ['venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']