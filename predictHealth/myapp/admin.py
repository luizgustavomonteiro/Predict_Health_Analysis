from django.contrib import admin
from .models import Regions, Notifications, Diseases
# Register your models here.

admin.site.register(Regions)
admin.site.register(Notifications)
admin.site.register(Diseases)