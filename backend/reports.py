from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from .utils import calculate_report_data, get_report_for_period
import plotly.graph_objects as go
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Sum, Count, Case, When, IntegerField
from calendar import monthrange
from django.utils.timezone import now
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Pair
from .models import Strategy  # Dodaj import modelu Strategy

import logging

logger = logging.getLogger(__name__)



@login_required
def reports_view(request):
    # Pobierz wybrany miesiąc i rok z parametrów URL (domyślnie aktualny miesiąc i rok)
    year = int(request.GET.get('year', now().year))
    month = int(request.GET.get('month', now().month))

    # Zbuduj datę dla wybranego miesiąca
    selected_date = date(year, month, 1)

    # Pobierz wszystkie transakcje użytkownika z wynikiem YES lub NO
    journal_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])
    pairs = Pair.objects.all()
    
    # Pobieramy strategie użytkownika
    strategies = Strategy.objects.filter(user=request.user)

    # Raporty dla różnych okresów
    total_report = calculate_report_data(journal_entries)
    monthly_report = get_report_for_period(journal_entries, days=30)
    
    # Raport dzisiejszy
    today = timezone.now().date()
    daily_entries = journal_entries.filter(entry_date__date=today)
    daily_report = calculate_report_data(daily_entries)

    # Zakres dat dla wybranego miesiąca
    first_day_of_month = selected_date.replace(day=1)
    days_in_month = monthrange(year, month)[1]
    last_day_of_month = selected_date.replace(day=days_in_month)

    # Filtrowanie dziennych transakcji dla wybranego miesiąca
    daily_pnl_data = journal_entries.filter(
        entry_date__date__gte=first_day_of_month, entry_date__date__lte=last_day_of_month
    ).values('entry_date__date').annotate(
        daily_pnl=Sum('pnl'),
        total_trades=Count('id'),
        win_trades=Sum(Case(When(win='YES', then=1), output_field=IntegerField()))
    )

    # Przygotowanie danych kalendarza na wybrany miesiąc
    daily_data = []
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        day_entry = next((entry for entry in daily_pnl_data if entry['entry_date__date'] == current_date), None)

        if day_entry:
            pnl = day_entry['daily_pnl']
            total_trades = day_entry['total_trades']
            win_trades = day_entry['win_trades']
            winrate = round((win_trades / total_trades) * 100, 2) if total_trades > 0 else 0
            daily_data.append({
                'date': current_date,
                'pnl': pnl,
                'total_trades': total_trades,
                'winrate': winrate
            })
        else:
            daily_data.append({
                'date': current_date,
                'pnl': None,
                'total_trades': 0,
                'winrate': None
            })

    # Logika do obliczenia pustych komórek na początku kalendarza
    first_weekday_of_month = first_day_of_month.weekday()
    empty_days_before = [''] * first_weekday_of_month
    total_cells = first_weekday_of_month + len(daily_data)
    empty_days_after = [''] * ((7 - total_cells % 7) % 7)

    # Poprzedni i następny miesiąc (nawigacja strzałkami)
    previous_month = selected_date - timedelta(days=1)
    previous_month_url = f"?year={previous_month.year}&month={previous_month.month}"
    next_month = selected_date + timedelta(days=days_in_month)
    next_month_url = f"?year={next_month.year}&month={next_month.month}"

    pie_fig_total = go.Figure(data=[go.Pie(
        labels=['Win', 'Lose'], 
        values=[total_report['yes_count'], total_report['no_count']],
        marker=dict(colors=['#4CAF50', '#FF6B6B'], line=dict(color='#ffffff', width=2))  # Zielony dla wygranych, czerwony dla przegranych
    )])
    pie_fig_total.update_layout(
        title="Win vs Lose - Total",
        title_font=dict(size=16, color='#4a4a4a'),
        paper_bgcolor='#f4f5f7',
        font=dict(color='#4a4a4a')
    )
    pie_chart_total_html = pie_fig_total.to_html(full_html=False)

    # Pie chart dla ostatnich 30 dni
    pie_fig_monthly = go.Figure(data=[go.Pie(
        labels=['Win', 'Lose'], 
        values=[monthly_report['yes_count'], monthly_report['no_count']],
        marker=dict(colors=['#4CAF50', '#FF6B6B'], line=dict(color='#ffffff', width=2))  # Zielony dla wygranych, czerwony dla przegranych
    )])
    pie_fig_monthly.update_layout(
        title="Win vs Lose - Last 30 Days",
        title_font=dict(size=16, color='#4a4a4a'),
        paper_bgcolor='#f4f5f7',
        font=dict(color='#4a4a4a')
    )
    pie_chart_monthly_html = pie_fig_monthly.to_html(full_html=False)

    # Pie chart dla dzisiejszego dnia
    pie_fig_daily = go.Figure(data=[go.Pie(
        labels=['Win', 'Lose'], 
        values=[daily_report['yes_count'], daily_report['no_count']],
        marker=dict(colors=['#4CAF50', '#FF6B6B'], line=dict(color='#ffffff', width=2))  # Zielony dla wygranych, czerwony dla przegranych
    )])
    pie_fig_daily.update_layout(
        title="Win vs Lose - Today",
        title_font=dict(size=16, color='#4a4a4a'),
        paper_bgcolor='#f4f5f7',
        font=dict(color='#4a4a4a')
        )
    pie_chart_daily_html = pie_fig_daily.to_html(full_html=False)

      

    # --------- Wykres słupkowy (PnL) z grafitową kolorystyką ---------
    dates = [entry['entry_date__date'].strftime('%Y-%m-%d') for entry in daily_pnl_data]
    pnl_values = [entry['daily_pnl'] for entry in daily_pnl_data]
    bar_fig_pnl = go.Figure(data=[go.Bar(
        x=dates, 
        y=pnl_values,
        marker_color=['#4CAF50' if x >= 0 else '#FF6B6B' for x in pnl_values]
    )])
    bar_fig_pnl.update_layout(
        title="Daily PnL for the Selected Month",
        title_font=dict(size=16, color='#4a4a4a'),
        xaxis=dict(
            title="Date",
            tickfont=dict(size=12, color='#4a4a4a'),
            tickangle=45,
            linecolor='#4a4a4a'
        ),
        yaxis=dict(
            title="PnL",
            tickfont=dict(size=12, color='#4a4a4a'),
            zeroline=True,
            zerolinecolor='#4a4a4a',
            linecolor='#4a4a4a'
        ),
        paper_bgcolor='#f4f5f7',
        plot_bgcolor='#ffffff'
    )
    bar_chart_pnl_html = bar_fig_pnl.to_html(full_html=False)

    # Przekazanie raportów, wykresów i strategii do szablonu
    return render(request, 'app_main/reports.html', {
        'total_report': total_report,
        'monthly_report': monthly_report,
        'daily_report': daily_report,
        'daily_data': daily_data,
        'empty_days_before': empty_days_before,
        'empty_days_after': empty_days_after,
        'pie_chart_total_html': pie_chart_total_html,
        'pie_chart_monthly_html': pie_chart_monthly_html,
        'pie_chart_daily_html': pie_chart_daily_html,
        'bar_chart_pnl_html': bar_chart_pnl_html,
        'pairs': pairs,
        'strategies': strategies,
        'current_month': selected_date.strftime('%B %Y'),
        'previous_month_url': previous_month_url,
        'next_month_url': next_month_url,
    })

@login_required
def filter_reports_view(request):
    # Pobieranie dat z parametrów GET
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    logger.info(f"Received start date: {start_date_str}, end date: {end_date_str}")

    if start_date_str and end_date_str:
        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            logger.info(f"Parsed start date: {start_date}, end date: {end_date}")
        except ValueError:
            logger.error(f"Invalid date format. Start: {start_date_str}, End: {end_date_str}")
            return JsonResponse({'error': 'Invalid date format'}, status=400)
    else:
        logger.warning("Missing date parameters.")
        return JsonResponse({'error': 'Missing date parameters'}, status=400)

    # Filtrowanie wpisów dziennika na podstawie zakresu dat
    journal_entries = JournalEntry.objects.filter(
        user=request.user,
        entry_date__date__gte=start_date,
        entry_date__date__lte=end_date,
        win__in=['YES', 'NO']
    )
    logger.info(f"Filtered journal entries: {journal_entries.count()} entries found.")

    # Generowanie raportu na podstawie przefiltrowanych danych
    report_data = calculate_report_data(journal_entries)
    logger.info(f"Report data: {report_data}")

    # Tworzenie wykresu kołowego (pie chart)
    pie_fig = go.Figure(data=[go.Pie(labels=['Win', 'Lose'], values=[report_data['yes_count'], report_data['no_count']])])
    pie_fig.update_layout(title=f"Win vs Lose - {start_date_str} to {end_date_str}")
    pie_chart_html = pie_fig.to_html(full_html=False)
    logger.info("Pie chart generated.")

    # Tworzenie wykresu słupkowego (PnL)
    pnl_entries = journal_entries.values('entry_date__date').annotate(daily_pnl=Sum('pnl')).order_by('entry_date__date')
    dates = [entry['entry_date__date'].strftime('%Y-%m-%d') for entry in pnl_entries]
    pnl_values = [entry['daily_pnl'] for entry in pnl_entries]

    if not dates or not pnl_values:
        logger.warning("No data available for bar chart (dates or pnl_values are missing).")

    bar_fig = go.Figure(data=[go.Bar(x=dates, y=pnl_values, marker_color=['green' if x >= 0 else 'red' for x in pnl_values])])
    bar_fig.update_layout(
        title=f"Daily PnL from {start_date_str} to {end_date_str}",
        xaxis_title="Date",
        yaxis_title="PnL",
        xaxis=dict(tickmode='array', tickvals=dates, ticktext=dates, tickangle=45),
        yaxis=dict(zeroline=True, zerolinecolor='black'),
    )
    bar_chart_html = bar_fig.to_html(full_html=False)
    logger.info("Bar chart generated.")

    # Zwracamy oba wykresy w odpowiedzi JSON
    return JsonResponse({
        'pie_chart_values': [report_data['yes_count'], report_data['no_count']],
        'pie_chart_labels': ['Win', 'Lose'],
        'bar_chart_dates': dates,
        'bar_chart_values': pnl_values
    })


@login_required
def winrate_by_currency_pair_view(request):
    try:
        # Pobranie pary walutowej od użytkownika z parametrów URL
        pair = request.GET.get('pair')
        logger.info(f"Requested pair: {pair}")

        if not pair:
            logger.error("No pair provided")
            return JsonResponse({'error': 'No pair provided'}, status=400)

        # Filtrowanie wpisów dziennika na podstawie wybranej pary walutowej
        journal_entries = JournalEntry.objects.filter(user=request.user, pair=pair)

        if not journal_entries.exists():
            logger.error(f"No journal entries found for pair: {pair}")
            return JsonResponse({'error': 'No journal entries found for this pair'}, status=404)

        # Obliczenie WinRate (procentowy wskaźnik wygranych transakcji)
        winrate_data = journal_entries.aggregate(
            total_trades=Count('id'),
            win_trades=Count(Case(When(win='YES', then=1), output_field=IntegerField())),
        )

        total_trades = winrate_data['total_trades']
        win_trades = winrate_data['win_trades']
        win_rate = (win_trades * 100.0 / total_trades) if total_trades > 0 else 0

        logger.info(f"Total trades: {total_trades}, Win trades: {win_trades}, Win rate: {win_rate}%")

        # Zwracamy wartości i etykiety dla wykresu kołowego
        return JsonResponse({
            'pie_chart_values': [win_trades, total_trades - win_trades],
            'pie_chart_labels': ['Win', 'Lose'],
            'pair': pair,
            'total_trades': total_trades,
            'win_trades': win_trades,
            'win_rate': win_rate,
        })
    
    except Exception as e:
        logger.error(f"Error processing WinRate for pair {pair}: {e}")
        return JsonResponse({'error': 'An error occurred while processing the request'}, status=500)

@login_required
def winrate_by_strategy_view(request):
    try:
        # Pobranie strategii od użytkownika
        strategy_name = request.GET.get('strategy')

        if not strategy_name:
            return JsonResponse({'error': 'No strategy provided'}, status=400)

        # Filtrowanie wpisów dziennika na podstawie strategii
        journal_entries = JournalEntry.objects.filter(user=request.user, strategy__name=strategy_name)

        if not journal_entries.exists():
            return JsonResponse({'error': 'No journal entries found for this strategy'}, status=404)

        # Obliczenie WinRate
        winrate_data = journal_entries.aggregate(
            total_trades=Count('id'),
            win_trades=Count(Case(When(win='YES', then=1), output_field=IntegerField())),
        )

        total_trades = winrate_data['total_trades']
        win_trades = winrate_data['win_trades']
        win_rate = (win_trades * 100.0 / total_trades) if total_trades > 0 else 0

        # Zwracamy wartości i etykiety dla wykresu kołowego
        return JsonResponse({
            'pie_chart_values': [win_trades, total_trades - win_trades],
            'pie_chart_labels': ['Win', 'Lose'],
            'strategy': strategy_name,
            'total_trades': total_trades,
            'win_trades': win_trades,
            'win_rate': win_rate,
        })
    
    except Exception as e:
        logger.error(f"Error processing WinRate for strategy {strategy_name}: {e}")
        return JsonResponse({'error': 'An error occurred while processing the request'}, status=500)
