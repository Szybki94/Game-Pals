from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils.timezone import now

import datetime


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    avatar = models.ImageField(default='avatars/random_avatar.jpg', upload_to="avatars")
    personal_info = models.TextField(blank=True, null=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)


class Invitation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    accepted = models.BooleanField(null=True)


class Group(models.Model):
    name = models.CharField(max_length=256)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user", blank=True, null=True)
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
    user = models.ManyToManyField(User, related_name='games', through='UserGames')


class UserGames(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)


class Event(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(null=True)
    start_time = models.DateTimeField()
    user = models.ManyToManyField(User, related_name="user_events", null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_events", null=True, blank=True)

    def __str__(self):
        text = "{0:40s} - {1:10d}"
        return text.format(self.name, self.id)  # to formatowanie nie działa w wyświetlaniu napisu na admin ;(


class Comment(models.Model):
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_comments")

    def __str__(self):
        return f"{self.create_date.strftime('%d/%m/%Y, %H:%M')} - {self.group_id}"
