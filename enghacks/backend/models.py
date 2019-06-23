from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils.timezone import now

class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, blank=False, unique=True)
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
        'IN_TRANSIT',
        'ARRIVED',
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    current_step = models.CharField(
        max_length=13,
        default=current_step_options[0]
    )
    date_time = models.DateTimeField(
        default=now,
    )
    start_location = models.CharField(
        null=True,
        blank=True,
        max_length=100,
    )
    end_location = models.CharField(
        null=True,
        blank=True,
        max_length=100,
    )
    completed_at = models.DateTimeField(
        null=True,
        auto_now=False,
    )

    def increment_step(self):
        current_step = self.current_step
        current_step_index = self.current_step_options.index(current_step)

        self.current_step = self.current_step_options[current_step_index + 1]
        self.save()

class Place(models.Model):
    direction_thread = models.ForeignKey(
        DirectionThread,
        on_delete=models.CASCADE,
        related_name='places_list'
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    distance = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=False,
    )
    address = models.CharField(
        max_length=100,
        blank=False,
    )
