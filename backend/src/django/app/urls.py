from django.contrib import admin
from django.urls import path, include
from heladeria import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auth.urls')),
    path('heladerias/', include(urls)),
    
]
