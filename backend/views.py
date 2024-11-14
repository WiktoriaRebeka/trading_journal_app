from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Currency, Pair, JournalEntry
import json
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.db.models import Q
from decimal import Decimal
from .models import Pair
from django.db.models import Case, When, IntegerField
from .models import Strategy, Attachment, JournalEntryAttachment
from django.shortcuts import render, get_object_or_404, redirect


import logging

logger = logging.getLogger(__name__)  # Używamy loggera Django

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


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import JournalEntry, Pair, Strategy

@login_required
def journal_view(request):
    journal_entries = JournalEntry.objects.filter(user=request.user)
    pairs = Pair.objects.all()
    strategies = Strategy.objects.filter(user=request.user)

    # Filter parameters
    pair_filter = request.GET.get('pair_filter')
    trade_type_filter = request.GET.get('trade_type_filter')
    strategy_filter = request.GET.get('strategy_filter')
    win_filter = request.GET.get('win_filter')
    date_sort = request.GET.get('date_sort', 'asc')  # Default to 'asc' if not provided

    # Apply filters
    if pair_filter:
        journal_entries = journal_entries.filter(pair=pair_filter)
    if trade_type_filter:
        journal_entries = journal_entries.filter(trade_type=trade_type_filter)
    if strategy_filter:
        journal_entries = journal_entries.filter(strategy__id=strategy_filter)
    if win_filter:
        journal_entries = journal_entries.filter(win=win_filter)

    # Sort by entry date
    if date_sort == 'desc':
        journal_entries = journal_entries.order_by('-entry_date')
    else:
        journal_entries = journal_entries.order_by('entry_date')

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'journal_entries': list(journal_entries.values(
                'id', 
                'entry_date', 
                'exit_date', 
                'currency', 
                'strategy__name', 
                'deposit',
                'calculated_risk_amount', 
                'calculated_position', 
                'calculated_leverage',
                'pair', 
                'trade_type', 
                'entry_price', 
                'stop_loss', 
                'win', 
                'pnl',
                'target_choice',  
                'target_price'
            ))
        }
        return JsonResponse(data)

    # HTML response
    return render(request, 'app_main/journal.html', {
        'journal_entries': journal_entries,
        'pairs': pairs,
        'strategies': strategies,
        'selected_pair': pair_filter,
        'selected_trade_type': trade_type_filter,
        'selected_strategy': strategy_filter,
        'selected_win': win_filter,
        'selected_sort': date_sort,  # Pass selected sorting option to the template
    })



@csrf_exempt
def add_to_journal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Dane przesłane do serwera:", data)
 # Pobieramy strategię
            strategy_id = data.get('strategy')
            strategy = Strategy.objects.get(id=strategy_id, user=request.user) if strategy_id else None

            # Lista wymaganych pól
            required_fields = ['currency', 'deposit', 'risk', 'risk_type', 'position', 'position_type', 'pair', 'trade_type', 'entry', 'stop_loss', 'fee', 'target_choice', 'calculated_leverage', 'calculated_position']

            for field in required_fields:
                if field not in data:
                    print(f"Brakujące pole: {field}")
                    return JsonResponse({'success': False, 'message': f'Missing field: {field}'}, status=400)

            # Pobieramy entry_date i exit_date z danych użytkownika
            entry_date = data.get('entry_date')
            exit_date = data.get('exit_date')

            # Konwersja entry_date i exit_date na format datetime
            if entry_date:
                try:
                    entry_date = timezone.make_aware(timezone.datetime.fromisoformat(entry_date))
                    print(f"Entry Date from input: {entry_date}")
                except ValueError:
                    print("Błąd parsowania daty wejścia, używam bieżącej daty")
                    entry_date = timezone.now()  # W przypadku błędu ustawiamy bieżącą datę

            if exit_date:
                try:
                    exit_date = timezone.make_aware(timezone.datetime.fromisoformat(exit_date))
                    print(f"Exit Date from input: {exit_date}")
                except ValueError:
                    print("Błąd parsowania daty wyjścia, ustawiono na None")
                    exit_date = None
            else:
                exit_date = None  # Jeśli nie ma daty wyjścia, zostawiamy ją jako None

            # Obliczamy wartość ryzyka w walucie lub procentach
            deposit = Decimal(data['deposit'])
            risk_value = Decimal(data['risk'])
            risk_type = data['risk_type']

            # Sprawdzamy, czy dane są prawidłowe
            if risk_value is None or deposit is None:
                print("Błąd: brak wartości ryzyka lub depozytu.")
                return JsonResponse({'success': False, 'message': 'Brak wartości ryzyka lub depozytu.'}, status=400)

            # Jeśli ryzyko podane jest w procentach, przeliczamy je na walutę
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
                win=None,  # Ustawienie pola 'win' na NULL przy tworzeniu nowego wpisu
                entry_date=entry_date,  # Ustawiamy datę wejścia
                exit_date=exit_date,  # Ustawiamy datę wyjścia
                strategy=strategy
            )
            journal_entry.save()
            print(f"New journal entry saved: {journal_entry}")
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
    pairs = Pair.objects.all()  # Pobieranie wszystkich par
    
    # Dodanie logów, aby sprawdzić, jakie pary zostały pobrane
    if pairs.exists():
        logger.info("Znalezione pary walutowe:")
        for pair in pairs:
            logger.info(f"Para walutowa: {pair.name}")
    else:
        logger.info("Nie znaleziono żadnych par walutowych w bazie.")

    return render(request, 'app_main/add_entry_modal.html', {
        'pairs': pairs  # Przekazujemy dostępne pary do szablonu
    })


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

@csrf_exempt
def create_manual_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Otrzymane dane z formularza (create_manual_entry):", data)

            # Pobieranie danych z formularza
            deposit = Decimal(data.get('deposit'))
            pnl = Decimal(data.get('pnl'))
            stop_loss = Decimal(data.get('stop_loss'))
            entry = Decimal(data.get('entry'))
            target_price = Decimal(data.get('target_price'))
            position = Decimal(data.get('position'))
            fee = Decimal(data.get('fee', 0))
            trade_type = data.get('trade_type')

            # Obliczenia związane z ryzykiem i lewarem
            if trade_type == 'long':
                stop_loss_percentage = ((entry - stop_loss) / entry) * 100
            elif trade_type == 'short':
                stop_loss_percentage = ((stop_loss - entry) / entry) * 100
            else:
                return JsonResponse({'success': False, 'message': 'Invalid trade type'}, status=400)

            adjusted_stop_loss = stop_loss_percentage + (2 * fee)
            print(f"Stop Loss Percentage: {stop_loss_percentage}")
            print(f"Adjusted Stop Loss (including fee): {adjusted_stop_loss}")

            if trade_type == 'long':
                profit_percentage = ((target_price - entry) / entry) * 100 - (2 * fee)
            elif trade_type == 'short':
                profit_percentage = ((entry - target_price) / entry) * 100 - (2 * fee)

            print(f"Profit Percentage (adjusted for fee): {profit_percentage}")

            if adjusted_stop_loss == 0:
                return JsonResponse({'success': False, 'message': 'Adjusted stop loss cannot be zero'}, status=400)

            risk_reward_ratio = round(profit_percentage / adjusted_stop_loss, 2)
            print(f"Calculated Risk Reward Ratio: {risk_reward_ratio}")

            risk = pnl / Decimal(risk_reward_ratio)
            print(f"Calculated Risk: {risk}")

            risk_percentage = (risk / deposit) * 100
            pnl = pnl if data.get('win') == 'YES' else -pnl

            leverage = round(((risk_percentage / 100) * deposit) / (adjusted_stop_loss / 100) / position, 0)
            print(f"Calculated Leverage: {leverage}")

            # Zwracanie wszystkich obliczonych wartości do frontend
            return JsonResponse({
                'success': True,
                'calculated_values': {
                    'risk_reward_ratio': float(risk_reward_ratio),
                    'calculated_risk': float(risk),
                    'calculated_risk_percentage': float(risk_percentage),
                    'calculated_leverage': float(leverage),
                    'calculated_pnl': float(pnl)
                }
            })

        except Exception as e:
            print(f"Błąd serwera (create_manual_entry): {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Niewłaściwa metoda HTTP'}, status=400)
@csrf_exempt
def add_to_journal_with_full_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Otrzymane dane z formularza (add_to_journal_with_full_data):", data)
# Pobieramy strategię
            strategy_id = data.get('strategy')
            strategy = Strategy.objects.get(id=strategy_id, user=request.user) if strategy_id else None

            # Pobieranie danych z formularza
            entry_date = data.get('entry_date')  # Pobranie daty wejścia wybranej przez użytkownika
            exit_date = data.get('exit_date')    # Pobranie daty wyjścia wybranej przez użytkownika

            # Konwersja dat wejścia i wyjścia na format datetime
            if entry_date:
                try:
                    entry_date = timezone.make_aware(timezone.datetime.fromisoformat(entry_date))
                    print(f"Entry Date from input: {entry_date}")
                except ValueError:
                    print("Błąd parsowania daty wejścia, używam bieżącej daty")
                    entry_date = timezone.now()  # W przypadku błędu używamy bieżącej daty
            else:
                entry_date = timezone.now()  # Jeśli nie ma daty wejścia, używamy bieżącej daty

            if exit_date:
                try:
                    exit_date = timezone.make_aware(timezone.datetime.fromisoformat(exit_date))
                    print(f"Exit Date from input: {exit_date}")
                except ValueError:
                    print("Błąd parsowania daty wyjścia, ustawiono na None")
                    exit_date = None  # Jeśli jest błąd, nie ustawiamy żadnej daty wyjścia
            else:
                exit_date = None  # Jeśli nie podano daty wyjścia, zostawiamy jako None

            # Pobieranie pozostałych danych
            currency = data.get('currency')
            deposit = Decimal(data.get('deposit'))
            pnl = Decimal(data.get('pnl'))
            stop_loss = Decimal(data.get('stop_loss'))
            entry = Decimal(data.get('entry'))
            target_price = Decimal(data.get('target_price'))
            position = Decimal(data.get('position'))
            fee = Decimal(data.get('fee', 0))
            trade_type = data.get('trade_type')
            win = data.get('win')
            pair_name = data.get('pair')
            risk_reward_ratio = Decimal(data.get('risk_reward_ratio'))
            calculated_leverage = Decimal(data.get('calculated_leverage'))

            # Zaokrąglamy risk_reward_ratio do 2 miejsc po przecinku i konwertujemy na string
            risk_reward_ratio = str(round(risk_reward_ratio, 2))

            # Sprawdzanie, czy para walutowa już istnieje, jeśli nie - zapisujemy ją
            pair, created = Pair.objects.get_or_create(name=pair_name)
            if created:
                print(f"Nowa para walutowa została zapisana: {pair_name}")

            # Wyświetlenie danych, które będą zapisane do bazy
            print(f"Currency: {currency}, Deposit: {deposit}, PnL: {pnl}, Pair: {pair.name}")
            print(f"Trade Type: {trade_type}, Win: {win}, Fee: {fee}, Position: {position}")
            print(f"Entry Price: {entry}, Stop Loss: {stop_loss}, Target Price: {target_price}")
            print(f"Risk Reward Ratio (zaokrąglone): {risk_reward_ratio}")
            print(f"Calculated Leverage: {calculated_leverage}")
            print(f"Entry Date: {entry_date}, Exit Date: {exit_date}")

            # Tworzenie wpisu w dzienniku
            journal_entry = JournalEntry.objects.create(
                user=request.user,
                entry_date=entry_date,  # Ustawiamy datę wejścia
                exit_date=exit_date,    # Ustawiamy datę wyjścia
                currency=currency,
                deposit=deposit,
                risk=pnl / Decimal(risk_reward_ratio),  # Obliczane tylko raz na podstawie przekazanego RRR
                risk_type='currency',
                position=position,
                position_type='currency',
                pair=pair.name,  # Zapisujemy nazwę pary walutowej
                trade_type=trade_type,
                entry_price=entry,
                stop_loss=stop_loss,
                fee=fee,
                target_price=target_price,
                calculated_leverage=calculated_leverage,  # Bez ponownego obliczania lewara
                calculated_position=position,
                pnl=pnl,
                win=win,
                target_choice=risk_reward_ratio,  # Zaokrąglona wartość jako string
                strategy=strategy, 
            )

            journal_entry.save()
            print(f"Wpis został dodany pomyślnie do bazy danych z ID {journal_entry.id}.")
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Błąd serwera (add_to_journal_with_full_data): {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Niewłaściwa metoda HTTP'}, status=400)

@csrf_exempt
def update_entry_dates(request, entry_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entry_date = data.get('entry_date')
            exit_date = data.get('exit_date')

            # Pobierz wpis na podstawie ID
            journal_entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)

            # Aktualizowanie daty wejścia
            if entry_date:
                try:
                    journal_entry.entry_date = timezone.make_aware(timezone.datetime.fromisoformat(entry_date))
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'Błąd parsowania daty wejścia'}, status=400)

            # Aktualizowanie daty wyjścia
            if exit_date:
                try:
                    journal_entry.exit_date = timezone.make_aware(timezone.datetime.fromisoformat(exit_date))
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'Błąd parsowania daty wyjścia'}, status=400)

            journal_entry.save()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@login_required
def strategies_view(request):
    # Pobranie strategii dla aktualnie zalogowanego użytkownika
    user_strategies = Strategy.objects.filter(user=request.user)
    
    # Pobranie załączników dla każdej strategii
    strategies_with_attachments = []
    for strategy in user_strategies:
        attachments = Attachment.objects.filter(strategy=strategy)
        strategies_with_attachments.append({
            'strategy': strategy,
            'attachments': attachments,
        })
    
    # Renderowanie widoku z tabelą strategii
    return render(request, 'app_main/strategies.html', {
        'strategies_with_attachments': strategies_with_attachments
    })

@csrf_exempt
@login_required
def update_strategy_journal_entry(request, entry_id):
    print("Funkcja update_strategy_journal_entry została wywołana.")
    if request.method == 'POST':
        try:
            # Pobieramy dane z żądania
            data = json.loads(request.body)
            strategy_id = data.get('strategy_id')

            # Logowanie danych
            print(f"Updating strategy for Entry ID: {entry_id}, with Strategy ID: {strategy_id}")

            if not strategy_id:
                return JsonResponse({'success': False, 'message': 'Brak ID strategii.'}, status=400)

            # Pobieramy wpis z dziennika
            journal_entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)

            # Pobieramy strategię
            strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)

            # Aktualizacja strategii w wpisie
            journal_entry.strategy = strategy
            journal_entry.save()

            return JsonResponse({'success': True})

        except Strategy.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Nie znaleziono strategii.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def upload_attachment_to_journal_entry(request, entry_id):
    if request.method == 'POST' and request.FILES.get('attachment'):
        # Pobranie wpisu dziennika
        journal_entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
        
        # Dodanie nowego załącznika
        attachment = JournalEntryAttachment.objects.create(
            journal_entry=journal_entry,
            file=request.FILES['attachment']  # Zapisujemy przesłany plik
        )
        attachment.save()

        # Powrót do widoku dziennika po przesłaniu pliku
        return redirect('journal')

    return JsonResponse({'error': 'Invalid request or missing file'}, status=400)

