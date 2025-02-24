from django.db import models
from django.contrib.auth.models import User


class Activity(models.Model):
    FOOD_CHOICES = [
        ('Italian'),
        ('Mexican'),
        ('American'),
        ('Chinese'),
    ]
    LOCATION_CHOICES = [
        ('Chicago')
    ]
    PEOPLE_CHOICES = [
        ('1'),
        ('2-3'),
        ('3-6'),
        ('6-10'),
        ('10+'),
    ]
    TIME_CHOICES = [
        ('Morning'),
        ('Afternoon'),
        ('Evening'),
        ('Night'),
    ]

    name = models.CharField(max_length=255)
    food = models.CharField(max_length=20, choices=FOOD_CHOICES)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    date = models.DateField()
    time = models.CharField(max_length=20, choices=TIME_CHOICES)
    num_people = models.CharField(max_length=10, choices=PEOPLE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


def __str__(self):
        return self.title