from django.urls import path
from .views import (
    ProveedorList, ProveedorDetail,
    ClienteList, ClienteDetail,
    EmpleadoList, EmpleadoDetail,
    SaborList, SaborDetail,
    ProductoList, ProductoDetail,
    CategoriaList, CategoriaDetail,
    VentaList, VentaDetail,
    DetalleVentaList, DetalleVentaDetail
)

urlpatterns = [
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
    
    # URLs del Detalle de las Ventas (Items)
    path('detalles/', DetalleVentaList.as_view()), 
    path('detalles/<int:id>/', DetalleVentaDetail.as_view()), 
    
    

]