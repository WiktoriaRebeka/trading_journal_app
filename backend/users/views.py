from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from .forms import LoginForm, RegisterForm
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:  # Sprawdzenie, czy konto jest aktywne
                login(request, user)
                return redirect('dashboard')  # Po zalogowaniu przekieruj na dashboard
            else:
                form.add_error(None, 'Niepoprawny email, hasło lub konto nieaktywne.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def dashboard_view(request):
    return render(request, 'app_main/dashboard.html')  # Zakładamy, że dashboard.html jest w templates/app_main

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Konto nieaktywne do czasu aktywacji
            user.save()

            # Wyślij e-mail aktywacyjny
            current_site = get_current_site(request)
            activation_link = reverse('activate', kwargs={'user_id': user.id})
            activation_url = f"http://{current_site.domain}{activation_link}"

            # Wysłanie e-maila aktywacyjnego (pójdzie do konsoli w trybie testowym)
            subject = 'Activate your account'
            message = f'Click the link to activate your account: {activation_url}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)

            return render(request, 'users/activation_pending.html')  # Informacja o wysłanym mailu
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

def activate_account(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True  # Aktywacja konta
    user.save()
    return redirect('login')  # Po aktywacji przekierowanie na stronę logowania
