from django.db import models

from weather.users_app.models import CustomUser


# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=128)
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='locations')
