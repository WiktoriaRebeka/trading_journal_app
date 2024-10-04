from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Ustawienie ścieżki dla panelu admina
    path('users/', include('users.urls')),  # Import ścieżek z aplikacji users
]
