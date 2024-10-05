from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Ścieżka do logowania
    path('register/', views.register_view, name='register'),  # Strona rejestracji
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Ścieżka do dashboardu
]
