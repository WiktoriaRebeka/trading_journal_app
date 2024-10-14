from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from .utils import calculate_report_data, get_report_for_period
import plotly.graph_objects as go
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db.models import Q, Case, When, IntegerField
from django.db.models import Count
from calendar import monthrange
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

@login_required
def reports_view(request):
    # Pobierz wszystkie transakcje użytkownika z wynikiem YES lub NO
    journal_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])

    # Raporty dla różnych okresów
    total_report = calculate_report_data(journal_entries)
    monthly_report = get_report_for_period(journal_entries, days=30)
    weekly_report = get_report_for_period(journal_entries, days=7)
    daily_report = get_report_for_period(journal_entries, days=1)

    # --------- Wykres kołowy (pie chart) dla ogólnego raportu ---------
    pie_fig_total = go.Figure(data=[go.Pie(labels=['Win', 'Lose'], 
                                           values=[total_report['yes_count'], total_report['no_count']])])
    pie_chart_total_html = pie_fig_total.to_html(full_html=False)

    # --------- Dzienny PnL (na podstawie PnL) ---------
    last_30_days = timezone.now() - timedelta(days=30)
    daily_pnl_data = journal_entries.filter(created_at__gte=last_30_days).values('created_at__date').annotate(
        daily_pnl=Sum('pnl'),
        total_trades=Count('id'),
        win_trades=Sum(Case(When(win='YES', then=1), output_field=IntegerField()))
    )

    # Przygotowanie danych dla wykresu słupkowego (na podstawie PnL)
    dates = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in daily_pnl_data]
    pnl_values = [entry['daily_pnl'] for entry in daily_pnl_data]

    # Tworzenie wykresu słupkowego dla PnL
    bar_fig_pnl = go.Figure(data=[go.Bar(x=dates, y=pnl_values, 
                                         marker_color=['green' if x >= 0 else 'red' for x in pnl_values])])
    bar_fig_pnl.update_layout(
        title="Daily PnL for the Last 30 Days",
        xaxis_title="Date",
        yaxis_title="PnL",
        yaxis=dict(zeroline=True, zerolinecolor='black'),
    )
    bar_chart_pnl_html = bar_fig_pnl.to_html(full_html=False)

    # Oblicz dzienny winrate (YES / (YES + NO))
    daily_data = []
    for entry in daily_pnl_data:
        date = entry['created_at__date']
        pnl = entry['daily_pnl']
        total_trades = entry['total_trades']
        win_trades = entry['win_trades']
        winrate = round((win_trades / total_trades) * 100, 2) if total_trades > 0 else 0  # Zaokrąglenie do 2 miejsc po przecinku
        daily_data.append({
        'date': date,
        'pnl': pnl,
        'total_trades': total_trades,
        'winrate': winrate  # Zaokrąglone winrate
    })

    # Logika do obliczenia pustych komórek na początku kalendarza
    today = now().date()
    days_in_month = monthrange(today.year, today.month)[1]
    first_day_of_month = today.replace(day=1)
    first_weekday_of_month = first_day_of_month.weekday()  # 0 to Monday

    # Puste komórki przed pierwszym dniem miesiąca
    empty_days_before = first_weekday_of_month

    # Dodanie dodatkowych pustych komórek na końcu, aby zachować pełny układ
    total_cells = empty_days_before + len(daily_data)
    empty_days_after = (7 - total_cells % 7) % 7  # Uzupełnienie do pełnych tygodni

    # Przekazanie raportów i wykresów do szablonu
    return render(request, 'app_main/reports.html', {
        'total_report': total_report,
        'monthly_report': monthly_report,
        'weekly_report': weekly_report,
        'daily_report': daily_report,
        'daily_data': daily_data,  # Przekazujemy dane do kalendarza
        'pie_chart_total_html': pie_chart_total_html,  # Dodanie wykresu kołowego
        'bar_chart_pnl_html': bar_chart_pnl_html,      # Dodanie wykresu PnL
    })


@login_required
def monthly_report_view(request):
    journal_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])
    monthly_report = get_report_for_period(journal_entries, days=30)

    return render(request, 'app_main/monthly_report.html', {
        'monthly_report': monthly_report,
    })

@login_required
def weekly_report_view(request):
    journal_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])
    weekly_report = get_report_for_period(journal_entries, days=7)

    return render(request, 'app_main/weekly_report.html', {
        'weekly_report': weekly_report,
    })

@login_required
def daily_report_view(request):
    journal_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])
    daily_report = get_report_for_period(journal_entries, days=1)

    return render(request, 'app_main/daily_report.html', {
        'daily_report': daily_report,
    })
