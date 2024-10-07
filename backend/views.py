from django.shortcuts import render
from .models import Currency, Pair
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JournalEntry
import json

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


@csrf_exempt  # Używaj ostrożnie - jeśli korzystasz z tokena CSRF, nie musisz tego używać
def save_currency(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            currency = data.get('currency')

            # Zapisz walutę lub wykonaj inną logikę
            print(f"Wybrana waluta: {currency}")

            # Zwróć odpowiedź JSON
            return JsonResponse({'status': 'success', 'currency': currency})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Błąd dekodowania JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Niewłaściwa metoda HTTP'}, status=400)


def journal_view(request):
    return render(request, 'app_main/journal.html')



@csrf_exempt
def add_to_journal(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Tworzenie nowego wpisu w dzienniku
        journal_entry = JournalEntry.objects.create(
            user=request.user,
            currency=data['currency'],
            deposit=data['deposit'],
            risk=data['risk'],
            risk_type=data['risk_type'],
            position=data['position'],
            position_type=data['position_type'],
            pair=data['pair'],
            trade_type=data['trade_type'],
            entry_price=data['entry'],
            stop_loss=data['stop_loss'],
            fee=data['fee'],
            target_choice=data['target_choice'],
            calculated_leverage=data['calculated_leverage'],
            calculated_position=data['calculated_position']
        )
        journal_entry.save()

        # Odpowiedź JSON potwierdzająca sukces
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})