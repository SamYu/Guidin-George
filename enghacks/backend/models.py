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
    sex_choices = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_information',
    )
    sex = models.CharField(
        max_length=6,
        choices=sex_choices,
        null=True,
    )
    date_of_birth = models.DateField(
        auto_now = False,
        null=True,
        blank=True
    )
    allergies = ArrayField(
        models.CharField(max_length=30, blank=True),
        null=True,
        size=20
    )
