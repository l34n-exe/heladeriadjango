from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from .models import (
    Empleado, Cliente, Sabor, Producto, Venta, DetalleVenta,
    Auditoria, MovimientoStock, MovimientoEnvase, Envase,
)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'puesto')
    search_fields = ('nombre', 'apellido', 'email', 'puesto')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'es_socio', 'puntos_acumulados')
    search_fields = ('nombre', 'apellido', 'email')
    readonly_fields = ('puntos_acumulados',)

@admin.register(Sabor)
class SaborAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'stock_kg', 'disponible')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'disponible')

    def save_model(self, request, obj, form, change):
        obj.save(usuario=request.user)


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('subtotal', 'gramos_unitarios')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'tipo_producto',
        'envase',
        'precio_base',
    )
    list_filter = ('activo', 'envase')
    search_fields = ('nombre', 'tipo_producto')
    list_filter = ('tipo_producto',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fecha_venta', 'cliente', 'empleado', 'estado', 'total',
        'metodo_pago', 'descuento_aplicado', 'puntos_canjeados',
        'puntos_otorgados',
    )
    search_fields = ('id', 'cliente__nombre', 'cliente__apellido', 'empleado__nombre', 'empleado__apellido')
    list_filter = ('fecha_venta', 'estado', 'metodo_pago')
    readonly_fields = ('fecha_venta', 'total')
    inlines = [DetalleVentaInline]

    def get_queryset(self, request):
        # Optimización: Evita N+1 queries trayendo cliente y empleado en la misma consulta
        qs = super().get_queryset(request)
        return qs.select_related('cliente', 'empleado')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado in {self.model.COMPLETADA, self.model.CANCELADA}:
            return [field.name for field in self.model._meta.fields]
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        obj.save(usuario=request.user)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('venta__id', 'producto__nombre')
    list_filter = ('producto__tipo_producto',)
    filter_horizontal = ('sabores',)
    readonly_fields = ('subtotal',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('venta', 'producto')


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'timestamp', 'usuario', 'venta', 'estado_anterior', 'estado_nuevo', 'motivo')
    list_filter = ('timestamp', 'estado_nuevo')
    search_fields = ('motivo', 'usuario__username')
    readonly_fields = [field.name for field in Auditoria._meta.fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'venta')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('pk', 'fecha', 'sabor', 'tipo_movimiento', 'cantidad_kg', 'stock_nuevo', 'motivo', 'usuario')
    list_filter = ('tipo_movimiento', 'fecha', 'sabor')
    search_fields = ('sabor__nombre', 'usuario__username', 'motivo') 
    readonly_fields = [field.name for field in MovimientoStock._meta.fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sabor', 'usuario', 'venta')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Envase)
class EnvaseAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'stock_unidades',
        'stock_minimo',
    )
    search_fields = ('nombre',)


@admin.register(MovimientoEnvase)
class MovimientoEnvaseAdmin(admin.ModelAdmin):
    list_display = (
        'fecha', 'envase', 'tipo_movimiento', 'cantidad_unidades',
        'stock_anterior', 'stock_nuevo', 'venta', 'usuario',
    )
    list_filter = ('tipo_movimiento', 'fecha', 'envase')
    search_fields = ('envase__nombre', 'usuario__username', 'motivo')
    readonly_fields = [field.name for field in MovimientoEnvase._meta.fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('envase', 'usuario', 'venta')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False