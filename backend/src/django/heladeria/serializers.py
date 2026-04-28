from rest_framework import serializers
from .models import Proveedor, Empleado, Cliente, Categoria, Sabor, Producto, Venta, DetalleVenta


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Proveedor
        fields = ['id', 'nombre', 'telefono', 'email', 'activo']


class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Empleado
        fields = ['id', 'nombre', 'apellido', 'email', 'telefono', 'direccion', 'puesto']


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Cliente
        fields = ['id', 'nombre', 'apellido', 'email', 'telefono', 'direccion', 'socio']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Categoria
        fields = ['id', 'nombre']


class SaborSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)

    class Meta:
        model  = Sabor
        fields = ['id', 'nombre', 'descripcion', 'disponible', 'stock_kg', 'proveedor', 'proveedor_nombre']

    def validate_stock_kg(self, value):
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value


class ProductoSerializer(serializers.ModelSerializer):
    sabores          = SaborSerializer(many=True, read_only=True)
    sabores_ids      = serializers.PrimaryKeyRelatedField(
                           queryset=Sabor.objects.all(), many=True,
                           write_only=True, source='sabores'
                       )
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model  = Producto
        fields = [
            'id', 'nombre', 'categoria', 'categoria_nombre',
            'presentacion', 'precio', 'sabores', 'sabores_ids',
            'stock_unidades', 'activo'
        ]

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a cero.')
        return value

    def validate_stock_unidades(self, value):
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model  = DetalleVenta
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['precio_unitario', 'subtotal']

    # Validación para asegurar que la cantidad sea positiva, el producto esté activo y haya stock suficiente
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a cero.')
        return value
    
    # Validación para asegurar que el producto esté activo y haya stock suficiente
    def validate(self, data):
        producto = data.get('producto')
        cantidad = data.get('cantidad')

        if producto and not producto.activo:
            raise serializers.ValidationError(
                {'producto': f'El producto "{producto.nombre}" no está activo.'}
            )
        if producto and cantidad and not producto.tiene_stock(float(cantidad)):
            raise serializers.ValidationError(
                {'cantidad': f'Stock insuficiente. Disponible: {producto.stock_unidades} unidades.'}
            )
        return data

class VentaSerializer(serializers.ModelSerializer):
    detalles        = DetalleVentaSerializer(many=True)
    empleado_nombre = serializers.CharField(source='empleado.nombre', read_only=True)
    cliente_nombre  = serializers.CharField(source='cliente.nombre', read_only=True)

    class Meta:
        model  = Venta
        fields = [
            'id', 'empleado', 'empleado_nombre', 'cliente', 'cliente_nombre',
            'fecha', 'medio_pago', 'estado', 'total', 'detalles'
        ]
        read_only_fields = ['fecha', 'total']
    
    # Validar que el empleado tenga permiso para registrar ventas
    def validate_empleado(self, value):
        if not value.puede_realizar_ventas():
            raise serializers.ValidationError(
                f'{value} tiene puesto "{value.get_puesto_display()}" y no puede registrar ventas.'
            )
        return value
    
    # Validar que no se puedan modificar ventas anuladas
    def validate(self, data):
        if self.instance and self.instance.estado == Venta.Estados.ANULADA:
            raise serializers.ValidationError('No se puede modificar una venta anulada.')
        return data
    
    # Al crear una venta, se deben crear también los detalles y calcular el total
    def create(self, validated_data):
        # Extraemos los detalles del diccionario validado
        detalles_data = validated_data.pop('detalles')

        # Validamos que haya al menos un detalle
        if not detalles_data:
            raise serializers.ValidationError({'detalles': 'La venta debe tener al menos un producto.'})
        
        # Creamos la venta sin los detalles primero
        venta = Venta.objects.create(**validated_data)

        # Creamos cada detalle asociado a la venta
        for detalle_data in detalles_data:
            DetalleVenta.objects.create(venta=venta, **detalle_data)

        # calcular_total() ya se llama desde DetalleVenta.save() pero lo refrescamos para devolver el valor actualizado
        venta.refresh_from_db()
        return venta
    
    # Al actualizar una venta, no se pueden modificar los detalles desde esta vista, solo los campos de la venta
    def update(self, instance, validated_data):
        validated_data.pop('detalles', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance