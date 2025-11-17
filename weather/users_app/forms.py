from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from weather.users_app.models import CustomUser
from django.forms import CharField
from django import forms


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for password in ('password1', 'password2'):
            self.fields[password].widget.attrs['maxlength'] = 30


class LoginUserForm(AuthenticationForm):
    username = CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = CharField(max_length=30, label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')
