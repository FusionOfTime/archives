from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("Поле имени пользователя обязательно.")

        if len(username) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа.")

        if len(username) > 150:
            raise ValidationError("Имя пользователя должно содержать не более 150 символов.")

        # Важная проверка: только разрешенные символы
        valid_chars = r'^[a-zA-Z0-9._@+-]+$'
        import re
        if not re.match(valid_chars, username):
            raise ValidationError(
                "Имя пользователя может содержать только латинские буквы, цифры, и символы @, ., +, -, _.")

        return username


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:  # Минимальная длина имени пользователя - 3 символа.
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа.")
        return username


class ProfileEditForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('username',)


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')