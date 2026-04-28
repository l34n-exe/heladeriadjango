from rest_framework import generics, permissions
from .models import Categoria, Producto, Proveedor, Sabor, Cliente, Empleado, Venta, DetalleVenta
from .serializers import (
    CategoriaSerializer, ProductoSerializer, ProveedorSerializer,
    SaborSerializer, ClienteSerializer, EmpleadoSerializer,
    VentaSerializer, DetalleVentaSerializer
)

class ProveedorList(generics.ListCreateAPIView):
    queryset         = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProveedorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClienteList(generics.ListCreateAPIView):
    queryset         = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClienteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmpleadoList(generics.ListCreateAPIView):
    queryset         = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmpleadoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.IsAuthenticated]


class SaborList(generics.ListCreateAPIView):
    queryset         = Sabor.objects.all()
    serializer_class = SaborSerializer
    permission_classes = [permissions.IsAuthenticated]

class SaborDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Sabor.objects.all()
    serializer_class = SaborSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductoList(generics.ListCreateAPIView):
    queryset         = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoriaList(generics.ListCreateAPIView):
    queryset         = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]


class VentaList(generics.ListCreateAPIView):
    queryset         = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]

class VentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]


class DetalleVentaList(generics.ListCreateAPIView):
    queryset         = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated]

class DetalleVentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset         = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated]