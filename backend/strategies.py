from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Strategy, Attachment


@login_required
def handle_add_strategy(request):
    """Obsługa dodawania nowej strategii."""
    if request.method == 'POST':
        strategy_name = request.POST['strategy_name']
        strategy_description = request.POST['strategy_description']
        timeframe = request.POST['timeframe']
        indicators = request.POST['indicators']
        entry_rules = request.POST['entry_rules']
        exit_rules = request.POST['exit_rules']
        strategy_type = request.POST['strategy_type']
        notes = request.POST.get('notes', '')  # Uwzględniamy możliwość braku notatek

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

        # Obsługa załączników
        if request.FILES.getlist('attachments'):
            for file in request.FILES.getlist('attachments'):
                Attachment.objects.create(strategy=strategy, file=file)

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

    return JsonResponse({'success': False})

@login_required
def delete_strategy(request, strategy_id):
    try:
        strategy = Strategy.objects.get(id=strategy_id, user=request.user)
        strategy.delete()
        return JsonResponse({'success': True})
    except Strategy.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Strategy not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    

