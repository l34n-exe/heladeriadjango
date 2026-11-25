from rest_framework import permissions
from .models import Empleado

class EsGerente(permissions.BasePermission):
    """
    Permite acceso total únicamente si el usuario autenticado es un Empleado con puesto de GERENTE,
    o si es superusuario.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.empleado.puesto == Empleado.GERENTE
        except Empleado.DoesNotExist:
            return False


class EsCajeroOGerente(permissions.BasePermission):
    """
    Permite acceso tanto a cajeros como a gerentes (ideal para registrar ventas, listar productos y sabores).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.empleado.puesto in {Empleado.GERENTE, Empleado.CAJERO}
        except Empleado.DoesNotExist:
            return False


class SoloLecturaGerencial(permissions.BasePermission):
    """
    Permite auditorías y movimientos de stock solo para lectura exclusiva del Gerente.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            try:
                return request.user.empleado.puesto == Empleado.GERENTE
            except Empleado.DoesNotExist:
                return False
        return False

class EsCajeroLecturaOGerenteEscritura(permissions.BasePermission):
    """
    Permite lectura (GET, HEAD, OPTIONS) a cajeros y gerentes.
    Permite escritura (POST, PUT, PATCH, DELETE) únicamente a gerentes (o superusuarios).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            puesto = request.user.empleado.puesto
            if puesto == Empleado.GERENTE:
                return True
            if puesto == Empleado.CAJERO and request.method in permissions.SAFE_METHODS:
                return True
            return False
        except Empleado.DoesNotExist:
            return False