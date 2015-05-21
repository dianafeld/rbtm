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
from models import Tomograph
from django.shortcuts import get_object_or_404
from django.core import files
import urllib2
import json
from requests.exceptions import Timeout
from django.forms import ValidationError
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger('django.request')

def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']

#отправляет включить/выключить томограф,ток,напряжение,заслонку открыть/закрыть и т.д.
   
def info_once_only(request, msg):
    if msg not in [m.message for m in get_messages(request)]:
        messages.info(request, msg)
@login_required
@user_passes_test(has_experiment_access)	
def experiment_view(request):
	tomo=get_object_or_404(Tomograph,pk=1)
	if tomo.state == 'off':
		info_once_only(request, u'Текущее состояние томографа: выключен')
	elif tomo.state == 'waiting':
		info_once_only(request, u'Текущее состояние томографа: ожидание')
	elif tomo.state == 'adjustment':
		info_once_only(request, u'Текущее состояние томографа: юстировка')
	elif tomo.state == 'experiment':
		info_once_only(request, u'Текущее состояние томографа: эксперимент')
   	if request.method == 'POST':
   		if 'on_exp' in request.POST:   #включить томограф
   			try: 
   				answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-on', timeout=1)
   				print answer.content
   				answer_check=json.loads(answer.content)
   				if answer.status_code != 200:
   					messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
   					logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
   					return redirect(reverse('experiment:index'))
   			except Timeout as e:
   				messages.warning(request, 'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже.')
   				logger.error(e)
   				return redirect(reverse('experiment:index'))
   			except BaseException as e:
   				logger.error(e)
   				messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
   				return redirect(reverse('experiment:index'))
   			if answer_check['success'] == True:
   				messages.success(request, u'Томограф включен')
   				tomo.state='waiting'
   				tomo.save()
   			else:
   				logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
   				messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
   		if 'of_exp' in request.POST:  #выключение томографа
   			try:
   				answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-off', timeout=1)
   				answer_check=json.loads(answer.content)
   				if answer.status_code != 200:
   					messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
   					logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
   			except Timeout as e:
   				messages.warning(request, 'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже.')
   				logger.error(e)
   				return redirect(reverse('experiment:index'))
   			except BaseException as e:
   				logger.error(e)
   				messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
   				return redirect(reverse('experiment:index'))
   			if answer_check['success'] == True:
   				messages.success(request, u'Томограф выключен')
   				print tomo.state
   				tomo.state='off'
   				tomo.save()
   			else:
   				logger.error(u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
   				messages.warning(request,u'Модуль "Эксперимент" не работает корректно в данный момент. Попробуйте позже')
   	return render(request, 'experiment/start.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
        'tomo': tomo.state
    })

@login_required
@user_passes_test(has_experiment_access)    
def experiment_adjustment(request):
	tomo=get_object_or_404(Tomograph,pk=1)
	print tomo.state
	if tomo.state == 'off':
		info_once_only(request, u'Текущее состояние томографа: выключен')
	elif tomo.state == 'waiting':
		info_once_only(request, u'Текущее состояние томографа: ожидание')
	elif tomo.state == 'adjustment':
		info_once_only(request, u'Текущее состояние томографа: юстировка')
	elif tomo.state == 'experiment':
		info_once_only(request, u'Текущее состояние томографа: эксперимент')
	if request.method == 'POST':
        #if tomo.state == 'waiting' or tomo.state == 'adjustment' :
            if 'move_hor_submit' in request.POST:   #подвинуть по горизонтали
                    try:
                        info = json.dumps(float(request.POST['move_hor']))  
                        answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-horizontal-position', info, timeout=1)
                        answer_check=json.loads(answer.content)
                        if answer.status_code != 200:
                            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            return redirect(reverse('experiment:index_adjustment'))
                    except Timeout as e:
                        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                        logger.error(e)
                        return redirect(reverse('experiment:index_adjustment'))
                    except BaseException as e:
                        logger.error(e)
                        messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                        return redirect(reverse('experiment:index_adjustment'))
                    if answer_check['success'] == True:
                        messages.success(request, u'Горизонтальное положение образца изменено.')
                        tomo.state='adjustment'
                        tomo.save()
                        print tomo.state
                    else:
                        logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                        messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
            if 'move_ver_submit' in request.POST:   #подвинуть по вертикали
                    try:
                        info = json.dumps(float(request.POST['move_ver']))  
                        answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-vertical-position', info, timeout=1)
                        answer_check=json.loads(answer.content)
                        if answer.status_code != 200:
                            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            return redirect(reverse('experiment:index_adjustment'))
                    except Timeout as e:
                        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                        logger.error(e)
                        return redirect(reverse('experiment:index_adjustment'))
                    except BaseException as e:
                        logger.error(e)
                        messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                        return redirect(reverse('experiment:index_adjustment'))
                    if answer_check['success'] == True:
                        messages.success(request, u'Вертикальное положение образца изменено.')
                        tomo.state ='adjustment'
                        tomo.save()
                    else:
                        logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                        messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
            if 'rotate_submit' in request.POST:   #повернуть
                    try:
                        info = json.dumps(float(request.POST['rotate']))  
                        answer = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-angle-position', info, timeout=1)
                        answer_check=json.loads(answer.content)
                        if answer.status_code != 200:
                            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            return redirect(reverse('experiment:index_adjustment'))
                    except Timeout as e:
                        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                        logger.error(e)
                        return redirect(reverse('experiment:index_adjustment'))
                    except BaseException as e:
                        logger.error(e)
                        messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                        return redirect(reverse('experiment:index_adjustment'))
                    if answer_check['success'] == True:
                        messages.success(request, u'Образец повернут.')
                        tomo.state ='adjustment'
                        tomo.save()
                    else:
                        logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                        messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
            if 'reset_submit' in request.POST:   #установить текущее положение за 0
                    try:    
                        answer = requests.get('http://109.234.34.140:5001/tomograph/1/motor/reset-angle-position', timeout=1)
                        answer_check=json.loads(answer.content)
                        if answer.status_code != 200:
                            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            return redirect(reverse('experiment:index_adjustment'))
                    except Timeout as e:
                        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                        logger.error(e)
                        return redirect(reverse('experiment:index_adjustment'))
                    except BaseException as e:
                        logger.error(e)
                        messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                        return redirect(reverse('experiment:index_adjustment'))
                    if answer_check['success'] == True:
                        messages.success(request, u'Текущее положение установлено за 0.')
                        tomo.state ='adjustment'
                        tomo.save()
                    else:
                        logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                        messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
            if 'gate' in request.POST:
                if request.POST['text_gate'] == 'open': #открыть заслонку
                    try:
                    	print tomo.state
                        answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/open/0', timeout=1)
                        answer_check=json.loads(answer.content)
                        if answer.status_code != 200:
                            messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                            return redirect(reverse('experiment:index_adjustment'))
                    except Timeout as e:
                        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                        logger.error(e)
                        return redirect(reverse('experiment:index_adjustment'))
                    except BaseException as e:
                        logger.error(e)
                        messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                        return redirect(reverse('experiment:index_adjustment'))
                    if answer_check['success'] == True:
                        messages.success(request, u'Заслонка открыта')
                        tomo.state ='adjustment'
                        tomo.save()
                    else:
                        logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                        messages.warning(request,u'Модуль "Эксперимент" неработает корректно в данный момент. Попробуйте позже')
                if request.POST['text_gate'] == 'close': #закрыть заслонку
                    try:
                        answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/close/0', timeout=1)
                        answer_check=json.loads(answer.content)
                        if answer.status_code != 200:
                                messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                                logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                                return redirect(reverse('experiment:index_adjustment'))
                    except Timeout as e:
                        messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
                        logger.error(e)
                        return redirect(reverse('experiment:index_adjustment'))
                    except BaseException as e:
                        logger.error(e)
                        messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                        return redirect(reverse('experiment:index_adjustment'))
                	if answer_check['success'] == True:
                		messages.success(request, u'Заслонка закрыта')
                		tomo.state='adjustment'
                		tomo.save()
                	else:
                		logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                		messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
            if 'experiment_on_voltage' in request.POST: #задать напряжение
                info = json.dumps(float(request.POST['voltage']))  
                try:
                    answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-voltage', info, timeout=1)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_adjustment'))
                except Timeout as e:
                    messages.warning(request, u'Нет ответа от модуля "Эксперимент".')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                except BaseException as e:
                    messages.warning(request, u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                print(answer_check)
                if answer_check['success'] == True:
                    messages.success(request, u'Напряжение установлено')
                    tomo.state ='adjustment'
                    tomo.save()
                else:
                    logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                    messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
            if 'experiment_on_current' in request.POST: #задать силу тока
                info = json.dumps(float(request.POST['current']))
                try:
                    answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-current', info, timeout=1)
                    answer_check = json.loads(answer.content)
                    if answer.status_code != 200:
                        messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
                        return redirect(reverse('experiment:index_adjustment'))
                except Timeout as e:
                    messages.warning(request, u'Нет ответа от модуля "Эксперимент".')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                except BaseException as e:
                    messages.warning(request, u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
                    logger.error(e)
                    return redirect(reverse('experiment:index_adjustment'))
                print(answer_check)
                if answer_check['success'] == True:
                    messages.success(request, u'Сила тока установлена')
                    tomo.state ='adjustment'
                    tomo.save()
                else:
                    logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                    messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
                    
            if 'picture_exposure_submit' in request.POST: #preview a picture
                try:
                    exposure = request.POST['picture_exposure']
                    #image_url = 'http://pngimg.com/upload/cat_PNG100.png'
                    #response = requests.get(image_url, stream=True)
                    image_url = 'http://109.234.34.140:5001/tomograph/1/detector/get-frame'
                    data = json.dumps(float(exposure))
                    response = requests.post(image_url, data, stream=True)
                    #print(response.content)
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
                            'full_access': (request.user.userprofile.role == 'EXP'),
                            'caption': 'Эксперимент',
                            'preview_path': os.path.join(settings.MEDIA_URL, file_name),
                            'preview': True,
                            'exposure': exposure,
                        }) 
                except BaseException as e:
                    messages.warning(request,u'Не удалось выполнить предпросмотр. Попробуйте повторно') 
                    logger.error(e)
	return render(request, 'experiment/adjustment.html', {
                'full_access': (request.user.userprofile.role == 'EXP'),
                'caption': 'Эксперимент',
                'state': tomo.state
            })                      

@login_required
@user_passes_test(has_experiment_access)          
def experiment_interface(request):
	tomo=get_object_or_404(Tomograph,pk=1)
	tomo.save()
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
				'experiment id': str(exp_id),
                'for storage':
                    {
                        'name':request.POST['name'],
                        'tegs':request.POST['type']
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
                })
			try:
		        	answer = requests.post('http://109.234.34.140:5001/tomograph/1/experiment/start', simple_experiment, timeout=1)
		        	answer_check=json.loads(answer.content)
		        	if answer.status_code != 200:
		        		messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
		        		logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
		        		return redirect(reverse('experiment:index_interface'))
		        except Timeout as e:
		        		messages.warning(request, u'Нет ответа от модуля "Эксперимент"')
		        		logger.error(e)
		        		return redirect(reverse('experiment:index_interface'))
		        except BaseException as e:
		        		logger.error(e)
		        		messages.warning(request, u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
		        		return redirect(reverse('experiment:index_interface'))
		        if answer_check['success'] == True:
		        		messages.success(request, u'Эксперимент успешно начался')
		        		tomo.state='experiment'
		        		tomo.save()
		        else:
		        		logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
		        		messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
		if 'turn_down' in request.POST:
		            try:    
		                answer = requests.get('http://109.234.34.140:5001/tomograph/1/experiment/stop', timeout=1)
		                answer_check=json.loads(answer.content)
		                if answer.status_code != 200:
		                    messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
		                    logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
		                    return redirect(reverse('experiment:index_interface'))
		            except Timeout as e:
		                messages.warning(request, u'Нет ответа от модуля "Эксперимент"')
		                logger.error(e)
		                return redirect(reverse('experiment:index_interface'))
		            except BaseException as e:
		                logger.error(e)
		                messages.warning(request, u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
		                return redirect(reverse('experiment:index_interface'))
		            if answer_check['success'] == True:
		                messages.success(request, u'Эксперимент окончен')
		                tomo.state ='off'
		                tomo.save()
		            else:
		            	logger.error(u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
		                messages.warning(request,u'Модуль "Эксперимент" работает некорректно в данный момент. Попробуйте позже')
	return render(request, 'experiment/interface.html', {
            'full_access': (request.user.userprofile.role == 'EXP'),
            'caption': 'Эксперимент',
            'tomo': tomo.state
        }) 
