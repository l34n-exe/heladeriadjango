from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.EmpleadoList.as_view()),
    path('empleados/<int:pk>/', views.EmpleadoDetail.as_view()),

    path('clientes/', views.ClienteList.as_view()),
    path('clientes/<int:pk>/', views.ClienteDetail.as_view()),

    path('sabores/', views.SaborList.as_view()),
    path('sabores/<int:pk>/', views.SaborDetail.as_view()),

    path('productos/', views.ProductoList.as_view()),
    path('productos/<int:pk>/', views.ProductoDetail.as_view()),

    path('ventas/', views.VentaList.as_view()),
    path('ventas/<int:pk>/', views.VentaDetail.as_view()),

    path('detalle-ventas/', views.DetalleVentaList.as_view()),
    path('detalle-ventas/<int:pk>/', views.DetalleVentaDetail.as_view()),
]