from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator




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
    phone = models.CharField(validators=[phone_validator], max_length=10, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)  # Use EmailField for email validation



    PICTURE_CHOICES = [
        ("1", "Picture 1"),
        ("2", "Picture 2"),
    ]

    picture = models.CharField(max_length=1, choices=PICTURE_CHOICES, default="1")  # Now stored as string
    location = models.CharField(max_length=100, default="Chicago", editable=False)  # Always Chicago
    FOOD_CHOICES = [
        ("Chinese", "Chinese"),
        ("Italian", "Italian"),
        ("American", "American"),
        ("Mexican", "Mexican")
    ]
    favorite_food = models.CharField(max_length=10, choices=FOOD_CHOICES, default="American")
    biography = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()



def __str__(self):
        return self.title