from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from .models import (
    Empleado, Cliente, Sabor, Producto, Venta, DetalleVenta,
    Auditoria, MovimientoStock, MovimientoEnvase, Envase,
)

class EmpleadoSerializer(serializers.ModelSerializer):
    fecha_contratacion = serializers.DateField(required=False)

    class Meta:
        model = Empleado
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['puntos_acumulados']


class SaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sabor
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class EnvaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envase
        fields = '__all__' 

class DetalleVentaSerializer(serializers.ModelSerializer):
    # Validamos explícitamente los IDs de sabores entrantes
    sabores = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Sabor.objects.all(),
        error_messages={'does_not_exist': 'Uno o más IDs de sabores proporcionados no existen.'}
    )
    cantidad = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'La cantidad debe ser mayor o igual a 1.',
            'invalid': 'La cantidad debe ser un número entero válido.'
        }
    )

    class Meta:
        model = DetalleVenta
        fields = ['id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal', 'gramos_unitarios', 'sabores']
        read_only_fields = ['venta', 'subtotal', 'gramos_unitarios', 'precio_unitario']

    def validate(self, data):
        producto = data.get('producto')
        sabores = data.get('sabores', [])

        # 1. Validar que el producto esté activo
        if producto and not producto.activo:
            raise serializers.ValidationError({'producto': 'El producto seleccionado no está activo o disponible para la venta.'})

        # 2. Validar sabores duplicados en el mismo ítem
        sabor_ids = [s.id for s in sabores]
        if len(sabor_ids) != len(set(sabor_ids)):
            raise serializers.ValidationError({'sabores': 'No se pueden repetir sabores dentro de un mismo detalle de venta.'})

        # 3. Validar límite máximo de sabores permitidos por el producto
        if producto and len(sabores) > producto.max_sabores:
            raise serializers.ValidationError({
                'sabores': f'El producto "{producto.nombre}" permite un máximo de {producto.max_sabores} sabores (se seleccionaron {len(sabores)}).'
            })

        # 4. Validar stock del envase necesario para el detalle
        if producto and producto.envase_id:
            cantidad = data.get('cantidad', getattr(self.instance, 'cantidad', 1))
            envase = producto.envase
            unidades_requeridas = cantidad
            if envase.stock_unidades < unidades_requeridas:
                raise serializers.ValidationError({
                    'producto': (
                        f'Stock insuficiente de envases "{envase.nombre}". '
                        f'Disponible: {envase.stock_unidades}, '
                        f'requerido: {unidades_requeridas}.'
                    )
                })

        # 5. Validar disponibilidad de cada sabor
        no_disponibles = [s.nombre for s in sabores if not s.disponible]
        if no_disponibles:
            raise serializers.ValidationError({
                'sabores': f'Los siguientes sabores no están disponibles actualmente: {", ".join(no_disponibles)}'
            })

        return data

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, allow_empty=False)
    puntos_canjeados = serializers.IntegerField(min_value=0, required=False)
    empleado_nombre = serializers.CharField(source='empleado.__str__', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.__str__', read_only=True, allow_null=True)

    class Meta:
        model = Venta
        fields = [
            'id', 'estado', 'cliente', 'cliente_nombre', 'empleado',
            'empleado_nombre', 'metodo_pago', 'fecha_venta', 'total',
            'descuento_aplicado', 'puntos_canjeados', 'puntos_otorgados',
            'detalles',
        ]
        read_only_fields = [
            'estado', 'fecha_venta', 'total', 'empleado',
            'descuento_aplicado', 'puntos_otorgados',
        ]

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError('La venta debe incluir al menos un detalle de producto.')
        return value

    def validate_puntos_canjeados(self, value):
        if value % Venta.PUNTOS_POR_CANJE != 0:
            raise serializers.ValidationError(
                f'Los puntos se canjean en bloques de {Venta.PUNTOS_POR_CANJE}.'
            )
        return value

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        
        try:
            with transaction.atomic():
                venta = Venta.objects.create(**validated_data)

                for detalle_data in detalles_data:
                    sabores_data = detalle_data.pop('sabores', [])
                    detalle = DetalleVenta.objects.create(venta=venta, **detalle_data)
                    if sabores_data:
                        detalle.sabores.set(sabores_data)

                venta.calcular_total()
            return venta
            
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                raise serializers.ValidationError(e.message_dict)
            raise serializers.ValidationError({'non_field_errors': e.messages if hasattr(e, 'messages') else str(e)})

    def update(self, instance, validated_data):
        # 1. Regla de negocio: No se puede modificar una venta que ya no está pendiente
        if instance.estado != Venta.PENDIENTE:
            raise serializers.ValidationError(
                {'estado': 'No se pueden modificar los datos o ítems de una venta que ya ha sido completada, cancelada o reembolsada.'}
            )

        detalles_data = validated_data.pop('detalles', None)

        try:
            with transaction.atomic():
                # Actualizar campos básicos de la venta (ej. cliente, método de pago)
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()

                # 2. Si se envían nuevos detalles, reemplazamos los anteriores de forma segura
                if detalles_data is not None:
                    instance.detalles.all().delete()
                    for detalle_data in detalles_data:
                        sabores_data = detalle_data.pop('sabores', [])
                        detalle = DetalleVenta.objects.create(venta=instance, **detalle_data)
                        if sabores_data:
                            detalle.sabores.set(sabores_data)

                # 3. Recalcular el total de la venta de forma atómica
                instance.calcular_total()
            return instance

        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                raise serializers.ValidationError(e.message_dict)
            raise serializers.ValidationError({'non_field_errors': e.messages if hasattr(e, 'messages') else str(e)})

class AuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Auditoria
        fields = ['id', 'timestamp', 'usuario', 'usuario_nombre', 'venta', 'estado_anterior', 'estado_nuevo', 'motivo']
        read_only_fields = ['id', 'timestamp', 'usuario', 'venta', 'estado_anterior', 'estado_nuevo', 'motivo']


class MovimientoEnvaseSerializer(serializers.ModelSerializer):
    envase_nombre = serializers.CharField(source='envase.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True, allow_null=True)

    class Meta:
        model = MovimientoEnvase
        fields = [
            'id', 'venta', 'usuario', 'usuario_nombre', 'envase',
            'envase_nombre', 'tipo_movimiento', 'cantidad_unidades',
            'stock_anterior', 'stock_nuevo', 'fecha', 'motivo',
        ]
        read_only_fields = fields


class MovimientoStockSerializer(serializers.ModelSerializer):
    sabor_nombre = serializers.CharField(source='sabor.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = MovimientoStock
        fields = [
            'id', 'venta', 'usuario', 'usuario_nombre', 'sabor', 
            'sabor_nombre', 'tipo_movimiento', 'cantidad_kg', 
            'stock_anterior', 'stock_nuevo', 'fecha', 'motivo'
        ]
        read_only_fields = [
            'id', 'venta', 'usuario', 'sabor', 'tipo_movimiento', 
            'cantidad_kg', 'stock_anterior', 'stock_nuevo', 'fecha', 'motivo'
        ]