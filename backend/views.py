from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Currency, Pair, JournalEntry
import json
from django.db.models import Q

def dashboard_view(request):
    print("Funkcja dashboard_view została wywołana")

    if request.method == 'POST':
        print("Formularz został wysłany metodą POST")
        
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

        try:
            deposit = float(deposit)
            risk = float(risk)
            position = float(position)
            entry = float(entry)
            stop_loss = float(stop_loss)
            fee = float(fee)
        except ValueError:
            print("Błąd konwersji danych z formularza")
            return render(request, 'app_main/dashboard.html', {
                'error': 'Błędne dane w formularzu',
                'currencies': Currency.objects.all(),
                'pairs': Pair.objects.all(),
            })

        # Logika obliczeń
        risk_value = (risk / 100) * deposit if risk_type == 'percent' else risk
        position_value = (position / 100) * deposit if position_type == 'percent' else position

        pair, created = Pair.objects.get_or_create(name=pair_name)
        if created:
            print(f"Nowa para walutowa dodana: {pair_name}")
        else:
            print(f"Para walutowa już istnieje: {pair_name}")

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

    currencies = Currency.objects.all()
    pairs = Pair.objects.all()

    return render(request, 'app_main/dashboard.html', {'currencies': currencies, 'pairs': pairs})


@csrf_exempt
def save_currency(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            currency = data.get('currency')

            print(f"Wybrana waluta: {currency}")
            return JsonResponse({'status': 'success', 'currency': currency})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Błąd dekodowania JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Niewłaściwa metoda HTTP'}, status=400)



@login_required
def journal_view(request):
    # Pobranie wszystkich wpisów użytkownika
    journal_entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')
    
    # Pobieranie dostępnych par walutowych do wyboru w filtrze
    pairs = Pair.objects.all()

    # Pobieranie parametrów filtrowania z zapytania GET
    pair_filter = request.GET.get('pair_filter')
    trade_type_filter = request.GET.get('trade_type_filter')
    target_filter = request.GET.get('target_filter')
    win_filter = request.GET.get('win_filter')

    # Filtrowanie według wybranych opcji
    if pair_filter:
        journal_entries = journal_entries.filter(pair=pair_filter)
    if trade_type_filter:
        journal_entries = journal_entries.filter(trade_type=trade_type_filter)
    if target_filter:
        journal_entries = journal_entries.filter(target_choice=target_filter)
    if win_filter:
        journal_entries = journal_entries.filter(win=win_filter)

    # Renderowanie strony z przefiltrowanymi wpisami
    return render(request, 'app_main/journal.html', {
        'journal_entries': journal_entries,
        'pairs': pairs,
    })

@csrf_exempt
def add_to_journal(request):
    if request.method == 'POST':
        try:
            # Wyświetlamy dane, które przychodzą na serwer
            data = json.loads(request.body)
            print("Dane przesłane do serwera:", data)

            # Lista wymaganych pól
            required_fields = ['currency', 'deposit', 'risk', 'risk_type', 'position', 'position_type', 'pair', 'trade_type', 'entry', 'stop_loss', 'fee', 'target_choice', 'calculated_leverage', 'calculated_position']

            # Sprawdzamy, czy wszystkie wymagane pola są obecne
            for field in required_fields:
                if field not in data:
                    print(f"Brakujące pole: {field}")
                    return JsonResponse({'success': False, 'message': f'Missing field: {field}'}, status=400)

            # Próba stworzenia nowego wpisu
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
                target_price=data['target_price'],  
                calculated_leverage=data['calculated_leverage'],
                calculated_position=data['calculated_position']
            )
            journal_entry.save()
            print("Wpis został pomyślnie dodany")
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            print("Błąd dekodowania JSON")
            return JsonResponse({'success': False, 'message': 'Błąd dekodowania JSON'}, status=400)
        except Exception as e:
            print(f"Błąd serwera: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def update_win(request, entry_id):
    if request.method == 'POST':
        try:
            journal_entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
            win_choice = request.POST.get('win_choice')

            if win_choice in ['YES', 'NO']:
                journal_entry.win = win_choice
                journal_entry.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@require_http_methods(["DELETE"])
@login_required
def delete_entry(request, entry_id):
    try:
        entry = JournalEntry.objects.get(id=entry_id, user=request.user)
        entry.delete()

        return JsonResponse({'success': True})
    except JournalEntry.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Wpis nie istnieje'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
