from rest_framework import serializers
from .models import Categoria, Producto, Proveedor, Sabor, Cliente, Empleado, Venta, ItemVenta, ItemVentaSabor


class ApiSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    descripcion = serializers.CharField()
    anio = serializers.IntegerField()
    
    def validate_anio(self, value):
        if value < 1900 or value > 2100:
            raise serializers.ValidationError("El año debe estar entre 1900 y 2100")
        return value

'''
class ProveedorSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    email = serializers.EmailField()
    telefono = serializers.CharField()
    direccion = serializers.CharField()
    
    def validate_telefono(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("El teléfono debe tener al menos 10 caracteres")
        return value
    
    def validate_email(self, value):
        if "@" not in value:
            raise serializers.ValidationError("El email debe contener @")
        return value
    
    def validate_direccion(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("La dirección debe tener al menos 5 caracteres")
        return value
    
    def validate(self, data):
        if data['nombre'] == data['email']:
            raise serializers.ValidationError("El nombre y el email no pueden ser iguales")
        return data

'''
class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class SaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sabor
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'


class ItemVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVenta
        fields = '__all__'


class ItemVentaSaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVentaSabor
        fields = '__all__'
