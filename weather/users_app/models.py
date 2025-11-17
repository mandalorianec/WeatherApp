from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    username = models.CharField("Логин", max_length=30, unique=True, blank=False)
    email = models.EmailField("Email", max_length=30, unique=True, blank=False)

