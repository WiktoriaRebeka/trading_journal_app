# backend/models.py

from django.db import models


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