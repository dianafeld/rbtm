# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.messages import get_messages
import logging
import hashlib
import datetime
import random
import requests
import tempfile
import os
from django.core import files
import urllib2
import json
from requests.exceptions import Timeout
from django.forms import ValidationError
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger('django.request')

TOMO = {'state': 'off'}


def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']


@login_required
@user_passes_test(has_experiment_access)
# отправляет включить/выключить томограф,ток,напряжение,заслонку открыть/закрыть и т.д.

def info_once_only(request, msg):
    if msg not in [m.message for m in get_messages(request)]:
        messages.info(request, msg)


def set_state(TOMO, new_state):
    TOMO['state'] = new_state


def experiment_view(request):
    '''if TOMO['state'] == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
        if TOMO['state'] == 'waiting':
            info_once_only(request, u'Текущее состояние томографа: ожидание')
            if TOMO['state'] == 'adjustment':
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                if TOMO['state'] == 'experiment':
                    info_once_only(request, u'Текущее состояние томографа: эксперимент')'''
    if request.method == 'POST':
        if 'on_exp' in request.POST:  # включить томограф
            if TOMO['state'] == 'off':
                try:
                    answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-on', timeout=1)
                    print answer.content
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index'))
                except Timeout as e:
                    messages.warning(request,
                                     'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже.')
                    logger.error(e)
                    return redirect(reverse('experiment:index'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index'))
                if answer_check['success'] == True:
                    messages.success(request, u'Томограф включен')
                    set_state(TOMO, 'waiting')
                else:
                    logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                    messages.warning(request,
                                     u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
            else:
                print TOMO['state']
                messages.warning(request, u'Томограф уже включен')
        if 'of_exp' in request.POST:  # выключение томографа
            if TOMO['state'] == 'waiting':
                try:
                    answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-off', timeout=1)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                except Timeout as e:
                    messages.warning(request,
                                     'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже.')
                    logger.error(e)
                    return redirect(reverse('experiment:index'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index'))
                if answer_check['success'] == True:
                    messages.success(request, u'Томограф включен')
                    set_state(TOMO, 'off')
                else:
                    logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                    messages.warning(request,
                                     u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
            else:
                print TOMO['state']
                messages.warning(request, u'Томограф не может быть выключен.')
    return render(request, 'experiment/start.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })


def experiment_adjustment(request):
    '''if TOMO['state'] == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
    elif TOMO['state'] == 'waiting':
        info_once_only(request, u'Текущее состояние томографа: ожидание')
    elif TOMO['state'] == 'adjustment':
        info_once_only(request, u'Текущее состояние томографа: юстировка')
    elif TOMO['state'] == 'experiment':
        info_once_only(request, u'Текущее состояние томографа: эксперимент')'''

    if request.method == 'POST':
        # if TOMO['state'] == 'waiting' or TOMO['state'] == 'adjustment' :
        if 'move_hor' in request.POST:  # подвинуть по горизонтали
            try:
                info = json.dumps(float(request.POST['move_hor']))
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-horizontal-position', info,
                                       timeout=1)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Горизонтальное положение образца изменено.')
                set_state(TOMO, 'adjustment')
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
        if 'move_ver' in request.POST:  # подвинуть по вертикали
            try:
                info = json.dumps(float(request.POST['move_ver']))
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-vertical-position', info,
                                       timeout=1)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Вертикальное положение образца изменено.')
                set_state(TOMO, 'adjustment')
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
        if 'rotate' in request.POST:  # повернуть
            try:
                info = json.dumps(float(request.POST['rotate']))
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-angle-position', info,
                                       timeout=1)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Образец повернут.')
                set_state(TOMO, 'adjustment')
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
        if 'reset' in request.POST:  # установить текущее положение за 0
            try:
                answer = requests.get('http://109.234.34.140:5001/tomograph/1/motor/reset-angle-position', timeout=1)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                logger.error(e)
                messages.warning(request,
                                 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Текущее положение установлено за 0.')
                set_state(TOMO, 'adjustment')
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
        if 'gate' in request.POST:
            if request.POST['text_gate'] == 'open':  # открыть заслонку
                try:
                    answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/open', timeout=1)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_adjustment'))
                except Timeout as e:
                    messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index_adjustment'))
                if answer_check['success'] == True:
                    messages.success(request, u'Заслонка открыта')
                    set_state(TOMO, 'adjustment')
                else:
                    logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                    messages.warning(request,
                                     u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
            if request.POST['text_gate'] == 'close':  # закрыть заслонку
                try:
                    answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/close', timeout=1)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_adjustment'))
                except Timeout as e:
                    messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index_adjustment'))
            if answer_check['success'] == True:
                messages.success(request, u'Заслонка закрыта')
                set_state(TOMO, 'adjustment')
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
        if 'experiment_on_voltage' in request.POST:  # задать напряжение
            info = json.dumps(float(request.POST['voltage']))
            try:
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-voltage', info, timeout=1)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, u'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                messages.warning(request,
                                 u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            print(answer_check)
            if answer_check['success'] == True:
                messages.success(request, u'Настройки установлены')
                set_state(TOMO, 'adjustment')
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
        if 'experiment_on_current' in request.POST:  # задать силу тока
            info = json.dumps(float(request.POST['current']))
            try:
                answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-current', info, timeout=1)
                answer_check = json.loads(answer.content)
                if answer.status_code != 200:
                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                        answer.status_code))
                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                    return redirect(reverse('experiment:index_adjustment'))
            except Timeout as e:
                messages.warning(request, u'Нет ответа от модуля "Эксперимент".')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            except BaseException as e:
                messages.warning(request,
                                 u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                logger.error(e)
                return redirect(reverse('experiment:index_adjustment'))
            print(answer_check)
            if answer_check['success'] == True:
                messages.success(request, u'Настройки установлены')
                set_state(TOMO, 'adjustment')
            else:
                logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                messages.warning(request,
                                 u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')

        if 'picture_exposure_submit' in request.POST:  # preview a picture
            try:
                # deserialize(answer_check['image'])
                # Steam the image from the url
                exposure = request.POST['picture_exposure']
                # image_url = 'http://cdn.playbuzz.com/cdn/0079c830-3406-4c05-a5c1-bc43e8f01479/7dd84d70-768b-492b-88f7-a6c70f2db2e9.jpg'
                image_url = 'http://109.234.34.140:5001/tomograph/1/detector/get-frame'
                data = json.dumps(float(exposure))
                response = requests.post(image_url, data, stream=True)
                print(response)
                if response.status_code != 200:
                    messages.warning(request, u'Не удалось получить картинку')
                    logger.error(u'Не удалось получить картинку, код ошибки: {}'.format(response.status_code))
                else:
                    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                    file_name = hashlib.sha1(salt + str(request.user.id)).hexdigest() + '.png'
                    temp_file = tempfile.TemporaryFile()
                    for block in response.iter_content(1024 * 8):
                        if not block:
                            break
                        temp_file.write(block)

                    path = default_storage.save(os.path.join(settings.MEDIA_ROOT, file_name), temp_file)
                    print(path)
                    return render(request, 'experiment/adjustment.html', {
                        'full_access': (request.user.userprofile.role == 'EXP'),
                        'caption': 'Эксперимент',
                        'preview_path': os.path.join(settings.MEDIA_URL, file_name),
                    })
            except BaseException as e:
                messages.warning(request, u'Не удалось выполнить предпросмотр. Попробуйте повторно')
                logger.error(e)

    return render(request, 'experiment/adjustment.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })


def experiment_interface(request):
    '''if TOMO['state'] == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
        if TOMO['state'] == 'waiting':
            info_once_only(request, u'Текущее состояние томографа: ожидание')
            if TOMO['state'] == 'adjustment':
                info_once_only(request, u'Текущее состояние томографа: юстировка')
                if TOMO['state'] == 'experiment':
                    info_once_only(request, u'Текущее состояние томографа: эксперимент')'''
    if request.method == 'POST':
        if 'parameters' in request.POST:
            if TOMO['state'] == 'waiting' or TOMO['state'] == 'adjustment':
                exp_id = uuid.uuid4()
                simple_experiment = json.dumps({
                    'experiment id': str(exp_id),
                    'for storage':
                        {
                            'name': request.POST['name'],
                            'tegs': request.POST['type']
                        },
                    'experiment parameters':
                        {
                            'advanced': False,
                            'DARK':
                                {
                                    'count': int(float(request.POST['dark_quantity'])),
                                    'exposure': float(request.POST['dark_exposure'])
                                },
                            'EMPTY':
                                {
                                    'count': int(float(request.POST['empty_quantity'])),
                                    'exposure': float(request.POST['dark_exposure'])
                                },
                            'DATA':
                                {
                                    'step count': int(float(request.POST['data_shots_quantity'])),
                                    'exposure': float(request.POST['data_shots_exposure']),
                                    'angle step': float(request.POST['data_angle']),
                                    'count per step': int(float(request.POST['data_same']))
                                }
                        }
                }
                )
                try:
                    answer = requests.post('http://109.234.34.140:5001/tomograph/1/experiment/start', simple_experiment,
                                           timeout=1)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_interface'))
                except Timeout as e:
                    messages.warning(request, u'Нет ответа от модуля "Эксперимент"')
                    logger.error(e)
                    return redirect(reverse('experiment:index_interface'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index_interface'))
                if answer_check['success'] == True:
                    messages.success(request, u'Эксперимент успешно начался')
                    set_state(TOMO, 'experiment')
                else:
                    logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
                    messages.warning(request,
                                     u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
            else:
                print TOMO['state']
                messages.warning(request, u'Эксперимент не может начаться. Проверьте, включен ли томограф.')
        if 'turn_down' in request.POST:
            if TOMO['state'] == 'experiment':
                try:
                    answer = requests.get('http://109.234.34.140:5001/tomograph/1/experiment/stop', timeout=1)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(
                            answer.status_code))
                        logger.error(
                            u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_interface'))
                except Timeout as e:
                    messages.warning(request, u'Нет ответа от модуля "Эксперимент"')
                    logger.error(e)
                    return redirect(reverse('experiment:index_interface'))
                except BaseException as e:
                    logger.error(e)
                    messages.warning(request,
                                     u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    return redirect(reverse('experiment:index_interface'))
                if answer_check['message'] == 'Experiment was finished successfully':
                    messages.success(request, u'Эксперимент окончен')
                    set_state(TOMO, 'off')
                else:
                    if answer_check['message'] == 'Experiment was emergency stopped':
                        messages.warning(request, u'Аварийное завершение эксперимента {}', error)
                        logger.error(u'Аварийное завершение эксперимента {}', error)
                    else:
                        logger.error(u'Эксперимент завершен кем-то еще.')
                        messages.warning(request, u'Эксперимент завершен кем-то еще.')
            else:
                print TOMO['state']
                messages.warning(request, u'Нельзя закончить эксперимент. Проверьте, идет ли эксперимент.')
    return render(request, 'experiment/interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })


''' function for viewing picture
            def plotImage(arr):
                fig = plt.figure(figsize=(5, 5), dpi=80, facecolor='w', edgecolor='w', frameon=True)
                imAx = plt.imshow(arr, origin='lower', interpolation='nearest')
                fig.colorbar(imAx, pad=0.01, fraction=0.1, shrink=1.00, aspect=20)'''

'''def show_image(request):
    if request.method == 'POST':
        if 'show_image' in request.POST:
            info = json.dumps({
                'experiment_id': '552aa5546c8dc50c93edacf0'})
            requests.post('http://mardanov@109.234.34.140:5006/storage/frames/get', info)
            show image
        return render(request, 'experiment/show_image.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })'''
