from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class DashboardTemplateTests(TestCase):
    def setUp(self):
        # Tworzymy użytkownika testowego
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_dashboard_template(self):
        # Logujemy się jako użytkownik testowy
        self.client.login(username='testuser', password='testpass')
        
        # Wysyłamy żądanie GET do widoku dashboard
        response = self.client.get(reverse('dashboard'))
        
        # Sprawdzamy, czy odpowiedź zawiera poprawny szablon
        self.assertTemplateUsed(response, 'app_main/dashboard.html')
        
        # Sprawdzamy, czy odpowiedź zawiera poprawny tekst powitalny
        self.assertContains(response, 'Welcome, testuser!')


class JournalTemplateTests(TestCase):
    def setUp(self):
        # Tworzymy użytkownika testowego
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_journal_template(self):
        # Logujemy się jako użytkownik testowy
        self.client.login(username='testuser', password='testpass')

        # Wysyłamy żądanie GET do widoku journal
        response = self.client.get(reverse('journal'))

        # Sprawdzamy, czy odpowiedź zawiera poprawny szablon
        self.assertTemplateUsed(response, 'app_main/journal.html')


class ReportsTemplateTests(TestCase):
    def setUp(self):
        # Tworzymy użytkownika testowego
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_reports_template(self):
        # Logujemy się jako użytkownik testowy
        self.client.login(username='testuser', password='testpass')

        # Wysyłamy żądanie GET do widoku reports
        response = self.client.get(reverse('reports'))

        # Sprawdzamy, czy odpowiedź zawiera poprawny szablon
        self.assertTemplateUsed(response, 'app_main/reports.html')


class StrategiesTemplateTests(TestCase):
    def setUp(self):
        # Tworzymy użytkownika testowego
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_strategies_template(self):
        # Logujemy się jako użytkownik testowy
        self.client.login(username='testuser', password='testpass')

        # Wysyłamy żądanie GET do widoku strategies
        response = self.client.get(reverse('strategies'))

        # Sprawdzamy, czy odpowiedź zawiera poprawny szablon
        self.assertTemplateUsed(response, 'app_main/strategies.html')
