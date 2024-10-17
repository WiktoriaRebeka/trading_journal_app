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
    print("Funkcja dashboard_view została wywołana")

    username = request.user.username
    
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

        print("Wyniki obliczeń:", results)

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

            print(f"Wybrana waluta: {currency}")
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


# Funkcja obliczająca PnL
def calculateWinNewEntry(risk_amount, risk_reward_ratio):
    """
    Oblicza PnL (zysk lub strata) na podstawie wartości ryzyka i współczynnika Risk Reward.
    """
    try:
        # Upewniamy się, że risk_reward_ratio jest liczbą
        if not isinstance(risk_reward_ratio, (int, float, Decimal)):
            raise ValueError("Risk Reward Ratio must be a number")
        
        # Obliczamy PnL jako ryzyko pomnożone przez współczynnik Risk Reward
        pnl_value = risk_amount * Decimal(risk_reward_ratio)
        return pnl_value
    except (ValueError, TypeError) as e:
        print(f"Error calculating PnL: {e}")
        return None

def calculate_leverage_based_on_position(deposit, risk, position):
    """
    Oblicza lewar na podstawie wielkości pozycji.
    """
    if position == 0:
        raise ValueError("Position cannot be zero")
    
    # Obliczamy wartość ryzyka
    risk_amount = (risk / 100) * deposit
    if risk_amount == 0:
        raise ValueError("Risk amount cannot be zero")
    
    # Obliczamy leverage na podstawie pozycji
    leverage = position / risk_amount
    return leverage


# Funkcja tworząca nowy wpis w dzienniku
@csrf_exempt
def create_manual_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Otrzymane dane z formularza:", data)

            # Pobieranie danych z formularza
            deposit = Decimal(data.get('deposit'))
            pnl = Decimal(data.get('pnl'))  # Nowe pole PnL
            stop_loss = Decimal(data.get('stop_loss'))
            entry = Decimal(data.get('entry'))
            target_price = Decimal(data.get('target_price'))
            position = Decimal(data.get('position'))
            fee = Decimal(data.get('fee', 0))
            trade_type = data.get('trade_type')

            # Obliczanie stop loss percentage (odległość stop loss od ceny wejścia w %)
            if trade_type == 'long':
                stop_loss_percentage = ((entry - stop_loss) / entry) * 100
            elif trade_type == 'short':
                stop_loss_percentage = ((stop_loss - entry) / entry) * 100
            else:
                return JsonResponse({'success': False, 'message': 'Invalid trade type'}, status=400)

            print(f"Stop Loss Percentage: {stop_loss_percentage}")

            # Uwzględnienie opłaty (fee)
            adjusted_stop_loss = stop_loss_percentage + (2 * fee)
            print(f"Adjusted Stop Loss (including fee): {adjusted_stop_loss}")

            # Obliczanie Risk Reward Ratio z uwzględnieniem typu transakcji i opłat
            if trade_type == 'long':
                profit_percentage = ((target_price - entry) / entry) * 100 - (2 * fee)
                print(f"Long Trade: Profit Percentage (adjusted for fee): {profit_percentage}")
            elif trade_type == 'short':
                profit_percentage = ((entry - target_price) / entry) * 100 - (2 * fee)
                print(f"Short Trade: Profit Percentage (adjusted for fee): {profit_percentage}")

            if adjusted_stop_loss == 0:
                return JsonResponse({'success': False, 'message': 'Adjusted stop loss cannot be zero'}, status=400)

            # Obliczanie i zaokrąglenie Risk Reward Ratio do 2 miejsc po przecinku
            risk_reward_ratio = round(profit_percentage / adjusted_stop_loss, 2)
            print(f"Calculated Risk Reward Ratio: {risk_reward_ratio}")

            # Obliczanie ryzyka na podstawie PnL i RRR
            risk = pnl / Decimal(risk_reward_ratio)
            print(f"Calculated Risk: {risk}")

            # Obliczenie ryzyka jako procentu depozytu
            risk_percentage = (risk / deposit) * 100
            print(f"Calculated Risk as Percentage of Deposit: {risk_percentage}")

            # Ustawienie wartości PnL
            pnl = pnl if data.get('win') == 'YES' else -pnl
            print(f"Calculated PnL: {pnl}")

            # Obliczanie ryzyka w walucie
            risk_value_in_currency = (risk_percentage / 100) * deposit
            print(f"Risk value in currency: {risk_value_in_currency}")
            # Obliczanie lewara
            # Obliczanie lewara na podstawie wzoru: ((risk_percentage * deposit) / adjusted_stop_loss) / position
            leverage = round(((risk_percentage / 100) * deposit) / (adjusted_stop_loss / 100) / position, 0)
            print(f"Calculated Leverage: {leverage}")

            # Ustawienie wartości dla calculated_position jako position
            calculated_position = position

            # Zapis do bazy danych
            journal_entry = JournalEntry.objects.create(
                user=request.user,
                currency=data.get('currency'),
                deposit=deposit,
                risk=risk,
                risk_type='currency',
                position=position,
                position_type=data.get('position_type', 'currency'),
                pair=data.get('pair'),
                trade_type=trade_type,
                entry_price=entry,
                stop_loss=stop_loss,
                fee=fee,
                target_price=target_price,
                calculated_leverage=leverage,
                calculated_position=calculated_position,
                pnl=pnl,
                win=data.get('win')
            )
            journal_entry.save()
            print("Journal entry saved successfully")
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Błąd serwera: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
def add_to_journal_with_full_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Otrzymane dane z formularza:", data)

            # Pobieranie danych z formularza i logowanie każdej wartości
            date_added = data.get('date_added')
            if not date_added:
                date_added = timezone.now()  # Jeśli nie podano daty, użyj bieżącej daty
            print(f"Date Added: {date_added}")

            currency = data.get('currency')
            print(f"Currency: {currency}")

            deposit = Decimal(data.get('deposit'))
            print(f"Deposit: {deposit}")

            pnl = Decimal(data.get('pnl'))
            print(f"PnL: {pnl}")

            stop_loss = Decimal(data.get('stop_loss'))
            print(f"Stop Loss: {stop_loss}")

            entry = Decimal(data.get('entry'))
            print(f"Entry Price: {entry}")

            target_price = Decimal(data.get('target_price'))
            print(f"Target Price: {target_price}")

            position = Decimal(data.get('position'))
            print(f"Position: {position}")

            fee = Decimal(data.get('fee', 0))
            print(f"Fee: {fee}")

            trade_type = data.get('trade_type')
            print(f"Trade Type: {trade_type}")

            win = data.get('win')
            print(f"Win: {win}")

            risk_reward_ratio = Decimal(data.get('risk_reward_ratio'))
            print(f"Risk Reward Ratio: {risk_reward_ratio}")

            # Obliczanie wartości ryzyka i lewara
            try:
                calculated_risk = pnl / risk_reward_ratio
                print(f"Calculated Risk: {calculated_risk}")

                calculated_leverage = round(((calculated_risk / deposit) * 100) / (stop_loss / 100), 0)
                print(f"Calculated Leverage: {calculated_leverage}")
            except Exception as calc_error:
                print(f"Błąd w obliczeniach ryzyka lub lewara: {calc_error}")
                return JsonResponse({'success': False, 'message': str(calc_error)}, status=500)

            # Tworzenie nowego wpisu w dzienniku
            journal_entry = JournalEntry.objects.create(
                user=request.user,
                date_added=date_added,
                currency=currency,
                deposit=deposit,
                risk=calculated_risk,
                risk_type='currency',
                position=position,
                position_type='currency',
                pair=data.get('pair'),
                trade_type=trade_type,
                entry_price=entry,
                stop_loss=stop_loss,
                fee=fee,
                target_price=target_price,
                calculated_leverage=calculated_leverage,
                calculated_position=position,
                pnl=pnl,
                win=win,
                risk_reward_ratio=risk_reward_ratio,
            )

            journal_entry.save()
            print("Wpis został dodany pomyślnie do bazy danych.")

            # Logowanie, aby upewnić się, że wpis pojawił się w bazie danych
            saved_entry = JournalEntry.objects.filter(id=journal_entry.id).first()
            if saved_entry:
                print(f"Wpis o ID {journal_entry.id} jest teraz w bazie danych.")
            else:
                print(f"Nie znaleziono wpisu o ID {journal_entry.id} w bazie danych po dodaniu.")

            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Błąd serwera: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    print("Niewłaściwa metoda HTTP, oczekiwano POST.")
    return JsonResponse({'success': False, 'message': 'Niewłaściwa metoda HTTP'}, status=400)


