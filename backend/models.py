# backend/models.py

from django.db import models
from django.contrib.auth.models import User  # Import modelu User

class Currency(models.Model):
    name = models.CharField(max_length=100)  # Nazwa waluty, np. dolar amerykański
    code = models.CharField(max_length=3)    # Kod waluty, np. USD
    symbol = models.CharField(max_length=5)  # Symbol waluty, np. $

    def __str__(self):
        return f"{self.name} ({self.code})"

class Pair(models.Model):
    name = models.CharField(max_length=10, unique=True)  # Np. BTC/USDT

    def __str__(self):
        return self.name

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    risk = models.DecimalField(max_digits=5, decimal_places=2)
    risk_type = models.CharField(max_length=10)
    position = models.DecimalField(max_digits=10, decimal_places=2)
    position_type = models.CharField(max_length=10)
    pair = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=5)
    entry_price = models.DecimalField(max_digits=10, decimal_places=4)
    stop_loss = models.DecimalField(max_digits=10, decimal_places=4)
    fee = models.DecimalField(max_digits=5, decimal_places=4)
    target_choice = models.CharField(max_length=20)  
    target_price = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    calculated_leverage = models.DecimalField(max_digits=5, decimal_places=2)
    calculated_position = models.DecimalField(max_digits=10, decimal_places=2)
    calculated_risk_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Nowe pole na obliczoną wartość ryzyka
    calculated_win_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    win = models.CharField(max_length=3, choices=[('YES', 'YES'), ('NO', 'NO')], null=True, blank=True)
    pnl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Nowe pole PnL
    date_added = models.DateTimeField(null=True, blank=True)  # Nowe pole na datę dodania wpisu
    entry_date = models.DateTimeField(null=True, blank=True)  # Data wejścia
    exit_date = models.DateTimeField(null=True, blank=True)  # Data wyjścia
    strategy = models.ForeignKey('Strategy', on_delete=models.SET_NULL, null=True, blank=True)  # Dodajemy strategię



    def __str__(self):
        return f'Entry for {self.pair} by {self.user}'


class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    timeframe = models.CharField(max_length=10)
    indicators = models.CharField(max_length=255)
    entry_rules = models.TextField()
    exit_rules = models.TextField()
    type = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Attachment(models.Model):
    strategy = models.ForeignKey(Strategy, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')

    def __str__(self):
        return self.file.name