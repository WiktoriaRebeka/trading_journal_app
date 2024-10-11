from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from .models import JournalEntry

@login_required
def reports_view(request):
    user_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])

    # Liczba transakcji YES i NO
    yes_count = user_entries.filter(win="YES").count()
    no_count = user_entries.filter(win="NO").count()
    total_trades = yes_count + no_count

    # Średni Risk-Reward Ratio
    target_entries = user_entries.exclude(target_choice__isnull=True).exclude(target_choice="")
    avg_risk_reward = target_entries.aggregate(Avg('target_choice'))['target_choice__avg']

    if total_trades > 0:
        win_rate = (yes_count / total_trades) * 100
    else:
        win_rate = 0

    return render(request, 'app_main/reports.html', {
        'yes_count': yes_count,
        'no_count': no_count,
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'avg_risk_reward': round(avg_risk_reward, 2) if avg_risk_reward else 0,
    })


@login_required
def monthly_report_view(request):
    one_month_ago = timezone.now() - timedelta(days=30)
    user_entries = JournalEntry.objects.filter(user=request.user, created_at__gte=one_month_ago, win__in=['YES', 'NO'])

    yes_count = user_entries.filter(win="YES").count()
    no_count = user_entries.filter(win="NO").count()
    total_trades = yes_count + no_count

    target_entries = user_entries.exclude(target_choice__isnull=True).exclude(target_choice="")
    avg_risk_reward = target_entries.aggregate(Avg('target_choice'))['target_choice__avg']

    if total_trades > 0:
        win_rate = (yes_count / total_trades) * 100
    else:
        win_rate = 0

    return render(request, 'app_main/monthly_report.html', {
        'yes_count': yes_count,
        'no_count': no_count,
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'avg_risk_reward': round(avg_risk_reward, 2) if avg_risk_reward else 0,
    })

# Dodaj również tygodniowy i dzienny widok, jeśli potrzebujesz
@login_required
def weekly_report_view(request):
    one_week_ago = timezone.now() - timedelta(days=7)
    user_entries = JournalEntry.objects.filter(user=request.user, created_at__gte=one_week_ago, win__in=['YES', 'NO'])

    yes_count = user_entries.filter(win="YES").count()
    no_count = user_entries.filter(win="NO").count()
    total_trades = yes_count + no_count

    target_entries = user_entries.exclude(target_choice__isnull=True).exclude(target_choice="")
    avg_risk_reward = target_entries.aggregate(Avg('target_choice'))['target_choice__avg']

    if total_trades > 0:
        win_rate = (yes_count / total_trades) * 100
    else:
        win_rate = 0

    return render(request, 'app_main/weekly_report.html', {
        'yes_count': yes_count,
        'no_count': no_count,
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'avg_risk_reward': round(avg_risk_reward, 2) if avg_risk_reward else 0,
    })


@login_required
def daily_report_view(request):
    today = timezone.now().date()
    user_entries = JournalEntry.objects.filter(user=request.user, created_at__date=today, win__in=['YES', 'NO'])

    yes_count = user_entries.filter(win="YES").count()
    no_count = user_entries.filter(win="NO").count()
    total_trades = yes_count + no_count

    target_entries = user_entries.exclude(target_choice__isnull=True).exclude(target_choice="")
    avg_risk_reward = target_entries.aggregate(Avg('target_choice'))['target_choice__avg']

    if total_trades > 0:
        win_rate = (yes_count / total_trades) * 100
    else:
        win_rate = 0

    return render(request, 'app_main/daily_report.html', {
        'yes_count': yes_count,
        'no_count': no_count,
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'avg_risk_reward': round(avg_risk_reward, 2) if avg_risk_reward else 0,
    })
