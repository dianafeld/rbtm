from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import forms as auth_forms, views as auth_views
from django.contrib.auth import login as auth_login, authenticate as auth_authenticate
from forms import UserRegistrationForm, UserProfileRegistrationForm, UserRoleRequestForm
from models import UserProfile, RoleRequest
from django.core.context_processors import csrf


def index(request):
    return render(request, 'index.html')


def group1(request):
    return render(request, 'group_1.html')


def group2(request):
    return render(request, 'group_2.html')


def group3(request):
    return render(request, 'group_3.html')


def registration_view(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        userprofile_form = UserProfileRegistrationForm(request.POST)
        if user_form.is_valid() and userprofile_form.is_valid():
            user = user_form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            new_profile = userprofile_form.save(commit=False)
            new_profile.user = user
            new_profile.save()
            userprofile_form.save_m2m()
            auth_login(request, user)
            return redirect('/role_request')
        else:
            return render(request, 'registration/registration_form.html', {
                'user_form': user_form,
                'userprofile_form': userprofile_form,
            })

    return render(request, 'registration/registration_form.html', {
        'user_form': UserRegistrationForm(),
        'userprofile_form': UserProfileRegistrationForm(),
    })


@login_required
def profile_view(request):
    # TODO Eugene
    return render(request, 'empty.html')


def is_superuser(user):
    return user.is_superuser


def storage_view(request):
    # TODO
    return render(request, 'storage.html', {"record_range": xrange(10)})


def storage_record_view(request, storage_record_id):
    # TODO
    return render(request, 'storage_record.html',
                  {"record_id": storage_record_id})


@user_passes_test(is_superuser)
def manage_requests_view(request):
    if request.method == 'POST':
        if request.POST['verdict'] == 'cancel':
            pass
        else:
            pass
            return redirect('/role_request')

    request_list = [rolerequest.user for rolerequest in RoleRequest.objects.exclude(role='NONE')]
    return render(request, 'manage_requests.html', {
        'request_list': request_list,
    })


@login_required
def role_request_view(request):
    if request.method == 'POST':
        role_form = UserRoleRequestForm(request.POST)
        if role_form.is_valid():
            new_request = role_form.save(commit=False)
            new_request.user = request.user.userprofile
            new_request.save()
            role_form.save_m2m()
            return redirect('/accounts/register/complete')
        else:
            return render(request, 'role_request.html', {
                'role_form': role_form,
            })

    return render(request, 'role_request.html', {
        'role_form': UserRoleRequestForm(),
    })
