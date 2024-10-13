from django.db.models import Avg
from datetime import timedelta
from django.utils import timezone

def calculate_report_data(journal_entries):
    """Funkcja pomocnicza do obliczania ogólnych statystyk."""
    yes_count = journal_entries.filter(win='YES').count()
    no_count = journal_entries.filter(win='NO').count()
    total_trades = yes_count + no_count
    win_rate = round((yes_count / total_trades) * 100, 2) if total_trades > 0 else 0
    avg_rrr = journal_entries.aggregate(Avg('target_choice'))['target_choice__avg']
    avg_rrr = round(avg_rrr, 2) if avg_rrr else 0
    min_win_rate = round((1 / (avg_rrr + 1)) * 100, 2) if avg_rrr else 0
    is_profitable = win_rate >= min_win_rate

    return {
        'total_trades': total_trades,
        'yes_count': yes_count,
        'no_count': no_count,
        'win_rate': win_rate,
        'avg_rrr': avg_rrr,
        'min_win_rate': min_win_rate,
        'is_profitable': is_profitable
    }


def get_report_for_period(journal_entries, days=None):
    """Funkcja pomocnicza do obliczania statystyk dla okresu (miesięczny, tygodniowy, dzienny)."""
    now = timezone.now()
    if days:
        start_date = now - timedelta(days=days)
        journal_entries = journal_entries.filter(created_at__gte=start_date)
    
    return calculate_report_data(journal_entries)
