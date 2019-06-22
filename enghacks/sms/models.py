from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='')
    email = models.EmailField()
    city = models.CharField(max_length=30)

class UserHealthInformation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_information',
    )
    date_of_birth = models.DateField()
    allergies = ArrayField(
        models.CharField(max_length=30, blank=True),
        null=True,
        size=20
    )
