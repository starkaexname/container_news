import re
from captcha.fields import CaptchaField, CaptchaTextInput
from django import forms
from django.core.exceptions import ValidationError
from .models import News
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Адрес электронной почты',
        widget=forms.EmailInput(
            attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=12, min_length=5, label='Имя пользователя', help_text='заполните поля',
        widget=forms.TextInput(
            attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        max_length=14, min_length=6, label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        max_length=14, min_length=6, label='Повтор пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email',  'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=12, min_length=5, label='Имя пользователя',
        widget=forms.TextInput(
            attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        max_length=14, min_length=6, label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class NewsForm(forms.ModelForm):
    # content = forms.CharField(widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"}), config_name="default")
    # title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # category = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = News
        fields = ['title', 'full_text', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'full_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if re.match(r'\d', title):
            raise ValidationError('Тема не должна начинаться с цифры')
        return title


class CustomCaptchaTextInput(CaptchaTextInput):
    pass


class ContactForm(forms.Form):
    subject = forms.CharField(
        max_length=60, min_length=5, label='Тема',
        widget=forms.TextInput(
            attrs={'class': 'form-control'})
    )
    content = forms.CharField(
        max_length=500, label='Текст письма', widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 15})
    )
    captcha = CaptchaField(widget=CustomCaptchaTextInput)
