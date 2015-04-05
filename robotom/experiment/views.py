from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test


def has_experiment_access(user):
    return user.userprofile.role in ['ADM', 'EXP']


@login_required
@user_passes_test(has_experiment_access)
def experiment_view(request):
    return render(request, 'experiment/experiment_index.html', {
        'full_access': (request.user.userprofile.role == 'EXP'),
    })

