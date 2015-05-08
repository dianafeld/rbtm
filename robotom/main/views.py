# -*- coding: utf-8 -*-
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from forms import UserRegistrationForm, UserProfileRegistrationForm, UserRoleRequestForm, UserProfileFormDisabled, UserProfileFormEnabled, InactiveAuthenticationForm
from models import UserProfile, RoleRequest
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
import logging
import hashlib
import datetime
import random
from serializers import UserSerializer
import requests
import urllib2
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.response import Response
from requests.exceptions import Timeout
from django.forms import ValidationError

logger = logging.getLogger('django.request')
rest_logger = logging.getLogger('rest_logger')

def index(request):
    return render(request, 'main/index.html', {'caption': 'ROBO-TOM'})


def group1(request):
    return render(request, 'main/group_1.html', {'caption': 'Группа 1'})


def group2(request):
    return render(request, 'main/group_2.html', {'caption': "Группа 2"})


def group3(request):
    return render(request, 'main/group_3.html', {'caption': "Группа 3"})


def confirm_view(request, activation_key):
    userprofile = get_object_or_404(UserProfile, activation_key=activation_key)
    userprofile.user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth_login(request, userprofile.user)
    userprofile.user.is_active = True
    userprofile.user.save()
    messages.success(request, 'Ваш профиль был успешно подтверждён!')
    return redirect(reverse('main:role_request'))

'''
Making attempt to send user data to another module.
If everything is OK, returns None, else returns redirect to error page
'''
def try_user_sending(request, err_text, address, user=None, user_info=None):
    if not settings.REQUEST_DEBUG:
        if not user_info:
            user_info = json.dumps({'username': user.username, 'password': user.password, 'role': 'GST'})
        try:
            answer = requests.post(address, user_info, timeout=1)
            if answer.status_code != 200:
                messages.warning(request, u'{}. Модуль "Хранилище" завершил работу с кодом ошибки {}'.format(err_text, answer.status_code))
                logger.error(u'{}. Модуль "Хранилище" завершил работу с кодом ошибки {}'.format(err_text, answer.status_code))
                return redirect(reverse('main:done'))
        except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Хранилище". {}.'. format(err_text))
                logger.error(e)
                return redirect(reverse('main:done'))
        except BaseException as e:
                logger.error(e)
                messages.warning(request, 'Ошибка связи с модулем "Хранилище", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('main:done'))
    return None


def registration_view(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        userprofile_form = UserProfileRegistrationForm(request.POST)
        if user_form.is_valid() and userprofile_form.is_valid():            
            user = user_form.save(commit=False)
            user.is_active = False
            new_profile = userprofile_form.save(commit=False)
            
            attempt = try_user_sending(request, u'Невозможно завершить регистрацию', settings.STORAGE_CREATE_USER_HOST, user=user)
            
            if attempt: #if something went wrong
                return attempt
            
            user.save()
            
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_key = hashlib.sha1(salt + user.email).hexdigest()
            new_profile.user = user
            new_profile.activation_key = activation_key
            activation_link = u'{}/accounts/confirm/{}'.format(request.get_host(), activation_key) 
            email_subject = '[Томограф] Подтверждение регистрации'
            email_body = u"Приветствуем Вас на сайте Robo-Tom, {}!\n Для активации аккаунта пройдите по следующей ссылке: {}".format(user.username, activation_link)

            try:
                send_mail(email_subject, email_body, 'robotomproject@gmail.com',
                        [user.email], fail_silently=False)
            except BaseException:
                messages.warning(request, 'Произошла ошибка при отправке письма о подтверждении регистрации. Попробуйте зарегистрироваться повторно, указав корректный email')
            else:
                messages.success(request, 'На указанный Вами адрес было отправлено письмо. Для завершения регистрации и подтверждения адреса перейдите по ссылке, указанной в письме')
            new_profile.save()
            userprofile_form.save_m2m()
            return redirect(reverse('main:done'))
        else:
            return render(request, 'registration/registration_form.html', {
            'user_form': user_form,
            'userprofile_form': userprofile_form,
            'caption': 'Регистрация'
            })

    return render(request, 'registration/registration_form.html', {
        'user_form': UserRegistrationForm(),
        'userprofile_form': UserProfileRegistrationForm(),
        'caption': 'Регистрация'
    })


def login_view(request):
    if request.method == 'POST':
        login_form = InactiveAuthenticationForm(data=request.POST)
        if login_form.is_valid():   
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                return redirect(reverse('main:profile'))
            else:
                return render(request, 'registration/login.html', {
                    'form': login_form,
                    'caption': 'Вход на сайт'
                })
        else:
            return render(request, 'registration/login.html', {
                'form': login_form,
                'caption': 'Вход на сайт'
            })
    else:   
        return render(request, 'registration/login.html', {
            'form': InactiveAuthenticationForm(),
            'caption': 'Вход на сайт'
        })


def done_view(request):
    return render(request, 'main/done.html', {'caption': 'Успех'})


@login_required
def profile_view(request):
    if not request.user.is_active:
        messages.info(request, u'Для доступа к профилю пользователя подтвердите свой email. Письмо с информацией для подтверждения было направлено Вам на указанный при регистрации ящик {}'.format(request.user.email))
        
    if request.method == 'POST':
        if 'edit_profile' in request.POST:
            return render(request, 'main/profile.html', {
                'caption': u'Профиль пользователя {}'.format(request.user.username),
                'profile_form': UserProfileFormEnabled(instance=request.user.userprofile),
                'mode': 'edit',
            })
        elif 'save_profile' in request.POST:
            userprofile_form = UserProfileFormEnabled(request.POST, instance=request.user.userprofile)
            if userprofile_form.is_valid():                    
                profile = userprofile_form.save(commit=False)
                user_info = json.dumps({'username': profile.user.username, 'password': profile.user.password, 'role': profile.rolerequest.role})
                attempt = try_user_sending(request, u'Невозможно сохранить изменения профиля', settings.STORAGE_ALT_USER_HOST, user_info=user_info)
                if attempt: #if something went wrong
                    return attempt
                profile.save()
                messages.success(request, 'Ваши данные были успешно сохранены!')
        elif 'cancel' in request.POST:
            messages.success(request, 'Изменений в профиль не было внесено')
        
    return render(request, 'main/profile.html', {
        'caption': u'Профиль пользователя {}'.format(request.user.username),
        'profile_form': UserProfileFormDisabled(instance=request.user.userprofile),
        'mode': 'view',
    })


def is_superuser(user):
    return user.is_superuser


def is_active(user):
    return user.is_active

# If user's request is not actual now, no information should be provided in database
def flush_userprofile_request(userprofile):
    userprofile.rolerequest.role = 'NONE'
    userprofile.rolerequest.comment = ''
    userprofile.rolerequest.save()


ACCEPT = 1
DECLINE = 0


def mail_verdict(request, user, site, role, verdict):
    if verdict == ACCEPT:
        subject = '[Томограф] Ваша заявка на присвоение роли удовлетворена'
        message = u'   Здравствуйте, {username}!\n\
  Поздравляем, Ваша заявка на присвоение роли "{role}" была удовлетворена администратором. Вы можете приступить к пользованию дополнительным функционалом сайта уже сейчас!\n\
  С уважением, администрация сайта {site}.'.format(site=site, username=user.userprofile.full_name, role=role)
    elif verdict == DECLINE:
        subject = '[Томограф] Ваша заявка на присвоение роли отклонена'
        message = u'  Здравствуйте, {username}!\n\
  К сожалению, Ваша заявка на присвоение роли "{role}" была отклонена администратором сайта. Ответьте на это письмо и подробно опишите свою ситуацию, если Вы считаете, что произошла ошибка.\n\
  С уважением, администрация сайта {site}.'.format(site=site, username=user.userprofile.full_name, role=role)
    else:
        return
    
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    except BaseException as e:
        messages.warning(request, u'При отправке письма по адресу \'{}\' произошла ошибка. Если адрес корректен, уточните причину возникновения ошибки в логах сервера'.format(user.email))
        logger.error(e)
    else:
        messages.success(request, u'Успешно отправлено сообщение по адресу \'{}\''.format(user.email))
        

def mail_role_request(request, role_request, site, manage_link):
    subject = '[Томограф] Новая заявка на сайте'
    message = u'На сайте {site} появилась новая заявка на изменение роли:\n\
  Имя пользователя: {username}\n\
  ФИО: {full_name}\n\
  Запрашивает роль: {role}\n\
  Дополнительный комментарий пользователя: {comment} \n\
  Страница управления заявками: {manage_link}'.format(site=site, username=role_request.user.user.username,
                                                      role=role_request.get_role_display(),
                                                      full_name=role_request.user.full_name,
                                                      comment=role_request.comment, manage_link=manage_link)

    send_mail(subject, message, settings.EMAIL_HOST_USER, [admin[1] for admin in settings.ADMINS], fail_silently=False)


@user_passes_test(is_superuser)
def manage_requests_view(request):
    if request.method == 'POST':
        profile_id = request.POST['profile_id']
        profile = get_object_or_404(UserProfile, pk=profile_id)
        site = request.get_host()
        role_long = profile.rolerequest.get_role_display()
        request_list = [rolerequest.user for rolerequest in RoleRequest.objects.exclude(role='NONE')]
        if 'accept' in request.POST:
            user_info = json.dumps({'username': profile.user.username, 'password': profile.user.password, 'role': profile.rolerequest.role})
            
            attempt = try_user_sending(request, u'Невозможно сохранить изменения', settings.STORAGE_ALT_USER_HOST, user_info=user_info)
            if attempt: #if something went wrong
                return attempt
            
            profile.user.is_superuser = False  # we must invalidate superuser and staff rights
            profile.user.is_staff = False  # if any error was made before
            profile.role = profile.rolerequest.role
            if profile.role == 'ADM':
                profile.user.is_superuser = True
                profile.user.is_staff = True
            profile.save()
            profile.user.save()
            messages.success(request, u'Запрос пользователя {} был успешно подтверждён'.format(profile.user.username))
            mail_verdict(request, profile.user, site, role_long, ACCEPT)
            flush_userprofile_request(profile)
        elif 'decline' in request.POST:
            messages.success(request, u'Запрос пользователя {} был успешно отклонён'.format(profile.user.username))
            mail_verdict(request, profile.user, site, role_long, DECLINE)
            flush_userprofile_request(profile)

    request_list = [rolerequest.user for rolerequest in RoleRequest.objects.exclude(role='NONE')]
    return render(request, 'main/manage_requests.html', {
        'request_list': request_list,
        'caption': 'Запросы смены роли'
    })


@login_required
def role_request_view(request):
    if not request.user.is_active:
        messages.info(request, u'Для доступа к странице подтвердите свой email. Письмо с информацией для подтверждения было направлено Вам на указанный при регистрации ящик {}'.format(request.user.email))
        
    if request.method == 'POST' and request.user.is_active:
        if RoleRequest.objects.filter(user__user__pk=request.user.pk):
            role_request = RoleRequest.objects.get(user__user__pk=request.user.pk)
            role_form = UserRoleRequestForm(request.POST, instance=role_request)
        else:
            role_form = UserRoleRequestForm(request.POST)

        if 'cancel' in request.POST:
            new_request = RoleRequest()
            new_request.user = request.user.userprofile
            new_request.role = 'NONE'
        elif 'submit' in request.POST:
            if role_form.is_valid():
                new_request = role_form.save(commit=False)
                new_request.user = request.user.userprofile
                new_request.save()
                role_form.save_m2m()
            else:
                return render(request, 'main/role_request.html', {
                    'role_form': role_form,
                    'caption': 'Запрос на изменение роли',
                })
        else:
            return render(request, 'main/role_request.html', {
                'role_form': role_form,
                'caption': 'Запрос на изменение роли',
            })
        
        if new_request.role != 'NONE':
            try:
                mail_role_request(request, new_request, request.get_host(), request.build_absolute_uri(reverse('main:manage_requests')))
            except BaseException as e:
                messages.warning(request, 'Произошла ошибка во время оповещения администратора о появлении новой заявки, из-за чего её рассмотрение может задержаться. Чтобы избежать этого, Вы можете связаться с администрацией сайта самостоятельно')
                logger.error(e)
            finally:
                messages.info(request, 'Ваша заявка на получение статуса зарегистрирована. После её рассмотрения вам будет направлено электронное письмо на email, указанный при регистрации')
        else:
            messages.info(request, u'Заявка не отправлена. Ваша роль "{}" не будет изменена'.format(request.user.userprofile.get_role_display())) 
            
        return redirect(reverse('main:done'))

    # if method is not 'POST'
    if RoleRequest.objects.filter(user__user__pk=request.user.pk):
        role_request = RoleRequest.objects.get(user__user__pk=request.user.pk)
        role_form = UserRoleRequestForm(instance=role_request)
    else:
        role_form = UserRoleRequestForm()
    return render(request, 'main/role_request.html', {
        'role_form': role_form,
        'caption': 'Запрос на изменение роли',
    })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(['GET', 'POST'])
def user_list(request):
    """
    Пока что тестовый view, отправляющий запросы
    """
    if request.method == 'GET':
        users = UserProfile.objects.all()
        serializer = UserSerializer(users, many=True)
        content = JSONRenderer().render(serializer.data)
        info = json.dumps({'select': 'all'})
 
        rest_logger.debug('Message here!') # an example of logging-to-file
        #requests.post('http://mardanov@109.234.34.140:5006/storage/experiments', info)
        # print "GET1"
        # requests.post('http://93.175.2.145:8009/test_rest/', info)
        # print get_client_ip(request)
        requests.post("http://" + str(get_client_ip(request)) + ":8000", info)

        # print "GET2"
        return render(request, 'main/rest_test.html', {'content': content, 'serializer': serializer.data})

    elif request.method == 'POST':
        users = UserProfile.objects.all()
        serializer = UserSerializer(users, many=True)
        content = JSONRenderer().render(serializer.data)
        info = json.dumps({'select': 'all'})
        #requests.post('http://mardanov@109.234.34.140:5006/storage/experiments', info)
        # print "POST1"
        #requests.get('http://93.175.2.145:8009/test_rest/')
        # print "POST2"
        return render(request, 'main/rest_test.html', {'content': content, 'serializer': serializer.data})
#
# @api_view(['GET', 'POST'])
# def user_list(request):
#     """git
#     Пока что тестовый view, отправляющий запросы
#     """
#     if request.method == 'GET':
#         users = UserProfile.objects.all()
#         serializer = UserSerializer(users, many=True)
#         content = JSONRenderer().render(serializer.data)
#         return render(request, 'main/rest_test.html', {'content': content, 'serializer': serializer.data})
#
#     elif request.method == 'POST':
#         if 'accept' in request.POST:
#             return render(request, 'main/rest_test.html', {'content': request.POST, 'serializer': 'accept'})
#         elif 'decline' in request.POST:
#             return render(request, 'main/rest_test.html', {'content': request.POST, 'serializer': 'decline'})
