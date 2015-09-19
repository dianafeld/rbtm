# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
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
from django.core import files
import json
from requests.exceptions import Timeout
import uuid
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseBadRequest

logger = logging.getLogger('django.request')


def has_experiment_access(user):
    return user.userprofile.is_admin or user.userprofile.is_experimentator


def info_once_only(request, msg):
    storage = get_messages(request)
    if msg not in [m.message for m in storage]:
        messages.info(request, msg)


def migrations():
    if len(Tomograph.objects.all()) == 0:
        Tomo = Tomograph(state='off')
        Tomo.save()


def try_request_post(request, address, content, source_page, stream=False):
    result = {'answer_check': None, 'error': None}
    try:
        answer = requests.post(address, content, timeout=settings.TIMEOUT_DEFAULT, stream=stream) 
        result['answer_check'] = json.loads(answer.content)
        if answer.status_code != 200:
            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            result['error'] = redirect(reverse(source_page))
    except Timeout as e:
        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
        logger.error(e)
        result['error'] = redirect(reverse(source_page))
    except BaseException as e:
        logger.error(e)
        messages.warning(request, 
            'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
        result['error'] = redirect(reverse(source_page))
    return result


def try_request_get(request, address, source_page):
    result = {'answer_check': None, 'error': None}
    try:
        answer = requests.get(address, timeout=settings.TIMEOUT_DEFAULT) 
        result['answer_check'] = json.loads(answer.content)
        if answer.status_code != 200:
            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
            result['error'] = redirect(reverse(source_page))
    except Timeout as e:
        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
        logger.error(e)
        result['error'] = redirect(reverse(source_page))
    except BaseException as e:
        logger.error(e)
        messages.warning(request, 
            'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
        result['error'] = redirect(reverse(source_page))
    return result


def check_result(answer_check, request, tomo, success_msg='', state_ru='', state_en=''):
    if answer_check['success']:
        messages.success(request, success_msg)
        info_once_only(request, u'Текущее состояние томографа: {}'.format(state_ru))
        tomo.state = state_en
        tomo.save()
    else:
        logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(
                    answer_check['error']))
        messages.warning(request, 
            u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже {}'.format(answer_check['error']))
        return render(request, 'experiment/adjustment.html', {
            'full_access': request.user.userprofile.is_experimentator,
            'caption': 'Эксперимент',
            'off': (tomo.state == 'off'),
            'waiting': (tomo.state == 'waiting'),
            'adj': (tomo.state == 'adjustment'),
            'exper': (tomo.state == 'experiment'),
            'tomograph': tomo,
        })

@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)
    if request.method == 'POST':
        if 'on_exp' in request.POST:  # включить томограф
            result = try_request_get(request, settings.EXPERIMENT_SOURCE_POWER_ON.format(1), 'experiment:index')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            check_result(answer_check, request, tomo, success_msg=u'Томограф включен', 
                                                            state_ru=u'ожидание', state_en='waiting')
            
        if 'of_exp' in request.POST:  # выключение томографа
            result = try_request_get(request, settings.EXPERIMENT_SOURCE_POWER_OFF.format(1), 'experiment:index')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            check_result(answer_check, request, tomo, success_msg=u'Томограф выключен', 
                                                      state_ru=u'выключен', state_en='off')
    else:
        if tomo.state == 'off':
            info_once_only(request, u'Текущее состояние томографа: выключен')
        elif tomo.state == 'waiting':
            info_once_only(request, u'Текущее состояние томографа: ожидание')
        elif tomo.state == 'adjustment':
            info_once_only(request, u'Текущее состояние томографа: юстировка')
        elif tomo.state == 'experiment':
            info_once_only(request, u'Текущее состояние томографа: эксперимент')

    return render(request, 'experiment/start.html', {
        'full_access': (request.user.userprofile.is_experimentator),
        'caption': 'Эксперимент',
        'off': (tomo.state == 'off'),
        'waiting': (tomo.state == 'waiting'),
        'adj': (tomo.state == 'adjustment'),
        'exper': (tomo.state == 'experiment')
    })


@login_required
@user_passes_test(has_experiment_access)
def experiment_adjustment(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)
    if tomo.state == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
    elif tomo.state == 'waiting':
        info_once_only(request, u'Текущее состояние томографа: ожидание')
    elif tomo.state == 'adjustment':
        info_once_only(request, u'Текущее состояние томографа: юстировка')
    elif tomo.state == 'experiment':
        info_once_only(request, u'Текущее состояние томографа: эксперимент')
    if request.method == 'POST':
        if 'refresh' in request.POST:
            try:
                if request.POST['refresh'] == 'voltage':
                    result = try_request_get(request, settings.EXPERIMENT_SOURCE_GET_VOLT.format(1), 'experiment:index_adjustment')
                    if result['error']:
                        return result['error']
                    answer_check = result['answer_check']
                    tomo.voltage = float(answer_check['result'])
                    check_status = check_result(answer_check, request, tomo, success_msg=u'Текущее напряжение успешно получено', 
                                                                            state_ru=u'юстировка', state_en=u'adjustment')
                elif request.POST['refresh'] == 'current':
                    result = try_request_get(request, settings.EXPERIMENT_SOURCE_GET_CURR.format(1), 'experiment:index_adjustment')
                    if result['error']:
                        return result['error']

                    answer_check = result['answer_check']
                    tomo.current = float(answer_check['result'])
                    check_status = check_result(answer_check, request, tomo, success_msg=u'Текущая сила тока успешно получена', 
                                                                            state_ru=u'юстировка', state_en=u'adjustment')
                elif request.POST['refresh'] == 'angle':
                    result = try_request_get(request, settings.EXPERIMENT_MOTOR_GET_ANGLE.format(1), 'experiment:index_adjustment')
                    if result['error']:
                        return result['error']

                    answer_check = result['answer_check']
                    tomo.angle = float(answer_check['result'])
                    check_status = check_result(answer_check, request, tomo, success_msg=u'Текущий угол поворота успешно получен', 
                                                                            state_ru=u'юстировка', state_en=u'adjustment')
                elif request.POST['refresh'] == 'vertical_shift':
                    result = try_request_get(request, settings.EXPERIMENT_MOTOR_GET_VERT.format(1), 'experiment:index_adjustment')
                    if result['error']:
                        return result['error']

                    answer_check = result['answer_check']
                    tomo.vertical_shift = int(answer_check['result'])
                    check_status = check_result(answer_check, request, tomo, success_msg=u'Текущий вертикальный сдвиг успешно получен', 
                                                                            state_ru=u'юстировка', state_en=u'adjustment')
                elif request.POST['refresh'] == 'horizontal_shift':
                    result = try_request_get(request, settings.EXPERIMENT_MOTOR_GET_HORIZ.format(1), 'experiment:index_adjustment')
                    if result['error']:
                        return result['error']

                    answer_check = result['answer_check']
                    tomo.horizontal_shift = int(answer_check['result'])
                    check_status = check_result(answer_check, request, tomo, success_msg=u'Текущий вертикальный сдвиг успешно получен', 
                                                                            state_ru=u'юстировка', state_en=u'adjustment')
                elif request.POST['refresh'] == 'shutter':
                    result = try_request_get(request, settings.EXPERIMENT_SHUTTER_GET_STATUS.format(1), 'experiment:index_adjustment')
                    if result['error']:
                        return result['error']

                    answer_check = result['answer_check']
                    tomo.shutter = answer_check['result']
                    check_status = check_result(answer_check, request, tomo, success_msg=u'Текущее состояние заслонки успешно получено', 
                                                                            state_ru=u'юстировка', state_en=u'adjustment')
            except BaseException as e:
                logger.error(e)
                messages.warning(request, 'В процессе обновления информации произошла непредвиденная ошибка. Подробнее: {}'.format(e))

        # if tomo.state == 'waiting' or tomo.state == 'adjustment' :
        if 'move_hor_submit' in request.POST:  # подвинуть по горизонтали
            info = json.dumps(int(request.POST['move_hor']))
            result = try_request_post(request, settings.EXPERIMENT_MOTOR_SET_HORIZ.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            tomo.horizontal_shift = int(request.POST['move_hor'])
            check_result(answer_check, request, tomo, success_msg=u'Горизонтальное положение образца изменено', 
                                                            state_ru=u'юстировка', state_en='adjustment')
        
        if 'move_ver_submit' in request.POST:  # подвинуть по вертикали
            info = json.dumps(int(request.POST['move_ver']))
            result = try_request_post(request, settings.EXPERIMENT_MOTOR_SET_VERT.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            tomo.vertical_shift= int(request.POST['move_ver'])
            check_result(answer_check, request, tomo, success_msg=u'Вертикальное положение образца изменено', 
                                                            state_ru=u'юстировка', state_en='adjustment')
    
        if 'rotate_submit' in request.POST:  # повернуть
            info = json.dumps(float(request.POST['rotate']))
            result = try_request_post(request, settings.EXPERIMENT_MOTOR_SET_ANGLE.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            tomo.angle = float(request.POST['rotate'])
            check_result(answer_check, request, tomo, success_msg=u'Образец повернут', 
                                                            state_ru=u'юстировка', state_en='adjustment')

        if 'reset_submit' in request.POST:  # установить текущее положение за 0
            result = try_request_get(request, settings.EXPERIMENT_MOTOR_RESET_ANGLE.format(1), 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            tomo.angle = 0
            check_result(answer_check, request, tomo, success_msg=u'Текущий угол поворота принят за 0', 
                                                            state_ru=u'юстировка', state_en='adjustment')
        
        if 'text_gate' in request.POST:
            if request.POST['gate_state'] == 'open':  # открыть заслонку
                result = try_request_get(request, settings.EXPERIMENT_SHUTTER_OPEN.format(1), 'experiment:index_adjustment')
                if result['error']:
                    return result['error']

                answer_check = result['answer_check']
                tomo.shutter = 'opened'
                check_result(answer_check, request, tomo, success_msg=u'Заслонка открыта', 
                                                            state_ru=u'юстировка', state_en='adjustment')

            elif request.POST['gate_state'] == 'close':  # закрыть заслонку
                result = try_request_get(request, settings.EXPERIMENT_SHUTTER_CLOSE.format(1), 'experiment:index_adjustment')
                if result['error']:
                    return result['error']

                answer_check = result['answer_check']
                tomo.shutter = 'closed'
                check_result(answer_check, request, tomo, success_msg=u'Заслонка закрыта', 
                                                            state_ru=u'юстировка', state_en='adjustment')

        if 'experiment_on_voltage' in request.POST:  # задать напряжение
            info = json.dumps(float(request.POST['voltage']))
            result = try_request_post(request, settings.EXPERIMENT_SOURCE_SET_VOLT.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            tomo.voltage = float(request.POST['voltage'])
            check_result(answer_check, request, tomo, success_msg=u'Напряжение установлено', 
                                                            state_ru=u'юстировка', state_en='adjustment')

        if 'experiment_on_current' in request.POST:  # задать силу тока
            info = json.dumps(float(request.POST['current']))
            result = try_request_post(request, settings.EXPERIMENT_SOURCE_SET_CURR.format(1), info, 'experiment:index_adjustment')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            tomo.current = float(request.POST['current'])
            check_result(answer_check, request, tomo, success_msg=u'Сила тока установлена', 
                                                            state_ru=u'юстировка', state_en='adjustment')

        if 'picture_exposure_submit' in request.POST:  # preview a picture
            try:
                exposure = request.POST['picture_exposure']
                data = json.dumps(float(exposure))
                response = requests.post(settings.EXPERIMENT_DETECTOR_GET_FRAME.format(1), data, stream=True)
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
                    return render(request, 'experiment/adjustment.html', {
                        'full_access': (request.user.userprofile.is_experimentator),
                        'caption': 'Эксперимент',
                        'preview_path': os.path.join(settings.MEDIA_URL, file_name),
                        'preview': True,
                        'exposure': exposure,
                        'off': (tomo.state == 'off'),
                        'waiting': (tomo.state == 'waiting'),
                        'adj': (tomo.state == 'adjustment'),
                        'exper': (tomo.state == 'experiment'),
                        'get_voltage_url': settings.EXPERIMENT_SOURCE_GET_VOLT,
                        'get_current_url': settings.EXPERIMENT_SOURCE_GET_CURR,
                        'get_vert_url': settings.EXPERIMENT_MOTOR_GET_VERT,
                        'get_horiz_url': settings.EXPERIMENT_MOTOR_GET_HORIZ,
                        'get_angle_url': settings.EXPERIMENT_MOTOR_GET_ANGLE,
                        'get_shutter_url': settings.EXPERIMENT_SHUTTER_GET_STATUS,
                    })
            except BaseException as e:
                messages.warning(request, u'Не удалось выполнить предпросмотр. Попробуйте повторно')
                logger.error(e)
    return render(request, 'experiment/adjustment.html', {
        'full_access': request.user.userprofile.is_experimentator,
        'caption': 'Эксперимент',
        'off': (tomo.state == 'off'),
        'waiting': (tomo.state == 'waiting'),
        'adj': (tomo.state == 'adjustment'),
        'exper': (tomo.state == 'experiment'),
        'get_voltage_url': settings.EXPERIMENT_SOURCE_GET_VOLT.format(1),
        'get_current_url': settings.EXPERIMENT_SOURCE_GET_CURR.format(1),
        'get_vert_url': settings.EXPERIMENT_MOTOR_GET_VERT.format(1),
        'get_horiz_url': settings.EXPERIMENT_MOTOR_GET_HORIZ.format(1),
        'get_angle_url': settings.EXPERIMENT_MOTOR_GET_ANGLE.format(1),
        'get_shutter_url': settings.EXPERIMENT_SHUTTER_GET_STATUS.format(1),
    })


@login_required
@user_passes_test(has_experiment_access)
def experiment_interface(request):
    migrations()
    tomo = get_object_or_404(Tomograph, pk=1)
    if tomo.state == 'off':
        info_once_only(request, u'Текущее состояние томографа: выключен')
    elif tomo.state == 'waiting':
        info_once_only(request, u'Текущее состояние томографа: ожидание')
    elif tomo.state == 'adjustment':
        info_once_only(request, u'Текущее состояние томографа: юстировка')
    elif tomo.state == 'experiment':
        info_once_only(request, u'Текущее состояние томографа: эксперимент')
    if request.method == 'POST':
        if 'parameters' in request.POST:
            exp_id = uuid.uuid4()
            simple_experiment = json.dumps({
                'exp_id': str(exp_id),
                'specimen': request.POST['name'],
                'tags': request.POST['tags'],
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

            answer_check = result['answer_check']
            check_result(answer_check, request, tomo, success_msg=u'Эксперимент успешно начался', 
                                                            state_ru=u'эксперимент', state_en='experiment')

        if 'turn_down' in request.POST:
            result = try_request_get(request, settings.EXPERIMENT_START.format(1), 'experiment:index_interface')
            if result['error']:
                return result['error']

            answer_check = result['answer_check']
            check_result(answer_check, request, tomo, success_msg=u'Эксперимент окончен', 
                                                            state_ru=u'ожидание', state_en='waiting')

    return render(request, 'experiment/interface.html', {
        'full_access': (request.user.userprofile.is_experimentator),
        'caption': 'Эксперимент',
        'off': (tomo.state == 'off'),
        'waiting': (tomo.state == 'waiting'),
        'adj': (tomo.state == 'adjustment'),
        'exper': (tomo.state == 'experiment')
    })


def set_voltage(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.voltage = float(request.POST["voltage"])
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def set_current(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.current = float(request.POST["current"])
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def set_angle(request):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.angle = float(request.POST["angle"])
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def set_horiz_shift(request):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.horizontal_shift = int(request.POST["horiz_shift"])
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def set_vert_shift(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.vertical_shift = int(request.POST["vert_shift"])
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def set_shutter(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.shutter = request.POST["shutter"]
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def power_on(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.state = 'waiting'
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def power_off(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.state = 'off'
        tomo.angle = None
        tomo.voltage = None
        tomo.current = None
        tomo.shutter = None
        tomo.horizontal_shift = None
        tomo.vertical_shift = None
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def experiment_start(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.state = 'experiment'
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')


def experiment_stop(request, tomo_num):
    try:
        tomo = get_object_or_404(Tomograph, pk=tomo_num)
        tomo.state = 'waiting'
        tomo.save()
    except BaseException as e:
        return HttpResponseBadRequest(json.dumps({'error': '{}'.format(e)}))
    return HttpResponse('')