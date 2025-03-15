from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator
from django.conf import settings  # Import settings to reference CustomUser

from django.db import models

class PlanConfirmation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to CustomUser

    favorite = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    formatted_date = models.CharField(max_length=255, null=True, blank=True)
    guests = models.IntegerField(null=True, blank=True)
    occasion = models.CharField(max_length=255, null=True, blank=True)
    order = models.TextField()

    restaurant_name = models.CharField(max_length=255, null=True, blank=True)
    restaurant_address = models.CharField(max_length=255, null=True, blank=True)

    restaurant_latitude = models.FloatField(null=True, blank=True)
    restaurant_longitude = models.FloatField(null=True, blank=True)
    event_latitude = models.FloatField(null=True, blank=True)
    event_longitude = models.FloatField(null=True, blank=True)

    event_name = models.CharField(max_length=255, null=True, blank=True)
    event_address = models.CharField(max_length=255, null=True, blank=True)

    title = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"Plan for {self.formatted_date or self.date} at {self.time} - {self.title or 'No Title'}"

class CustomUserManager(BaseUserManager):
    """Manager for custom user model with email as username"""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and return a regular user with an email"""
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100, default="")  # Use Django's built-in first_name
    last_name = models.CharField(max_length=100, default="")   # Use Django's built-in last_name

    phone_validator = RegexValidator(
        regex=r"^\d{10}$",
        message="Phone number must be exactly 10 digits, with no spaces or special characters."
    )
    phone = models.CharField(validators=[phone_validator], max_length=10, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)  # Use EmailField for email validation

    picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)  # Stores profile images
    location = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)

    interests = models.JSONField(default=list, blank=True)  # Stores a list of user interests
    favorite_cuisines = models.JSONField(default=list, blank=True)  # Stores a list of cuisines
    diet_restrictions = models.JSONField(default=list, blank=True)  # Stores a list of dietary restrictions

    objects = CustomUserManager()

def __str__(self):
        return self.title