from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    avatar = models.ImageField(blank=True, default='random.jpg')
    personal_info = models.TextField(null=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)


class Game(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    image = models.ImageField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='games')
