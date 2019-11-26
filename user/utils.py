# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, authenticate, update_session_auth_hash, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN, INTERNAL_RESET_URL_TOKEN
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.views import View

from main.utils import message, render_template
from user.forms import LoginForm, RegistrationForm, PasswordResetForm, PasswordChangeForm

INTERNAL_RESET_SESSION_UIDB = '_password_reset_uidb64'

class UserAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):

        user_model = get_user_model()

        try:

            try:
                user = user_model.objects.get(username=username)
                if check_password(password, user.password):
                    return user
                else:
                    return None
            except:
                user = user_model.objects.get(email=username)
                if check_password(password, user.password):
                    return user
                else:
                    return None

        except user_model.DoesNotExist:
            return None


def login_view(request):
    if request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            login_user = login_form.save()
            if login_user:
                login(request, login_user)
                return JsonResponse({'response': "Good", 'result': 'success', 'url': reverse('main'), })
        else:
            response = render_template('LoginRegistration/login_form.html',
                                       {'login_form': login_form}, request)
            return JsonResponse({'response': response, 'result': 'error'})


def registration_view(request):
    if request.POST:
        registration_form = RegistrationForm(request.POST)
        if registration_form.is_valid():
            login_user = registration_form.save()
            if login_user:
                login(request, login_user)
                return JsonResponse({'response': "Good", 'result': 'success', 'url': reverse('main'), })
        else:
            response = render_template('LoginRegistration/registration_form.html',
                                       {'registration_form': registration_form}, request)
            return JsonResponse({'response': response, 'result': 'error'})


def password_reset_handler_view(request):
    if request.POST:
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data['email']
            password_reset_form.save(request)
            return JsonResponse(
                {'message': message("На ваш почтовый адрес отправлена инструкция о восстановлении пароля!", request),
                 'result': 'success', 'url': '', })
        else:
            response = render_template('PasswordReset/password_reset_form.html',
                                       {'password_reset_form': password_reset_form}, request)
            return JsonResponse({'response': response, 'result': 'error'})


class password_reset_change_view(View):
    token_generator = default_token_generator

    def get(self, request, uidb64, token):

        self.user = self.get_user(uidb64)

        if self.user is not None:
            if token == INTERNAL_RESET_URL_TOKEN:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    password_change_form = PasswordChangeForm()
                    context = {'password_change_form': password_change_form}
                    return render(request, 'PasswordReset/password_change.html', context)
            else:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    self.request.session[INTERNAL_RESET_SESSION_UIDB] = uidb64
                    redirect_url = self.request.path.replace(token, INTERNAL_RESET_URL_TOKEN)
                    return HttpResponseRedirect(redirect_url)

        return HttpResponseRedirect(reverse('permission'))

    def post(self, request, *args, **kwargs):
        session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
        uid = self.request.session.get(INTERNAL_RESET_SESSION_UIDB)
        self.user = self.get_user(uid)
        if self.user is not None:
            if self.token_generator.check_token(self.user, session_token):
                password_change_form = PasswordChangeForm(request.POST)
                if password_change_form.is_valid():
                    password = password_change_form.cleaned_data['password']
                    self.user.set_password(password)
                    self.user.save()
                    del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
                    del self.request.session[INTERNAL_RESET_SESSION_UIDB]
                    update_session_auth_hash(request, self.user)
                    login_user = authenticate(username=self.user.username, password=password)
                    if login_user:
                        login(request, login_user)
                        return JsonResponse({'response': "Good", 'result': 'success', 'url': reverse('main'), })
                else:
                    response = render_template('PasswordReset/password_change_form.html',
                                               {'password_change_form': password_change_form}, request)
                    return JsonResponse({'response': response, 'result': 'error'})

        return HttpResponseRedirect(reverse('permission'))

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model()._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist, ValidationError):
            user = None
        return user


def password_change_view(request):
    if request.user.profile.social:
        return redirect('permission')

    if request.POST:
        password_change_form = PasswordChangeForm(request.POST)
        if password_change_form.is_valid():
            password = password_change_form.cleaned_data['password']
            user = request.user
            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'response': "Good", 'result': 'success', 'message':message('Пароль успешно изменен!',request), 'url': reverse('main'), })
        else:
            response = render_template('PasswordReset/password_change_form.html',
                                       {'password_change_form': password_change_form}, request)
            return JsonResponse({'response': response, 'result': 'error'})
