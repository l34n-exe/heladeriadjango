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

    def validate(self, attrs):
        if self.instance is None and attrs.get('estado', Venta.PENDIENTE) != Venta.PENDIENTE:
            raise serializers.ValidationError(
                'Una venta nueva debe comenzar en estado pendiente.'
            )
        return attrs


class DetalleVentaSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    def validate(self, attrs):
        venta = attrs.get('venta', getattr(self.instance, 'venta', None))
        producto = attrs.get('producto', getattr(self.instance, 'producto', None))
        sabores = attrs.get('sabores', None)

        if venta and venta.estado != Venta.PENDIENTE:
            raise serializers.ValidationError(
                'Solo se pueden modificar detalles de una venta pendiente.'
            )

        if producto and sabores is not None:
            if len(sabores) > producto.max_sabores:
                raise serializers.ValidationError(
                    f'El producto {producto.nombre} permite un máximo de '
                    f'{producto.max_sabores} sabores.'
                )

            permitidos = set(
                producto.sabores_disponibles.filter(disponible=True).values_list('pk', flat=True)
            )
            if not {sabor.pk for sabor in sabores}.issubset(permitidos):
                raise serializers.ValidationError(
                    'Uno o más sabores seleccionados no están disponibles para este producto.'
                )

        return attrs

    class Meta:
        model = DetalleVenta
        fields = '__all__'
        read_only_fields = ['subtotal', 'gramos_unitarios']

