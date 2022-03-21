from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(blank=True)
    friends = models.ManyToManyField(User, related_name='friends')


class Game(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    image = models.ImageField(blank=True)
    users = models.ManyToManyField(User, related_name='games')

