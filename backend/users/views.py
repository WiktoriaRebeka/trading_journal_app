from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Po zalogowaniu przekieruj na dashboard
            else:
                form.add_error(None, 'Niepoprawny email lub hasło')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})
