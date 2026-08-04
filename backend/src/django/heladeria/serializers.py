from .models import Cliente, DetalleVenta, Empleado, Producto, Sabor, Venta
from rest_framework import serializers


class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class SaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sabor
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'
        read_only_fields = ['total', 'fecha_venta']


class DetalleVentaSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = DetalleVenta
        fields = '__all__'
        read_only_fields = ['subtotal']

