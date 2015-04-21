# coding=utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test


def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']

def power_on(request):
	requests.get('http://109.234.34.140:5001/module-experiment/v1.0/source/power-on')
	return render(request)



@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    return render(request, 'experiment/Interface.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
        'caption': 'Эксперимент',
    })
