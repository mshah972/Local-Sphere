from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def SphereAi(request):
    return render(request, 'SphereAi.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')

def planConfirmation(request):
    return render(request, 'planConfirmation.html')

def forgot(request):
    return render(request, 'forgot.html')