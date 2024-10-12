from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from .models import JournalEntry

@login_required
@login_required
def reports_view(request):
    now = timezone.now()

    # Pobierz wszystkie transakcje użytkownika z wynikiem YES lub NO
    journal_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])

    # ---- Raport ogólny ----
    yes_count_total = journal_entries.filter(win='YES').count()
    no_count_total = journal_entries.filter(win='NO').count()
    total_trades_total = yes_count_total + no_count_total

    win_rate_total = round((yes_count_total / total_trades_total) * 100, 2) if total_trades_total > 0 else 0

    # Średnie Risk-Reward Ratio (RRR) dla ogółu
    avg_rrr_total = journal_entries.aggregate(Avg('target_choice'))['target_choice__avg']
    avg_rrr_total = round(avg_rrr_total, 2) if avg_rrr_total else 0

    # Minimalny wymagany win rate dla ogółu
    min_win_rate_total = round((1 / (avg_rrr_total + 1)) * 100, 2) if avg_rrr_total else 0
    is_profitable_total = win_rate_total >= min_win_rate_total

    # ---- Raport miesięczny ----
    one_month_ago = now - timedelta(days=30)
    journal_entries_month = journal_entries.filter(created_at__gte=one_month_ago)

    yes_count_month = journal_entries_month.filter(win='YES').count()
    no_count_month = journal_entries_month.filter(win='NO').count()
    total_trades_month = yes_count_month + no_count_month
    win_rate_month = round((yes_count_month / total_trades_month) * 100, 2) if total_trades_month > 0 else 0

    # Średnie RRR dla raportu miesięcznego
    avg_rrr_month = journal_entries_month.aggregate(Avg('target_choice'))['target_choice__avg']
    avg_rrr_month = round(avg_rrr_month, 2) if avg_rrr_month else 0

    # Minimalny wymagany win rate dla raportu miesięcznego
    min_win_rate_month = round((1 / (avg_rrr_month + 1)) * 100, 2) if avg_rrr_month else 0
    is_profitable_month = win_rate_month >= min_win_rate_month

    # ---- Raport tygodniowy ----
    one_week_ago = now - timedelta(days=7)
    journal_entries_week = journal_entries.filter(created_at__gte=one_week_ago)

    yes_count_week = journal_entries_week.filter(win='YES').count()
    no_count_week = journal_entries_week.filter(win='NO').count()
    total_trades_week = yes_count_week + no_count_week
    win_rate_week = round((yes_count_week / total_trades_week) * 100, 2) if total_trades_week > 0 else 0

    # Średnie RRR dla raportu tygodniowego
    avg_rrr_week = journal_entries_week.aggregate(Avg('target_choice'))['target_choice__avg']
    avg_rrr_week = round(avg_rrr_week, 2) if avg_rrr_week else 0

    # Minimalny wymagany win rate dla raportu tygodniowego
    min_win_rate_week = round((1 / (avg_rrr_week + 1)) * 100, 2) if avg_rrr_week else 0
    is_profitable_week = win_rate_week >= min_win_rate_week

    # ---- Raport dzienny ----
    today = now.date()  # Dzisiaj jako data (bez godziny)
    journal_entries_day = journal_entries.filter(created_at__date=today)

    yes_count_day = journal_entries_day.filter(win='YES').count()
    no_count_day = journal_entries_day.filter(win='NO').count()
    total_trades_day = yes_count_day + no_count_day

    win_rate_day = round((yes_count_day / total_trades_day) * 100, 2) if total_trades_day > 0 else 0

    # Średnie RRR dla raportu dziennego
    avg_rrr_day = journal_entries_day.aggregate(Avg('target_choice'))['target_choice__avg']
    avg_rrr_day = round(avg_rrr_day, 2) if avg_rrr_day else 0

    # Minimalny wymagany win rate dla raportu dziennego
    min_win_rate_day = round((1 / (avg_rrr_day + 1)) * 100, 2) if avg_rrr_day else 0
    is_profitable_day = win_rate_day >= min_win_rate_day

    # Przekazanie zmiennych do szablonu
    return render(request, 'app_main/reports.html', {
        'total_trades_total': total_trades_total,
        'yes_count_total': yes_count_total,
        'no_count_total': no_count_total,
        'win_rate_total': win_rate_total,
        'avg_rrr_total': avg_rrr_total,
        'min_win_rate_total': min_win_rate_total,
        'is_profitable_total': is_profitable_total,

        'total_trades_month': total_trades_month,
        'yes_count_month': yes_count_month,
        'no_count_month': no_count_month,
        'win_rate_month': win_rate_month,
        'avg_rrr_month': avg_rrr_month,
        'min_win_rate_month': min_win_rate_month,
        'is_profitable_month': is_profitable_month,

        'total_trades_week': total_trades_week,
        'yes_count_week': yes_count_week,
        'no_count_week': no_count_week,
        'win_rate_week': win_rate_week,
        'avg_rrr_week': avg_rrr_week,
        'min_win_rate_week': min_win_rate_week,
        'is_profitable_week': is_profitable_week,

        'total_trades_day': total_trades_day,
        'yes_count_day': yes_count_day,
        'no_count_day': no_count_day,
        'win_rate_day': win_rate_day,
        'avg_rrr_day': avg_rrr_day,
        'min_win_rate_day': min_win_rate_day,
        'is_profitable_day': is_profitable_day,
    })

@login_required
def monthly_report_view(request):
    one_month_ago = timezone.now() - timedelta(days=30)
    user_entries = JournalEntry.objects.filter(user=request.user, created_at__gte=one_month_ago, win__in=['YES', 'NO'])

    yes_count = user_entries.filter(win="YES").count()
    no_count = user_entries.filter(win="NO").count()
    total_trades = yes_count + no_count

    avg_rrr = user_entries.aggregate(Avg('target_choice'))['target_choice__avg']
    avg_rrr = round(avg_rrr, 2) if avg_rrr else 0

    win_rate = round((yes_count / total_trades) * 100, 2) if total_trades > 0 else 0

    return render(request, 'app_main/monthly_report.html', {
        'yes_count': yes_count,
        'no_count': no_count,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_rrr': avg_rrr,
    })

@login_required
def weekly_report_view(request):
    one_week_ago = timezone.now() - timedelta(days=7)
    user_entries = JournalEntry.objects.filter(user=request.user, created_at__gte=one_week_ago, win__in=['YES', 'NO'])

    yes_count = user_entries.filter(win="YES").count()
    no_count = user_entries.filter(win="NO").count()
    total_trades = yes_count + no_count

    avg_rrr = user_entries.aggregate(Avg('target_choice'))['target_choice__avg']
    avg_rrr = round(avg_rrr, 2) if avg_rrr else 0

    win_rate = round((yes_count / total_trades) * 100, 2) if total_trades > 0 else 0

    return render(request, 'app_main/weekly_report.html', {
        'yes_count': yes_count,
        'no_count': no_count,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_rrr': avg_rrr,
    })

@login_required
def daily_report_view(request):
    # Pobierz dzisiejszą datę
    today = timezone.now().date()

    # Filtruj wpisy na podstawie dokładnej daty (bez uwzględnienia czasu)
    user_entries = JournalEntry.objects.filter(
        user=request.user, 
        created_at__date=today,  # Dopasowujemy tylko datę, bez czasu
        win__in=['YES', 'NO']
    )

    # Obliczenia dla transakcji z wynikiem YES i NO
    yes_count = user_entries.filter(win="YES").count()
    no_count = user_entries.filter(win="NO").count()
    total_trades = yes_count + no_count

    # Obliczamy średnie Risk-Reward Ratio dla wpisów, które mają określony target_choice
    target_entries = user_entries.exclude(target_choice__isnull=True).exclude(target_choice="")
    avg_risk_reward = target_entries.aggregate(Avg('target_choice'))['target_choice__avg']

    # Obliczamy WinRate
    if total_trades > 0:
        win_rate = (yes_count / total_trades) * 100
    else:
        win_rate = 0

    # Renderowanie strony z wynikami
    return render(request, 'app_main/daily_report.html', {
        'yes_count': yes_count,
        'no_count': no_count,
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'avg_risk_reward': round(avg_risk_reward, 2) if avg_risk_reward else 0,
    })

