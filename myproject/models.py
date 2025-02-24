from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator




class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):

    Fname = models.CharField(max_length=100, default="")
    Lname = models.CharField(max_length=100, default="")
    phone_validator = RegexValidator(
        regex=r"^\d{10}$",
        message="Phone number must be exactly 10 digits, with no spaces or special characters."
    )
    Phone = models.CharField(validators=[phone_validator], max_length=10, unique=True, blank=True, null=True)



    PICTURE_CHOICES = [
        ("1", "Picture 1"),
        ("2", "Picture 2"),
    ]

    Picture = models.CharField(max_length=1, choices=PICTURE_CHOICES, default="1")  # Now stored as string
    Location = models.CharField(max_length=100, default="Chicago", editable=False)  # Always Chicago
    FOOD_CHOICES = [
        ("Chinese", "Chinese"),
        ("Italian", "Italian"),
        ("American", "American"),
        ("Mexican", "Mexican")
    ]
    Favorite_Food = models.CharField(max_length=10, choices=FOOD_CHOICES, default="American")
    Biography = models.CharField(max_length=255, blank=True, null=True)
    objects = CustomUserManager()



def __str__(self):
        return self.title