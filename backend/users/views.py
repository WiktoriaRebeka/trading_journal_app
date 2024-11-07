from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from .forms import LoginForm, RegisterForm, PasswordResetRequestForm, SetNewPasswordForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string

def login_view(request):
    print("Funkcja login_view została wywołana")  # Debugging
    if request.method == 'POST':
        print("POST request otrzymany")  # Debugging
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Logujemy dane wprowadzone przez użytkownika
            print(f"Próba logowania - email: {email}, password: {password}")  # Debugging

            # Spróbuj wyszukać użytkownika na podstawie adresu email
            try:
                user = User.objects.get(email=email)
                print(f"Użytkownik znaleziony: {user.email}")  # Debugging
            except User.DoesNotExist:
                user = None
                print("Użytkownik nie istnieje.")  # Debugging

            # Jeśli użytkownik został znaleziony, sprawdzamy hasło
            if user is not None and user.check_password(password):
                if user.is_active:
                    # Logowanie użytkownika
                    login(request, user)
                    print(f"Użytkownik zalogowany: {user.email}")  # Debugging
                    return redirect('dashboard')
                else:
                    # Konto jest nieaktywne
                    print(f"Konto nieaktywne: {user.email}")  # Debugging
                    form.add_error(None, 'Konto jest nieaktywne.')
            else:
                # Niepoprawny email lub hasło
                print("Błąd logowania: niepoprawny email lub hasło.")  # Debugging
                form.add_error(None, 'Niepoprawny email lub hasło.')
        else:
            print("Formularz logowania nie jest poprawny.")  # Debugging
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



# Widok do żądania resetowania hasła
def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Tworzenie linku do resetowania hasła
                current_site = get_current_site(request)
                mail_subject = 'Reset your password'
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = reverse('password_reset', kwargs={'uidb64': uid, 'token': token})
                reset_url = f"http://{current_site.domain}{reset_link}"
                
                # Wysłanie e-maila
                message = render_to_string('users/password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                })
                send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                return render(request, 'users/password_reset_done.html')
            except User.DoesNotExist:
                form.add_error('email', 'User with this email does not exist.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'users/password_reset_request.html', {'form': form})

# Widok do ustawienia nowego hasła
def password_reset_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                return redirect('login')
        else:
            form = SetNewPasswordForm()
        return render(request, 'users/password_reset_form.html', {'form': form})
    else:
        return render(request, 'users/password_reset_invalid.html')