from decimal import Decimal
from typing import cast

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework.response import Response

from .models import DetalleVenta, Empleado, Producto, Sabor, Venta


class ApiAuthenticationTests(APITestCase):
	def setUp(self):
		self.client = APIClient()

	def test_productos_requiere_jwt(self):
		response = self.client.get('/heladerias/productos/')
		self.assertEqual(response.status_code, 401)

	def test_usuario_autenticado_puede_listar_productos(self):
		usuario = User.objects.create_user(username='api-user', password='test-password')
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
		)
		self.producto = Producto.objects.create(
			nombre='Pote',
			tipo_producto=Producto.POTE_1KG,
			max_sabores=1,
			precio_base=Decimal('100.00'),
			gramos=1000,
		)
		self.producto.sabores_disponibles.add(self.sabor)

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

	def test_cancelar_devuelve_stock_y_bloquea_detalles(self):
		venta, detalle = self.crear_venta_con_detalle()
		venta.estado = Venta.COMPLETADA
		venta.save()
		venta.estado = Venta.CANCELADA
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
		producto.sabores_disponibles.add(self.sabor)
		venta = Venta.objects.create(empleado=self.empleado)
		detalle = DetalleVenta.objects.create(venta=venta, producto=producto)

		with self.assertRaises(ValidationError):
			detalle.sabores.set([self.sabor])

	def test_agregar_sabor_directamente_aplica_las_mismas_validaciones(self):
		otro_sabor = Sabor.objects.create(
			nombre='Frutilla',
			categoria=Sabor.FRUTAL,
		)
		venta = Venta.objects.create(empleado=self.empleado)
		detalle = DetalleVenta.objects.create(venta=venta, producto=self.producto)

		with self.assertRaises(ValidationError):
			detalle.sabores.add(otro_sabor)