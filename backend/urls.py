from django.contrib import admin
from django.urls import path, include
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Ustawienie ścieżki dla panelu admina
    path('users/', include('users.urls')),  # Import ścieżek z aplikacji users
    path('', user_views.login_view, name='login'),  # ścieżka dla strony głównej na login
]
