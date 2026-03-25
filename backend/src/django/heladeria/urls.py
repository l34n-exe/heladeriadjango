from django.urls import path
from .views import (
    crear_categoria, listar_categorias, obtener_categoria, first_api, serial_v1,
    ProveedorList, ProveedorDetail,
    ClienteList, ClienteDetail,
    EmpleadoList, EmpleadoDetail,
    SaborList, SaborDetail,
    ProductoList, ProductoDetail,
    CategoriaList, CategoriaDetail,
    VentaList, VentaDetail,
    ItemVentaList, ItemVentaDetail,
    ItemVentaSaborList, ItemVentaSaborDetail
)

urlpatterns = [
    # URLs legacy (mantener por compatibilidad)
    path('crear_categoria/<str:nombre>/<str:tipo>/<str:descripcion>/', crear_categoria), 
    path('listar_categorias/', listar_categorias), 
    path('obtener_categoria/<int:id>/', obtener_categoria), 
    path('first_api/', first_api), 
    path('serial_v1/', serial_v1), 
    
    # URLs de Proveedores
    path('proveedores/', ProveedorList.as_view()), 
    path('proveedores/<int:id>/', ProveedorDetail.as_view()), 
    
    # URLs de Clientes
    path('clientes/', ClienteList.as_view()), 
    path('clientes/<int:id>/', ClienteDetail.as_view()), 
    
    # URLs de Empleados
    path('empleados/', EmpleadoList.as_view()), 
    path('empleados/<int:id>/', EmpleadoDetail.as_view()), 
    
    # URLs de Sabores
    path('sabores/', SaborList.as_view()), 
    path('sabores/<int:id>/', SaborDetail.as_view()), 
    
    # URLs de Productos
    path('productos/', ProductoList.as_view()), 
    path('productos/<int:id>/', ProductoDetail.as_view()), 
    
    # URLs de Categorías
    path('categorias/', CategoriaList.as_view()), 
    path('categorias/<int:id>/', CategoriaDetail.as_view()), 
    
    # URLs de Ventas
    path('ventas/', VentaList.as_view()), 
    path('ventas/<int:id>/', VentaDetail.as_view()), 
    
    # URLs de Items de Venta
    path('items-venta/', ItemVentaList.as_view()), 
    path('items-venta/<int:id>/', ItemVentaDetail.as_view()), 
    
    # URLs de Items de Venta Sabor
    path('items-venta-sabor/', ItemVentaSaborList.as_view()), 
    path('items-venta-sabor/<int:id>/', ItemVentaSaborDetail.as_view()), 
]