from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    avatar = models.ImageField(default='avatars/random_avatar.jpg', upload_to="avatars")
    personal_info = models.TextField(blank=True, null=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)


class Group(models.Model):
    name = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_groups")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="user_groups")
    is_admin = models.BooleanField(default=False)
    is_extra_user = models.BooleanField(default=False)


class Game(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    image = models.ImageField(blank=True, null=True)
    user = models.ManyToManyField(User, related_name='games')


class Event(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(null=True)
    start_time = models.DateTimeField()
    user = models.ManyToManyField(User, related_name="user_events")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_events")
