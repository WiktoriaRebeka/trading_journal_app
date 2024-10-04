from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254, 
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'})
    )
