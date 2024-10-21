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

    # Raporty dla różnych okresów (nie zmieniają się z miesiącem)
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
            # Dodaj puste dni, gdzie nie było żadnych transakcji
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
    empty_days_after = [''] * ((7 - total_cells % 7) % 7)  # Lista pustych miejsc

    # Poprzedni i następny miesiąc (nawigacja strzałkami)
    previous_month = selected_date - timedelta(days=1)
    previous_month_url = f"?year={previous_month.year}&month={previous_month.month}"
    next_month = selected_date + timedelta(days=days_in_month)
    next_month_url = f"?year={next_month.year}&month={next_month.month}"

    # --------- Tworzenie wykresu kołowego (pie chart) dla ogólnego raportu ---------
    pie_fig_total = go.Figure(data=[go.Pie(labels=['Win', 'Lose'], 
                                           values=[total_report['yes_count'], total_report['no_count']])])
    pie_fig_total.update_layout(title="Win vs Lose - Total")
    pie_chart_total_html = pie_fig_total.to_html(full_html=False)

    # Pie chart dla ostatnich 30 dni
    pie_fig_monthly = go.Figure(data=[go.Pie(labels=['Win', 'Lose'], 
                                             values=[monthly_report['yes_count'], monthly_report['no_count']])])
    pie_fig_monthly.update_layout(title="Win vs Lose - Last 30 Days")
    pie_chart_monthly_html = pie_fig_monthly.to_html(full_html=False)

    # Pie chart dla dzisiejszego dnia
    pie_fig_daily = go.Figure(data=[go.Pie(labels=['Win', 'Lose'], 
                                           values=[daily_report['yes_count'], daily_report['no_count']])])
    pie_fig_daily.update_layout(title="Win vs Lose - Today")
    pie_chart_daily_html = pie_fig_daily.to_html(full_html=False)

    # Przygotowanie danych dla wykresu słupkowego (PnL)
    dates = [entry['entry_date__date'].strftime('%Y-%m-%d') for entry in daily_pnl_data]
    pnl_values = [entry['daily_pnl'] for entry in daily_pnl_data]

    # Tworzenie wykresu słupkowego dla PnL
    bar_fig_pnl = go.Figure(data=[go.Bar(x=dates, y=pnl_values, 
                                         marker_color=['green' if x >= 0 else 'red' for x in pnl_values])])
    bar_fig_pnl.update_layout(
        title="Daily PnL for the Selected Month",
        xaxis_title="Date",
        yaxis_title="PnL",
        yaxis=dict(zeroline=True, zerolinecolor='black'),
    )
    bar_chart_pnl_html = bar_fig_pnl.to_html(full_html=False)

    # Przekazanie raportów i wykresów do szablonu
    return render(request, 'app_main/reports.html', {
        'total_report': total_report,
        'monthly_report': monthly_report,
        'daily_report': daily_report,
        'daily_data': daily_data,  # Przekazujemy dane do kalendarza
        'empty_days_before': empty_days_before,  # Puste dni przed
        'empty_days_after': empty_days_after,    # Puste dni po
        'pie_chart_total_html': pie_chart_total_html,  # Dodanie wykresu kołowego (total)
        'pie_chart_monthly_html': pie_chart_monthly_html,  # Dodanie wykresu kołowego (30 dni)
        'pie_chart_daily_html': pie_chart_daily_html,  # Dodanie wykresu kołowego (dzienny)
        'bar_chart_pnl_html': bar_chart_pnl_html,      # Dodanie wykresu PnL
        'current_month': selected_date.strftime('%B %Y'),  # Nazwa miesiąca
        'previous_month_url': previous_month_url,  # URL do poprzedniego miesiąca
        'next_month_url': next_month_url,  # URL do następnego miesiąca
    })
