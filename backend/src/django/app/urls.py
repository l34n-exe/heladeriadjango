from django.contrib import admin
from django.urls import path, include
from heladeria import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('heladerias/', include('heladeria.urls')),
    path('heladerias/auth/', include('auth_app.urls')), 
]