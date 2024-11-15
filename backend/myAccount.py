# myAccount.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages

@login_required
def my_account_view(request):
    return render(request, "app_main/my_account.html")


# Zmiana e-maila z weryfikacją
@login_required
def send_verification_code(request):
    if request.method == "POST":
        new_email = request.POST.get("new_email")
        # Tu powinno się wygenerować i wysłać kod weryfikacyjny na nowy e-mail
        # Kod do wysyłania e-maila...
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Zmiana hasła
@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        user = request.user
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Utrzymanie sesji po zmianie hasła
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Incorrect current password"})
    return JsonResponse({"success": False})

# Dodawanie metody płatności
@login_required
def add_payment_method(request):
    if request.method == "POST":
        # Obsługa zapisu danych karty w bazie
        card_number = request.POST.get("card_number")
        expiry_date = request.POST.get("expiry_date")
        cvv = request.POST.get("cvv")
        # Kod zapisu nowej metody płatności...
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Usuwanie metody płatności
@login_required
def delete_payment_method(request, method_id):
    if request.method == "DELETE":
        # Logika usunięcia metody płatności z bazy
        # Przykład: PaymentMethod.objects.filter(id=method_id, user=request.user).delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Wyświetlanie historii płatności
@login_required
def payment_history(request):
    # Pobranie historii płatności użytkownika i przekazanie jej do szablonu
    # Example: payments = Payment.objects.filter(user=request.user).order_by("-date")
    # context = {"payments": payments}
    return render(request, "payment_history.html")
