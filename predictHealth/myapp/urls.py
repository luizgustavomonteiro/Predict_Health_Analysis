from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name ="home"),
    path('maps', views.maps_views, name = "maps"),
    path('trends', views.trends_views, name = "trends"),
]


