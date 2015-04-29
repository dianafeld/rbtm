# coding=utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login

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
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.response import Response


def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']

@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    return render(request, 'experiment/Interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })   
     
def check(request):
	if request.method == 'POST':
		if 'on' in request.POST:	   
			return render(request, 'experiment/Interface.html', {
		    'full_access': (request.user.userprofile.role == 'EXP'),
		    'caption': 'Эксперимент',
		}) 
		if 'off' in request.POST:	   
			return render(request, 'experiment/Interface.html', {
		    'full_access': (request.user.userprofile.role == 'EXP'),
		    'caption': 'Эксперимент',
		}) 
    
@api_view(['GET','POST'])
def experiment_start(request):
	if request.method == 'POST':
		if 'experiment_on' in request.POST:
			info = json.dumps({
				'experiment_id': '552aa5546c8dc50c93edacf0',
				'voltage': request.POST['voltage'],
				'current': request.POST['current']
				})
			req = requests.post('http://109.234.34.140:5001/tomograph/1/source/set-operating-mode', info)
		return render(request, 'experiment/Interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })
    
def send_parameters(request):
	if request.method == 'POST':
		if 'start_experiment' in request.POST:
				simple_experiment = json.dumps(
				{
				'experiment id': '552aa5546c8dc50c93edacf0',
				'advanced': False,
				'specimen': 'Gekkonidae',
				'DARK':
				{
				'count': 10,
				'exposure': 0.12
				},
				'EMPTY':
				{
				'count': 20,
				'exposure': 3
				},
				'DATA':
				{
				'step count': 6,
				'exposure': 3,
				'angle step': 1.34,
				'count per step': 1
				}
				}
				)
				requests.post('http://mardanov@109.234.34.140:5006/storage/experiments/post', simple_experiment)
				print("sgg")
				'''requests.post('http://109.234.34.140:5001/tomograph/1/experiment/start', simple_experiment)'''
		return render(request, 'experiment/Interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })	
        if 'load_from_database' in request.POST:
        	id = json.dumps({'experiment id': '552aa5546c8dc50c93edacf0'})
        	req = requests.post('http://mardanov@109.234.34.140:5006/storage/experiments/get', id)
        	parameters = json.loads(requests.data)    	
        return render(request, 'experiment/Interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })

''' function for viewing picture
			def plotImage(arr):
				fig = plt.figure(figsize=(5, 5), dpi=80, facecolor='w', edgecolor='w', frameon=True)
				imAx = plt.imshow(arr, origin='lower', interpolation='nearest')
				fig.colorbar(imAx, pad=0.01, fraction=0.1, shrink=1.00, aspect=20)'''
				    
def show_image(request):
	if request.method == 'POST':
		if 'show_image' in request.POST:
			info = json.dumps({
				'experiment_id': '552aa5546c8dc50c93edacf0'})
			requests.post('http://mardanov@109.234.34.140:5006/storage/frames/get', info)
			'''show image'''
		return render(request, 'experiment/Interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })
    	   


        
        
        
        

