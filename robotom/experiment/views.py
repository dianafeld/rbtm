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
#from rest_framework import request.Request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.response import Response
from requests.exceptions import Timeout
from django.forms import ValidationError
import uuid

logger = logging.getLogger('django.request')

def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']

@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    return render(request, 'experiment/start.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })
    
def experiment_view_adjustment(request):
    return render(request, 'experiment/adjustment.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })   
          
def experiment_view_interface(request):
    return render(request, 'experiment/interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })     
             
@api_view(['GET','POST'])
#отправляет ток,напряжение,заслонку и т.д.
def experiment_start(request):
	if request.method == 'GET':
		if 'turn_on':
			answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-on', timeout=1)
			answer_check=json.loads(answer.content)
			print(answer_check['success'])
			if answer_check['success'] == True:
				Tomo.condition = True
			return render(request, 'experiment/start.html', {
				'full_access': (request.user.userprofile.role == 'EXP'),
				'caption': 'Эксперимент',
			})
			try:
				answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-on', timeout=1)
				answer_check=json.loads(answer.content)
				if answer.status_code != "HTTP_200_OK":
					messages.warning(request, u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(123, answer.status_code))
					logger.error(u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(answer.status_code))
					return redirect(reverse('experiment:index'))
			except Timeout as e:
				messages.warning(request, 'Нет ответа от модуля "Эксперимент". {}.'. format(123))
				logger.error(e)
				return redirect(reverse('experiment:index'))
			except BaseException as e:
				logger.error(e)
				messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
				return redirect(reverse('experiment:index'))
				if answer_check['success'] == True:
					messages.success(request, u'Томограф включен')
		if 'turn_off':
			answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-off', timeout=1)
			answer_check=json.loads(answer.content)
			print(answer_check['success'])
			Tomo.condition = False
			return render(request, 'experiment/start.html', {
				'full_access': (request.user.userprofile.role == 'EXP'),
				'caption': 'Эксперимент',
			})	
			try:
				answer = requests.get('http://109.234.34.140:5001/tomograph/1/source/power-off', timeout=1)
				answer_check=json.loads(answer.content)
				if answer.status_code != "HTTP_200_OK":
					messages.warning(request, u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(123, answer.status_code))
					logger.error(u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(123, answer.status_code))
					return redirect(reverse('experiment:index'))
			except Timeout as e:
				messages.warning(request, 'Нет ответа от модуля "Эксперимент". {}.'. format(123))
				logger.error(e)
				return redirect(reverse('experiment:index'))
			except BaseException as e:
				logger.error(e)
				messages.warning(request, 'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
				return redirect(reverse('experiment:index'))
				if answer_check['success'] == True:
					messages.success(request, u'Томограф выключен')
	if request.method == 'POST':
		if 'experiment_on' in request.POST:
			Experiment.exp_id = uuid.uuid4()
			info = json.dumps({
				'experiment_id': str(Experiment.exp_id),
				'voltage': float(request.POST['voltage']),
				'current': float(request.POST['current'])
				})
			#answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-operating-mode', info, timeout=1)
			#answer_check=json.loads(answer.content)
			#print(answer_check['success'])	
			try:
					answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-operating-mode', info, timeout=1)
					if answer.status_code != "HTTP_200_OK":
						messages.warning(request, u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(123, answer.status_code))
						logger.error(u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(123, answer.status_code))
						return redirect(reverse('experiment:index_adjustment'))
			except Timeout as e:
				messages.warning(request, u'Нет ответа от модуля "Эксперимент". {}.'. format(123, answer.status_code))
				logger.error(e)
				return redirect(reverse('experiment:index_adjustment'))
			except BaseException as e:
				messages.warning(request, u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
				logger.error(e)
				return redirect(reverse('experiment:index_adjustment'))
				if answer_check['success'] == True:
					messages.success(request, u'Настройки установлены')
		return render(request, 'experiment/adjustment.html', {
					'full_access': (request.user.userprofile.role == 'EXP'),
					'caption': 'Эксперимент',
				})						
		
def in_process(request):
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
					if answer.status_code != "HTTP_200_OK":
						messages.warning(request, u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(123, answer.status_code))
						logger.error(u'{}. Модуль "Эксперимент" завершил работу с кодом ошибки {}'.format(123, answer.status_code))
						return redirect(reverse('experiment:send_parameters'))
			except Timeout as e:
					messages.warning(request, u'Нет ответа от модуля "Эксперимент". {}.'. format(123))
					logger.error(e)
					return redirect(reverse('experiment:send_parameters'))
			except BaseException as e:
					logger.error(e)
					messages.warning(request, u'Ошибка связи с модулем "Эксперимент", невозможно сохранить данные. Возможно, отсутствует подключение к сети. Попробуйте снова через некоторое время или свяжитесь с администратором')
					return redirect(reverse('experiment:send_parameters'))
					if answer_check['success'] == True:
						messages.success(request, u'Настройки установлены')
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
        
        
        

