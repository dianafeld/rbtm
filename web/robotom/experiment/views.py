# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.messages import get_messages
import logging
import hashlib
import random
import requests
import tempfile
import os
from models import Tomograph
from django.shortcuts import get_object_or_404
import json
from requests.exceptions import Timeout
import uuid
import time
import datetime
from django.core.files.storage import default_storage
from functools import wraps

experiment_logger = logging.getLogger('experiment_logger')


def has_experiment_access(user):
    return user.userprofile.is_admin or user.userprofile.is_experimentator


def info_once_only(request, msg):
    storage = get_messages(request)
    if msg not in [m.message for m in storage]:
        messages.info(request, msg)


def migrations():
    if len(Tomograph.objects.all()) == 0:
        tomo = Tomograph(state='unavailable')
        tomo.save()


def try_request_post(request, address, content, source_page, stream=False):
    result = {'response_dict': None, 'error': None}
    try:
        answer = requests.post(address, content, timeout=settings.TIMEOUT_DEFAULT, stream=stream) 
        result['response_dict'] = json.loads(answer.content)
        if answer.status_code != 200:
            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            experiment_logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            result['error'] = redirect(reverse(source_page))
    except Timeout as e:
        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
        experiment_logger.error(e)
        result['error'] = redirect(reverse(source_page))
    except BaseException as e:
        experiment_logger.error(e)
        messages.warning(request, 
            'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
        result['error'] = redirect(reverse(source_page))
    return result


def try_request_get(request, address, source_page=''):
    result = {'response_dict': None, 'error': None}
    try:
        answer = requests.get(address, timeout=settings.TIMEOUT_DEFAULT) 
        result['response_dict'] = json.loads(answer.content)
        if answer.status_code != 200:
            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            experiment_logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            if source_page:
                result['error'] = redirect(reverse(source_page))
            else:
                result['error'] = u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code)
    except Timeout as e:
        messages.warning(request, 'Нет ответа от модуля "Эксперимент"')
        experiment_logger.error(e)
        if source_page:
            result['error'] = redirect(reverse(source_page))
        else:
            result['error'] = 'Нет ответа от модуля "Эксперимент"'

    except BaseException as e:
        experiment_logger.error(e)
        messages.warning(request, 
            'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
        if source_page:
            result['error'] = redirect(reverse(source_page))
        else:
            result['error'] = 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором'

    return result


def check_result(response_dict, request, tomo, success_msg=''):
    if response_dict['success']:
        if success_msg:
            messages.success(request, success_msg)
        tomo.save()
    else:
        experiment_logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    response_dict['error']))
        messages.warning(request, 
            u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(response_dict['error']))
        return render(request, 'experiment/adjustment.html', {
            'full_access': request.user.userprofile.is_experimentator,
            'caption': 'Эксперимент',
            'tomograph': tomo,
            'get_voltage_url': settings.EXPERIMENT_SOURCE_GET_VOLT.format(1),
            'get_current_url': settings.EXPERIMENT_SOURCE_GET_CURR.format(1),
            'get_vert_url': settings.EXPERIMENT_MOTOR_GET_VERT.format(1),
            'get_horiz_url': settings.EXPERIMENT_MOTOR_GET_HORIZ.format(1),
            'get_angle_url': settings.EXPERIMENT_MOTOR_GET_ANGLE.format(1),
            'get_shutter_url': settings.EXPERIMENT_SHUTTER_GET_STATUS.format(1),
        })


def set_current_state_msg(request, tomo):
    if tomo.state == 'unavailable':
        info_once_only(request, u'Текущее состояние томографа: недоступен')
    elif tomo.state == 'ready':
        info_once_only(request, u'Текущее состояние томографа: ожидание')
    elif tomo.state == 'experiment':
        info_once_only(request, u'Текущее состояние томографа: эксперимент')


def get_current_state(request, tomo):
    try:
        result = try_request_get(request, settings.EXPERIMENT_GET_STATE.format(1))
        if result['error']:
            tomo.state = 'unavailable'
        else:
            response_dict = result['response_dict']
            tomo.state = response_dict['result']
    except BaseException as e:
        tomo.state = 'unavailable'
    tomo.save()


def update_state_before_run(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        tomo = get_object_or_404(Tomograph, pk=1)
        get_current_state(request, tomo)
        set_current_state_msg(request, tomo)
        result = view(request, *args, **kwargs)
        return result
    return wrapped


@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)
    if request.method == 'POST':
        if 'on_exp' in request.POST: 
            result = try_request_get(request, settings.EXPERIMENT_SOURCE_POWER_ON.format(1), 'experiment:index')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Томограф включен')
            
        if 'of_exp' in request.POST:
            result = try_request_get(request, settings.EXPERIMENT_SOURCE_POWER_OFF.format(1), 'experiment:index')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Томограф выключен')
    
    get_current_state(request, tomo)
    set_current_state_msg(request, tomo)
    return render(request, 'experiment/start.html', {
        'caption': 'Эксперимент',
        'tomograph': tomo,
    })


@update_state_before_run
@login_required
@user_passes_test(has_experiment_access)
def experiment_adjustment(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)

    if request.method == 'POST':
        if 'move_hor_submit' in request.POST:
            info = json.dumps(int(request.POST['move_hor']))
            result = try_request_post(request, settings.EXPERIMENT_MOTOR_SET_HORIZ.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Горизонтальное положение образца изменено')
        
        if 'move_ver_submit' in request.POST: 
            info = json.dumps(int(request.POST['move_ver']))
            result = try_request_post(request, settings.EXPERIMENT_MOTOR_SET_VERT.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Вертикальное положение образца изменено')
    
        if 'rotate_submit' in request.POST: 
            info = json.dumps(float(request.POST['rotate']))
            result = try_request_post(request, settings.EXPERIMENT_MOTOR_SET_ANGLE.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Образец повернут')

        if 'reset_submit' in request.POST: 
            result = try_request_get(request, settings.EXPERIMENT_MOTOR_RESET_ANGLE.format(1), 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Текущий угол поворота принят за 0')
        
        if 'text_gate' in request.POST:
            if request.POST['gate_state'] == 'open': 
                result = try_request_get(request, settings.EXPERIMENT_SHUTTER_OPEN.format(1), 'experiment:index_adjustment')
                if result['error']:
                    return result['error']

                response_dict = result['response_dict']
                check_result(response_dict, request, tomo, success_msg=u'Заслонка открыта')

            elif request.POST['gate_state'] == 'close': 
                result = try_request_get(request, settings.EXPERIMENT_SHUTTER_CLOSE.format(1), 'experiment:index_adjustment')
                if result['error']:
                    return result['error']

                response_dict = result['response_dict']
                check_result(response_dict, request, tomo, success_msg=u'Заслонка закрыта')

        if 'experiment_on_voltage' in request.POST: 
            info = json.dumps(float(request.POST['voltage']))
            result = try_request_post(request, settings.EXPERIMENT_SOURCE_SET_VOLT.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Напряжение установлено')

        if 'experiment_on_current' in request.POST: 
            info = json.dumps(float(request.POST['current']))
            result = try_request_post(request, settings.EXPERIMENT_SOURCE_SET_CURR.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Сила тока установлена')

        if 'picture_exposure_submit' in request.POST: 
            try:
                exposure = request.POST['picture_exposure']
                data = json.dumps(float(exposure))
                response = requests.post(settings.EXPERIMENT_DETECTOR_GET_FRAME.format(1), data, stream=True)
                if response.status_code != 200:
                    messages.warning(request, u'Не удалось получить картинку')
                    experiment_logger.error(u'Не удалось получить картинку, код ошибки: {}'.format(response.status_code))
                else:
                    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                    file_name = hashlib.sha1(salt + str(request.user.id)).hexdigest() + '.png'
                    temp_file = tempfile.TemporaryFile()
                    for block in response.iter_content(1024 * 8):
                        if not block:
                            break
                        temp_file.write(block)

                    path = default_storage.save(os.path.join(settings.MEDIA_ROOT, file_name), temp_file)
                    return render(request, 'experiment/adjustment.html', {
                        'caption': 'Эксперимент',
                        'preview_path': os.path.join(settings.MEDIA_URL, file_name),
                        'preview': True,
                        'exposure': exposure,
                        'get_voltage_url': settings.EXPERIMENT_SOURCE_GET_VOLT.format(1),
                        'get_current_url': settings.EXPERIMENT_SOURCE_GET_CURR.format(1),
                        'get_vert_url': settings.EXPERIMENT_MOTOR_GET_VERT.format(1),
                        'get_horiz_url': settings.EXPERIMENT_MOTOR_GET_HORIZ.format(1),
                        'get_angle_url': settings.EXPERIMENT_MOTOR_GET_ANGLE.format(1),
                        'get_shutter_url': settings.EXPERIMENT_SHUTTER_GET_STATUS.format(1),
                        'tomograph': tomo,
                    })
            except BaseException as e:
                messages.warning(request, u'Не удалось выполнить предпросмотр. Попробуйте повторно')
                experiment_logger.error(e)

    return render(request, 'experiment/adjustment.html', {
        'caption': 'Эксперимент',
        'get_voltage_url': settings.EXPERIMENT_SOURCE_GET_VOLT.format(1),
        'get_current_url': settings.EXPERIMENT_SOURCE_GET_CURR.format(1),
        'get_vert_url': settings.EXPERIMENT_MOTOR_GET_VERT.format(1),
        'get_horiz_url': settings.EXPERIMENT_MOTOR_GET_HORIZ.format(1),
        'get_angle_url': settings.EXPERIMENT_MOTOR_GET_ANGLE.format(1),
        'get_shutter_url': settings.EXPERIMENT_SHUTTER_GET_STATUS.format(1),
        'tomograph': tomo,
    })


@login_required
@user_passes_test(has_experiment_access)
def experiment_interface(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)

    if request.method == 'POST':
        if 'parameters' in request.POST:
            exp_id = uuid.uuid4()
            timestamp = time.time()
            current_datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            simple_experiment = json.dumps({
                'exp_id': str(exp_id),
                'specimen': request.POST['name'],
                'tags': request.POST['tags'],
                'timestamp': timestamp,
                'datetime': current_datetime,
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
            })

            result = try_request_post(request, settings.EXPERIMENT_START.format(1), simple_experiment, 'experiment:index_interface')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Эксперимент успешно начался')

        if 'turn_down' in request.POST:
            result = try_request_get(request, settings.EXPERIMENT_STOP.format(1), 'experiment:index_interface')
            if result['error']:
                return result['error']

            response_dict = result['response_dict']
            check_result(response_dict, request, tomo, success_msg=u'Эксперимент окончен')

    get_current_state(request, tomo)
    set_current_state_msg(request, tomo)
    return render(request, 'experiment/interface.html', {
        'caption': 'Эксперимент',
        'tomograph': tomo,
    })
