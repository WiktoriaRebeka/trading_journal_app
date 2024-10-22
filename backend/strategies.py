from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Strategy

@login_required
def handle_add_strategy(request):
    """Obsługa dodawania nowej strategii."""
    if request.method == 'POST':
        # Sprawdzenie, czy wszystkie wymagane pola są wypełnione
        strategy_name = request.POST.get('strategy_name', '').strip()
        strategy_description = request.POST.get('strategy_description', '').strip()
        timeframe = request.POST.get('timeframe', '').strip()
        indicators = request.POST.get('indicators', '').strip()
        entry_rules = request.POST.get('entry_rules', '').strip()
        exit_rules = request.POST.get('exit_rules', '').strip()
        strategy_type = request.POST.get('strategy_type', '').strip()
        notes = request.POST.get('notes', '').strip()  # Uwzględniamy możliwość braku notatek

        # Walidacja danych
        if not strategy_name or not strategy_description or not timeframe or not indicators or not entry_rules or not exit_rules or not strategy_type:
            return JsonResponse({'success': False, 'error': 'Please fill in all required fields.'})

        # Zapis strategii do bazy danych
        strategy = Strategy.objects.create(
            user=request.user,
            name=strategy_name,
            description=strategy_description,
            timeframe=timeframe,
            indicators=indicators,
            entry_rules=entry_rules,
            exit_rules=exit_rules,
            type=strategy_type,
            notes=notes,
        )

        # Zwracamy dane w formacie JSON do dodania wiersza
        return JsonResponse({
            'success': True,
            'strategy': {
                'name': strategy.name,
                'description': strategy.description,
                'timeframe': strategy.timeframe,
                'indicators': strategy.indicators,
                'entry_rules': strategy.entry_rules,
                'exit_rules': strategy.exit_rules,
                'type': strategy.type,
                'notes': strategy.notes,
            }
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
