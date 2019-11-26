# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from order.models import Address


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин или email'
        self.fields['password'].label = 'Пароль'
        self.fields['username'].help_text = 'Логин или email'
        self.fields['password'].help_text = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=username).exists():
                self.add_error("username", "Пользователь с данным логином не зарегистрирован в системе!")

        user = None
        try:
            user = User.objects.get(username=username)
        except:
            try:
                user = User.objects.get(email=username)
            except:
                self.add_error("password", "Неверный пароль!")
                return

        if not user.check_password(password):
            self.add_error("password", "Неверный пароль!")
            return

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        return authenticate(username=username, password=password)


class RegistrationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['email'].label = 'Email'

        self.fields['username'].help_text = 'Логин'
        self.fields['password'].help_text = 'Пароль'
        self.fields['email'].help_text = 'Email'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        try:
            email = self.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                self.add_error('email', 'Пользователь с данным почтовым адресом уже зарегистрирован!')
        except:
            pass

        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Пользователь с данным логином уже зарегистрирован в системе!')

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']
        new_user = User()
        new_user.username = username
        new_user.set_password(password)
        new_user.email = email
        new_user.save()
        return authenticate(username=username, password=password)


class PasswordResetForm(forms.Form):
    email = forms.EmailField()

    def get_users(self, email):
        active_users = get_user_model()._default_manager.filter(**{
            '%s__iexact' % get_user_model().get_email_field_name(): email,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())

    def save(self, request):

        email = self.cleaned_data["email"]

        for user in self.get_users(email):
            context = {
                'email': email,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': PasswordResetTokenGenerator().make_token(user),
            }

            from main.utils import send_html_email
            send_html_email(request, 'PasswordReset/password_reset_email.html', "Восстановление пароля", email, context)

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = 'Email'
        self.fields['email'].help_text = 'Email'

    def clean(self):
        try:
            email = self.cleaned_data['email']
            user = User.objects.filter(email=email)
            if not user.exists():
                self.add_error('email', 'Пользователь с данным почтовым адресом не зарегистрирован!')
            if user.exists() and user[0].profile.social:
                self.add_error('email', 'Войдите через социальные сети!')
        except:
            pass


class PasswordChangeForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = 'Новый пароль'
        self.fields['password_confirm'].label = 'Повторите пароль'
        self.fields['password'].help_text = 'Новый пароль'
        self.fields['password_confirm'].help_text = 'Повторите пароль'

    def clean(self):
        password_confirm = self.cleaned_data['password_confirm']
        password = self.cleaned_data['password']
        if password != password_confirm:
            self.add_error("password_confirm", "Пароли не совпадают!")


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean(self):
        try:
            email = self.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                if User.objects.filter(email=email)[0] != self.instance:
                    self.add_error('email', 'Пользователь с данным почтовым адресом уже зарегистрирован!')
        except:
            pass


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

    def set_readonly(self):
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True

        if self.cleaned_data['room'] == None:
            self.fields['room'].widget.attrs['placeholder'] = ''

        if self.cleaned_data['area'] == None:
            self.fields['area'].widget.attrs['placeholder'] = ''
