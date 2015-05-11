# coding=utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login

from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render_to_response
import logging
import hashlib
import datetime
import random
import requests
import urllib2
import json
import uuid
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.response import Response
from requests.exceptions import Timeout

experiment_id = False
user_with_experiment = False

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
    
def experiment_view_image(request):
    return render(request, 'experiment/show_image.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })     
             
@api_view(['GET','POST'])
def experiment_start(request):
	if request.method == 'POST':
		if 'experiment_on' in request.POST:
			experiment_id = uuid.uuid4()
			info = json.dumps({
				'experiment_id': str(experiment_id),
				'voltage': float(request.POST['voltage']),
				'current': float(request.POST['current'])
				})
			print("i am in experiment")
			try:
				answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-operating-mode', info, timeout=1)
				if answer.status_code != 200:
					messages.warning(request, u'Эксперимент не может начаться.Модуль "Эксперимент" завершился с кодом ошибки {}'.format(answer.status_code))
					logger.error(u'Эксперимент не может начаться.Модуль "Эксперимент" завершился с кодом ошибки {}'.format(answer.status_code))
		    		return redirect(reverse('experiment:start_experiment'))
				if answer.status_code == 200:
					user_with_experiment = request.user.id
					messages.success(request, 'Эксперимент начался')		                	        				
			except Timeout as e:
				messages.warning(request, 'Нет ответа от модуля "Эксперимент", попробуйте позже')
				logger.error(e)
				return redirect(reverse('experiment:start_experiment'))                  
	return render(request, 'experiment/adjustment.html', {
								'full_access': (request.user.userprofile.role == 'EXP'),
								'caption': 'Эксперимент',
							})						

def in_process(request):
	if request.method == 'POST':
		if 'processing' in request.POST:
			info = json.dumps({
				'experiment_id': str(experiment_id),
				})
			print("i am in process")
			answer = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-operating-mode', info)         				
	return render(request, 'experiment/interface.html', {
			'full_access': (request.user.userprofile.role == 'EXP'),
			'caption': 'Эксперимент',
		})
		
def show_image(request):
	if request.method == 'POST':
		if 'image_parameters' in request.POST:
				simple_experiment = json.dumps({
				'experiment id': str(experiment_id),
				'advanced': False,
				'specimen': 'Gekkonidae',
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
				'step count': request.POST['data_quantity'],
				'exposure': request.POST['data_exposure'],
				'angle step': request.POST['data_angle'],
				'count per step': request.POST['data_same']
				}
				}
				)
				requests.post('http://mardanov@109.234.34.140:5006/storage/experiments/post', simple_experiment)
				print("отправляем Рустаму данные показа изображения")
				requests.post('http://109.234.34.140:5001/tomograph/1/experiment/start', simple_experiment)
		return render(request, 'experiment/show_image.html', {
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
    	   


        
        
        
        

