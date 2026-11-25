from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Empleado, Cliente, Sabor, Producto, Venta, DetalleVenta,
    Auditoria, MovimientoStock, MovimientoEnvase, Envase,
)
from .serializers import (
    EmpleadoSerializer, ClienteSerializer, SaborSerializer, 
    ProductoSerializer, VentaSerializer, DetalleVentaSerializer, 
    AuditoriaSerializer, MovimientoStockSerializer,
    MovimientoEnvaseSerializer, EnvaseSerializer,
)
from .permissions import EsGerente, EsCajeroOGerente, SoloLecturaGerencial, EsCajeroLecturaOGerenteEscritura


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [EsGerente]  # Solo los gerentes administran empleados


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [EsCajeroOGerente]  # Cajeros y gerentes gestionan clientes


class SaborViewSet(viewsets.ModelViewSet):
    queryset = Sabor.objects.all()
    serializer_class = SaborSerializer
    permission_classes = [EsCajeroLecturaOGerenteEscritura]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [EsCajeroLecturaOGerenteEscritura]

class EnvaseViewSet(viewsets.ModelViewSet):
    queryset = Envase.objects.all()
    serializer_class = EnvaseSerializer
    permission_classes = [EsCajeroLecturaOGerenteEscritura]

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [EsCajeroOGerente]

    def perform_create(self, serializer):
        # Asignamos el empleado logueado automáticamente si existe
        empleado = getattr(self.request.user, 'empleado', None)
        serializer.save(empleado=empleado)

    def _cambiar_estado(self, request, nuevo_estado):
        venta = self.get_object()
        venta.cambiar_estado(nuevo_estado, usuario=request.user)
        return Response(self.get_serializer(venta).data)

    @action(detail=True, methods=['post'], permission_classes=[EsCajeroOGerente])
    def completar(self, request, pk=None):
        return self._cambiar_estado(request, Venta.COMPLETADA)

    @action(detail=True, methods=['post'], permission_classes=[EsCajeroOGerente])
    def cancelar(self, request, pk=None):
        return self._cambiar_estado(request, Venta.CANCELADA)

    @action(detail=True, methods=['post'], permission_classes=[EsGerente])
    def reembolsar(self, request, pk=None):
        return self._cambiar_estado(request, Venta.REEMBOLSADA)


class DetalleVentaViewSet(viewsets.ReadOnlyModelViewSet):
    """Los detalles se crean y editan solo a través de la venta (VentaSerializer)."""
    queryset = DetalleVenta.objects.select_related('producto', 'venta').prefetch_related('sabores').order_by('-pk')
    serializer_class = DetalleVentaSerializer
    permission_classes = [EsCajeroOGerente]


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.select_related('usuario', 'venta').all()
    serializer_class = AuditoriaSerializer
    permission_classes = [SoloLecturaGerencial]


class MovimientoStockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoStock.objects.select_related('usuario', 'venta', 'sabor').all()
    serializer_class = MovimientoStockSerializer
    permission_classes = [SoloLecturaGerencial]


class MovimientoEnvaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoEnvase.objects.select_related('usuario', 'venta', 'envase').all()
    serializer_class = MovimientoEnvaseSerializer
    permission_classes = [SoloLecturaGerencial]