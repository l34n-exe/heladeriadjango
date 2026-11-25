from decimal import Decimal
from typing import cast
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework.response import Response
from django.contrib.auth import get_user_model


from .models import (
    DetalleVenta, Empleado, Producto, Sabor, Venta, Cliente,
    MovimientoStock, MovimientoEnvase, Envase,
)


class ApiAuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_productos_requiere_jwt(self):
        response = self.client.get('/heladerias/productos/')
        self.assertEqual(response.status_code, 401)

    def test_usuario_autenticado_puede_listar_productos(self):
        usuario = User.objects.create_user(username='api-user', password='test-password')
        # Vinculamos un empleado con puesto CAJERO para que cumpla con EsCajeroOGerente
        Empleado.objects.create(
            nombre='Cajero', apellido='Test', email='cajero@test.com',
            puesto=Empleado.CAJERO, user=usuario
        )
        
        client = APIClient()
        client.force_authenticate(user=usuario)

        response = cast(Response, client.get('/heladerias/productos/'))

        self.assertEqual(response.status_code, 200)

    def test_crear_empleado_devuelve_fecha_de_contratacion_valida(self):
        usuario = User.objects.create_user(
            username='employee-api-user',
            password='test-password',
            is_staff=True,
        )
        # Vinculamos un empleado con puesto GERENTE para que cumpla con EsGerente
        Empleado.objects.create(
            nombre='Gerente', apellido='Test', email='gerente@test.com',
            puesto=Empleado.GERENTE, user=usuario
        )

        client = APIClient()
        client.force_authenticate(user=usuario)

        response = cast(Response, client.post(
            '/heladerias/empleados/',
            {
                'nombre': 'Juan',
                'apellido': 'Perez',
                'email': 'juan-test@example.com',
                'puesto': Empleado.CAJERO,
            },
            format='json',
        ))

        self.assertEqual(response.status_code, 201)
        response_data = cast(dict[str, object], response.data)
        self.assertRegex(cast(str, response_data['fecha_contratacion']), r'^\d{4}-\d{2}-\d{2}$')

    def test_usuario_autenticado_sin_staff_no_puede_escribir(self):
        usuario = User.objects.create_user(username='read-only-user', password='test-password')
        client = APIClient()
        client.force_authenticate(user=usuario)

        response = client.post(
            '/heladerias/empleados/',
            {
                'nombre': 'No',
                'apellido': 'Autorizado',
                'email': 'no-autorizado@example.com',
                'puesto': Empleado.CAJERO,
            },
            format='json',
        )

        response = cast(Response, response)
        self.assertEqual(response.status_code, 403)


class VentaIntegrityTests(TestCase):
    def setUp(self):
        self.empleado = Empleado.objects.create(
            nombre='Ana',
            apellido='Gomez',
            email='ana@example.com',
            puesto=Empleado.CAJERO,
        )
        self.sabor = Sabor.objects.create(
            nombre='Chocolate',
            categoria=Sabor.CHOCOLATE,
            stock_kg=Decimal('2.000'),
            disponible=True,
        )
        self.producto = Producto.objects.create(
            nombre='Pote',
            tipo_producto=Producto.POTE_1KG,
            max_sabores=1,
            precio_base=Decimal('100.00'),
            gramos=1000,
        )

    def crear_venta_con_detalle(self):
        venta = Venta.objects.create(empleado=self.empleado)
        detalle = DetalleVenta.objects.create(venta=venta, producto=self.producto)
        detalle.sabores.add(self.sabor)
        return venta, detalle

    def test_completar_descuenta_stock_y_no_permite_volver_a_pendiente(self):
        venta, _ = self.crear_venta_con_detalle()

        venta.estado = Venta.COMPLETADA
        venta.save()
        self.sabor.refresh_from_db()
        self.assertEqual(self.sabor.stock_kg, Decimal('1.000'))

        venta.estado = Venta.PENDIENTE
        with self.assertRaises(ValidationError):
            venta.save()

    def test_no_se_puede_crear_venta_completada_sin_detalles(self):
        with self.assertRaises(ValidationError):
            Venta.objects.create(empleado=self.empleado, estado=Venta.COMPLETADA)

    def test_defaults_del_producto_se_aplican_por_tipo(self):
        producto = Producto.objects.create(
            nombre='Pote de medio kilo',
            tipo_producto=Producto.POTE_500G,
            precio_base=Decimal('50.00'),
        )

        self.assertEqual(producto.gramos, 500)
        self.assertEqual(producto.max_sabores, 3)

    def test_borrado_masivo_no_elimina_ventas_cerradas(self):
        venta, _ = self.crear_venta_con_detalle()
        venta.estado = Venta.COMPLETADA
        venta.save()

        with self.assertRaises(ValidationError):
            Venta.objects.filter(pk=venta.pk).delete()

    def test_reembolsar_devuelve_stock_y_bloquea_detalles(self):
        venta, detalle = self.crear_venta_con_detalle()
        venta.estado = Venta.COMPLETADA
        venta.save()
        
        # Una venta completada se reembolsa (no se cancela)
        venta.estado = Venta.REEMBOLSADA
        venta.save()

        self.sabor.refresh_from_db()
        self.assertEqual(self.sabor.stock_kg, Decimal('2.000'))

        detalle.cantidad = 2
        with self.assertRaises(ValidationError):
            detalle.save()
        with self.assertRaises(ValidationError):
            detalle.delete()

    def test_detalle_rechaza_sabor_no_disponible_para_el_producto(self):
        otro_sabor = Sabor.objects.create(
            nombre='Frutilla',
            categoria=Sabor.FRUTAL,
            disponible=False,
        )
        venta = Venta.objects.create(empleado=self.empleado)
        detalle = DetalleVenta.objects.create(venta=venta, producto=self.producto)

        with self.assertRaises(ValidationError):
            detalle.sabores.set([otro_sabor])

    def test_producto_sin_maximo_de_sabores_no_acepta_sabores(self):
        producto = Producto.objects.create(
            nombre='Postre',
            tipo_producto=Producto.POSTRE,
            max_sabores=0,
            precio_base=Decimal('100.00'),
        )
        venta = Venta.objects.create(empleado=self.empleado)
        detalle = DetalleVenta.objects.create(venta=venta, producto=producto)

        with self.assertRaises(ValidationError):
            detalle.sabores.set([self.sabor])


class VentaStockTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cajero1', password='password123')
        self.empleado = Empleado.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan@heladeria.com',
            puesto=Empleado.CAJERO,
            user=self.user
        )
        self.cliente = Cliente.objects.create(
            nombre='María',
            apellido='Gómez',
            email='maria@cliente.com'
        )
        self.sabor = Sabor.objects.create(
            nombre='Frutilla al Agua',
            categoria=Sabor.FRUTAL,
            stock_kg=Decimal('5.000'),
            disponible=True
        )
        self.producto = Producto.objects.create(
            nombre='Pote 1 KG',
            tipo_producto=Producto.POTE_1KG,
            gramos=1000,
            max_sabores=2,
            precio_base=Decimal('5000.00'),
            activo=True
        )

    def test_venta_exitosa_descuenta_stock(self):
        venta = Venta.objects.create(
            empleado=self.empleado,
            cliente=self.cliente,
            metodo_pago=Venta.EFECTIVO,
            estado=Venta.PENDIENTE
        )
        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=1
        )
        detalle.sabores.add(self.sabor)
        venta.calcular_total()
        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        self.sabor.refresh_from_db()
        self.assertEqual(self.sabor.stock_kg, Decimal('4.000'))

        movimiento = MovimientoStock.objects.filter(
            sabor=self.sabor, 
            tipo_movimiento=MovimientoStock.SALIDA
        ).first()
        self.assertIsNotNone(movimiento)
        self.assertEqual(movimiento.cantidad_kg, Decimal('1.000'))  # type: ignore[union-attr]

    def test_stock_insuficiente_lanza_error(self):
        self.producto.gramos = 6000
        self.producto.save()

        venta = Venta.objects.create(
            empleado=self.empleado,
            metodo_pago=Venta.EFECTIVO,
            estado=Venta.PENDIENTE
        )
        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=1
        )
        detalle.sabores.add(self.sabor)

        with self.assertRaises(ValidationError):
            venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        self.sabor.refresh_from_db()
        self.assertEqual(self.sabor.stock_kg, Decimal('5.000'))

    def test_reembolsar_venta_devuelve_stock(self):
        """Verifica que al reembolsar una venta completada, el stock se devuelva automáticamente."""
        venta = Venta.objects.create(
            empleado=self.empleado,
            metodo_pago=Venta.EFECTIVO,
            estado=Venta.PENDIENTE
        )
        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=1
        )
        detalle.sabores.add(self.sabor)
        
        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)
        self.sabor.refresh_from_db()
        self.assertEqual(self.sabor.stock_kg, Decimal('4.000'))

        # Cambiamos a REEMBOLSADA
        venta.cambiar_estado(Venta.REEMBOLSADA, usuario=self.user)
        self.sabor.refresh_from_db()
        self.assertEqual(self.sabor.stock_kg, Decimal('5.000'))

        movimiento_entrada = MovimientoStock.objects.filter(
            sabor=self.sabor, 
            tipo_movimiento=MovimientoStock.ENTRADA
        ).last()
        self.assertIsNotNone(movimiento_entrada)
        self.assertEqual(movimiento_entrada.cantidad_kg, Decimal('1.000'))  # type: ignore[union-attr]

class StockVentaTests(TestCase):
    """Cubre la salida de stock al completar una venta y su reversión al reembolsar."""

    def setUp(self):
        self.user = get_user_model().objects.create_user('cajera', password='x')  # type: ignore
        self.empleado = Empleado.objects.create(
            nombre='Ana', apellido='Pérez', email='ana@example.com',
            puesto=Empleado.CAJERO, user=self.user,
        )
        # POTE_1KG toma por defecto 1000 g y 4 sabores máximo (ver Producto.save)
        self.pote = Producto.objects.create(
            nombre='Pote 1 kg', tipo_producto=Producto.POTE_1KG, precio_base=Decimal('10000.00'),
        )

    # --- helpers -------------------------------------------------------------

    def crear_sabores(self, cantidad, stock='10.000'):
        return [
            Sabor.objects.create(
                nombre=f'Sabor {i}', categoria=Sabor.CREMA, stock_kg=Decimal(stock),
            )
            for i in range(1, cantidad + 1)
        ]

    def crear_venta(self, sabores, producto=None, cantidad=1):
        venta = Venta.objects.create(empleado=self.empleado)
        detalle = DetalleVenta.objects.create(
            venta=venta, producto=producto or self.pote, cantidad=cantidad,
        )
        detalle.sabores.set(sabores)
        return venta

    def stock(self, sabor):
        sabor.refresh_from_db()
        return sabor.stock_kg

    # --- tests ---------------------------------------------------------------

    def test_completar_venta_genera_un_solo_movimiento_por_sabor(self):
        sabores = self.crear_sabores(2)

        venta = self.crear_venta(sabores)
        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        for sabor in sabores:
            movimientos = MovimientoStock.objects.filter(sabor=sabor)
            self.assertEqual(movimientos.count(), 1)
            mov = movimientos.get()
            self.assertEqual(mov.tipo_movimiento, MovimientoStock.SALIDA)
            self.assertEqual(mov.venta, venta)
            self.assertEqual(mov.usuario, self.user)
            self.assertEqual(mov.stock_anterior - mov.stock_nuevo, mov.cantidad_kg)
        self.assertFalse(MovimientoStock.objects.filter(motivo__icontains='merma').exists())

    def test_los_gramos_se_reparten_entre_los_sabores(self):
        sabores = self.crear_sabores(4)

        venta = self.crear_venta(sabores)  # pote de 1 kg con 4 sabores
        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        for sabor in sabores:
            self.assertEqual(self.stock(sabor), Decimal('9.750'))  # 250 g de cada uno

    def test_el_reparto_no_pierde_gramos_cuando_no_es_exacto(self):
        sabores = self.crear_sabores(3)

        venta = self.crear_venta(sabores)  # 1000 g / 3 sabores
        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        descontado = sum(Decimal('10.000') - self.stock(s) for s in sabores)
        self.assertEqual(descontado, Decimal('1.000'))

    def test_reembolso_devuelve_exactamente_lo_que_salio(self):
        sabores = self.crear_sabores(3)
        venta = self.crear_venta(sabores, cantidad=2)
        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        # El producto cambia de gramaje después de vender: el reembolso no debe verse afectado
        Producto.objects.filter(pk=self.pote.pk).update(gramos=500)
        venta.cambiar_estado(Venta.REEMBOLSADA, usuario=self.user)

        for sabor in sabores:
            self.assertEqual(self.stock(sabor), Decimal('10.000'))
        entradas = MovimientoStock.objects.filter(venta=venta, tipo_movimiento=MovimientoStock.ENTRADA)
        self.assertEqual(entradas.count(), 3)

    def test_stock_insuficiente_no_descuenta_nada(self):
        abundante = self.crear_sabores(1)[0]
        escaso = Sabor.objects.create(
            nombre='Escaso', categoria=Sabor.FRUTAL, stock_kg=Decimal('0.100'),
        )
        venta = self.crear_venta([abundante, escaso])  # necesita 500 g de cada uno

        with self.assertRaises(ValidationError):
            venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        self.assertEqual(self.stock(abundante), Decimal('10.000'))
        self.assertEqual(self.stock(escaso), Decimal('0.100'))
        self.assertFalse(MovimientoStock.objects.filter(venta=venta).exists())
        venta.refresh_from_db()
        self.assertEqual(venta.estado, Venta.PENDIENTE)

class AuditoriaVentaTests(TestCase):
    """La auditoría registra la creación y los cambios de estado, con usuario."""

    def setUp(self):
        self.user = get_user_model().objects.create_user('gerente', password='x') # type: ignore
        self.empleado = Empleado.objects.create(
            nombre='Luis', apellido='Gómez', email='luis@example.com',
            puesto=Empleado.GERENTE, user=self.user,
        )
        self.pote = Producto.objects.create(
            nombre='Pote 1 kg', tipo_producto=Producto.POTE_1KG, precio_base=Decimal('10000.00'),
        )
        self.vaso = Producto.objects.create(
            nombre='Vaso', tipo_producto=Producto.VASO, precio_base=Decimal('3000.00'),
        )
        self.sabor = Sabor.objects.create(
            nombre='Chocolate', categoria=Sabor.CHOCOLATE, stock_kg=Decimal('10.000'),
        )

    def nueva_venta(self):
        venta = Venta(empleado=self.empleado)
        venta.save(usuario=self.user)
        return venta

    def auditorias(self, venta):
        return list(venta.auditorias.order_by('pk'))

    def test_crear_venta_registra_una_auditoria_con_usuario(self):
        venta = self.nueva_venta()

        auditorias = self.auditorias(venta)
        self.assertEqual(len(auditorias), 1)
        aud = auditorias[0]
        self.assertEqual(aud.estado_anterior, '')
        self.assertEqual(aud.estado_nuevo, Venta.PENDIENTE)
        self.assertEqual(aud.usuario, self.user)
        self.assertEqual(aud.motivo, 'Creación de venta')

    def test_agregar_detalles_no_genera_auditorias_extra(self):
        venta = self.nueva_venta()

        DetalleVenta.objects.create(venta=venta, producto=self.pote, cantidad=1)
        DetalleVenta.objects.create(venta=venta, producto=self.vaso, cantidad=2)

        self.assertEqual(len(self.auditorias(venta)), 1)
        venta.refresh_from_db()
        self.assertEqual(venta.total, Decimal('16000.00'))

    def test_cambios_que_no_son_de_estado_no_se_auditan(self):
        venta = self.nueva_venta()

        venta.metodo_pago = Venta.TARJETA
        venta.save(usuario=self.user)

        self.assertEqual(len(self.auditorias(venta)), 1)

    def test_completar_y_reembolsar_registran_el_estado_anterior_correcto(self):
        venta = self.nueva_venta()
        detalle = DetalleVenta.objects.create(venta=venta, producto=self.pote, cantidad=1)
        detalle.sabores.set([self.sabor])

        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)
        venta.cambiar_estado(Venta.REEMBOLSADA, usuario=self.user)

        auditorias = self.auditorias(venta)
        self.assertEqual(
            [(a.estado_anterior, a.estado_nuevo) for a in auditorias],
            [
                ('', Venta.PENDIENTE),
                (Venta.PENDIENTE, Venta.COMPLETADA),
                (Venta.COMPLETADA, Venta.REEMBOLSADA),
            ],
        )
        self.assertTrue(all(a.usuario == self.user for a in auditorias))


class TotalVentaTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user('cajera', password='x') # type: ignore
        self.empleado = Empleado.objects.create(
            nombre='Ana', apellido='Pérez', email='ana@example.com',
            puesto=Empleado.CAJERO, user=user,
        )
        self.pote = Producto.objects.create(
            nombre='Pote 1 kg', tipo_producto=Producto.POTE_1KG, precio_base=Decimal('10000.00'),
        )
        self.vaso = Producto.objects.create(
            nombre='Vaso', tipo_producto=Producto.VASO, precio_base=Decimal('3000.00'),
        )

    def test_el_total_se_recalcula_al_eliminar_un_detalle(self):
        venta = Venta.objects.create(empleado=self.empleado)
        DetalleVenta.objects.create(venta=venta, producto=self.pote, cantidad=1)
        detalle_vaso = DetalleVenta.objects.create(venta=venta, producto=self.vaso, cantidad=2)
        venta.refresh_from_db()
        self.assertEqual(venta.total, Decimal('16000.00'))

        detalle_vaso.delete()

        venta.refresh_from_db()
        self.assertEqual(venta.total, Decimal('10000.00'))

    def test_calcular_total_no_pasa_por_venta_save(self):
        venta = Venta.objects.create(empleado=self.empleado)
        DetalleVenta.objects.create(venta=venta, producto=self.pote, cantidad=1)

        with patch.object(Venta, 'save') as save_mock:
            venta.calcular_total()

        save_mock.assert_not_called()
        self.assertEqual(venta.total, Decimal('10000.00'))

class VentaApiActionsTestCase(APITestCase):
    def setUp(self):
        self.user_gerente = User.objects.create_user(username='gerente1', password='password123')
        self.empleado_gerente = Empleado.objects.create(
            nombre='Carlos', apellido='Gerente', email='carlos@heladeria.com',
            puesto=Empleado.GERENTE, user=self.user_gerente
        )
        self.user_cajero = User.objects.create_user(username='cajero1', password='password123')
        self.empleado_cajero = Empleado.objects.create(
            nombre='Lucía', apellido='Cajera', email='lucia@heladeria.com',
            puesto=Empleado.CAJERO, user=self.user_cajero
        )
        self.sabor = Sabor.objects.create(
            nombre='Menta Granizada', categoria=Sabor.CREMA, stock_kg=Decimal('5.000'), disponible=True
        )
        self.producto = Producto.objects.create(
            nombre='Pote 1KG', tipo_producto=Producto.POTE_1KG, gramos=1000, max_sabores=1, precio_base=Decimal('1000.00')
        )
        self.venta = Venta.objects.create(empleado=self.empleado_cajero, estado=Venta.PENDIENTE)
        self.detalle = DetalleVenta.objects.create(venta=self.venta, producto=self.producto, cantidad=1)
        self.detalle.sabores.add(self.sabor)
        self.venta.calcular_total()

    def test_cajero_no_puede_crear_producto_pero_gerente_si(self):
        self.client.force_authenticate(user=self.user_cajero) # type: ignore
        response = self.client.post('/heladerias/productos/', {
            'nombre': 'Nuevo Pote', 'tipo_producto': Producto.POTE_500G, 'precio_base': Decimal('500.00')
        }, format='json')
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=self.user_gerente) # type: ignore
        response = self.client.post('/heladerias/productos/', {
            'nombre': 'Nuevo Pote', 'tipo_producto': Producto.POTE_500G, 'precio_base': Decimal('500.00')
        }, format='json')
        self.assertEqual(response.status_code, 201)

    def test_accion_cancelar_venta_pendiete(self):
        self.client.force_authenticate(user=self.user_cajero) # type: ignore
        response = self.client.post(f'/heladerias/ventas/{self.venta.pk}/cancelar/')
        self.assertEqual(response.status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado, Venta.CANCELADA)

    def test_accion_reembolsar_venta_completada(self):
        self.venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user_cajero)

        self.client.force_authenticate(user=self.user_gerente) # type: ignore
        response = self.client.post(f'/heladerias/ventas/{self.venta.pk}/reembolsar/')
        self.assertEqual(response.status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado, Venta.REEMBOLSADA)


class BeneficiosSocioTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='socio-cajero', password='password123')
        self.empleado = Empleado.objects.create(
            nombre='Ana', apellido='Socio', email='ana-socio@heladeria.com',
            puesto=Empleado.CAJERO, user=self.user,
        )
        self.cliente = Cliente.objects.create(
            nombre='Lucia', apellido='Cliente', email='lucia-socio@cliente.com',
            es_socio=True, puntos_acumulados=200,
        )
        self.sabor = Sabor.objects.create(
            nombre='Vainilla Socio', categoria=Sabor.CREMA,
            stock_kg=Decimal('10.000'), disponible=True,
        )
        self.producto = Producto.objects.create(
            nombre='Pote Socio', tipo_producto=Producto.POTE_1KG,
            gramos=1000, max_sabores=1, precio_base=Decimal('2500.00'),
        )

    def crear_venta(self, puntos_canjeados=0):
        venta = Venta.objects.create(
            empleado=self.empleado,
            cliente=self.cliente,
            metodo_pago=Venta.EFECTIVO,
        )
        detalle = DetalleVenta.objects.create(
            venta=venta, producto=self.producto, cantidad=1,
        )
        detalle.sabores.add(self.sabor)
        venta.calcular_total()
        venta.puntos_canjeados = puntos_canjeados
        return venta

    def test_cliente_socio_acumula_puntos_al_completar(self):
        venta = self.crear_venta()

        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        self.cliente.refresh_from_db()
        venta.refresh_from_db()
        self.assertEqual(self.cliente.puntos_acumulados, 220)
        self.assertEqual(venta.puntos_otorgados, 20)

    def test_cliente_socio_puede_canjear_puntos(self):
        venta = self.crear_venta(puntos_canjeados=100)

        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        self.cliente.refresh_from_db()
        venta.refresh_from_db()
        self.assertEqual(venta.descuento_aplicado, Decimal('500.00'))
        self.assertEqual(venta.puntos_canjeados, 100)
        self.assertEqual(venta.total, Decimal('2000.00'))
        self.assertEqual(self.cliente.puntos_acumulados, 120)

    def test_reembolsar_revierte_canje_y_acumulacion(self):
        venta = self.crear_venta(puntos_canjeados=100)
        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)
        venta.cambiar_estado(Venta.REEMBOLSADA, usuario=self.user)

        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.puntos_acumulados, 200)

    def test_cliente_socio_debe_tener_suficientes_puntos(self):
        venta = self.crear_venta(puntos_canjeados=300)

        with self.assertRaises(ValidationError):
            venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.puntos_acumulados, 200)


class EnvaseStockTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('envase-user', password='x')  # type: ignore
        self.empleado = Empleado.objects.create(
            nombre='Pedro', apellido='Ventas', email='pedro-envases@example.com',
            puesto=Empleado.CAJERO, user=self.user,
        )
        self.envase = Envase.objects.create(
            nombre='Pote descartable', stock_unidades=3,
        )
        self.sabor = Sabor.objects.create(
            nombre='Limón', categoria=Sabor.FRUTAL,
            stock_kg=Decimal('10.000'), disponible=True,
        )
        self.producto = Producto.objects.create(
            nombre='Pote envase', tipo_producto=Producto.POTE_1KG,
            gramos=1000, max_sabores=1, precio_base=Decimal('1000.00'),
            envase=self.envase,
        )

    def crear_venta(self, cantidad=1):
        venta = Venta.objects.create(empleado=self.empleado)
        detalle = DetalleVenta.objects.create(
            venta=venta, producto=self.producto, cantidad=cantidad,
        )
        detalle.sabores.add(self.sabor)
        return venta

    def test_completar_descuenta_envases_y_reembolsar_devuelve(self):
        venta = self.crear_venta(cantidad=2)

        venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)
        self.envase.refresh_from_db()
        self.assertEqual(self.envase.stock_unidades, 1)
        movimiento_salida = MovimientoEnvase.objects.filter(
            venta=venta,
            envase=self.envase,
            tipo_movimiento=MovimientoEnvase.SALIDA,
        ).get()
        self.assertEqual(movimiento_salida.cantidad_unidades, 2)
        self.assertEqual(movimiento_salida.usuario, self.user)

        venta.cambiar_estado(Venta.REEMBOLSADA, usuario=self.user)
        self.envase.refresh_from_db()
        self.assertEqual(self.envase.stock_unidades, 3)
        movimiento_entrada = MovimientoEnvase.objects.filter(
            venta=venta,
            envase=self.envase,
            tipo_movimiento=MovimientoEnvase.ENTRADA,
        ).get()
        self.assertEqual(movimiento_entrada.cantidad_unidades, 2)

    def test_stock_insuficiente_de_envases_impide_completar(self):
        self.envase.stock_unidades = 1
        self.envase.save()
        venta = self.crear_venta(cantidad=2)

        with self.assertRaises(ValidationError):
            venta.cambiar_estado(Venta.COMPLETADA, usuario=self.user)

        venta.refresh_from_db()
        self.envase.refresh_from_db()
        self.assertEqual(venta.estado, Venta.PENDIENTE)
        self.assertEqual(self.envase.stock_unidades, 1)


class VentaFlujoApiTests(APITestCase):
    def setUp(self):
        self.user_cajero = User.objects.create_user(username='flujo-cajero', password='password123')
        self.cajero = Empleado.objects.create(
            nombre='Ana', apellido='Caja', email='ana-flujo@heladeria.com',
            puesto=Empleado.CAJERO, user=self.user_cajero,
        )
        self.user_gerente = User.objects.create_user(username='flujo-gerente', password='password123')
        Empleado.objects.create(
            nombre='Gus', apellido='Gerente', email='gus-flujo@heladeria.com',
            puesto=Empleado.GERENTE, user=self.user_gerente,
        )
        self.envase = Envase.objects.create(nombre='Pote flujo', stock_unidades=5)
        self.sabor = Sabor.objects.create(
            nombre='Frutilla', categoria=Sabor.FRUTAL, stock_kg=Decimal('5.000'), disponible=True,
        )
        self.producto = Producto.objects.create(
            nombre='Pote 1KG flujo', tipo_producto=Producto.POTE_1KG, gramos=1000,
            max_sabores=1, precio_base=Decimal('1000.00'), envase=self.envase,
        )
        self.client.force_authenticate(user=self.user_cajero)  # type: ignore

    def crear_venta_api(self):
        response = self.client.post('/heladerias/ventas/', {
            'metodo_pago': 'EFECTIVO',
            'detalles': [{'producto': self.producto.pk, 'cantidad': 1, 'sabores': [self.sabor.pk]}],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)  # type: ignore[attr-defined]
        return Venta.objects.get(pk=response.data['id'])  # type: ignore[attr-defined]

    def test_completar_venta_descuenta_stock_y_envases(self):
        venta = self.crear_venta_api()

        response = self.client.post(f'/heladerias/ventas/{venta.pk}/completar/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['estado'], Venta.COMPLETADA)  # type: ignore[attr-defined]
        self.sabor.refresh_from_db()
        self.envase.refresh_from_db()
        self.assertEqual(self.sabor.stock_kg, Decimal('4.000'))
        self.assertEqual(self.envase.stock_unidades, 4)

    def test_completar_sin_stock_devuelve_400_y_no_cambia_estado(self):
        venta = self.crear_venta_api()
        Sabor.objects.filter(pk=self.sabor.pk).update(stock_kg=Decimal('0.500'))

        response = self.client.post(f'/heladerias/ventas/{venta.pk}/completar/')

        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)  # type: ignore[attr-defined]
        venta.refresh_from_db()
        self.assertEqual(venta.estado, Venta.PENDIENTE)

    def test_completar_venta_cancelada_devuelve_400(self):
        venta = self.crear_venta_api()
        self.client.post(f'/heladerias/ventas/{venta.pk}/cancelar/')

        response = self.client.post(f'/heladerias/ventas/{venta.pk}/completar/')

        self.assertEqual(response.status_code, 400)

    def test_no_se_puede_borrar_venta_completada(self):
        venta = self.crear_venta_api()
        self.client.post(f'/heladerias/ventas/{venta.pk}/completar/')

        response = self.client.delete(f'/heladerias/ventas/{venta.pk}/')

        self.assertEqual(response.status_code, 400)
        self.assertTrue(Venta.objects.filter(pk=venta.pk).exists())

    def test_se_puede_borrar_venta_pendiente(self):
        venta = self.crear_venta_api()

        response = self.client.delete(f'/heladerias/ventas/{venta.pk}/')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Venta.objects.filter(pk=venta.pk).exists())

    def test_borrar_producto_con_ventas_devuelve_409(self):
        self.crear_venta_api()
        self.client.force_authenticate(user=self.user_gerente)  # type: ignore

        response = self.client.delete(f'/heladerias/productos/{self.producto.pk}/')

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_detalles_de_venta_son_solo_lectura(self):
        venta = self.crear_venta_api()
        detalle = venta.detalles.get()  # type: ignore[attr-defined]

        listado = self.client.get('/heladerias/detalle-ventas/')
        alta = self.client.post('/heladerias/detalle-ventas/', {
            'venta': venta.pk, 'producto': self.producto.pk, 'cantidad': 1, 'sabores': [],
        }, format='json')
        edicion = self.client.patch(f'/heladerias/detalle-ventas/{detalle.pk}/', {'cantidad': 3}, format='json')

        self.assertEqual(listado.status_code, 200)
        self.assertEqual(listado.data['results'][0]['venta'], venta.pk)  # type: ignore[attr-defined]
        self.assertEqual(alta.status_code, 405)
        self.assertEqual(edicion.status_code, 405)

    def test_gerente_lista_movimientos_de_envases(self):
        venta = self.crear_venta_api()
        self.client.post(f'/heladerias/ventas/{venta.pk}/completar/')
        self.client.force_authenticate(user=self.user_gerente)  # type: ignore

        response = self.client.get('/heladerias/movimientos-envases/')

        self.assertEqual(response.status_code, 200)
        movimiento = response.data['results'][0]  # type: ignore[attr-defined]
        self.assertEqual(movimiento['envase_nombre'], self.envase.nombre)
        self.assertEqual(movimiento['usuario_nombre'], self.user_cajero.username)


class DetalleVentaCambioProductoTests(TestCase):
    def test_cambiar_producto_actualiza_precio_y_gramos(self):
        user = User.objects.create_user(username='detalle-cambio', password='x')
        empleado = Empleado.objects.create(
            nombre='Eva', apellido='Caja', email='eva-detalle@heladeria.com',
            puesto=Empleado.CAJERO, user=user,
        )
        chico = Producto.objects.create(
            nombre='Cucurucho', tipo_producto=Producto.CUCURUCHO, gramos=150,
            max_sabores=1, precio_base=Decimal('100.00'),
        )
        grande = Producto.objects.create(
            nombre='Pote 1KG cambio', tipo_producto=Producto.POTE_1KG, gramos=1000,
            max_sabores=1, precio_base=Decimal('900.00'),
        )
        venta = Venta.objects.create(empleado=empleado)
        detalle = DetalleVenta.objects.create(venta=venta, producto=chico, cantidad=1)

        detalle.producto = grande
        detalle.save()

        detalle.refresh_from_db()
        venta.refresh_from_db()
        self.assertEqual(detalle.precio_unitario, Decimal('900.00'))
        self.assertEqual(detalle.gramos_unitarios, 1000)
        self.assertEqual(venta.total, Decimal('900.00'))
