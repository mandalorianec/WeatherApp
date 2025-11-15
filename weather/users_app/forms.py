from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from weather.users_app.models import CustomUser
from django.forms import EmailField, CharField
from django import forms


class SignUpForm(UserCreationForm):
    email = EmailField(max_length=254, help_text="Обязательное поле")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


    class Meta:
        model = get_user_model()
        fields = ('username', 'password')
