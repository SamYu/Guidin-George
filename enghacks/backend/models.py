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

class DirectionThread(models.Model): 

    current_step_options = [
        'USER_LOCATION',
        'DESTINATION',
        'DEST_CHOICES',
        'ARRIVED',
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL
    )
    current_step = models.CharField(
        choices=current_step_options,
        default=current_step_options[0]
    )
    date_time = models.DateTimeField(
        auto_now=True,
    )
    start_location = models.CharField()
    end_location = models.CharField()
    completed_at = models.DateTimeField()

    # def incrementStep(self):
    #     current_step = self.current_step
    #     current_step_index = self.current_step_options.index(current_step)

    #     self.update(
    #         current_step=self.current_step_options[current_step_index + 1]
    #     )

        