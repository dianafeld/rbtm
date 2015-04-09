# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login
from forms import UserRegistrationForm, UserProfileRegistrationForm, UserRoleRequestForm
from models import UserProfile, RoleRequest
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
import logging

logger = logging.getLogger('django.request')

def index(request):
    return render(request, 'main/index.html', {'caption': 'ROBO-TOM'})


def group1(request):
    return render(request, 'main/group_1.html', {'caption': 'Группа 1'})


def group2(request):
    return render(request, 'main/group_2.html', {'caption': "Группа 2"})


def group3(request):
    return render(request, 'main/group_3.html', {'caption': "Группа 3"})


def registration_view(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        userprofile_form = UserProfileRegistrationForm(request.POST)
        if user_form.is_valid() and userprofile_form.is_valid():
            user = user_form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            new_profile = userprofile_form.save(commit=False)
            new_profile.user = user
            new_profile.save()
            userprofile_form.save_m2m()
            auth_login(request, user)
            messages.success(request, 'Регистрация успешно завершена')
            return redirect(reverse('main:role_request'))
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


def done_view(request):
    return render(request, 'main/done.html', {'caption': 'Успех'})


@login_required
def profile_view(request):
    # TODO Eugene
    return render(request, 'main/empty.html', {'caption': 'Профиль'})


def is_superuser(user):
    return user.is_superuser


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
        message = u'Здравствуйте, {username}!\n\
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
        messages.success(request, u'Успешно отправлено сообщение по адресу \' {}\''.format(user.email))
        

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
        if 'accept' in request.POST:
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
    if request.method == 'POST':
        if RoleRequest.objects.filter(user__user__pk=request.user.pk):
            role_request = RoleRequest.objects.get(user__user__pk=request.user.pk)
            role_form = UserRoleRequestForm(request.POST, instance=role_request)
        else:
            role_form = UserRoleRequestForm(request.POST)

        if role_form.is_valid():
            new_request = role_form.save(commit=False)
            new_request.user = request.user.userprofile
            new_request.save()
            role_form.save_m2m()
            if new_request.role != 'NONE':
                try:
                    mail_role_request(request, new_request, request.get_host(), request.build_absolute_uri(reverse('main:manage_requests')))
                except BaseException as e:
                    messages.warning(request, 'Произошла ошибка во время оповещения администратора о появлении новой заявки, из-за чего её рассмотрение может задержаться. Чтобы избежать этого, Вы можете связаться с администрацией сайта самостоятельно')
                    logger.error(e)
                finally:
                    messages.info(request,
                              'Ваша заявка на получение статуса зарегистрирована. После её рассмотрения вам будет направлено электронное письмо на email, указанный при регистрации')
            else:
                messages.info(request, 'Вам автоматически присвоен статус "Гость"')
            
            if 'next' in request.POST:
                next = request.POST['next']
                if next == '':
                    return redirect(reverse('main:done'))
                else:
                    return redirect(next)
            else:
                return redirect(reverse('main:done'))
        else:
            return render(request, 'main/role_request.html', {
                'role_form': role_form,
                'caption': 'Запрос на изменение роли',
            })

    if RoleRequest.objects.filter(user__user__pk=request.user.pk):
        role_request = RoleRequest.objects.get(user__user__pk=request.user.pk)
        role_form = UserRoleRequestForm(instance=role_request)
    else:
        role_form = UserRoleRequestForm()
    return render(request, 'main/role_request.html', {
        'role_form': role_form,
        'caption': 'Запрос на изменение роли',
    })
