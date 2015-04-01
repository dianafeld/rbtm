from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login
from forms import UserRegistrationForm, UserProfileRegistrationForm, UserRoleRequestForm
from models import UserProfile, RoleRequest
from django.contrib.auth.models import User
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



#If user's request is not actual now, no information should be provided in database
def flush_userprofile_request(userprofile):
    userprofile.rolerequest.role = 'NONE'
    userprofile.rolerequest.comment = ''
    userprofile.rolerequest.save()


@user_passes_test(is_superuser)
def manage_requests_view(request):
    if request.method == 'POST':
        profile_id = request.POST['profile_id']
        profile = get_object_or_404(UserProfile, pk=profile_id)
        if 'accept' in request.POST:
            profile.user.is_superuser = False # we must invalidate superuser and staff rights
            profile.user.is_staff = False     # if any error was made before
            profile.role = profile.rolerequest.role
            if profile.role == 'ADM':
                profile.user.is_superuser = True
                profile.user.is_staff = True
            profile.save()
            profile.user.save()
            flush_userprofile_request(profile)    
        elif 'decline' in request.POST:
            flush_userprofile_request(profile)
            
    request_list = [rolerequest.user for rolerequest in RoleRequest.objects.exclude(role='NONE')]
    return render(request, 'manage_requests.html', {
        'request_list': request_list,
    })


@login_required
def role_request_view(request):
    if request.method == 'POST':
        if User.objects.filter(pk=request.user.pk):
            role_request = RoleRequest.objects.get(user__user__pk=request.user.pk)
            role_form = UserRoleRequestForm(request.POST, instance=role_request)
        else:
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
        
    if User.objects.filter(pk=request.user.pk):
        role_request = RoleRequest.objects.get(user__user__pk=request.user.pk)
        role_form = UserRoleRequestForm(instance=role_request)
    else:
        role_form = UserRoleRequestForm()
    return render(request, 'role_request.html', {
        'role_form': role_form,
    })
