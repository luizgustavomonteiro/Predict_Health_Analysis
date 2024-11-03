from django.db import models

# Create your models here.

# Models to store de datadownloads from TabnetDataSus
# This data will be download using Selenium to mapping the webpage http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sinannet/cnv/denguebbr.def
# Check Script Selenium here C:\Dev\HealthPredict\predictHealth\myapp\selenium_scripts

# Classes for each table at database
class Diseases(models.Model):
    disease_id = models.AutoField(primary_key=True) #Automatically incrementing unique ID
    disease_name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.disease_name 


class Regions(models.Model):
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.region_name
    

class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True)
    disease = models.ForeignKey(Diseases, on_delete=models.CASCADE)
    region = models.ForeignKey(Regions, on_delete=models.CASCADE)
    notification_week = models.IntegerField()
    notification_year = models.IntegerField()
    cases_confirmed = models.IntegerField()
    deaths_confirmed = models.IntegerField()

    def __str__(self):
        return f"Notification for {self.disease} in {self.region} for Week {self.notification_week}, Year {self.notification_year}"


