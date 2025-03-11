from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, ResearchArea
from django.utils.translation import gettext_lazy as _


class EmailVerificationForm(forms.Form):
    otp_code = forms.CharField(label="OTP Code", max_length=6)


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'interests', 'research_area')


class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)


class AccountAuthenticationForm(forms.ModelForm):
    """
      Form for Logging in  users
    """
    fingerprint = forms.CharField(max_length=255, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('email', 'password', 'fingerprint')
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'fingerprint': forms.HiddenInput(attrs={'class': 'form-control'})
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'role', 'research_area', 'interests', 'birth_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['research_area'].queryset = ResearchArea.objects.all()


# forms.py
from django import forms

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
