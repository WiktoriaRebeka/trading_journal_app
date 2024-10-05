from django.shortcuts import render
from backend.models import Currency

def dashboard_view(request):
    currencies = Currency.objects.all()  # Pobieranie wszystkich walut z bazy danych
    return render(request, 'app_main/dashboard.html', {'currencies': currencies})
