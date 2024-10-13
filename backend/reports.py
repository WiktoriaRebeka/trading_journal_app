from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from .utils import calculate_report_data, get_report_for_period

@login_required
def reports_view(request):
    # Pobierz wszystkie transakcje użytkownika z wynikiem YES lub NO
    journal_entries = JournalEntry.objects.filter(user=request.user, win__in=['YES', 'NO'])

    # Raporty dla różnych okresów
    total_report = calculate_report_data(journal_entries)
    monthly_report = get_report_for_period(journal_entries, days=30)
    weekly_report = get_report_for_period(journal_entries, days=7)
    daily_report = get_report_for_period(journal_entries, days=1)

    # Przekazanie raportów do szablonu
    return render(request, 'app_main/reports.html', {
        'total_report': total_report,
        'monthly_report': monthly_report,
        'weekly_report': weekly_report,
        'daily_report': daily_report,
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
