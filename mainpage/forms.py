from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import (
    Category, Product, Review, Profile
)
import re

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отзыв...'}),
        }
        labels = {
            'rating': 'Оценка',
            'comment': 'Комментарий',
        }

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите имя',
            'pattern': '[A-ZА-Я][a-zа-я]*',
            'title': 'Имя должно начинаться с заглавной буквы и содержать только буквы'
        }),
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите фамилию',
            'pattern': '[A-ZА-Я][a-zа-я]*',
            'title': 'Фамилия должна начинаться с заглавной буквы и содержать только буквы'
        }),
        label='Фамилия'
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите логин',
            'minlength': '3',
            'maxlength': '150'
        }),
        label='Логин'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@mail.com'
        }),
        label='Email'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль',
            'minlength': '8'
        }),
        label='Пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтвердите пароль',
            'minlength': '8'
        }),
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[A-ZА-Я][a-zа-я]*$', first_name):
            raise forms.ValidationError('Имя должно начинаться с заглавной буквы и содержать только буквы')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[A-ZА-Я][a-zа-я]*$', last_name):
            raise forms.ValidationError('Фамилия должна начинаться с заглавной буквы и содержать только буквы')
        return last_name

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов')
        if not any(c.isdigit() for c in password1):
            raise forms.ValidationError('Пароль должен содержать хотя бы одну цифру')
        if not any(c.isupper() for c in password1):
            raise forms.ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(user=user)
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите логин'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        })
    )


class FeedbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ваше имя'
        }),
        validators=[
            RegexValidator(
                r'^[A-ZА-Я][a-zа-я]*$',
                'Имя должно начинаться с заглавной буквы и содержать только буквы'
            )
        ]
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ваш email'
        })
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+7 (___) ___-__-__'
        })
    )

    subject = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Тема сообщения'
        })
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 5,
            'placeholder': 'Ваше сообщение'
        })
    )