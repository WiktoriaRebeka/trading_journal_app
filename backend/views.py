from django.shortcuts import render
from .models import Currency, Pair
from django.http import JsonResponse

def dashboard_view(request):
    print("Funkcja dashboard_view została wywołana")  # Sprawdzamy, czy funkcja jest w ogóle uruchamiana

    if request.method == 'POST':
        print("Formularz został wysłany metodą POST")  # Sprawdzamy, czy żądanie jest typu POST
        
        # Zbierz dane z formularza
        currency = request.POST.get('currency')
        deposit = request.POST.get('deposit')
        risk = request.POST.get('risk')
        risk_type = request.POST.get('risk_type')
        position = request.POST.get('position')
        position_type = request.POST.get('position_type')
        pair_name = request.POST.get('pair')
        entry = request.POST.get('entry')
        stop_loss = request.POST.get('stop_loss')
        fee = request.POST.get('fee', 0)

        print(f"Data from form: currency={currency}, deposit={deposit}, risk={risk}, pair={pair_name}, entry={entry}")

        # Dodaj logikę sprawdzania i przetwarzania formularza, podobnie jak wcześniej
        try:
            deposit = float(deposit)
            risk = float(risk)
            position = float(position)
            entry = float(entry)
            stop_loss = float(stop_loss)
            fee = float(fee)
        except ValueError:
            print("Błąd konwersji danych z formularza")  # Sprawdzenie błędów konwersji
            return render(request, 'app_main/dashboard.html', {
                'error': 'Błędne dane w formularzu',
                'currencies': Currency.objects.all(),
                'pairs': Pair.objects.all(),
            })

        # Logika obliczeń i przetwarzania
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

        if created:
            print(f"Nowa para walutowa dodana: {pair_name}")
        else:
            print(f"Para walutowa już istnieje: {pair_name}")

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

        print("Wyniki obliczeń:", results)

    # Pobierz waluty i pary walutowe z bazy danych
    currencies = Currency.objects.all()
    pairs = Pair.objects.all()

    return render(request, 'app_main/dashboard.html', {'currencies': currencies, 'pairs': pairs})
