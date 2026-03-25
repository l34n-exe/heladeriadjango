from unicodedata import numeric
from django.http import HttpResponse, JsonResponse
from datetime import date
from .models import Categoria, Producto, Proveedor, Sabor, Cliente, Empleado, Venta, ItemVenta, ItemVentaSabor
from .serializers import ApiSerializer, ProveedorSerializer, ClienteSerializer, SaborSerializer, ProductoSerializer, EmpleadoSerializer, VentaSerializer, ItemVentaSerializer, ItemVentaSaborSerializer, CategoriaSerializer
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render
from rest_framework import mixins, generics, status, permissions
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.

def crear_categoria(request, nombre, tipo, descripcion):
    categoria = Categoria.objects.create(nombre=nombre, tipo=tipo, descripcion=descripcion)
    mensaje= f"Categoria creada: 'id:{categoria.id}' '{categoria.nombre}', tipo: '{categoria.tipo}', descripcion: '{categoria.descripcion}'"
    return HttpResponse(mensaje)
    
def listar_categorias(request):
    categorias = Categoria.objects.all()
    mensaje = "Categorías: " + ", ".join([categoria.nombre for categoria in categorias])
    return HttpResponse(mensaje)

def obtener_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    mensaje = f"Categoria: {categoria.nombre}, tipo: {categoria.tipo}, descripcion: {categoria.descripcion}"
    return HttpResponse(mensaje)

def first_api(request):
    if request.method == "GET":
        respuesta = {
            'nombre': 'Heladería',
            'descripcion': 'Heladería de la Universidad',
            'anio': date.today().year
        }
        return JsonResponse(respuesta)
    elif request.method == "POST":
        datos = json.loads(request.body)
        nombre = datos['nombre']
        descripcion = datos['descripcion']
        
        respuesta = {
            'nombre': nombre,
            'descripcion': descripcion,
            'anio': date.today().year
        }
        return JsonResponse(respuesta)
    return None

@csrf_exempt
def serial_v1(request):
    if request.method == "POST":
        datos = json.loads(request.body)
        serializer = ApiSerializer(data=datos)
        if serializer.is_valid():
            return JsonResponse(serializer.validated_data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)
    return None

@csrf_exempt
def proveedor_v1(request):
    if request.method == "GET":
        respuesta = {
            "nombre": "Proveedor 1",
            "email": "proveedor1@gmail.com",
            "telefono": "123456789",
            "direccion": "Calle 123"
        }
        return JsonResponse(respuesta)
    elif request.method == "POST":
        datos = json.loads(request.body)
        nombre = datos['nombre']
        email = datos['email']
        telefono = datos['telefono']
        direccion = datos['direccion']
        
        respuesta = {
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'direccion': direccion
        }
        return JsonResponse(respuesta)
    return None

@csrf_exempt
def serial_v2(request):
    if request.method == "POST":
        datos = json.loads(request.body)
        serializer = ProveedorSerializer(data=datos)
        if serializer.is_valid():
            return JsonResponse(serializer.validated_data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)
    return None

'''
@csrf_exempt
def ProveedorList(request):
    if request.method == "GET":
        proveedores = Proveedor.objects.all()
        serializer = ProveedorResponseSerializer(proveedores, many=True)
        return JsonResponse(serializer.data, safe=False)
    if request.method == "POST":
        datos = json.loads(request.body)
        serializer = ProveedorResponseSerializer(data=datos)
        if serializer.is_valid():
            proveedor = serializer.save()  # Guardar en la base de datos
            return JsonResponse(ProveedorResponseSerializer(proveedor).data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)
    return None

@csrf_exempt
def ProveedorDetail(request, id):
    if request.method == "GET":
        proveedor = Proveedor.objects.get(id=id)
        serializer = ProveedorResponseSerializer(proveedor)
        return JsonResponse(serializer.data)
    if request.method == "PUT":
        proveedor = Proveedor.objects.get(id=id)
        datos = json.loads(request.body)
        serializer = ProveedorResponseSerializer(proveedor, data=datos)
        if serializer.is_valid():
            proveedor = serializer.save()  # Guardar en la base de datos
            return JsonResponse(ProveedorResponseSerializer(proveedor).data, status=200)
        else:
            return JsonResponse(serializer.errors, status=400)
    if request.method == "DELETE":
        proveedor = Proveedor.objects.get(id=id)
        proveedor.delete()
        return JsonResponse({}, status=204)
    return None
'''
class ProveedorAPIView(APIView):
    def get(self, request):
        proveedores = Proveedor.objects.all()
        serializer = ProveedorSerializer(proveedores, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProveedorSerializer(data=request.data)
        if serializer.is_valid():
            proveedor = serializer.save()
            return Response(ProveedorSerializer(proveedor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProveedorDetailAPIView(APIView):
    def get(self, request, id):
        proveedor = Proveedor.objects.get(id=id)
        serializer = ProveedorSerializer(proveedor)
        return Response(serializer.data)
    
    def put(self, request, id):
        proveedor = Proveedor.objects.get(id=id)
        serializer = ProveedorSerializer(proveedor, data=request.data)
        if serializer.is_valid():
            proveedor = serializer.save()
            return Response(ProveedorSerializer(proveedor).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        proveedor = Proveedor.objects.get(id=id)
        proveedor.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
class ProveedorMixinList(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
class ProveedorMixinDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    lookup_field = 'id'  
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class ProveedorList(generics.ListCreateAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ProveedorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class ClienteList(generics.ListCreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ClienteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class EmpleadoList(generics.ListCreateAPIView):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
class EmpleadoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class SaborList(generics.ListCreateAPIView):
    queryset = Sabor.objects.all()
    serializer_class = SaborSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class SaborDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sabor.objects.all()
    serializer_class = SaborSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class ProductoList(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ProductoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class CategoriaList(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class CategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class VentaList(generics.ListCreateAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class VentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class ItemVentaList(generics.ListCreateAPIView):
    queryset = ItemVenta.objects.all()
    serializer_class = ItemVentaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ItemVentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemVenta.objects.all()
    serializer_class = ItemVentaSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
class ItemVentaSaborList(generics.ListCreateAPIView):
    queryset = ItemVentaSabor.objects.all()
    serializer_class = ItemVentaSaborSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ItemVentaSaborDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemVentaSabor.objects.all()
    serializer_class = ItemVentaSaborSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    
