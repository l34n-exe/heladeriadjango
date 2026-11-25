from rest_framework.routers import DefaultRouter

from .views import (
    AuditoriaViewSet,
    ClienteViewSet,
    DetalleVentaViewSet,
    EmpleadoViewSet,
    MovimientoStockViewSet,
    ProductoViewSet,
    SaborViewSet,
    VentaViewSet,
    EnvaseViewSet, MovimientoEnvaseViewSet,
)

router = DefaultRouter()

router.register('empleados', EmpleadoViewSet, basename='empleado')
router.register('clientes', ClienteViewSet, basename='cliente')
router.register('sabores', SaborViewSet, basename='sabor')
router.register('productos', ProductoViewSet, basename='producto')
router.register('ventas', VentaViewSet, basename='venta')
router.register(
    'detalle-ventas',
    DetalleVentaViewSet,
    basename='detalle-venta',
)
router.register(
    'auditorias',
    AuditoriaViewSet,
    basename='auditoria',
)
router.register(
    'movimientos-stock',
    MovimientoStockViewSet,
    basename='movimiento-stock',
)
router.register(
    'envases',
    EnvaseViewSet,
    basename='envase',
)
router.register(
    'movimientos-envases',
    MovimientoEnvaseViewSet,
    basename='movimiento-envase',
)

urlpatterns = router.urls