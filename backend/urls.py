from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),  # Ustawienie ścieżki dla panelu admina
]
