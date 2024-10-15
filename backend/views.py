
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Currency, Pair, JournalEntry
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from decimal import Decimal
from .models import Pair

def dashboard_view(request):

    username = request.user.username
    
    if request.method == 'POST':
        
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

        try:
            deposit = float(deposit)
            risk = float(risk)
            position = float(position)
            entry = float(entry)
            stop_loss = float(stop_loss)
            fee = float(fee)
        except ValueError:
            return render(request, 'app_main/dashboard.html', {
                'error': 'Błędne dane w formularzu',
                'currencies': Currency.objects.all(),
                'pairs': Pair.objects.all(),
            })

        # Logika obliczeń
        risk_value = (risk / 100) * deposit if risk_type == 'percent' else risk
        position_value = (position / 100) * deposit if position_type == 'percent' else position

        # Zapis nowej pary
        pair, created = Pair.objects.get_or_create(name=pair_name)
        if created:
            print(f"Nowa para walutowa została utworzona: {pair_name}")
        else:
            print(f"Para walutowa już istnieje: {pair_name}")

        all_pairs = Pair.objects.all()
        print("Wszystkie dostępne pary walutowe w bazie danych:")
        for p in all_pairs:
            print(f"Para: {p.name}")

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


    currencies = Currency.objects.all()
    pairs = Pair.objects.all()

    return render(request, 'app_main/dashboard.html', {
        'currencies': currencies,
        'pairs': pairs,
        'username': username  
    })


@csrf_exempt
def save_currency(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            currency = data.get('currency')

            return JsonResponse({'status': 'success', 'currency': currency})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Błąd dekodowania JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Niewłaściwa metoda HTTP'}, status=400)

@csrf_exempt
def save_pair(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pair_name = data.get('pair')

            # Tworzenie nowej pary, jeśli jeszcze nie istnieje
            pair, created = Pair.objects.get_or_create(name=pair_name)
            if created:
                return JsonResponse({'success': True, 'message': 'Nowa para zapisana'})
            else:
                return JsonResponse({'success': False, 'message': 'Para już istnieje'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Niewłaściwa metoda HTTP'})



@login_required
def journal_view(request):
    # Pobieramy wszystkie wpisy użytkownika posortowane według daty stworzenia
    journal_entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')

    # Pobieramy dostępne pary do filtrowania
    pairs = Pair.objects.all()

    # Pobieranie filtrów z GET requestu
    pair_filter = request.GET.get('pair_filter')
    trade_type_filter = request.GET.get('trade_type_filter')
    target_filter = request.GET.get('target_filter')
    win_filter = request.GET.get('win_filter')

    # Filtrowanie danych na podstawie przekazanych filtrów
    if pair_filter:
        journal_entries = journal_entries.filter(pair=pair_filter)
    if trade_type_filter:
        journal_entries = journal_entries.filter(trade_type=trade_type_filter)
    if target_filter:
        journal_entries = journal_entries.filter(target_choice=target_filter)
    if win_filter:
        journal_entries = journal_entries.filter(win=win_filter)

    # Debugowanie - logowanie wartości calculated_risk_amount i calculated_win_amount
    for entry in journal_entries:
        print(f"Entry {entry.id}: calculated_risk_amount={entry.calculated_risk_amount}, calculated_win_amount={entry.calculated_win_amount}")

    # Renderowanie strony z przefiltrowanymi wpisami oraz dostępne pary
    return render(request, 'app_main/journal.html', {
        'journal_entries': journal_entries,
        'pairs': pairs,
    })

@csrf_exempt
def add_to_journal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Dane przesłane do serwera:", data)

            # Lista wymaganych pól
            required_fields = ['currency', 'deposit', 'risk', 'risk_type', 'position', 'position_type', 'pair', 'trade_type', 'entry', 'stop_loss', 'fee', 'target_choice', 'calculated_leverage', 'calculated_position']

            for field in required_fields:
                if field not in data:
                    print(f"Brakujące pole: {field}")
                    return JsonResponse({'success': False, 'message': f'Missing field: {field}'}, status=400)

            # Obliczamy wartość ryzyka i wygranej w walucie
            deposit = Decimal(data['deposit'])
            risk_value = Decimal(data['risk'])
            risk_type = data['risk_type']

            # Sprawdzamy, czy dane są prawidłowe
            if risk_value is None or deposit is None:
                print("Błąd: brak wartości ryzyka lub depozytu.")
                return JsonResponse({'success': False, 'message': 'Brak wartości ryzyka lub depozytu.'}, status=400)

            # Obliczamy wartość ryzyka w walucie
            risk_amount = (risk_value / 100) * deposit if risk_type == 'percent' else risk_value
            print(f"Obliczona wartość ryzyka (risk_amount): {risk_amount}")  # Wyświetlenie wartości ryzyka

            target_choice = data['target_choice']
            win_amount = calculateWin(risk_amount, target_choice)
            print(f"Obliczona wartość wygranej (win_amount): {win_amount}")  # Wyświetlenie wartości wygranej

            # Tworzenie nowego wpisu w dzienniku
            journal_entry = JournalEntry.objects.create(
                user=request.user,
                currency=data['currency'],
                deposit=deposit,
                risk=risk_value,
                risk_type=risk_type,
                position=data['position'],
                position_type=data['position_type'],
                pair=data['pair'],
                trade_type=data['trade_type'],
                entry_price=data['entry'],
                stop_loss=data['stop_loss'],
                fee=data['fee'],
                target_choice=target_choice,
                target_price=data['target_price'],  
                calculated_leverage=data['calculated_leverage'],
                calculated_position=data['calculated_position'],
                calculated_risk_amount=risk_amount,  # Przypisujemy wartość obliczoną w walucie
                calculated_win_amount=win_amount,    # Przypisujemy wartość wygranej w walucie
                pnl=None,  # PnL początkowo ustawione na None
                win=None  # Ustawienie pola 'win' na NULL przy tworzeniu nowego wpisu
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
            # Pobierz wpis z dziennika na podstawie entry_id
            journal_entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
            win_choice = request.POST.get('win_choice')

            # Pobierz wcześniej obliczone wartości ryzyka i wygranej z bazy danych
            risk_amount = journal_entry.calculated_risk_amount
            win_amount = journal_entry.calculated_win_amount

            if risk_amount is None or win_amount is None:
                return JsonResponse({'success': False, 'message': 'Brak obliczonych wartości ryzyka lub wygranej.'}, status=400)

            print(f"Risk amount for entry {entry_id}: {risk_amount}")
            print(f"Win amount for entry {entry_id}: {win_amount}")

            # Zaktualizuj PnL na podstawie wyboru YES/NO
            if win_choice == "YES":
                journal_entry.pnl = win_amount
                print(f"Calculated PnL for win YES: {win_amount}")
            elif win_choice == "NO":
                journal_entry.pnl = -risk_amount
                print(f"Calculated PnL for win NO: {-risk_amount}")
            else:
                journal_entry.pnl = None  # Resetuje wartość PnL
                print(f"Resetting PnL to None")

            # Zaktualizuj status wygranej (win)
            journal_entry.win = win_choice
            journal_entry.save()

            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error in update_win: {e}")
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

# Funkcja obliczająca wartość PnL dla "Win"
def calculateWin(risk_amount, target_choice):
    try:
        # Sprawdź, czy target_choice jest liczbą, jeśli tak, bez użycia replace
        if isinstance(target_choice, int) or isinstance(target_choice, float):
            target_multiplier = float(target_choice)
        else:
            # Jeśli to jest string, usuń "R"
            target_multiplier = float(target_choice.replace("R", ""))  # Usuwamy "R" z wartości
        
        # Obliczamy PnL jako ryzyko pomnożone przez mnożnik
        pnl_value = risk_amount * Decimal(target_multiplier)  # Używamy Decimal do mnożenia
        return pnl_value
    except ValueError:
        return None


# Funkcja ładująca modal
def load_add_entry_modal(request):
    return render(request, 'app_main/add_entry_modal.html')

# Obliczanie wielkości pozycji na podstawie lewara
def calculate_position_based_on_leverage(deposit, risk, leverage):
    if leverage == 0:
        raise ValueError("Leverage cannot be zero")
    position = (risk / 100) * deposit * leverage
    return position

# Obliczanie lewara na podstawie wielkości pozycji
def calculate_leverage_based_on_position(deposit, risk, position):
    if position == 0:
        raise ValueError("Position cannot be zero")
    leverage = position / ((risk / 100) * deposit)
    return leverage

# Funkcja obliczająca PnL
def calculateWinNewEntry(risk_amount, target_choice):
    try:
        # Upewniamy się, że target_choice jest liczbowy
        if isinstance(target_choice, (int, float)):
            target_multiplier = float(target_choice)
        else:
            target_multiplier = float(str(target_choice).replace("R", ""))  # Usuwamy "R"
        
        # Obliczamy PnL jako ryzyko pomnożone przez mnożnik
        pnl_value = risk_amount * Decimal(target_multiplier)
        return pnl_value
    except ValueError:
        return None

# Funkcja tworząca nowy wpis w dzienniku
@csrf_exempt
def create_manual_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Otrzymane dane z formularza:", data)

            # Pobieranie danych z formularza
            deposit = data.get('deposit')
            print(f"Received deposit: {deposit}")
            if deposit is None or deposit == '':
                return JsonResponse({'success': False, 'message': 'Deposit is missing'}, status=400)
            deposit = Decimal(deposit)

            risk = data.get('risk')
            print(f"Received risk: {risk}")
            if risk is None or risk == '':
                return JsonResponse({'success': False, 'message': 'Risk is missing'}, status=400)
            risk = Decimal(risk)

            stop_loss = data.get('stop_loss')
            print(f"Received stop_loss: {stop_loss}")
            if stop_loss is None or stop_loss == '':
                return JsonResponse({'success': False, 'message': 'Stop Loss is missing'}, status=400)
            stop_loss = Decimal(stop_loss)

            entry = data.get('entry')
            print(f"Received entry: {entry}")
            if entry is None or entry == '':
                return JsonResponse({'success': False, 'message': 'Entry is missing'}, status=400)
            entry = Decimal(entry)

            # Pobieranie opcjonalnych pól
            fee = Decimal(data.get('fee', 0))
            print(f"Received fee: {fee}")
            target_price = data.get('calculated_target_price')
            leverage = data.get('calculated_leverage')

            if target_price is not None:
                target_price = Decimal(target_price)
            if leverage is not None:
                leverage = Decimal(leverage)

            print(f"Received target_price: {target_price}, leverage: {leverage}")

            # Sprawdzenie, czy podano target price lub lewar
            if target_price is None and leverage is None:
                return JsonResponse({'success': False, 'message': 'Either target price or leverage must be provided'}, status=400)

            # Obliczanie brakującej wartości, jeśli jedna z nich jest pusta
            if target_price is None and leverage is not None:
                position = calculate_position_based_on_leverage(deposit, risk, leverage)
                print(f"Calculated position based on leverage: {position}")
            elif leverage is None and target_price is not None:
                leverage = calculate_leverage_based_on_position(deposit, risk, position)
                print(f"Calculated leverage based on position: {leverage}")

            # Obliczanie Risk Reward Ratio
            try:
                risk_reward_ratio = (target_price - entry) / (entry - stop_loss)
                print(f"Calculated Risk Reward Ratio: {risk_reward_ratio}")
            except ZeroDivisionError:
                return JsonResponse({'success': False, 'message': 'Entry price and stop loss cannot be the same'}, status=400)

            # Obliczanie PnL
            try:
                pnl = calculateWinNewEntry(risk, risk_reward_ratio) if data.get('win') == 'YES' else -risk
                print(f"Calculated PnL: {pnl}")
            except Exception as e:
                print(f"Error calculating PnL: {e}")
                return JsonResponse({'success': False, 'message': f'Error calculating PnL: {str(e)}'}, status=500)

            # Zapis do bazy danych
            journal_entry = JournalEntry.objects.create(
                user=request.user,
                currency=data.get('currency'),
                deposit=deposit,
                risk=risk,
                risk_type=data.get('risk_type', 'percent'),
                position=position if leverage is not None else None,
                position_type=data.get('position_type', 'currency'),
                pair=data.get('pair'),
                trade_type=data.get('trade_type', 'long'),
                entry_price=entry,
                stop_loss=stop_loss,
                fee=fee,
                target_price=target_price if leverage is None else None,
                calculated_leverage=leverage,
                pnl=pnl,
                win=data.get('win')
            )
            journal_entry.save()
            print("Journal entry saved successfully")
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Błąd serwera: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)