from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from .models import Cliente, DetalleVenta, Empleado, Producto, Sabor, Venta
from .serializers import (
    ClienteSerializer, DetalleVentaSerializer, EmpleadoSerializer,
    ProductoSerializer, SaborSerializer, VentaSerializer,
)


class EmpleadoList(generics.ListCreateAPIView):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.AllowAny]

class EmpleadoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.AllowAny]


class ClienteList(generics.ListCreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.AllowAny]

class ClienteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.AllowAny]


class SaborList(generics.ListCreateAPIView):
    queryset = Sabor.objects.all()
    serializer_class = SaborSerializer
    permission_classes = [permissions.AllowAny]

class SaborDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sabor.objects.all()
    serializer_class = SaborSerializer
    permission_classes = [permissions.AllowAny]


class ProductoList(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

class ProductoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]


class VentaList(generics.ListCreateAPIView):
    # Optimiza consultas con select_related para evitar el problema N+1.
    queryset = Venta.objects.select_related('cliente', 'empleado').prefetch_related(
        'detalles__producto', 'detalles__sabores'
    ).all()
    serializer_class = VentaSerializer
    permission_classes = [permissions.AllowAny]

class VentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Venta.objects.select_related('cliente', 'empleado').prefetch_related(
        'detalles__producto', 'detalles__sabores'
    ).all()
    serializer_class = VentaSerializer
    permission_classes = [permissions.AllowAny]

    def perform_destroy(self, instance):
        # Impide eliminar ventas completadas o canceladas.
        # El modelo también lo valida, pero este control da un error más claro a la API.
        if instance.estado in (Venta.COMPLETADA, Venta.CANCELADA):
            raise ValidationError(
                f"No se puede eliminar una venta con estado {instance.get_estado_display()}."
            )
        super().perform_destroy(instance)


class DetalleVentaList(generics.ListCreateAPIView):
    queryset = DetalleVenta.objects.select_related('venta', 'producto').prefetch_related('sabores').all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.AllowAny]

class DetalleVentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DetalleVenta.objects.select_related('venta', 'producto').prefetch_related('sabores').all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.AllowAny]

    def perform_destroy(self, instance):
        # Impide eliminar detalles de ventas completadas o canceladas.
        if instance.venta.estado in (Venta.COMPLETADA, Venta.CANCELADA):
            raise ValidationError(
                "No se pueden eliminar detalles de una venta completada o cancelada."
            )
        super().perform_destroy(instance)