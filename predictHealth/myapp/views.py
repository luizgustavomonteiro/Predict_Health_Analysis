from django.shortcuts import render
#from .models import Regions, Diseases, Notifications

# Create your views here.
# This is the controler, the brain behind the app

def home(request):
    return render(request, 'home.html', {})

def trends_views(request):
    return render(request, 'trends.html', {})

def maps_views(request):
    return render(request, 'maps.html', {})