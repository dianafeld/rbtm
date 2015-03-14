from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def group1(request):
    return render(request, 'group_1.html')

def group2(request):
    return render(request, 'group_2.html')

def group3(request):
    return render(request, 'group_3.html')
