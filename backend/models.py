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
    target_choice = models.CharField(max_length=5)
    calculated_leverage = models.DecimalField(max_digits=5, decimal_places=2)
    calculated_position = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Entry for {self.pair} by {self.user}'
