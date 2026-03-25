from django.contrib import admin
from .models import Categoria, Producto, Proveedor, Sabor, Venta, ItemVenta, ItemVentaSabor, Cliente, Empleado

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Proveedor)
admin.site.register(Sabor)
admin.site.register(Venta)
admin.site.register(ItemVenta)
admin.site.register(ItemVentaSabor)
admin.site.register(Cliente)
admin.site.register(Empleado)

