from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

def index(request):
    return render(request, 'index.html')

def group1(request):
    return render(request, 'group_1.html')

def group2(request):
    return render(request, 'group_2.html')

def group3(request):
    return render(request, 'group_3.html')

@login_required
def profile_view(request):
    #TODO Eugene
    return render(request, 'empty.html')

def has_experiment_access(user):
    return (user.userprofile.role in ['ADM', 'RES', 'EXP'])

@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    return render(request, 'experiment.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
    })

def storage_view(request):
    #TODO
    return render(request, 'storage.html', {"record_range": xrange(10)})

def storage_record_view(request, storage_record_id):
    #TODO
    return render(request, 'storage_record.html', 
        {"record_id": storage_record_id})
