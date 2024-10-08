from django.shortcuts import render
from .models import Currency, Pair
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JournalEntry
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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

        # Sprawdzenie, czy para walutowa istnieje, jeśli nie – dodaj ją
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
    journal_entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app_main/journal.html', {'journal_entries': journal_entries})


@csrf_exempt
def add_to_journal(request):
    if request.method == 'POST':
        try:
            # Próbujemy wczytać dane JSON z requesta
            data = json.loads(request.body)
            print(data)  # Dodaj to, aby zobaczyć, co faktycznie przychodzi
            
            # Walidacja - upewnij się, że wszystkie wymagane pola istnieją
            required_fields = ['currency', 'deposit', 'risk', 'risk_type', 'position', 'position_type', 'pair', 'trade_type', 'entry', 'stop_loss', 'fee', 'target_choice', 'calculated_leverage', 'calculated_position']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'success': False, 'message': f'Missing field: {field}'}, status=400)

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

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Błąd dekodowania JSON'}, status=400)
        except Exception as e:
            # Wyjątek ogólny - zwraca dokładny błąd w odpowiedzi
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def update_win(request, entry_id):
    if request.method == 'POST':
        try:
            # Pobierz wpis na podstawie ID
            journal_entry = get_object_or_404(JournalEntry, id=entry_id)
            
            # Pobierz wartość "win" z formularza
            win_choice = request.POST.get('win_choice')

            # Zaktualizuj pole "win"
            if win_choice in ['YES', 'NO']:
                journal_entry.win = win_choice
                journal_entry.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)