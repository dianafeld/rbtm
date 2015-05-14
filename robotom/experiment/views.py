# coding=utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
import logging
import hashlib
import datetime
import random
import requests
import urllib2
import json
from models import Tomo, Experiment
#from rest_framework import request
#from rest_framework import status
#from rest_framework.decorators import api_view
#from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, StaticHTMLRenderer
#from rest_framework.response import Response
from requests.exceptions import Timeout
from django.forms import ValidationError
import uuid

logger = logging.getLogger('django.request')

def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']

@login_required
@user_passes_test(has_experiment_access)
#отправляет включить/выключить томограф,ток,напряжение,заслонку открыть/закрыть и т.д.
#@api_view(['GET','POST'])
   
def experiment_view(request):
	if request.method == 'POST':
		if 'on_exp' in request.POST:   #включить томограf
			try: #обработка ошибок
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
					#tomo.on = True
					#tomo.save()
			else:
				logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
				messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
		if 'of_exp' in request.POST:  #выключение томографа
			try:
				answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-off', timeout=1)
				answer_check=json.loads(answer.content)
				if answer.status_code != 200:
					messages.warning(request, u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
					logger.error(u'Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
					return redirect(reverse('experiment:index'))
			except Timeout as e:
				messages.warning(request, 'Нет ответа от модуля "Эксперимент".')
				logger.error(e)
				return redirect(reverse('experiment:index'))
			except BaseException as e:
				logger.error(e)
				messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
				return redirect(reverse('experiment:index'))
			if answer_check['success'] == True:
					messages.success(request, u'Томограф выключен')
			else:
				logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
				messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
	return render(request, 'experiment/start.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })
    
def experiment_adjustment(request):
	if request.method == 'POST':
		if 'gate' in request.POST:   #открыть заслонку
			if request.POST['text_gate'] == 'open':
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
			else:
				logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
				messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
		if 'experiment_on' in request.POST:
			Experiment.exp_id = uuid.uuid4()
			info = json.dumps({
				'experiment_id': str(Experiment.exp_id),
				'voltage': float(request.POST['voltage']),
				'current': float(request.POST['current'])
				})	
			try:
				answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-operating-mode', info, timeout=1)
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
			else:
				logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
				messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
	return render(request, 'experiment/adjustment.html', {
				'full_access': (request.user.userprofile.role == 'EXP'),
				'caption': 'Эксперимент',
			})						
          
def experiment_interface(request):
	if request.method == 'POST':
		if 'parameters' in request.POST:
			Experiment.exp_id = uuid.uuid4()
			simple_experiment = json.dumps({
				'experiment id': str(Experiment.exp_id),
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
						'count': request.POST['dark_quantity'],
						'exposure': request.POST['dark_exposure']
						},
						'EMPTY':
						{
						'count': request.POST['empty_quantity'],
						'exposure': request.POST['dark_exposure']
						},
						'DATA':
						{
						'step count':request.POST['data_quantity'],
						'exposure':request.POST['data_exposure'],
						'angle step': request.POST['data_angle'],
						'count per step': request.POST['data_same']
						}
					}
				}
				)
			try:
					answer = requests.post('http://109.234.34.140:5001/tomograph/1/experiment/begin', simple_experiment, timeout=1)
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
			else:
				logger.error(u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
				messages.warning(request,u'Модуль эксперимент не работает корректно в данный момент. Попробуйте позже')
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
