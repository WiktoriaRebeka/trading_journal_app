from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Ścieżka dla panelu admina
    path('users/', include('users.urls')),  # Import ścieżek z aplikacji users
    path('activate/<int:user_id>/', user_views.activate_account, name='activate'),  # Ścieżka aktywacji konta
    path('', user_views.login_view, name='login'),  # Ścieżka główna do logowania
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('save_currency/', views.save_currency, name='save_currency'),
    path('journal/', views.journal_view, name='journal'),  # Ścieżka do dziennika
    path('add-to-journal/', views.add_to_journal, name='add_to_journal'),
    path('update-win/<int:entry_id>/', views.update_win, name='update_win'),
    path('delete-entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('save-pair/', views.save_pair, name='save_pair'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reports/', views.reports_view, name='reports'), 

]
