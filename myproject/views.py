from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
def SphereAi(request):
    return render(request, 'SphereAi.html')