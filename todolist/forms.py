from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField

from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Логін',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Логін', 'class': 'form-control'})
    )
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'class': 'form-control'}))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=50)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class TaskForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'priority', 'ended_at']
        widgets = {
            'ended_at': DateInput(),
        }
