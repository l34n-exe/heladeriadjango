from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("heladerias/", include("heladeria.urls")),
    path("heladerias/auth/", include("auth_app.urls")),
]