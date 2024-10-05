# backend/views.py

from django.shortcuts import render
from .models import Currency, Pair
from django.http import JsonResponse

def dashboard_view(request):
    if request.method == 'POST':
        currency = request.POST.get('currency')
        deposit = float(request.POST.get('deposit'))
        risk = float(request.POST.get('risk'))
        risk_type = request.POST.get('risk_type')
        position = float(request.POST.get('position'))
        position_type = request.POST.get('position_type')
        pair_name = request.POST.get('pair')
        entry = float(request.POST.get('entry'))
        stop_loss = float(request.POST.get('stop_loss'))
        fee = float(request.POST.get('fee'))

        # Przetwarzanie ryzyka i pozycji
        if risk_type == 'percent':
            risk_value = (risk / 100) * deposit
        else:
            risk_value = risk

        if position_type == 'percent':
            position_value = (position / 100) * deposit
        else:
            position_value = position

        # Sprawdzenie czy para walutowa istnieje, jeśli nie – dodaj ją
        pair, created = Pair.objects.get_or_create(name=pair_name)

        # Zwracanie wyników do terminala na razie
        results = {
            'currency': currency,
            'deposit': deposit,
            'risk_value': risk_value,
            'position_value': position_value,
            'pair': pair.name,
            'entry': entry,
            'stop_loss': stop_loss,
            'fee': fee,
        }

        print(results)  # Wyświetlenie wyników w terminalu (zamiast JSON)

    # Pobierz waluty i pary walutowe z bazy danych
    currencies = Currency.objects.all()
    pairs = Pair.objects.all()

    return render(request, 'app_main/dashboard.html', {'currencies': currencies, 'pairs': pairs})
