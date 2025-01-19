from django.db import models

from django.contrib.auth.models import User


# Models
class URL(models.Model):
    original_url = models.URLField(unique=True)
    short_url = models.CharField(max_length=10, unique=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    expiration_time = models.DateTimeField()

class Analytics(models.Model):
    short_url = models.ForeignKey(URL, on_delete=models.CASCADE)
    access_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()


    

