# coding=utf-8
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
import urllib2
import json
#from rest_framework import request
#from rest_framework import status
#from rest_framework.decorators import api_view
#from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, StaticHTMLRenderer
#from rest_framework.response import Response
from requests.exceptions import Timeout
from django.forms import ValidationError
import uuid

logger = logging.getLogger('django.request')

TOMO={'state':'off'}

def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']

@login_required
@user_passes_test(has_experiment_access)
#отправляет включить/выключить томограф,ток,напряжение,заслонку открыть/закрыть и т.д.
#@api_view(['GET','POST'])
   
def info_once_only(request, msg):
    if msg not in [m.message for m in get_messages(request)]:
        messages.info(request, msg)

def experiment_view(request):
	if TOMO['state'] == 'off':
		info_once_only(request, u'Текущее состояние томографа: выключен')
		if TOMO['state'] == 'waiting':
			messages.info_once_only(request, u'Текущее состояние томографа: ожидание')
			if TOMO['state'] == 'adjustment':
				messages.info_once_only(request, u'Текущее состояние томографа: юстировка')
				if TOMO['state'] == 'experiment':
					messages.info_once_only(request, u'Текущее состояние томографа: эксперимент')
	if request.method == 'POST':
		if 'on_exp' in request.POST:   #включить томограф
			if TOMO['state'] == 'off':
				try: 
					answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-on', timeout=1)
					print answer.content
					answer_check=json.loads(answer.content)
					if answer.status_code != 200:
						messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
						logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
						return redirect(reverse('experiment:index'))
				except Timeout as e:
					messages.warning(request, 'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже.')
					logger.error(e)
					return redirect(reverse('experiment:index'))
				except BaseException as e:
					logger.error(e)
					messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
					return redirect(reverse('experiment:index'))
				if answer_check['success'] == True:
						messages.success(request, u'Томограф включен')
						TOMO['state'] = 'waiting'
				else:
					logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
					messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			else:
				print TOMO['state']
				messages.warning(request,u'Томограф уже включен')
		if 'of_exp' in request.POST:  #выключение томографа
			if TOMO['state'] == 'waiting':
				try:
					answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-off', timeout=1)
					answer_check=json.loads(answer.content)
					if answer.status_code != 200:
						messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
						logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
				except Timeout as e:
					messages.warning(request, 'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже.')
					logger.error(e)
					return redirect(reverse('experiment:index'))
				except BaseException as e:
					logger.error(e)
					messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
					return redirect(reverse('experiment:index'))
				if answer_check['success'] == True:
						messages.success(request, u'Томограф включен')
						TOMO['state'] = 'off'
				else:
					logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
					messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			else:
				print TOMO['state']
				messages.warning(request,u'Томограф не может быть выключен.')
	return render(request, 'experiment/start.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })
    
def experiment_adjustment(request):
	if TOMO['state'] == 'off':
		info_once_only(request, u'Текущее состояние томографа: выключен')
		if TOMO['state'] == 'waiting':
			messages.info_once_only(request, u'Текущее состояние томографа: ожидание')
			if TOMO['state'] == 'adjustment':
				messages.info_once_only(request, u'Текущее состояние томографа: юстировка')
				if TOMO['state'] == 'experiment':
					messages.info_once_only(request, u'Текущее состояние томографа: эксперимент')
	if request.method == 'POST':
		if TOMO['state'] == 'waiting' or TOMO['state'] == 'adjustment' :
			if 'move_hor' in request.POST:   #подвинуть по горизонтали
					try:
						info = json.dumps({
						float(request.POST['move_hor'])
						})	
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
						TOMO['state'] = 'adjustment'
					else:
						logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
						messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			if 'move_ver' in request.POST:   #подвинуть по вертикали
					try:
						info = json.dumps({
						float(request.POST['move_ver'])
						})	
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
						TOMO['state'] = 'adjustment'
					else:
						logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
						messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			if 'rotate' in request.POST:   #повернуть
					try:
						info = json.dumps({
						float(request.POST['rotate'])
						})	
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
						TOMO['state'] = 'adjustment'
					else:
						logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
						messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			if 'reset' in request.POST:   #установить текущее положение за 0
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
						TOMO['state'] = 'adjustment'
					else:
						logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
						messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			if 'picture_exposure' in request.POST:   #установить текущее положение за 0
					try:
						info = json.dumps({
						float(request.POST['picture_exposure'])
						})	
						answer = requests.get('http://109.234.34.140:5001/tomograph/1/detector/get-frame', timeout=1)
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
						#показать картинку
						TOMO['state'] = 'adjustment'
					else:
						logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
						messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			if 'gate' in request.POST:
				if request.POST['text_gate'] == 'open': #открыть заслонку
					try:
						answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/open', timeout=1)
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
						TOMO['state'] = 'adjustment'
					else:
						logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
						messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
				if request.POST['text_gate'] == 'close': #закрыть заслонку
					try:
						answer = requests.get('http://109.234.34.140:5001/tomograph/1/shutter/close', timeout=1)
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
					TOMO['state'] = 'adjustment'
				else:
					logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
					messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			if 'experiment_on_voltage' in request.POST: #задать напряжение
				info = json.dumps({
					'voltage': float(request.POST['voltage'])
					})	
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
					messages.success(request, u'Настройки установлены')
					TOMO['state'] = 'adjustment'
				else:
					logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
					messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			if 'experiment_on_current' in request.POST: #задать силу тока
				info = json.dumps({
					'current': float(request.POST['current'])
					})
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
					messages.success(request, u'Настройки установлены')
					TOMO['state'] = 'adjustment'
				else:
					logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
					messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')	
		else:
			print TOMO['state']
			messages.warning(request,u'Невозможно установить параметры. Начните юстировку')
	return render(request, 'experiment/adjustment.html', {
				'full_access': (request.user.userprofile.role == 'EXP'),
				'caption': 'Эксперимент',
			})						
          
def experiment_interface(request):
	if TOMO['state'] == 'off':
		info_once_only(request, u'Текущее состояние томографа: выключен')
		if TOMO['state'] == 'waiting':
			messages.info_once_only(request, u'Текущее состояние томографа: ожидание')
			if TOMO['state'] == 'adjustment':
				messages.info_once_only(request, u'Текущее состояние томографа: юстировка')
				if TOMO['state'] == 'experiment':
					messages.info_once_only(request, u'Текущее состояние томографа: эксперимент')
	if request.method == 'POST':
		if 'parameters' in request.POST:
			if TOMO['state'] == 'waiting' or TOMO['state'] == 'adjustment':	
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
					}
					)
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
					TOMO['state'] = 'experiment'
				else:
					logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
					messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
			else:
				print TOMO['state']
				messages.warning(request,u'Эксперимент не может начаться. Проверьте, включен ли томограф.')
		if 'turn_down' in request.POST:
			if TOMO['state'] == 'experiment':
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
				if answer_check['message'] == 'Experiment was finished successfully':
					messages.success(request, u'Эксперимент окончен')
				else:
					if answer_check['message'] == 'Experiment was emergency stopped':
						messages.warning(request,u'Аварийное завершение эксперимента {}',error)
						logger.error(u'Аварийное завершение эксперимента {}',error)	
					else:
						logger.error(u'Эксперимент завершен кем-то еще.')
						messages.warning(request,u'Эксперимент завершен кем-то еще.')
			else:
				print TOMO['state']
				messages.warning(request,u'Нельзя закончить эксперимент. Проверьте, идет ли эксперимент.')
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
